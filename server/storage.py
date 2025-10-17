from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from .config import cfg

Base = declarative_base()
engine = create_engine(cfg.DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(Integer, primary_key=True)
    cid = Column(String, unique=True, index=True)
    customer_name = Column(String)
    room = Column(String, unique=True, index=True)
    room_key = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String)
    type = Column(String)
    text = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted = Column(Boolean, default=False)
    chat = relationship("ChatSession", back_populates="messages")

class AdminSession(Base):
    __tablename__ = "admin_sessions"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TestSchedule(Base):
    __tablename__ = "test_schedules"
    id = Column(Integer, primary_key=True)
    time_hhmm = Column(String)
    enabled = Column(Boolean, default=True)
    tz = Column(String, default=cfg.TZ)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return dict(id=self.id, time_hhmm=self.time_hhmm, enabled=self.enabled, tz=self.tz)

def init_db():
    Base.metadata.create_all(engine)

def get_or_create_chat(cid, customer_name=None, room=None, room_key=None):
    from .utils import generate_secret
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(cid=cid).first()
        if not chat:
            chat = ChatSession(
                cid=cid,
                customer_name=customer_name or "Misafir",
                room=room or cid,
                room_key=room_key or generate_secret()
            )
            s.add(chat)
            s.commit()
            s.refresh(chat)
        return chat.id

def get_chat_by_room(room):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room, active=True).first()
        return chat

def verify_room_key(room, room_key):
    with SessionLocal() as s:
        chat = s.query(ChatSession).filter_by(room=room, room_key=room_key, active=True).first()
        return chat is not None

def get_room_key(cid):
    with SessionLocal() as s:
        c = s.query(ChatSession).filter_by(cid=cid).first()
        return c.room_key if c else None

def add_message(chat_id, role, type_, text=None, media_url=None):
    with SessionLocal() as s:
        m = Message(chat_id=chat_id, role=role, type=type_, text=text, media_url=media_url)
        s.add(m)
        s.commit()
        s.refresh(m)
        return m

def list_chats():
    with SessionLocal() as s:
        return [(c.id, c.cid, c.customer_name, c.created_at) for c in s.query(ChatSession).filter_by(active=True).order_by(ChatSession.created_at.desc()).all()]

def get_messages(chat_id):
    with SessionLocal() as s:
        rows = s.query(Message).filter_by(chat_id=chat_id, deleted=False).order_by(Message.created_at.desc()).limit(100).all()
        rows.reverse()
        return [(m.role, m.type, m.text, m.media_url, m.created_at) for m in rows]

def delete_chat(chat_id):
    with SessionLocal() as s:
        chat = s.get(ChatSession, chat_id)
        if chat:
            chat.active = False
            s.commit()

def list_test_schedules():
    with SessionLocal() as s:
        return s.query(TestSchedule).order_by(TestSchedule.time_hhmm).all()

def add_test_schedule(time_hhmm, enabled=True, tz=None):
    with SessionLocal() as s:
        row = TestSchedule(time_hhmm=time_hhmm, enabled=enabled, tz=tz or cfg.TZ)
        s.add(row)
        s.commit()
        s.refresh(row)
        return row

def update_test_schedule(rid, time_hhmm=None, enabled=None, tz=None):
    with SessionLocal() as s:
        row = s.get(TestSchedule, rid)
        if not row:
            return None
        if time_hhmm is not None:
            row.time_hhmm = time_hhmm
        if enabled is not None:
            row.enabled = enabled
        if tz is not None:
            row.tz = tz
        row.updated_at = datetime.utcnow()
        s.commit()
        s.refresh(row)
        return row

def delete_test_schedule(rid):
    with SessionLocal() as s:
        row = s.get(TestSchedule, rid)
        if row:
            s.delete(row)
            s.commit()
