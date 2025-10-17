from flask_socketio import Namespace, emit, join_room, leave_room
from .storage import get_or_create_chat, add_message, get_room_key
from .telegram_bot import send_text_for_room, notify_telegram
from .config import cfg
from bleach import clean
import logging

logger = logging.getLogger(__name__)

def validate_and_sanitize(text, max_length=500):
    """Input validation and sanitization"""
    if not isinstance(text, str):
        raise ValueError("Input must be string")
    if len(text) == 0 or len(text) > max_length:
        raise ValueError(f"Text length must be 1-{max_length}")
    return clean(text, tags=[], strip=True)

ROOM_STATE = {}

class ChatNS(Namespace):
    def __init__(self, ns, sio):
        super().__init__(ns)
        self.sio = sio

    def on_connect(self):
        logger.info(f"Client connected to chat namespace: {self.sid}")
    
    def on_disconnect(self):
        logger.info(f'ChatNS disconnect: {self.sid}')

    def on_join(self, data):
        try:
            chat_id = data.get('chat_id')
            name = data.get('name', 'Misafir')
            if not chat_id:
                emit('error', {'msg': 'Missing chat_id'})
                return
            name = validate_and_sanitize(name, max_length=50)
            join_room(chat_id)
            get_or_create_chat(chat_id, name)
            logger.info(f"User {name} joined chat {chat_id}")
            send_text_for_room(chat_id, f"✅ {name} chat'e girdi")
            notify_telegram(chat_id, 'text', f"👋 {name} joined chat {chat_id}", None, name)
            emit('room:key', {'room_key': get_room_key(chat_id)})
        except ValueError as e:
            logger.warning(f"Join validation error: {e}")
            emit('error', {'msg': str(e)})
        except Exception as e:
            logger.error(f"Join error: {e}")
            emit('error', {'msg': 'Server error'})

    def on_send(self, data):
        try:
            chat_id = data.get('chat_id')
            role = data.get('role', 'user')
            type_ = data.get('type', 'text')
            text = data.get('text', '')
            name = data.get('name', 'Customer')
            
            if not all([chat_id, role, type_]):
                emit('error', {'msg': 'Missing fields'})
                return
            
            if role not in ['user', 'admin']:
                emit('error', {'msg': 'Invalid role'})
                return
            
            if type_ not in ['text', 'image', 'audio']:
                emit('error', {'msg': 'Invalid type'})
                return
            
            if type_ == 'text':
                text = validate_and_sanitize(text, max_length=500)
            
            name = validate_and_sanitize(name, max_length=50)
            db_chat_id = get_or_create_chat(chat_id)
            add_message(db_chat_id, role, type_, text)
            logger.info(f"Message sent in {chat_id}: {role} - {type_}")
            emit('chat:message', {'chat_id': chat_id, 'role': role, 'type': type_, 'text': text, 'name': name}, to=chat_id, include_self=False)
            
            if role == 'user':
                notify_telegram(chat_id, type_, text, text if type_ in ['image', 'audio'] else None, name)
        except ValueError as e:
            logger.warning(f"Send validation error: {e}")
            emit('error', {'msg': str(e)})
        except Exception as e:
            logger.error(f"Send error: {e}")
            emit('error', {'msg': 'Server error'})

class CallNS(Namespace):
    def __init__(self, ns, sio):
        super().__init__(ns)
        self.sio = sio

    def on_join(self, data):
        if not cfg.ENABLE_CALLS:
            emit('error', {'code': 'calls_disabled'})
            return
        
        from .storage import verify_room_key
        room = data.get('room') or data.get('chat_id')
        room_key = data.get('room_key')
        
        if cfg.REQUIRE_ROOM_KEY:
            if not room_key or not verify_room_key(room, room_key):
                logger.warning(f"join.rejected room={room} reason=invalid_key")
                emit('error', {'code': 'invalid_room_key'})
                return
        
        state = ROOM_STATE.setdefault(room, {'accepted': False, 'members': set()})
        
        if len(state['members']) >= cfg.MAX_ROOM_MEMBERS:
            logger.warning(f"join.rejected room={room} reason=room_full")
            emit('error', {'code': 'room_full'})
            return
        
        state['members'].add(self.sid)
        join_room(room)
        logger.info(f"call.joined room={room} sid={self.sid}")

    def on_call_ring(self, data):
        if not cfg.ENABLE_CALLS:
            return
        room = data.get('room') or data['chat_id']
        logger.info(f"call.ring room={room}")
        emit('call:incoming', {'chat_id': room, 'fromName': data.get('from')}, to=room, include_self=False)

    def on_call_accept(self, data):
        if not cfg.ENABLE_CALLS:
            return
        room = data.get('room') or data['chat_id']
        state = ROOM_STATE.get(room)
        if state:
            state['accepted'] = True
        logger.info(f"call.accepted room={room}")
        emit('call:accepted', {'chat_id': room}, to=room)

    def on_call_decline(self, data):
        room = data.get('room') or data['chat_id']
        logger.info(f"call.declined room={room}")
        emit('call:declined', {'chat_id': room}, to=room)

    def on_rtc_offer(self, data):
        if not cfg.ENABLE_CALLS:
            return
        room = data.get('room') or data['chat_id']
        state = ROOM_STATE.get(room)
        if not state or not state.get('accepted'):
            logger.warning(f"rtc.blocked room={room} event=offer")
            return
        emit('rtc:offer', data, to=room, include_self=False)

    def on_rtc_answer(self, data):
        if not cfg.ENABLE_CALLS:
            return
        room = data.get('room') or data['chat_id']
        state = ROOM_STATE.get(room)
        if not state or not state.get('accepted'):
            logger.warning(f"rtc.blocked room={room} event=answer")
            return
        emit('rtc:answer', data, to=room, include_self=False)

    def on_rtc_candidate(self, data):
        if not cfg.ENABLE_CALLS:
            return
        room = data.get('room') or data['chat_id']
        state = ROOM_STATE.get(room)
        if not state or not state.get('accepted'):
            logger.warning(f"rtc.blocked room={room} event=candidate")
            return
        emit('rtc:candidate', data, to=room, include_self=False)

    def on_call_end(self, data):
        try:
            room = data.get('room') or data.get('chat_id')
            if not room:
                logger.warning('call:end missing room')
                return
            
            if room not in ROOM_STATE:
                logger.warning(f'call:end for non-existent room: {room}')
                return
            
            state = ROOM_STATE[room]
            state['accepted'] = False
            
            emit('call:ended', {'chat_id': room}, to=room)
            logger.info(f"call.ended room={room}")
        except Exception as e:
            logger.error(f"on_call_end error: {e}")

    def on_disconnect(self):
        sid = self.sid
        logger.info(f'CallNS disconnect: {sid}')
        
        try:
            rooms_to_delete = []
            
            for room_id, state in list(ROOM_STATE.items()):
                if sid in state.get('members', set()):
                    state['members'].discard(sid)
                    leave_room(room_id)
                    logger.debug(f'Removed {sid} from room {room_id}')
                    
                    if not state['members']:
                        rooms_to_delete.append(room_id)
                        logger.info(f'Room {room_id} is now empty, marking for cleanup')
            
            for room_id in rooms_to_delete:
                del ROOM_STATE[room_id]
                logger.info(f'Deleted empty room {room_id}')
                
        except Exception as e:
            logger.error(f"disconnect.error: {e}")
