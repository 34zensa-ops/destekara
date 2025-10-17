# 🚀 DEPLOYMENT GUIDE - Git + Render.com

> Konuşma platformunu GitHub'a yükleyip Render.com'da deploy etme rehberi

---

## 📋 ÖN HAZIRLIK

### 1. Gerekli Hesaplar
- ✅ GitHub hesabı (https://github.com)
- ✅ Render.com hesabı (https://render.com)
- ✅ Git kurulu (https://git-scm.com)

### 2. Proje Kontrolü
```bash
cd c:\Users\BTA\Desktop\konuşma

# Dosya yapısı kontrol
dir

# Gerekli dosyalar:
# ✓ server/
# ✓ static/
# ✓ templates/
# ✓ requirements.txt
# ✓ render.yaml
# ✓ .gitignore
# ✓ README.md
```

---

## 🔧 ADIM 1: GIT HAZIRLIK

### .gitignore Kontrolü
```bash
# .gitignore dosyası doğru mu kontrol et
type .gitignore

# Şunlar ignore edilmeli:
# ✓ .env (local secrets)
# ✓ __pycache__/
# ✓ *.sqlite3 (local database)
# ✓ .venv/
```

### Git Başlat
```bash
# Git repository başlat
git init

# Tüm dosyaları ekle
git add .

# İlk commit
git commit -m "Initial commit: Konuşma platformu"

# Durum kontrol
git status
# Output: "nothing to commit, working tree clean"
```

---

## 📤 ADIM 2: GITHUB'A YÜKLE

### GitHub Repository Oluştur

1. **GitHub'a git:** https://github.com
2. **New repository** tıkla
3. **Repository ayarları:**
   ```
   Repository name: konusma
   Description: Sesli ve Yazılı Konuşma Platformu
   Visibility: Public (veya Private)
   ❌ Initialize with README (zaten var)
   ❌ Add .gitignore (zaten var)
   ❌ Choose a license (zaten var)
   ```
4. **Create repository** tıkla

### Remote Ekle ve Push

```bash
# GitHub repository URL'ini kopyala
# Örnek: https://github.com/YOUR_USERNAME/konusma.git

# Remote ekle
git remote add origin https://github.com/YOUR_USERNAME/konusma.git

# Branch adını main yap (eski projeler master kullanır)
git branch -M main

# GitHub'a push
git push -u origin main

# Şifre isterse: GitHub Personal Access Token kullan
# Settings → Developer settings → Personal access tokens → Generate new token
```

### Push Doğrulama
```bash
# GitHub'da repository'yi aç
# Tüm dosyalar görünmeli:
# ✓ server/
# ✓ static/
# ✓ templates/
# ✓ requirements.txt
# ✓ render.yaml
# ✓ README.md

# .env dosyası OLMAMALI (gitignore'da)
```

---

## ☁️ ADIM 3: RENDER.COM DEPLOY

### Render Dashboard

1. **Render'a git:** https://dashboard.render.com
2. **Sign in with GitHub** (önerilen)
3. **New +** → **Web Service** tıkla

### Repository Bağla

1. **Connect a repository:**
   - GitHub hesabını bağla
   - Repository listesinde `konusma` bul
   - **Connect** tıkla

2. **Eğer repository görünmüyorsa:**
   - **Configure account** tıkla
   - GitHub'da Render'a erişim ver
   - Repository'yi seç

### Service Ayarları

```yaml
Name: konusma-app
Region: Frankfurt (EU Central)
Branch: main
Root Directory: (boş bırak)
Runtime: Python 3
Build Command: pip install --upgrade pip && pip install -r requirements.txt
Start Command: gunicorn -k eventlet -w 1 server.app:app --bind 0.0.0.0:$PORT
```

**Plan Seçimi:**
- **Free:** Test için (uyku modu var, 750 saat/ay)
- **Starter ($7/ay):** Production için (7/24 aktif)

### Environment Variables

**Render Dashboard → Environment sekmesi:**

#### Zorunlu Değişkenler:
```env
FLASK_ENV=production
SECRET_KEY=<AUTO_GENERATED>  # Render otomatik oluşturur
TZ=Europe/Istanbul
ALLOWED_ORIGINS=https://konusma-app.onrender.com
DATABASE_URL=sqlite:///./data.sqlite3
REQUIRE_ROOM_KEY=true
MAX_ROOM_MEMBERS=2
ENABLE_CALLS=true
RATE_LIMIT_HOURLY=100
RATE_LIMIT_DAILY=1000
```

#### Opsiyonel (Telegram):
```env
TELEGRAM_BOT_TOKEN=<YOUR_BOT_TOKEN>
TELEGRAM_ADMIN_CHAT_ID=<YOUR_CHAT_ID>
TELEGRAM_WEBHOOK_URL=https://konusma-app.onrender.com/tg/webhook
```

#### Opsiyonel (TURN Server):
```env
TURN_URL=<YOUR_TURN_URL>
TURN_USERNAME=<YOUR_TURN_USER>
TURN_CREDENTIAL=<YOUR_TURN_PASS>
```

### Deploy Başlat

1. **Create Web Service** tıkla
2. Deploy başlar (5-10 dakika)
3. Logs'u izle:
   ```
   Building...
   Installing dependencies...
   Starting server...
   ==> Your service is live 🎉
   ```

---

## ✅ ADIM 4: DEPLOY DOĞRULAMA

### Health Check
```bash
# Render URL'ini al (örnek: https://konusma-app.onrender.com)
curl https://konusma-app.onrender.com/health

# Beklenen response:
# {"ok": true, "status": "healthy"}
```

### Browser Test
1. **URL'i aç:** https://konusma-app.onrender.com
2. **Welcome screen görünmeli**
3. **İsim gir ve chat başlat**
4. **Mesaj gönder** (çalışmalı)

### Admin Panel Test
1. **URL:** https://konusma-app.onrender.com/admin
2. **OTP:** `demo`
3. **Giriş yap**
4. **Sohbet listesi görünmeli**

### Test Panel
1. **URL:** https://konusma-app.onrender.com/test
2. **"Çalıştır" butonu**
3. **Testler çalışmalı**

---

## 🔧 ADIM 5: RENDER YAPILANDIRMA

### Auto-Deploy Ayarla

**Render Dashboard → Settings:**

1. **Auto-Deploy:** ON
   - GitHub'a her push'ta otomatik deploy
   
2. **Health Check Path:** `/healthz`
   - Render otomatik kontrol eder

3. **Environment Variables:**
   - Değişiklik yapınca **Save** tıkla
   - Otomatik redeploy olur

### Custom Domain (Opsiyonel)

**Render Dashboard → Settings → Custom Domain:**

1. **Add Custom Domain**
2. **Domain gir:** `konusma.yourdomain.com`
3. **DNS ayarları:**
   ```
   Type: CNAME
   Name: konusma
   Value: konusma-app.onrender.com
   ```
4. **SSL otomatik:** Let's Encrypt

### Persistent Disk (Database)

**ÖNEMLİ:** Render Free plan'de disk ephemeral (geçici)

**Çözüm 1: Starter Plan**
- Persistent disk dahil
- Database kaybolmaz

**Çözüm 2: External Database**
```env
# PostgreSQL kullan (önerilen)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

**Çözüm 3: Backup Sistemi**
- Günlük database backup
- External storage (S3, Dropbox)

---

## 📊 ADIM 6: MONİTORİNG

### Render Logs

**Dashboard → Logs sekmesi:**
```bash
# Real-time logs
# Errors, warnings, info messages
# Socket.IO connections
# HTTP requests
```

### Metrics

**Dashboard → Metrics sekmesi:**
- CPU usage
- Memory usage
- Request count
- Response time

### Alerts (Starter+ plan)

**Dashboard → Settings → Notifications:**
- Deploy başarısız
- Health check fail
- High memory usage

---

## 🔄 GÜNCELLEME WORKFLOW

### Kod Değişikliği Yap

```bash
# Dosyaları düzenle
# Örnek: server/app.py

# Değişiklikleri kontrol
git status

# Değişiklikleri ekle
git add .

# Commit
git commit -m "Fix: Socket.IO connection issue"

# GitHub'a push
git push origin main
```

### Otomatik Deploy

1. **Push sonrası Render otomatik deploy başlar**
2. **Dashboard → Events:** Deploy durumu
3. **Logs:** Build ve deploy logs
4. **5-10 dakika sonra:** Yeni versiyon live

### Manuel Deploy

**Dashboard → Manual Deploy:**
- **Deploy Latest Commit** tıkla
- Son commit'i deploy eder

---

## 🆘 SORUN GİDERME

### Deploy Başarısız

**Semptom:** Build failed

**Çözüm:**
```bash
# Render logs kontrol
# Hata mesajını oku

# Yaygın hatalar:
1. requirements.txt eksik dependency
   → pip freeze > requirements.txt

2. Python version uyumsuz
   → runtime.txt ekle: python-3.12.0

3. Import errors
   → Lokal test: python -m server.app
```

### Health Check Fail

**Semptom:** Service unhealthy

**Çözüm:**
```bash
# /health endpoint kontrol
curl https://konusma-app.onrender.com/health

# Logs kontrol
# Server başladı mı?
# Port dinliyor mu?

# Environment variables kontrol
# SECRET_KEY set?
# ALLOWED_ORIGINS doğru?
```

### Database Kayboldu

**Semptom:** Chat history yok

**Çözüm:**
```bash
# Free plan: Disk ephemeral
# Her deploy'da database sıfırlanır

# Çözüm:
1. Starter plan'e geç (persistent disk)
2. PostgreSQL kullan (external)
3. Backup sistemi kur
```

### Socket.IO Bağlanamıyor

**Semptom:** Chat çalışmıyor

**Çözüm:**
```bash
# ALLOWED_ORIGINS kontrol
# Render URL ekli mi?
ALLOWED_ORIGINS=https://konusma-app.onrender.com

# CORS logs kontrol
# Browser console: CORS error?

# WebSocket support
# Render WebSocket destekler (OK)
```

### Yavaş Response

**Semptom:** Sayfa yavaş yükleniyor

**Çözüm:**
```bash
# Free plan: Cold start (ilk istek yavaş)
# 15 dakika inactivity sonrası uyur

# Çözüm:
1. Starter plan (7/24 aktif)
2. Uptime monitor (UptimeRobot)
   → Her 5 dakikada ping at
   → Uyumayı engeller
```

---

## 🔐 GÜVENLİK

### Secrets Yönetimi

**✅ DOĞRU:**
```bash
# Render Environment Variables
SECRET_KEY=<auto_generated>
TELEGRAM_BOT_TOKEN=<secret>
```

**❌ YANLIŞ:**
```python
# Kod içinde hardcoded
SECRET_KEY = "my-secret-key"  # ASLA YAPMA!
```

### HTTPS

**Render otomatik HTTPS:**
- Let's Encrypt SSL
- Auto-renewal
- HTTPS redirect (Talisman ile)

### Environment Variables

**Render Dashboard → Environment:**
- Şifreli saklanır
- Logs'da görünmez
- Deploy'da güncellenir

---

## 📈 PRODUCTION CHECKLIST

### Deploy Öncesi

- [ ] Lokal test (python -m server.app)
- [ ] Git commit (tüm değişiklikler)
- [ ] .env secrets kontrol
- [ ] requirements.txt güncel
- [ ] .gitignore doğru

### Deploy Sonrası

- [ ] Health check (curl /health)
- [ ] Browser test (index.html)
- [ ] Admin panel test
- [ ] Socket.IO test (chat)
- [ ] WebRTC test (call)
- [ ] Logs kontrol (errors?)

### İlk 24 Saat

- [ ] Uptime monitoring
- [ ] Error tracking
- [ ] Performance metrics
- [ ] User feedback

---

## 🎯 HIZLI KOMUTLAR

### Git
```bash
# Status
git status

# Add all
git add .

# Commit
git commit -m "message"

# Push
git push origin main

# Pull
git pull origin main

# Logs
git log --oneline
```

### Render CLI (Opsiyonel)
```bash
# Install
npm install -g @render/cli

# Login
render login

# Deploy
render deploy

# Logs
render logs
```

---

## 📞 DESTEK

### Render Support
- **Docs:** https://render.com/docs
- **Community:** https://community.render.com
- **Status:** https://status.render.com

### GitHub Issues
- **Repository:** https://github.com/YOUR_USERNAME/konusma/issues
- **Bug report:** Issue aç
- **Feature request:** Issue aç

---

## ✅ BAŞARILI DEPLOY!

```
🎉 Konuşma platformu live!

URL: https://konusma-app.onrender.com
Admin: https://konusma-app.onrender.com/admin
Test: https://konusma-app.onrender.com/test

Status: ✅ Healthy
Deploy: ✅ Successful
SSL: ✅ Active
```

**Sonraki Adımlar:**
1. Custom domain ekle (opsiyonel)
2. Monitoring kur (UptimeRobot)
3. Backup sistemi kur
4. User feedback topla
5. Feature geliştir

---

**Son Güncelleme:** 2024
**Versiyon:** 1.0
**Durum:** Production Ready ✅
