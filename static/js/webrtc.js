async function initCall(socket, chatId) {
  try {
    const res = await fetch('/v1/api/ice-servers');
    if (!res.ok) throw new Error('ICE sunucuları alınamadı');
    const { iceServers } = await res.json();
    const pc = new RTCPeerConnection({ iceServers });
    console.log('RTCPeerConnection oluşturuldu');
  
  const remoteAudio = document.getElementById('remoteAudio');
  remoteAudio.autoplay = true;
  remoteAudio.playsInline = true;
  
  const toggle = document.getElementById('btnSpeaker');
  if (toggle && typeof remoteAudio.setSinkId === 'function') {
    let useSpeaker = false;
    toggle.onclick = async () => {
      useSpeaker = !useSpeaker;
      try {
        await remoteAudio.setSinkId(useSpeaker ? 'speaker' : 'default');
        toggle.setAttribute('aria-pressed', String(useSpeaker));
      } catch(e) { console.warn('setSinkId not allowed', e); }
    };
  }
  
  pc.ontrack = (e) => {
    remoteAudio.srcObject = e.streams[0];
  };
  
  pc.onicecandidate = (e) => {
    if (e.candidate) {
      socket.emit('rtc:candidate', { chat_id: chatId, candidate: e.candidate });
    }
  };
  
    return pc;
  } catch (error) {
    console.error('initCall hatası:', error);
    throw new Error('Arama başlatılamadı: ' + error.message);
  }
}

async function startOfferFlow(socket, pc, chatId, fromName) {
  try {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        },
        video: false
      });
    } catch (err) {
      if (err.name === 'NotAllowedError') {
        throw new Error('Mikrofon erişimi reddedildi. Lütfen tarayıcı ayarlarından izin verin.');
      } else if (err.name === 'NotFoundError') {
        throw new Error('Mikrofon bulunamadı. Lütfen cihazınızı kontrol edin.');
      } else if (err.name === 'NotReadableError') {
        throw new Error('Mikrofon başka bir uygulama tarafından kullanılıyor.');
      } else {
        throw new Error('Mikrofon erişim hatası: ' + err.message);
      }
    }
    
    stream.getTracks().forEach(t => pc.addTrack(t, stream));
    socket.emit('call:ring', { chat_id: chatId, from: fromName || 'Kullanıcı' });
    
    socket.on('call:accepted', async () => {
      try {
        const offer = await pc.createOffer({ offerToReceiveAudio: true });
        await pc.setLocalDescription(offer);
        socket.emit('rtc:offer', { chat_id: chatId, sdp: pc.localDescription });
      } catch (error) {
        console.error('Offer oluşturma hatası:', error);
        throw error;
      }
    });
    
    socket.on('call:declined', () => {
      pc.close();
      alert('Arama reddedildi');
    });
  } catch (err) {
    console.error('startOfferFlow hatası:', err);
    alert('Arama başlatılamadı: ' + err.message);
    throw err;
  }
}

function bindAnswering(socket, pc, chatId) {
  socket.on('rtc:offer', async ({ sdp }) => {
    try {
      await pc.setRemoteDescription(sdp);
      
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true
          },
          video: false
        });
      } catch (err) {
        if (err.name === 'NotAllowedError') {
          alert('Mikrofon erişimi reddedildi. Lütfen tarayıcı ayarlarından izin verin.');
        } else if (err.name === 'NotFoundError') {
          alert('Mikrofon bulunamadı.');
        } else {
          alert('Mikrofon hatası: ' + err.message);
        }
        throw err;
      }
      
      stream.getTracks().forEach(t => pc.addTrack(t, stream));
      
      const ans = await pc.createAnswer();
      await pc.setLocalDescription(ans);
      socket.emit('rtc:answer', { chat_id: chatId, sdp: pc.localDescription });
    } catch (err) {
      console.error('Answer hatası:', err);
    }
  });
  
  socket.on('rtc:answer', async ({ sdp }) => {
    try {
      await pc.setRemoteDescription(sdp);
    } catch (err) {
      console.error('Remote description hatası:', err);
      alert('Bağlantı hatası oluştu');
    }
  });
  
  socket.on('rtc:candidate', async ({ candidate }) => {
    try {
      if (candidate) await pc.addIceCandidate(candidate);
    } catch (err) {
      console.error('ICE candidate hatası:', err);
    }
  });
}
