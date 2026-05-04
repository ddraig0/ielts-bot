# 🎓 IELTS Hazırlıq Botu

AI ilə işləyən, aylıq 10 AZN olan kommersial IELTS hazırlıq Telegram botu.

---

## 📁 Fayl Strukturu

```
ielts_bot/
├── bot.py              # Ana bot faylı
├── config.py           # Konfiqurasiya
├── database.py         # SQLite verilənlər bazası
├── ai_service.py       # Claude AI inteqrasiyası
├── keyboards.py        # Telegram klaviaturalar
├── requirements.txt    # Python kitabxanalar
├── .env.example        # Mühit dəyişənləri nümunəsi
├── setup.sh            # Quraşdırma skripti
└── handlers/
    ├── start.py        # /start, ana menyu
    ├── reading.py      # Reading bölməsi
    ├── listening.py    # Listening bölməsi
    ├── writing.py      # Writing + AI qiymətləndirmə
    ├── speaking.py     # Speaking simulyasiyası
    ├── subscription.py # Abunəlik/ödəniş
    └── admin.py        # Admin paneli
```

---

## ⚡ Quraşdırma (5 Dəqiqə)

### 1. Tələblər
- Python 3.10+
- Telegram Bot Token (@BotFather)
- Anthropic API Key (console.anthropic.com)

### 2. Quraşdırma

```bash
# Klonla və qur
cd ielts_bot
chmod +x setup.sh
./setup.sh

# Mühit dəyişənlərini təyin et
cp .env.example .env
nano .env  # doldur

# Botu işə sal
python bot.py
```

### 3. .env Faylı

```env
BOT_TOKEN=7812345678:AAF...
ANTHROPIC_API_KEY=sk-ant-...
ADMIN_IDS=123456789
```

---

## 🤖 Bot Xüsusiyyətləri

### 📖 Reading
- AI tərəfindən yaradılan akademik mətnlər
- 5 sual (True/False/NG, Çoxlu seçim, Boşluq doldurma)
- Ani cavab yoxlama + izahat
- Band Score hesablaması

### 🎧 Listening
- Transkrip əsaslı məşq (real imtahanda audio)
- AI-destekli çevik cavab yoxlama
- Müxtəlif ssenarilər (universitet, hotel, mühazirə...)

### ✍️ Writing
- **Task 1:** Qrafik/Cədvəl təsviri
- **Task 2:** Əsaslandırılmış esse
- 4 kriteriya üzrə AI qiymətləndirmə (Band 0-9)
- Spesifik düzəliş nümunələri

### 🎙️ Speaking
- **Part 1:** Şəxsi suallar (3 sual desti)
- **Part 2:** Cue Card tapşırığı
- **Part 3:** Mövzu müzakirəsi
- AI tərəfindən qiymətləndirmə

---

## 💰 Abunəlik Sistemi

| Plan | Qiymət |
|------|--------|
| 1 ay | 10 AZN |
| 3 ay | 25 AZN |
| 6 ay | 45 AZN |
| Sınaq dövrü | 3 gün (pulsuz) |

**Ödəniş prosesi:**
1. İstifadəçi ödəniş edir → ekran görüntüsü adminə göndərir
2. Admin `/admin` → "Ödəniş Təsdiqlə" → ID + ay sayı daxil edir
3. Bot avtomatik istifadəçiyə bildiriş göndərir

---

## 👑 Admin Paneli

`/admin` komandası ilə:

| Funksiya | Təsvir |
|----------|--------|
| 📊 Statistika | Ümumi istifadəçi, abunəçi, gəlir |
| 👥 İstifadəçilər | Son 20 istifadəçi siyahısı |
| ✅ Ödəniş Təsdiqlə | Manual abunəlik əlavəsi |
| 🚫 Ban | İstifadəçi bloklamaq |

**Yayım:** `/broadcast [mesaj]` — bütün istifadəçilərə göndərir

---

## 🚀 Server-ə Deploy Etmək (VPS)

```bash
# systemd servis yaradın
sudo nano /etc/systemd/system/ielts-bot.service
```

```ini
[Unit]
Description=IELTS Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ielts_bot
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ielts-bot
sudo systemctl start ielts-bot
sudo systemctl status ielts-bot
```

---

## 📈 Gəlir Hesablaması

| İstifadəçi | Aylıq Gəlir |
|------------|-------------|
| 10 abunəçi | 100 AZN |
| 50 abunəçi | 500 AZN |
| 100 abunəçi | 1000 AZN |

**Xərc:** Anthropic API (~0.50-2 AZN/istifadəçi/ay)

---

## 🔧 Gələcək Xüsusiyyətlər (Tövsiyə)

- [ ] Kapital/M10 avtomatik ödəniş inteqrasiyası
- [ ] İstifadəçi irəliləyiş statistikası
- [ ] Həftəlik e-mail/bot hesabatı
- [ ] Mock imtahan (tam 3 saatlıq test)
- [ ] Vocabulary builder modulu
