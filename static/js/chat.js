function renderMsg(listEl, { role, type, text, time }) {
  const li = document.createElement('li');
  li.className = `msg ${role}`;
  
  if (type === 'text') {
    li.innerHTML = `<div>${escapeHtml(text)}</div>`;
  } else if (type === 'image') {
    li.innerHTML = `<div><img src="${text}" alt="image" style="max-width:220px;border-radius:12px"/></div>`;
  } else if (type === 'audio') {
    li.innerHTML = `<div><audio controls src="${text}"></audio></div>`;
  }
  
  listEl.appendChild(li);
  listEl.scrollTop = listEl.scrollHeight;
}

function ts() {
  const d = new Date();
  return d.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
