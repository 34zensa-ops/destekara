async function toggleSpeaker(audioEl, speakerOn) {
  if (!('setSinkId' in HTMLMediaElement.prototype)) {
    console.log('setSinkId desteklenmiyor (iOS Safari)');
    return;
  }
  
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioOutputs = devices.filter(d => d.kind === 'audiooutput');
    
    if (audioOutputs.length > 0) {
      const deviceId = speakerOn ? audioOutputs[0].deviceId : 'default';
      await audioEl.setSinkId(deviceId);
    }
  } catch (err) {
    console.error('Ses çıkışı değiştirilemedi:', err);
  }
}
