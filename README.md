# 📞 Sesli ve Yazılı Konuşma

> Modern, mobil-first chat + WebRTC sesli/görüntülü arama platformu

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

## ✨ Özellikler

### 📱 Kullanıcı Deneyimi
- 🎆 Modern UI/UX - Mobil-first, responsive tasarım
- 💬 Anlık Mesajlaşma - Socket.IO ile gerçek zamanlı
- 📞 Sesli Arama - WebRTC P2P teknolojisi
- 🌍 Cross-Platform - Tüm cihazlarda çalışır
- 😊 Emoji Desteği - Hızlı emoji seçimi

### 👨‍💼 Admin Yönetimi
- 🔐 Güvenli Giriş - OTP tabanlı kimlik doğrulama
- 📈 Chat Yönetimi - Sohbet geçmişi ve analiz
- 🤖 Telegram Entegrasyonu - Bot bildirimleri
- 🧪 Test Sistemi - Otomatik sağlık kontrolleri
- 🔧 Bakım Araçları - Sistem temizleme ve onarım

### 🔒 Güvenlik & Performans
- 🛡️ CORS Koruması - Domain whitelist
- 🔐 Room Key Authentication - Zorunlu oda anahtarları
- 👥 Room Capacity Limits - Maksimum 2 kişi
- 🚪 Accept-Gate - RTC olayları kabul sonrası
- 🔄 TURN Server - NAT traversal desteği
- 📉 Structured Logging - Detaylı sistem logları
- ⚡ Rate Limiting - Yapılandırılabilir limitler
- ❤️ Health Monitoring - Canlılık kontrolü
- 🚀 Production Ready - Gunicorn + Eventlet

## 💻 Lokal Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/YOUR_USERNAME/konusma.git
cd konusma

# Sanal ortam oluşturun
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Uygulamayı başlatın
python -m server.app
```

🌐 **Tarayıcıda açın:** http://localhost:10000/

### Ortam Değişkenleri

`.env` dosyası oluştur (`.env.example`'dan kopyala):

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
TZ=Europe/Istanbul
DATABASE_URL=sqlite:///./data.sqlite3

# CORS
ALLOWED_ORIGINS=http://localhost:10000

# Telegram (opsiyonel)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
TELEGRAM_WEBHOOK_URL=https://your-app.onrender.com/tg/webhook
```

## 🚀 Deploy (Render.com)

### 1. GitHub'a Push
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_REPO_URL
git push -u origin main
```

### 2. Render'da Deploy

1. **[Render Dashboard](https://dashboard.render.com/)** → **New** → **Web Service**
2. **GitHub repo'nuzu bağlayın:** `YOUR_USERNAME/konusma`
3. **Ayarlar:**
   ```
   Name: konusma-app
   Environment: Python 3
   Build Command: pip install --upgrade pip && pip install -r requirements.txt
   Start Command: python -m server.app
   Plan: Free
   ```

### 3. Environment Variables
Render Dashboard → Environment sekmesinde ekleyin:

```env
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
TZ=Europe/Istanbul
ALLOWED_ORIGINS=https://YOUR-APP-NAME.onrender.com

# Telegram (opsiyonel)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_ADMIN_CHAT_ID=your-chat-id
TELEGRAM_WEBHOOK_URL=https://YOUR-APP-NAME.onrender.com/tg/webhook
```

🔑 **SECRET_KEY oluşturmak için:** 
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📱 Kullanım Kılavuzu

### 👥 Müşteri Paneli (/)
1. İsminizi girin
2. Mesajlaşmaya başlayın
3. Sağ üstteki 📞 butonuyla sesli arama başlatın

### 👨‍💼 Admin Paneli (/admin)
1. OTP: `demo` (test için)
2. Bekleyen sohbetleri görün
3. Sohbete tıklayarak mesaj geçmişini açın
4. 📞 Arama başlat veya 🗑️ Sil butonlarını kullanın

### 🧪 Test Paneli (/test)
1. "Tüm testleri çalıştır" butonu ile anlık test
2. Test saatleri ekleyin (HH:MM formatı)
3. "Repair" ile sistem temizliği

## 🔧 Teknoloji Stack

### Backend
- 🐍 Python 3.12+
- 🌶️ Flask 3.1.0
- 🔌 Flask-SocketIO 5.4.1
- ⚡ Eventlet 0.36.1
- 🗄 SQLAlchemy 2.0.36
- ⏰ APScheduler 3.10.4

### Frontend
- 🎨 Modern CSS - Custom properties, Grid, Flexbox
- 📱 Mobile-First - Responsive design
- ⚡ Vanilla JavaScript - No framework dependencies
- 📞 WebRTC - P2P audio calls
- 🔌 Socket.IO Client - Real-time updates

### Database & Storage
- 🗄 SQLite - Embedded database
- 📋 Session Management - User state

## 📁 Dosya Yapısı

```
konuşma/
├─ server/
│  ├─ app.py              # Flask ana uygulama
│  ├─ config.py           # Ortam config
│  ├─ storage.py          # SQLite modelleri
│  ├─ signaling.py        # Socket.IO eventleri
│  ├─ telegram_bot.py     # Telegram entegrasyonu
│  ├─ scheduler.py        # APScheduler
│  ├─ testsuite.py        # Test suite
│  ├─ repair.py           # Repair işlemleri
│  └─ utils.py            # Yardımcı fonksiyonlar
├─ templates/
│  ├─ index.html          # Kullanıcı arayüzü
│  ├─ admin.html          # Admin paneli
│  └─ test.html           # Test arayüzü
├─ static/
│  ├─ css/                # Stil dosyaları
│  └─ js/                 # JavaScript modülleri
├─ requirements.txt       # Python bağımlılıkları
├─ Dockerfile            # Docker imajı
├─ render.yaml           # Render.com config
└─ README.md             # Bu dosya
```

## 🌐 API Endpoints

### REST API
- `GET /` - Kullanıcı arayüzü
- `GET /admin` - Admin paneli
- `GET /test` - Test arayüzü
- `GET /health` - Sağlık kontrolü
- `GET /api/chats` - Sohbet listesi
- `GET /api/chats/:id/messages` - Mesaj geçmişi
- `DELETE /api/chats/:id` - Sohbet sil
- `GET /api/test/schedule` - Test saatleri
- `POST /api/test/schedule` - Test saati ekle
- `PUT /api/test/schedule/:id` - Test saati güncelle
- `DELETE /api/test/schedule/:id` - Test saati sil
- `POST /api/test/run` - Testleri çalıştır
- `POST /api/repair/run` - Repair çalıştır

### Socket.IO - /chat
- `join` - Odaya katıl
- `send` - Mesaj gönder
- `chat:message` - Mesaj al

### Socket.IO - /call
- `join` - Arama odasına katıl
- `call:ring` - Arama başlat
- `call:accept` - Aramayı kabul et
- `call:decline` - Aramayı reddet
- `rtc:offer` - WebRTC offer
- `rtc:answer` - WebRTC answer
- `rtc:candidate` - ICE candidate
- `call:end` - Aramayı sonlandır

## 🔐 Güvenlik

- CORS beyaz liste koruması
- HttpOnly admin oturumu
- Input sanitization (XSS koruması)
- HTTPS önerilir (WebRTC için gerekli)

## 📱 Mobil Uyumluluk

- ✅ Android Chrome/Firefox
- ✅ iOS Safari
- ✅ Tablet ve masaüstü
- ✅ 44px+ dokunma hedefleri
- ✅ 100svh viewport desteği

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing`)
5. Pull Request açın

## 📄 Lisans

**MIT License** - Özgürce kullanılabilir, değiştirilebilir ve dağıtılabilir.

## 👥 Katkıda Bulunun

1. **Fork** edin
2. **Feature branch** oluşturun (`git checkout -b feature/amazing-feature`)
3. **Commit** edin (`git commit -m 'Add amazing feature'`)
4. **Push** edin (`git push origin feature/amazing-feature`)
5. **Pull Request** açın

## 🐛 Sorun Bildirimi

Sorun mu buldunuz? [GitHub Issues](https://github.com/YOUR_USERNAME/konusma/issues) sayfasından bildirebilirsiniz.

## 📧 İletişim

Sorularınız için GitHub Issues kullanın veya repository'yi star'layıp takip edin!

---

<div align="center">

**⭐ Beğendiyseniz star vermeyi unutmayın!**

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/konusma?style=social)](https://github.com/YOUR_USERNAME/konusma/stargazers)

</div>
