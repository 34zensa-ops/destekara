const emojis = ['😊','😂','❤️','👍','🎉','🔥','💯','😍','🙌','✨'];

function setupEmojiPicker(inputEl) {
  const picker = document.getElementById('emojiPicker');
  const btnEmoji = document.getElementById('btnEmoji');
  
  if (!picker || !btnEmoji) return;
  
  picker.innerHTML = '';
  picker.className = 'emoji-picker hidden';
  
  emojis.forEach(emoji => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'emoji-item';
    btn.textContent = emoji;
    btn.onclick = () => {
      inputEl.value += emoji;
      picker.classList.add('hidden');
      inputEl.focus();
    };
    picker.appendChild(btn);
  });
  
  btnEmoji.onclick = () => {
    picker.classList.toggle('hidden');
  };
  
  document.addEventListener('click', (e) => {
    if (!picker.contains(e.target) && e.target !== btnEmoji) {
      picker.classList.add('hidden');
    }
  });
}


