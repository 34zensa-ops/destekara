const socket = io('/chat');
const callSocket = io('/call');
const threads = document.getElementById('threads');
const msgs = document.getElementById('msgs');
const txt = document.getElementById('txt');
let currentChatId = null;
let currentDbId = null;
let currentRoomKey = null;
let isLoggedIn = false;

document.getElementById('btnOtp').onclick = () => {
  const otp = document.getElementById('otp').value.trim();
  if (otp === 'demo') {
    isLoggedIn = true;
    document.getElementById('otpModal').style.display = 'none';
    document.querySelector('.admin-panel').style.display = 'flex';
    loadChats();
  } else {
    alert('Geçersiz OTP');
  }
};

document.getElementById('otp').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') document.getElementById('btnOtp').click();
});

async function loadChats() {
  try {
    const res = await fetch('/api/chats');
    if (!res.ok) throw new Error('Failed to load chats');
    
    const chats = await res.json();
    if (!Array.isArray(chats)) throw new Error('Invalid response format');
    
    threads.innerHTML = '';
    chats.forEach(c => {
      const li = document.createElement('li');
      li.className = 'thread-item';
      
      const avatar = document.createElement('div');
      avatar.className = 'thread-avatar';
      avatar.textContent = '👤';
      
      const info = document.createElement('div');
      info.className = 'thread-info';
      
      const name = document.createElement('div');
      name.className = 'thread-name';
      name.textContent = c.name || 'Misafir';
      
      const preview = document.createElement('div');
      preview.className = 'thread-preview';
      preview.textContent = 'Son mesaj';
      
      const time = document.createElement('div');
      time.className = 'thread-time';
      time.textContent = new Date(c.created).toLocaleTimeString('tr-TR', {hour:'2-digit',minute:'2-digit'});
      
      info.appendChild(name);
      info.appendChild(preview);
      li.appendChild(avatar);
      li.appendChild(info);
      li.appendChild(time);
      li.onclick = () => openThread(c.id, c.cid, c.name);
      
      threads.appendChild(li);
    });
  } catch (error) {
    console.error('loadChats error:', error);
    alert('Sohbetler yüklenemedi: ' + error.message);
  }
}

async function openThread(dbId, cid, name) {
  try {
    currentChatId = cid;
    currentDbId = dbId;
    document.getElementById('threadTitle').textContent = name || cid;
    socket.emit('join', { chat_id: cid });
    
    try {
      const r = await fetch(`/api/chats/${encodeURIComponent(cid)}`);
      if (!r.ok) throw new Error('Room key fetch failed');
      const j = await r.json();
      if (!j.room_key) throw new Error('Invalid room key response');
      currentRoomKey = j.room_key;
      callSocket.emit('join', { chat_id: cid, room: cid, room_key: currentRoomKey });
    } catch(e) {
      console.error('room_key fetch failed', e);
    }
    
    msgs.innerHTML = '';
    
    document.getElementById('threadsSidebar').classList.add('hidden');
    document.getElementById('chatPanel').classList.add('active');

    const res = await fetch(`/api/chats/${dbId}/messages`);
    if (!res.ok) throw new Error('Failed to load messages');
    
    const messages = await res.json();
    if (!Array.isArray(messages)) throw new Error('Invalid messages format');
    
    messages.forEach(m => {
      renderMsg(msgs, { role: m.role, type: m.type, text: m.text, time: new Date(m.time).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) });
    });
  } catch (error) {
    console.error('openThread error:', error);
    alert('Sohbet açılamadı: ' + error.message);
  }
}

document.getElementById('btnSend').onclick = () => {
  if (!currentChatId || !isLoggedIn) return;
  const text = txt.value.trim();
  if (!text) return;
  const m = { role: 'admin', type: 'text', text, time: ts() };
  renderMsg(msgs, m);
  socket.emit('send', { chat_id: currentChatId, ...m });
  txt.value = '';
};

txt.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') document.getElementById('btnSend').click();
});

socket.on('chat:message', (m) => {
  if (m.chat_id === currentChatId) {
    renderMsg(msgs, { ...m, role: 'user', time: ts() });
  }
  loadChats();
});

document.getElementById('btnPhone').onclick = async () => {
  if (!currentChatId || !isLoggedIn) return;
  try {
    const pc = await initCall(callSocket, currentChatId);
    bindAnswering(callSocket, pc, currentChatId);
    await startOfferFlow(callSocket, pc, currentChatId);
  } catch (error) {
    console.error('Call initiation error:', error);
    alert('Arama başlatılamadı: ' + error.message);
  }
};

callSocket.on('call:incoming', async (data) => {
  if (data.chat_id === currentChatId) {
    if (confirm(`${data.fromName || 'Kullanıcı'} arıyor. Kabul edilsin mi?`)) {
      try {
        callSocket.emit('call:accept', { chat_id: currentChatId });
        const pc = await initCall(callSocket, currentChatId);
        bindAnswering(callSocket, pc, currentChatId);
      } catch (error) {
        console.error('Call accept error:', error);
        alert('Arama kabul edilemedi: ' + error.message);
        callSocket.emit('call:decline', { chat_id: currentChatId });
      }
    } else {
      callSocket.emit('call:decline', { chat_id: currentChatId });
    }
  }
});

document.getElementById('btnDelete').onclick = async () => {
  if (!currentDbId || !isLoggedIn) return;
  if (confirm('Bu sohbeti silmek istediğinize emin misiniz?')) {
    try {
      const res = await fetch(`/api/chats/${currentDbId}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      
      currentChatId = null;
      currentDbId = null;
      currentRoomKey = null;
      msgs.innerHTML = '';
      document.getElementById('threadTitle').textContent = 'Sohbet Seçin';
      document.getElementById('threadsSidebar').classList.remove('hidden');
      document.getElementById('chatPanel').classList.remove('active');
      loadChats();
    } catch (error) {
      console.error('Delete error:', error);
      alert('Sohbet silinemedi: ' + error.message);
    }
  }
};

document.getElementById('btnToTest').onclick = () => {
  window.location.href = '/test';
};

document.getElementById('btnImg').onclick = () => {
  document.getElementById('fileImg').click();
};

document.getElementById('btnAud').onclick = () => {
  document.getElementById('fileAud').click();
};

document.getElementById('fileImg').onchange = (e) => {
  if (!currentChatId || !isLoggedIn) return;
  const file = e.target.files[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) { alert('Images only'); return; }
  if (file.size > 5 * 1024 * 1024) { alert('Max 5MB'); return; }
  const reader = new FileReader();
  reader.onload = () => {
    const m = { role: 'admin', type: 'image', text: reader.result, time: ts() };
    renderMsg(msgs, m);
    socket.emit('send', { chat_id: currentChatId, ...m });
  };
  reader.readAsDataURL(file);
};

document.getElementById('fileAud').onchange = (e) => {
  if (!currentChatId || !isLoggedIn) return;
  const file = e.target.files[0];
  if (!file) return;
  if (!file.type.startsWith('audio/')) { alert('Audio only'); return; }
  if (file.size > 10 * 1024 * 1024) { alert('Max 10MB'); return; }
  const reader = new FileReader();
  reader.onload = () => {
    const m = { role: 'admin', type: 'audio', text: reader.result, time: ts() };
    renderMsg(msgs, m);
    socket.emit('send', { chat_id: currentChatId, ...m });
  };
  reader.readAsDataURL(file);
};

setupEmojiPicker(txt);
