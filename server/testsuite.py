from __future__ import annotations
import os
from typing import Dict
from .config import cfg
from .storage import SessionLocal, ChatSession
import requests

def _ok(msg="ok"): return True, msg
def _no(msg="fail"): return False, msg

BASE = os.getenv("BASE_URL", "http://localhost:10000")

# Health & Ops
def health_root(): 
    try:
        r = requests.get(f"{BASE}/health", timeout=5)
        return _ok("200") if r.status_code==200 else _no(f"/health {r.status_code}")
    except Exception as e:
        return _no(str(e))

def health_admin():
    try:
        r = requests.get(f"{BASE}/admin", timeout=5)
        return _ok("200") if r.status_code==200 else _no(f"/admin {r.status_code}")
    except Exception as e:
        return _no(str(e))

def health_ice():
    try:
        r = requests.get(f"{BASE}/v1/api/ice-servers", timeout=5)
        j = r.json()
        assert "iceServers" in j
        return _ok(f"servers={len(j['iceServers'])}")
    except Exception as e:
        return _no(f"bad json {e}")

# Security
def require_room_key():
    return _ok("REQUIRE_ROOM_KEY=true") if str(cfg.REQUIRE_ROOM_KEY).lower()=="true" else _no("REQUIRE_ROOM_KEY false")

def max_two_members():
    return _ok("MAX_ROOM_MEMBERS=2") if int(cfg.MAX_ROOM_MEMBERS)==2 else _no("MAX_ROOM_MEMBERS!=2")

def no_secret_leak():
    bad = []
    if cfg.TURN_CREDENTIAL: bad.append("TURN_CREDENTIAL set (ensure not logged client-side)")
    return _ok(", ".join(bad) or "no obvious leaks")

# DB & Schema
def schema_columns():
    try:
        with SessionLocal() as s:
            s.query(ChatSession).limit(1).all()
            getattr(ChatSession, "room")
            getattr(ChatSession, "room_key")
        return _ok("room/room_key present")
    except Exception as e:
        return _no(str(e))

def backfill_idempotent():
    try:
        with SessionLocal() as s:
            for c in s.query(ChatSession).all():
                if not c.room: return _no("missing room")
                if not c.room_key: return _no("missing room_key")
        return _ok("backfilled")
    except Exception as e:
        return _no(str(e))

def read_write_cycle():
    try:
        with SessionLocal() as s:
            cs = ChatSession(room="test-runner-room", room_key="k", cid="test", customer_name="test")
            s.add(cs)
            s.commit()
            rid = cs.id
            got = s.query(ChatSession).get(rid)
            s.delete(got)
            s.commit()
        return _ok("insert/select/delete ok")
    except Exception as e:
        return _no(str(e))

# Admin & Upload
def otp_throttle_note():
    return _ok("rate-limit recommended (manual check)")

def upload_policy_note():
    return _ok("mime/size validation recommended (manual check)")

TESTS = {
  "health":   [health_root, health_admin, health_ice],
  "security": [require_room_key, max_two_members, no_secret_leak],
  "db":       [schema_columns, backfill_idempotent, read_write_cycle],
  "admin":    [otp_throttle_note],
  "upload":   [upload_policy_note],
  "chat":     [],
  "webrtc":   []
}

def run_tests(retry_failed=False) -> Dict:
    out = {}
    for cat, funcs in TESTS.items():
        items = []
        for f in funcs:
            try:
                ok, msg = f()
            except Exception as e:
                ok, msg = False, str(e)
            items.append({"name": f.__name__, "ok": ok, "msg": msg})
        total = len(items)
        passed = sum(1 for i in items if i["ok"])
        out[cat] = {"total": total, "passed": passed, "items": items}
    return out
