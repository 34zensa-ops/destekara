from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
import logging
import os
from .config import cfg

load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from .storage import init_db, list_chats, get_messages, delete_chat, get_room_key
from .signaling import ChatNS, CallNS
from .scheduler import start_scheduler, refresh_jobs
from .telegram_bot import tg_bp
from .testsuite import run_tests
from .repair import run_repair, plan_safe, apply_safe
import threading
import time
import datetime as dt
import json

app = Flask(__name__, static_folder="../static", template_folder="../templates")
app.config.update(
    SECRET_KEY=cfg.SECRET_KEY,
    SESSION_COOKIE_SECURE=os.getenv('FLASK_ENV') == 'production',
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600,
    WTF_CSRF_TIME_LIMIT=None
)

csrf = CSRFProtect(app)

if os.getenv('FLASK_ENV') == 'production':
    from flask_talisman import Talisman
    Talisman(app, 
             force_https=True, 
             strict_transport_security_max_age=31536000,
             content_security_policy=False)

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{cfg.RATE_LIMIT_HOURLY}/hour", f"{cfg.RATE_LIMIT_DAILY}/day"],
    storage_uri="memory://"
)

ALLOWED = [o.strip() for o in cfg.ALLOWED_ORIGINS.split(',') if o.strip()]

@app.after_request
def cors(resp):
    o = request.headers.get('Origin')
    if o in ALLOWED:
        resp.headers['Access-Control-Allow-Origin'] = o
        resp.headers['Vary'] = 'Origin'
        resp.headers['Access-Control-Allow-Credentials'] = 'true'
    elif '*' in ALLOWED:
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.after_request
def security(resp):
    resp.headers.setdefault('X-Content-Type-Options', 'nosniff')
    resp.headers.setdefault('X-Frame-Options', 'DENY')
    resp.headers.setdefault('X-XSS-Protection', '1; mode=block')
    resp.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    if os.getenv('FLASK_ENV') == 'production':
        resp.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    resp.headers.setdefault('Content-Security-Policy',
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.socket.io; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' wss: https:; "
        "media-src 'self' blob:; "
        "frame-ancestors 'none';")
    return resp

socketio = SocketIO(app, cors_allowed_origins=ALLOWED if '*' not in ALLOWED else '*', async_mode='threading')

app.register_blueprint(tg_bp, url_prefix="/tg")

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/admin")
def admin():
    return render_template("admin.html")

@app.get("/test")
def test():
    return render_template("test.html")

@app.get("/health")
@app.get("/healthz")
@limiter.exempt
@csrf.exempt
def health():
    logger.info("Health check requested")
    return {"ok": True, "status": "healthy"}

# OTP System
_OTP_STORE = {}

@app.post("/api/admin/request-otp")
@limiter.limit("3 per minute")
@csrf.exempt
def request_otp():
    import random
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    _OTP_STORE['current'] = otp
    _OTP_STORE['timestamp'] = time.time()
    
    try:
        from .telegram_bot import send_text
        send_text(f"🔐 Admin OTP Kodu:\n\n{otp}\n\nGeçerlilik: 5 dakika")
        logger.info(f"OTP generated and sent to Telegram")
        return jsonify({"ok": True, "message": "OTP Telegram'a gönderildi"})
    except Exception as e:
        logger.error(f"OTP send error: {e}")
        return jsonify({"ok": False, "error": "Telegram yapılandırması eksik"}), 500

@app.post("/api/admin/verify-otp")
@limiter.limit("5 per minute")
@csrf.exempt
def verify_otp():
    data = request.get_json(silent=True) or {}
    otp = data.get('otp', '').strip()
    
    if 'current' not in _OTP_STORE:
        return jsonify({"ok": False, "error": "OTP bulunamadı. Lütfen yeni OTP isteyin."}), 400
    
    if time.time() - _OTP_STORE.get('timestamp', 0) > 300:
        del _OTP_STORE['current']
        return jsonify({"ok": False, "error": "OTP süresi doldu. Lütfen yeni OTP isteyin."}), 400
    
    if otp == _OTP_STORE['current']:
        del _OTP_STORE['current']
        logger.info("OTP verified successfully")
        return jsonify({"ok": True, "message": "Giriş başarılı"})
    else:
        logger.warning(f"Invalid OTP attempt: {otp}")
        return jsonify({"ok": False, "error": "Geçersiz OTP"}), 401

@app.get("/api/chats")
def get_chats():
    chats = list_chats()
    return jsonify([{"id": c[0], "cid": c[1], "name": c[2], "created": c[3].isoformat()} for c in chats])

@app.get("/api/chats/<int:chat_id>/messages")
def get_chat_messages(chat_id):
    msgs = get_messages(chat_id)
    return jsonify([{"role": m[0], "type": m[1], "text": m[2], "media": m[3], "time": m[4].isoformat()} for m in msgs])

@app.delete("/api/chats/<int:chat_id>")
@csrf.exempt
def del_chat(chat_id):
    delete_chat(chat_id)
    return {"ok": True}

@app.post("/api/chats/bulk-delete")
@csrf.exempt
def api_chat_bulk_delete():
    ids = (request.json or {}).get("cids", [])
    if not ids:
        return jsonify({"ok": True, "deleted": 0})
    from .storage import SessionLocal, ChatSession
    with SessionLocal() as s:
        q = s.query(ChatSession).filter(ChatSession.cid.in_(ids))
        count = 0
        for c in q.all():
            c.active = False
            count += 1
        s.commit()
    return jsonify({"ok": True, "deleted": count})

@app.post("/api/test/run")
@limiter.limit("10 per minute")
@csrf.exempt
def api_test_run():
    data = request.get_json(silent=True) or {}
    retry_failed = bool(data.get("retryFailed"))
    logger.info(f"Running tests (retry_failed={retry_failed})")
    out = run_tests(retry_failed=retry_failed)
    return jsonify(out)

@app.route("/api/repair/run", methods=["GET", "POST"])
@limiter.limit("5 per minute")
@csrf.exempt
def api_repair_run():
    data = request.get_json(silent=True) or {}
    mode = data.get("mode", "safe")
    dry = bool(data.get("dryRun", True))
    if mode != "safe":
        return jsonify({"error": "only safe mode enabled"}), 400
    logger.info(f"Running repair (mode={mode}, dry={dry})")
    if dry:
        return jsonify({"plan": plan_safe(), "applied": False})
    else:
        applied = apply_safe()
        return jsonify({"plan": plan_safe(), "applied": True, "result": applied})

_TEST_SCHEDULE = []
_SCHED_STOP = False

def _schedule_loop():
    last_run = set()
    while not _SCHED_STOP:
        now = dt.datetime.now().strftime("%H:%M")
        if now in _TEST_SCHEDULE and now not in last_run:
            res = run_tests()
            try:
                from .telegram_bot import notify_telegram
                notify_telegram('system', 'text', "🧪 Test run\n" + json.dumps(res)[:3500], None, 'System')
            except Exception:
                pass
            last_run.add(now)
        if dt.datetime.now().second == 0:
            last_run = {t for t in last_run if t == now}
        time.sleep(1)

threading.Thread(target=_schedule_loop, daemon=True).start()

@app.get("/api/test/schedule")
def api_test_schedule_get():
    return jsonify({"times": _TEST_SCHEDULE})

@app.post("/api/test/schedule")
@csrf.exempt
def api_test_schedule_post():
    data = request.get_json(silent=True) or {}
    t = data.get("time")
    if t and t not in _TEST_SCHEDULE:
        _TEST_SCHEDULE.append(t)
    return jsonify({"ok": True, "times": _TEST_SCHEDULE})

@app.delete("/api/test/schedule/<t>")
@csrf.exempt
def api_test_schedule_del(t):
    try:
        _TEST_SCHEDULE.remove(t)
    except ValueError:
        pass
    return jsonify({"ok": True, "times": _TEST_SCHEDULE})

@app.get("/v1/api/ice-servers")
def ice_servers():
    servers = [{"urls": "stun:stun.l.google.com:19302"}]
    if cfg.TURN_URL and cfg.TURN_USERNAME and cfg.TURN_CREDENTIAL:
        servers.append({"urls": cfg.TURN_URL, "username": cfg.TURN_USERNAME, "credential": cfg.TURN_CREDENTIAL})
    return jsonify({"iceServers": servers})

@app.get("/api/chats/<cid>")
def api_chat_get(cid):
    rk = get_room_key(cid)
    if not rk:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"room_key": rk})

@app.get("/debug/memory")
@limiter.exempt
def debug_memory():
    """Memory usage endpoint (development only)"""
    if os.getenv('FLASK_ENV') != 'development':
        return jsonify({"error": "Not available"}), 403
    
    try:
        import psutil
        from .signaling import ROOM_STATE
        
        process = psutil.Process()
        memory = process.memory_info()
        
        return jsonify({
            "rss_mb": round(memory.rss / 1024 / 1024, 2),
            "vms_mb": round(memory.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2),
            "room_state_size": len(ROOM_STATE),
            "rooms": list(ROOM_STATE.keys()),
            "room_details": {k: {"members": len(v.get('members', set())), "accepted": v.get('accepted', False)} for k, v in ROOM_STATE.items()}
        })
    except ImportError:
        return jsonify({"error": "psutil not installed"}), 500
    except Exception as e:
        logger.error(f"Memory debug error: {e}")
        return jsonify({"error": str(e)}), 500

socketio.on_namespace(ChatNS('/chat', socketio))
socketio.on_namespace(CallNS('/call', socketio))

def main():
    logger.info("Starting application...")
    init_db()
    start_scheduler()
    logger.info(f"Server running on port {os.environ.get('PORT', '10000')}")
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", "10000")), allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    main()
