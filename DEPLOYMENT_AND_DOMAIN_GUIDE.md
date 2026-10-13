# 🌐 پنجاب فارمیسی (Punjab Pharmacy) - مکمل گائیڈ برائے VS Code اور ڈومین ہوسٹنگ (VS Code & Domain Deployment Guide)

یہ دستاویز آپ کو مرحلہ وار بتاتی ہے کہ آپ اس مکمل ویب سائٹ کو اپنے کمپیوٹر میں **VS Code** کے اندر کیسے چلا سکتے ہیں، اور بعد میں اسے اپنی مرضی کی ڈومین (مثلاً `punjabpharmacy.com` یا `punjabpharmacy.pk`) کے ساتھ انٹرنیٹ پر لائیو کیسے کر سکتے ہیں۔

---

## 📁 1. پروجیکٹ کی فائلوں کی تفصیل (Project Files Overview)

آپ کے پروجیکٹ کے فولڈر میں تمام ضروری فائلیں موجود ہیں:

| فائل کا نام | تفصیل (Description) |
|---|---|
| `app.py` | بیک اینڈ سرور (Flask)، تمام ڈیٹا بیس ماڈلز، REST APIs، جی میل نوٹیفیکیشنز اور لاگ ان لاجک |
| `pharmacy.db` | خودکار SQLite ڈیٹابیس (32 اصلی پاکستانی ادویات، آرڈرز، نسخہ جات، جی میل لاگز اور سیٹنگز) |
| `static/index.html` | ویب سائٹ کا مکمل فرنٹ اینڈ (ہوم پیج، کارٹ، چیک آؤٹ، انوائس، ایڈمن پینل، نسخہ اپ لوڈ) |
| `static/app.js` | کلائنٹ سائیڈ جاوا اسکرپٹ (سرچ، فلٹرز، کارٹ، لائیو اسٹیٹس پولنگ، ایڈمن کنٹرول) |
| `static/styles.css` | ماڈرن ڈیزائن اسٹائلنگ اور پرنٹ انوائس سیٹنگز |
| `requirements.txt` | پائتھون لائبریریوں کی لسٹ (`flask`, `waitress`, `gunicorn`) |
| `run.bat` | ونڈوز کے لیے ایک کلک رنر (Double-click to Run) |
| `run.ps1` | پاور شیل رنر (PowerShell Launcher) |
| `test_api.py` | آٹومیٹڈ ٹیسٹ فائل (تمام 9 فنکشنز کے ٹیسٹ) |
| `.vscode/launch.json` | VS Code کے اندر F5 دبا کر ڈائریکٹ چلانے کی سیٹنگ |
| `uploads/` | مریضوں کے اپ لوڈ کردہ نسخوں کی تصاویر کا فولڈر |

---

## 💻 2. VS Code میں چلانے کا طریقہ (How to Run in VS Code)

### طریقہ کار (Step-by-Step):

1. **VS Code اوپن کریں:**
   - اپنے کمپیوٹر پر **Visual Studio Code** کھولیں۔
   - مینو سے **File -> Open Folder** پر کلک کریں اور `farmacy` فولڈر منتخب کریں۔

2. **پائتھون اور ڈیپینڈنسیز چیک کریں:**
   - VS Code میں ٹرمینل کھولیں (**Terminal -> New Terminal** یا کی بورڈ سے `Ctrl + ~` دبائیں)۔
   - ٹرمینل میں یہ کمانڈ لکھ کر انٹر دبائیں:
   ```bash
   pip install -r requirements.txt
   ```

3. **سرور اسٹارٹ کریں:**
   - ٹرمینل میں یہ کمانڈ لکھیں:
   ```bash
   python app.py
   ```
   - آپ کے سامنے یہ میسج آئے گا:
   ```
   Serving on: http://127.0.0.1:5000
   ```

4. **براؤزر میں دیکھیں:**
   - اپنے گوگل کروم یا کسی بھی براؤزر میں کھولیں:
   ```
   http://127.0.0.1:5000
   ```
   - ویب سائٹ بالکل اسی طرح چلتی ہوئی آپ کے سامنے کھل جائے گی!

5. **VS Code F5 شارٹ کٹ (One-Key Run):**
   - آپ کی سہولت کے لیے ہم نے `.vscode/launch.json` شامل کر دیا ہے۔
   - آپ صرف کی بورڈ سے **F5** دبائیں، ویب سرور فوری اسٹارٹ ہو جائے گا۔

---

## 🌍 3. ڈومین خریدنے اور لائیو کرنے کا طریقہ (Domain & Hosting Setup)

ویب سائٹ کو انٹرنیٹ پر لائیو کرنے کے لیے دو چیزیں درکار ہوتی ہیں:
1. **ڈومین (Domain Name):** مثلاً `punjabpharmacy.com` یا `punjabpharmacy.pk`
2. **ہوسٹنگ (Web Hosting / Server):** جہاں یہ پائتھون کوڈ 24 گھنٹے چلے۔

---

### مرحلہ 1: ڈومین خریدنا (Buy Domain)

1. **.com یا .net ڈومین کے لیے:**
   - ویب سائٹس: [Namecheap.com](https://www.namecheap.com) یا [GoDaddy.com](https://www.godaddy.com)
   - اپنی پسند کا نام سرچ کریں (مثلاً `punjabpharmacy.com`) اور خرید لیں (تقریباً 10$ سے 12$ سالانہ)۔

2. **.pk ڈومین کے لیے (پاکستان کا آفیشل ڈومین):**
   - ویب سائٹس: [PKNIC.net.pk](https://www.pknic.net.pk) یا [HosterPK.com](https://hosterpk.com)
   - مثلاً: `punjabpharmacy.pk` یا `punjabpharmacy.com.pk` (تقریباً 2500 سے 3500 روپے برائے 2 سال)۔

---

### مرحلہ 2: ہوسٹنگ منتخب کرنا (Choose Hosting)

آپ کے پاس 3 بہترین راستے ہیں:

#### 🥇 آپشن A: Render.com یا Railway.app (سب سے آسان اور فری / سستا)
یہ پائتھون کے لیے سب سے بہترین کلاؤڈ پلیٹ فارمز ہیں۔
1. [Render.com](https://render.com) پر فری اکاؤنٹ بنائیں۔
2. اپنا یہ فولڈر **GitHub** پر اپ لوڈ کریں (`git push`)۔
3. Render پر جا کر **New -> Web Service** منتخب کریں اور اپنی GitHub ریپو کنیکٹ کریں۔
4. سیٹنگز درج کریں:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. آپ کو فری لائیو ایڈریس مل جائے گا (مثلاً `punjab-pharmacy.onrender.com`)۔
6. **کسٹم ڈومین جوڑنا:**
   - Render کے ڈیش بورڈ میں **Custom Domains** پر کلک کریں۔
   - اپنی ڈومین لکھیں (مثلاً `punjabpharmacy.com`)۔
   - Render آپ کو ایک `CNAME` یا `A Record` دے گا۔
   - اپنے ڈومین پرووائیڈر (Namecheap/PKNIC) کے DNS میں جا کر وہ ریکارڈ ایڈ کر دیں۔ ڈومین لائیو ہو جائے گی اور SSL (https://) خودکار لگ جائے گا!

---

#### 🥈 آپشن B: PythonAnywhere.com (سادہ پائتھون ہوسٹنگ)
1. [PythonAnywhere.com](https://www.pythonanywhere.com) پر اکاؤنٹ بنائیں۔
2. **Files** ٹیب میں یہ فولڈر زپ کر کے اپ لوڈ اور ان زپ کریں۔
3. **Web** ٹیب میں **Add a new web app -> Flask -> Python 3.10+** منتخب کریں۔
4. ڈائریکٹری کا راستہ `farmacy` اور WSGI فائل میں `from app import app as application` رکھیں۔
5. اپنی کسٹم ڈومین کنیکٹ کریں۔

---

#### 🥉 آپشن C: VPS (Virtual Private Server - Hostinger / DigitalOcean / Hetzner)
اگر آپ چاہتے ہیں کہ ڈیٹا اور سرور مکمل آپ کا ہو:
1. ایک 5$ والا Ubuntu VPS خریدیں۔
2. Nginx اور Gunicorn انسٹال کریں:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx certbot python3-certbot-nginx -y
   ```
3. پروجیکٹ کاپی کریں اور سروس بنائیں:
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```
4. مفت SSL سرٹیفکیٹ لگائیں:
   ```bash
   sudo certbot --nginx -d punjabpharmacy.com -d www.punjabpharmacy.com
   ```

---

## 🔒 4. ایڈمن کنٹرول اور سیکیورٹی کی اہم معلومات

- **مجاز ایڈمن موبائل:** `03045518658`
- **سیکیورٹی پن (Admin PIN):** `7860`
- **ایڈمن Gmail:** `hammadfareed876@gmail.com`
- **ہیلپ لائن:** `03095518882`
- **لوکیشن:** کوٹ سلطان، ضلع لیہ (Kot Sultan, Layyah)

جب بھی آپ سرور کو لائیو کریں گے، یہ تمام سیکیورٹی فیچرز اور جی میل نوٹیفیکیشنز آن لائن ڈومین پر بھی بالکل ایسے ہی 100% پرفیکٹ کام کریں گے۔
