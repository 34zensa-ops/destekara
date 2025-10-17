const socket = io('/chat');
const callSocket = io('/call');
const msgs = document.getElementById('msgs');
const txt = document.getElementById('txt');

let roomKey = null;
let chatId = null;
let pc = null;
let userName = null;

const nameModal = document.getElementById('nameModal');
const nameInput = document.getElementById('nameInput');
const btnStartChat = document.getElementById('btnStartChat');

// Check if user already has a name
userName = localStorage.getItem('name');
if (userName) {
  startChat(userName);
} else {
  nameModal.style.display = 'flex';
}

btnStartChat.onclick = () => {
  const name = nameInput.value.trim();
  if (!name) {
    alert('Lütfen adınızı girin');
    return;
  }
  if (name.length > 30) {
    alert('İsim en fazla 30 karakter olabilir');
    return;
  }
  localStorage.setItem('name', name);
  startChat(name);
};

nameInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') btnStartChat.click();
});

function startChat(name) {
  userName = name;
  chatId = `${userName}-${Math.random().toString(16).slice(2, 8)}`;
  
  nameModal.style.display = 'none';
  document.getElementById('chatContainer').classList.add('active');
  
  socket.emit('join', { chat_id: chatId, name: userName });
}

socket.on('room:key', (data) => {
  roomKey = data.room_key;
  callSocket.emit('join', { chat_id: chatId, room: chatId, room_key: roomKey });
});

document.getElementById('btnSend').onclick = () => {
  const text = txt.value.trim();
  if (!text) return;
  const m = { role: 'user', type: 'text', text, name: userName, time: ts() };
  renderMsg(msgs, m);
  socket.emit('send', { chat_id: chatId, ...m });
  txt.value = '';
};

txt.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') document.getElementById('btnSend').click();
});

document.getElementById('btnImg').onclick = () => {
  document.getElementById('fileImg').click();
};

document.getElementById('btnAud').onclick = () => {
  document.getElementById('fileAud').click();
};

document.getElementById('fileImg').onchange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (!file.type.startsWith('image/')) { alert('Images only'); return; }
  if (file.size > 5 * 1024 * 1024) { alert('Max 5MB'); return; }
  const reader = new FileReader();
  reader.onload = () => {
    const m = { role: 'user', type: 'image', text: reader.result, name: userName, time: ts() };
    renderMsg(msgs, m);
    socket.emit('send', { chat_id: chatId, ...m });
  };
  reader.readAsDataURL(file);
};

document.getElementById('fileAud').onchange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (!file.type.startsWith('audio/')) { alert('Audio only'); return; }
  if (file.size > 10 * 1024 * 1024) { alert('Max 10MB'); return; }
  const reader = new FileReader();
  reader.onload = () => {
    const m = { role: 'user', type: 'audio', text: reader.result, name: userName, time: ts() };
    renderMsg(msgs, m);
    socket.emit('send', { chat_id: chatId, ...m });
  };
  reader.readAsDataURL(file);
};

socket.on('chat:message', (m) => {
  renderMsg(msgs, { ...m, role: 'admin', time: ts() });
});

document.getElementById('btnCall').onclick = async () => {
  try {
    document.getElementById('chatContainer').classList.remove('active');
    document.getElementById('callScreen').classList.add('active');
    
    pc = await initCall(callSocket, chatId);
    bindAnswering(callSocket, pc, chatId);
    await startOfferFlow(callSocket, pc, chatId, userName);
  } catch (error) {
    console.error('Arama başlatma hatası:', error);
    document.getElementById('chatContainer').classList.add('active');
    document.getElementById('callScreen').classList.remove('active');
    alert('Arama başlatılamadı: ' + error.message);
  }
};

callSocket.on('call:incoming', async (data) => {
  if (confirm(`${data.fromName || 'Admin'} arıyor. Kabul edilsin mi?`)) {
    try {
      callSocket.emit('call:accept', { chat_id: chatId });
      if (!pc) {
        pc = await initCall(callSocket, chatId);
        bindAnswering(callSocket, pc, chatId);
      }
      document.getElementById('chatContainer').classList.remove('active');
      document.getElementById('callScreen').classList.add('active');
    } catch (error) {
      console.error('Arama kabul hatası:', error);
      alert('Arama kabul edilemedi: ' + error.message);
      callSocket.emit('call:decline', { chat_id: chatId });
    }
  } else {
    callSocket.emit('call:decline', { chat_id: chatId });
  }
});

callSocket.on('call:ended', () => {
  if (pc) {
    pc.close();
    pc = null;
  }
  alert('Arama sonlandı');
});

setupEmojiPicker(txt);
