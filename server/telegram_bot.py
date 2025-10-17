from flask import Blueprint, request
import requests
from .config import cfg
from .storage import SessionLocal, ChatSession, Message
from datetime import datetime

tg_bp = Blueprint("tg", __name__)

API = f"https://api.telegram.org/bot{cfg.TELEGRAM_BOT_TOKEN}"

def send_text(text, topic_id=None):
    if not cfg.TELEGRAM_BOT_TOKEN or not cfg.TELEGRAM_ADMIN_CHAT_ID:
        return
    payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "text": text}
    if topic_id:
        payload["message_thread_id"] = topic_id
    try:
        requests.post(f"{API}/sendMessage", json=payload, timeout=5)
    except:
        pass

def send_text_for_room(cid, text):
    send_text(f"[CID: {cid}]\n{text}")

def notify_telegram(cid, msg_type, text=None, media_url=None, customer_name=None):
    if not cfg.TELEGRAM_BOT_TOKEN or not cfg.TELEGRAM_ADMIN_CHAT_ID:
        return
    
    prefix = f"💬 {customer_name or 'Customer'} [CID: {cid}]"
    
    try:
        if msg_type == 'text' and text:
            payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "text": f"{prefix}\n{text}"}
            requests.post(f"{API}/sendMessage", json=payload, timeout=5)
        elif msg_type == 'image' and media_url:
            if media_url.startswith('data:image'):
                payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "caption": prefix, "photo": media_url}
                requests.post(f"{API}/sendPhoto", json=payload, timeout=5)
        elif msg_type == 'audio' and media_url:
            if media_url.startswith('data:audio'):
                payload = {"chat_id": cfg.TELEGRAM_ADMIN_CHAT_ID, "caption": prefix, "audio": media_url}
                requests.post(f"{API}/sendAudio", json=payload, timeout=5)
    except Exception as e:
        pass

@tg_bp.post("/webhook")
def webhook():
    upd = request.get_json(silent=True) or {}
    msg = upd.get("message") or upd.get("channel_post")
    if not msg:
        return {"ok": True}
    text = msg.get("text", "")
    cid = None
    if "[CID:" in text:
        try:
            cid = text.split("[CID:")[1].split("]")[0].strip()
        except:
            pass
    if not cid:
        return {"ok": True}
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(cid=cid).first()
        if not chat:
            return {"ok": True}
        m = Message(chat_id=chat.id, role="admin", type="text", text=text, created_at=datetime.utcnow())
        s.add(m)
        s.commit()
    return {"ok": True}
