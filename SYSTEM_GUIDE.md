# 🏗️ KONUŞMA PLATFORMU - SİSTEM REHBERİ

> Baştan sona tüm sistem mimarisi, dosya yapısı ve sorun giderme kılavuzu

---

## 📁 DOSYA YAPISI VE GÖREVLER

```
konuşma/
├── server/                   # BACKEND (Python Flask)
│   ├── app.py               # ⭐ ANA UYGULAMA - Flask server, API endpoints
│   ├── config.py            # 🔧 YAPILANDIRMA - .env değişkenleri
│   ├── signaling.py         # 🔌 SOCKET.IO - Chat ve Call event handlers
│   ├── storage.py           # 💾 VERİTABANI - SQLAlchemy modelleri
│   ├── telegram_bot.py      # 📱 TELEGRAM - Bildirim sistemi
│   ├── scheduler.py         # ⏰ ZAMANLANMIŞ GÖREVLER - APScheduler
│   ├── testsuite.py         # 🧪 TEST SİSTEMİ - Otomatik testler
│   ├── repair.py            # 🔧 ONARIM - Sistem temizleme
│   └── utils.py             # 🛠️ YARDIMCILAR - Timestamp, helpers
│
├── static/                   # FRONTEND ASSETS
│   ├── css/
│   │   ├── main.css         # 🎨 ANA STİLLER - Layout, components
│   │   ├── chat.css         # 💬 CHAT STİLLERİ - Messages, emoji picker
│   │   └── admin.css        # 👨‍💼 ADMİN STİLLERİ - Admin panel
│   └── js/
│       ├── client.js        # 👤 MÜŞTERİ UYGULAMASI - Ana logic
│       ├── admin.js         # 👨‍💼 ADMİN UYGULAMASI - Admin logic
│       ├── webrtc.js        # 📞 WEBRTC - Arama sistemi
│       ├── chat.js          # 💬 CHAT - Mesaj rendering
│       ├── ui.js            # 🎨 UI - Emoji picker, helpers
│       ├── media.js         # 🎥 MEDYA - Timer, controls
│       └── test_runner_client.js  # 🧪 TEST CLIENT - Test UI
│
├── templates/                # HTML SAYFALAR
│   ├── index.html           # 👤 MÜŞTERİ ARAYÜZÜ
│   ├── admin.html           # 👨‍💼 ADMİN PANELİ
│   └── test.html            # 🧪 TEST PANELİ
│
├── .env                      # 🔐 ORTAM DEĞİŞKENLERİ (local)
├── .env.example              # 📋 TEMPLATE
├── .gitignore                # 🚫 Git ignore
├── data.sqlite3              # 💾 VERİTABANI
├── Dockerfile                # 🐳 Docker config
├── LICENSE                   # 📄 MIT Lisans
├── README.md                 # 📖 Genel dokümantasyon
├── render.yaml               # ☁️ Render.com deploy
└── requirements.txt          # 📦 Python dependencies
```

---

## 🔄 SİSTEM MİMARİSİ

### 1. İSTEK AKIŞI (Request Flow)

```
[Kullanıcı] → [Browser] → [Flask App] → [Database]
                    ↓
              [Socket.IO] → [WebRTC]
                    ↓
              [Telegram Bot]
```

### 2. KATMANLAR (Layers)

#### **KATMAN 1: FRONTEND (Browser)**
- **Görev:** Kullanıcı arayüzü, WebRTC, Socket.IO client
- **Dosyalar:** `templates/*.html`, `static/js/*.js`, `static/css/*.css`
- **Sorun Giderme:** Browser console, Network tab

#### **KATMAN 2: BACKEND (Flask)**
- **Görev:** HTTP API, Socket.IO server, business logic
- **Dosyalar:** `server/app.py`, `server/signaling.py`
- **Sorun Giderme:** Server logs, `/health` endpoint

#### **KATMAN 3: DATABASE (SQLite)**
- **Görev:** Veri saklama, chat sessions, messages
- **Dosyalar:** `data.sqlite3`, `server/storage.py`
- **Sorun Giderme:** SQLite browser, database queries

#### **KATMAN 4: EXTERNAL (Telegram)**
- **Görev:** Admin bildirimleri
- **Dosyalar:** `server/telegram_bot.py`
- **Sorun Giderme:** Telegram bot logs, API errors

---

## 📄 DOSYA DETAYLARI

### 🔥 KRİTİK DOSYALAR (Bozulursa sistem çalışmaz)

#### **server/app.py** - Ana Uygulama
```python
# NE YAPAR:
- Flask app başlatır
- HTTP endpoints tanımlar (/, /admin, /test, /api/*)
- Socket.IO namespaces kaydeder
- CORS, CSRF, rate limiting ayarlar
- Security headers ekler

# BOZULURSA:
- Uygulama başlamaz
- HTTP 500 hatası
- Socket.IO bağlanamaz

# MÜDAHALE:
1. Syntax error kontrol: python -m py_compile server/app.py
2. Import errors kontrol: python -c "from server.app import app"
3. Logs kontrol: tail -f logs/app.log
```

#### **server/signaling.py** - Socket.IO Events
```python
# NE YAPAR:
- /chat namespace: Mesajlaşma events
- /call namespace: WebRTC signaling
- Input validation ve sanitization
- ROOM_STATE yönetimi

# BOZULURSA:
- Chat mesajları gönderilmez
- Arama çalışmaz
- Socket.IO disconnect

# MÜDAHALE:
1. Socket.IO connection kontrol: socket.connected
2. Event handlers kontrol: console.log
3. ROOM_STATE kontrol: GET /debug/memory
```

#### **server/storage.py** - Database
```python
# NE YAPAR:
- SQLAlchemy modelleri (ChatSession, Message)
- CRUD operations
- Database initialization

# BOZULURSA:
- Database errors
- Chat history yüklenemez
- Mesajlar kaydedilmez

# MÜDAHALE:
1. Database file kontrol: ls -la data.sqlite3
2. Schema kontrol: sqlite3 data.sqlite3 ".schema"
3. Backup restore: cp backup.sqlite3 data.sqlite3
```

### ⚙️ YARDIMCI DOSYALAR (Bozulursa özellik kaybı)

#### **server/config.py** - Yapılandırma
```python
# NE YAPAR:
- .env dosyasından değişkenleri okur
- Config class tanımlar
- Varsayılan değerler

# BOZULURSA:
- .env değişkenleri okunamaz
- Varsayılan değerler kullanılır

# MÜDAHALE:
1. .env dosyası kontrol: cat .env
2. Config değerleri kontrol: python -c "from server.config import cfg; print(cfg.SECRET_KEY)"
```

#### **server/telegram_bot.py** - Telegram
```python
# NE YAPAR:
- Admin'e bildirim gönderir
- Text, image, audio relay

# BOZULURSA:
- Bildirimler gelmez
- Chat çalışmaya devam eder

# MÜDAHALE:
1. Bot token kontrol: echo $TELEGRAM_BOT_TOKEN
2. API test: curl https://api.telegram.org/bot<TOKEN>/getMe
```

#### **server/scheduler.py** - Zamanlayıcı
```python
# NE YAPAR:
- APScheduler ile zamanlanmış görevler
- Test otomasyonu

# BOZULURSA:
- Otomatik testler çalışmaz
- Manuel test çalışır

# MÜDAHALE:
1. Scheduler logs kontrol
2. Test schedule kontrol: GET /api/test/schedule
```

#### **server/testsuite.py** - Test Sistemi
```python
# NE YAPAR:
- 7 kategori test (health, security, db, admin, upload, chat, webrtc)
- Test sonuçları JSON

# BOZULURSA:
- Test paneli çalışmaz
- Uygulama çalışır

# MÜDAHALE:
1. Manuel test: POST /api/test/run
2. Test logs kontrol
```

#### **server/repair.py** - Onarım
```python
# NE YAPAR:
- ROOM_STATE temizleme
- Database backfill
- Safe operations

# BOZULURSA:
- Onarım butonu çalışmaz
- Manuel temizlik gerekir

# MÜDAHALE:
1. ROOM_STATE kontrol: GET /debug/memory
2. Manuel cleanup: Python shell
```

### 🎨 FRONTEND DOSYALARI

#### **static/js/client.js** - Müşteri App
```javascript
// NE YAPAR:
- Socket.IO bağlantısı
- Mesaj gönderme/alma
- File upload
- Name modal

// BOZULURSA:
- Müşteri chat çalışmaz
- Admin çalışır

// MÜDAHALE:
1. Console errors kontrol
2. Socket.IO connection: socket.connected
3. Event listeners kontrol
```

#### **static/js/admin.js** - Admin App
```javascript
// NE YAPAR:
- OTP login
- Thread list
- Chat panel
- Admin messaging

// BOZULURSA:
- Admin panel çalışmaz
- Müşteri çalışır

// MÜDAHALE:
1. Console errors kontrol
2. OTP kontrol: "demo"
3. API calls kontrol: Network tab
```

#### **static/js/webrtc.js** - WebRTC
```javascript
// NE YAPAR:
- RTCPeerConnection
- getUserMedia
- Offer/Answer flow
- ICE candidates

// BOZULURSA:
- Arama çalışmaz
- Chat çalışır

// MÜDAHALE:
1. Mikrofon izni kontrol
2. ICE servers kontrol: GET /v1/api/ice-servers
3. WebRTC errors: console.log
```

---

## 🔧 SORUN GİDERME (Troubleshooting)

### 🚨 YAYGIN SORUNLAR

#### **1. Uygulama Başlamıyor**
```bash
# SEMPTOM:
- python -m server.app hata veriyor
- Import errors

# ÇÖZÜM:
1. Dependencies kontrol:
   pip install -r requirements.txt

2. Python version kontrol:
   python --version  # 3.12+ olmalı

3. Syntax errors:
   python -m py_compile server/app.py

4. .env dosyası kontrol:
   cp .env.example .env
```

#### **2. Socket.IO Bağlanamıyor**
```bash
# SEMPTOM:
- socket.connected = false
- Chat mesajları gönderilmiyor

# ÇÖZÜM:
1. CORS kontrol:
   # .env
   ALLOWED_ORIGINS=http://localhost:10000

2. Socket.IO server kontrol:
   curl http://localhost:10000/socket.io/

3. Browser console:
   socket.io.js yüklendi mi?

4. Firewall:
   Port 10000 açık mı?
```

#### **3. Database Errors**
```bash
# SEMPTOM:
- SQLAlchemy errors
- Chat history yüklenmiyor

# ÇÖZÜM:
1. Database file kontrol:
   ls -la data.sqlite3

2. Schema kontrol:
   sqlite3 data.sqlite3 ".schema"

3. Yeniden oluştur:
   rm data.sqlite3
   python -c "from server.storage import init_db; init_db()"

4. Backup restore:
   cp backup.sqlite3 data.sqlite3
```

#### **4. WebRTC Çalışmıyor**
```bash
# SEMPTOM:
- Arama başlamıyor
- Mikrofon erişimi reddediliyor

# ÇÖZÜM:
1. HTTPS kontrol:
   # WebRTC HTTPS gerektirir (localhost hariç)

2. Mikrofon izni:
   # Browser settings → Permissions

3. ICE servers:
   curl http://localhost:10000/v1/api/ice-servers

4. Browser compatibility:
   # Chrome/Firefox latest version
```

#### **5. Telegram Bildirimleri Gelmiyor**
```bash
# SEMPTOM:
- Admin'e bildirim gitmiyor

# ÇÖZÜM:
1. Bot token kontrol:
   echo $TELEGRAM_BOT_TOKEN

2. Bot test:
   curl https://api.telegram.org/bot<TOKEN>/getMe

3. Chat ID kontrol:
   echo $TELEGRAM_ADMIN_CHAT_ID

4. Logs kontrol:
   # server/telegram_bot.py errors
```

#### **6. CSS/JS Yüklenmiyor**
```bash
# SEMPTOM:
- Sayfa stil yok
- JavaScript çalışmıyor

# ÇÖZÜM:
1. Static files kontrol:
   ls -la static/css/
   ls -la static/js/

2. Flask static folder:
   # app.py: static_folder="../static"

3. Browser cache:
   Ctrl+Shift+R (hard refresh)

4. Network tab:
   # 404 errors kontrol
```

---

## 🔍 DEBUG ARAÇLARI

### 1. Health Check
```bash
curl http://localhost:10000/health
# Response: {"ok": true, "status": "healthy"}
```

### 2. Memory Monitor (Development)
```bash
curl http://localhost:10000/debug/memory
# Response: {
#   "rss_mb": 45.23,
#   "room_state_size": 3,
#   "rooms": ["room1", "room2"]
# }
```

### 3. Database Inspect
```bash
sqlite3 data.sqlite3
.tables
SELECT * FROM chat_sessions;
SELECT * FROM messages LIMIT 10;
.quit
```

### 4. Logs
```bash
# Application logs
tail -f logs/app.log

# Error logs
grep ERROR logs/app.log

# Socket.IO logs
grep "socket.io" logs/app.log
```

### 5. Browser DevTools
```javascript
// Console
console.log(socket.connected);
console.log(callSocket.connected);
console.log(roomKey);

// Network tab
// Filter: socket.io
// Check: WebSocket connection

// Application tab
// Storage → Local Storage
// Check: name, session data
```

---

## 🚀 DEPLOYMENT KONTROL

### Pre-Deploy Checklist
```bash
# 1. Dependencies
pip install -r requirements.txt

# 2. Environment
cat .env
# SECRET_KEY set?
# ALLOWED_ORIGINS correct?
# FLASK_ENV=production?

# 3. Database
python -c "from server.storage import init_db; init_db()"

# 4. Tests
curl http://localhost:10000/health

# 5. Security
# HTTPS enabled?
# CSRF protection active?
# Rate limiting configured?
```

### Post-Deploy Verification
```bash
# 1. Health check
curl https://your-domain.com/health

# 2. Socket.IO
# Browser console: socket.connected

# 3. Database
# Chat session oluştur ve kontrol

# 4. Logs
tail -f /var/log/konusma/app.log

# 5. Monitoring
# Uptime monitor active?
# Error tracking configured?
```

---

## 📊 SİSTEM DURUMU KONTROL

### Hızlı Durum Kontrolü
```bash
# 1. Process çalışıyor mu?
ps aux | grep python

# 2. Port dinliyor mu?
netstat -tulpn | grep 10000

# 3. Database erişilebilir mi?
sqlite3 data.sqlite3 "SELECT COUNT(*) FROM chat_sessions;"

# 4. Disk alanı yeterli mi?
df -h

# 5. Memory kullanımı?
free -m
```

### Performans Metrikleri
```bash
# Response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:10000/

# Database size
du -h data.sqlite3

# Log size
du -h logs/

# Memory usage
curl http://localhost:10000/debug/memory
```

---

## 🔐 GÜVENLİK KONTROL

### Security Headers
```bash
curl -I https://your-domain.com/
# Check:
# - Strict-Transport-Security
# - X-Content-Type-Options: nosniff
# - X-Frame-Options: DENY
# - Content-Security-Policy
```

### CSRF Protection
```bash
# POST without token should fail
curl -X POST http://localhost:10000/api/test/run
# Expected: 400 Bad Request
```

### Rate Limiting
```bash
# 50+ rapid requests
for i in {1..60}; do curl http://localhost:10000/health; done
# Expected: 429 Too Many Requests
```

---

## 📞 DESTEK VE BAKIM

### Günlük Kontroller
- [ ] Health endpoint çalışıyor mu?
- [ ] Logs'da error var mı?
- [ ] Database boyutu normal mi?
- [ ] Memory kullanımı stabil mi?

### Haftalık Kontroller
- [ ] Backup alındı mı?
- [ ] Performance metrikleri normal mi?
- [ ] Security scan yapıldı mı?
- [ ] Dependencies güncel mi?

### Aylık Kontroller
- [ ] Database optimize edildi mi?
- [ ] Logs rotate edildi mi?
- [ ] Monitoring dashboard review
- [ ] User feedback analizi

---

## 🆘 ACİL DURUM

### Sistem Çöktü
```bash
# 1. Restart
systemctl restart konusma

# 2. Logs kontrol
tail -100 logs/app.log

# 3. Database kontrol
sqlite3 data.sqlite3 "PRAGMA integrity_check;"

# 4. Backup restore (son çare)
cp backup.sqlite3 data.sqlite3
systemctl restart konusma
```

### Database Bozuldu
```bash
# 1. Backup kontrol
ls -la backups/

# 2. Integrity check
sqlite3 data.sqlite3 "PRAGMA integrity_check;"

# 3. Restore
cp backups/latest.sqlite3 data.sqlite3

# 4. Yeniden oluştur (son çare)
rm data.sqlite3
python -c "from server.storage import init_db; init_db()"
```

### Memory Leak
```bash
# 1. Memory kontrol
curl http://localhost:10000/debug/memory

# 2. ROOM_STATE temizle
curl -X POST http://localhost:10000/api/repair/run

# 3. Restart
systemctl restart konusma
```

---

## 📚 EK KAYNAKLAR

- **README.md**: Genel dokümantasyon
- **requirements.txt**: Python dependencies
- **.env.example**: Environment template
- **Dockerfile**: Docker deployment
- **render.yaml**: Render.com config

---

**Son Güncelleme:** 2024
**Versiyon:** 1.0
**Durum:** Production Ready ✅
