from __future__ import annotations
from typing import Dict
from .storage import SessionLocal, ChatSession
from .signaling import ROOM_STATE
from .utils import generate_secret

def plan_safe() -> Dict:
    empty_rooms = [r for r, st in ROOM_STATE.items() if not (st.get('members') or set())]
    missing = 0
    with SessionLocal() as s:
        for c in s.query(ChatSession).all():
            if not getattr(c, "room", None) or not getattr(c, "room_key", None):
                missing += 1
    return {
        "room_state_cleanup": {"empty_rooms": empty_rooms},
        "db_backfill": {"missing_records": missing},
        "ice_reload": True,
        "session_purge": {"expired_example": 0}
    }

def apply_safe() -> Dict:
    applied = {"room_state_cleanup":0, "db_backfill":0, "ice_reload":True, "session_purge":0}

    # ROOM_STATE cleanup
    empty_rooms = [r for r, st in list(ROOM_STATE.items()) if not (st.get('members') or set())]
    for r in empty_rooms:
        ROOM_STATE.pop(r, None)
    applied["room_state_cleanup"] = len(empty_rooms)

    # DB backfill (idempotent)
    with SessionLocal() as s:
        cnt = 0
        for c in s.query(ChatSession).all():
            changed = False
            if not getattr(c, "room", None):
                c.room = getattr(c, "cid", None) or f"room-{generate_secret(8)}"
                changed = True
            if not getattr(c, "room_key", None):
                c.room_key = generate_secret()
                changed = True
            if changed: cnt += 1
        s.commit()
        applied["db_backfill"] = cnt

    return applied

def run_repair():
    return {"repaired": True, "message": "Use /api/repair/run with mode=safe"}
