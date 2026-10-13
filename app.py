import os
import sqlite3
import json
import uuid
import urllib.parse
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pharmacy.db')

ADMIN_PHONE = "03045518658"
ADMIN_PIN = "7860"
HELPLINE_PHONE = "03095518882"
ADMIN_GMAIL = "hammadfareed876@gmail.com"
LOCATION_NAME = "Kot Sultan, District Layyah (کوٹ سلطان، ضلع لیہ)"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(reset_products=False):
    conn = get_db()
    cursor = conn.cursor()
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            generic_name TEXT,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            original_price REAL,
            dosage TEXT,
            pack_size TEXT,
            manufacturer TEXT,
            requires_prescription INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 100,
            description TEXT,
            image_url TEXT,
            featured INTEGER DEFAULT 0
        )
    ''')
    
    # Orders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_email TEXT,
            city TEXT NOT NULL,
            address TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            subtotal REAL NOT NULL,
            discount REAL DEFAULT 0,
            delivery_fee REAL DEFAULT 0,
            total REAL NOT NULL,
            status TEXT DEFAULT 'Pending Verification',
            prescription_file TEXT,
            notes TEXT,
            items_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Prescriptions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id TEXT PRIMARY KEY,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            notes TEXT,
            file_path TEXT NOT NULL,
            file_name TEXT NOT NULL,
            status TEXT DEFAULT 'Under Pharmacist Review',
            created_at TEXT NOT NULL
        )
    ''')

    # Customer Order Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            seen INTEGER DEFAULT 0
        )
    ''')

    # Admin Instant Alerts & 12-Hour Reminders Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            alert_type TEXT NOT NULL, -- 'NEW_ORDER' or 'REMINDER_12H'
            message TEXT NOT NULL,
            customer_name TEXT,
            customer_phone TEXT,
            total REAL,
            created_at TEXT NOT NULL,
            seen INTEGER DEFAULT 0
        )
    ''')

    # Admin Settings (Gmail, preferences)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    # Email Notification Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL,
            to_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'Prepared'
        )
    ''')

    # Seed default admin gmail (hammadfareed876@gmail.com)
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_gmail'")
    existing_gmail = cursor.fetchone()
    if not existing_gmail:
        cursor.execute("INSERT INTO settings (key, value) VALUES ('admin_gmail', ?)", (ADMIN_GMAIL,))
    else:
        cursor.execute("UPDATE settings SET value = ? WHERE key = 'admin_gmail'", (ADMIN_GMAIL,))

    if reset_products:
        cursor.execute('DELETE FROM products')
        seed_pakistan_products(cursor)
    else:
        cursor.execute('SELECT COUNT(*) FROM products')
        count = cursor.fetchone()[0]
        if count == 0:
            seed_pakistan_products(cursor)
        
    conn.commit()
    conn.close()

# Automatically ensure database tables & seed data are initialized on startup
try:
    init_db(reset_products=False)
except Exception as e:
    print("Startup DB init error:", e)

def seed_pakistan_products(cursor):
    """
    Most common medicines available in every medical store across Pakistan
    with authentic MRP (original_price) and competitive discounted retail prices (price).
    """
    pakistan_medicines = [
        # Pain, Fever & Cold Relief
        {
            "name": "Panadol 500mg Tablets",
            "generic_name": "Paracetamol",
            "category": "Pain, Fever & Cold",
            "price": 58.0,
            "original_price": 65.0,
            "dosage": "500mg Tablet",
            "pack_size": "Strip of 20 Tablets",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 0,
            "stock": 500,
            "description": "Pakistan's #1 trusted medicine for rapid relief from headache, fever, body aches and pains.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Panadol Extra",
            "generic_name": "Paracetamol 500mg + Caffeine 65mg",
            "category": "Pain, Fever & Cold",
            "price": 90.0,
            "original_price": 100.0,
            "dosage": "500mg / 65mg Tablet",
            "pack_size": "Strip of 20 Tablets",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 0,
            "stock": 420,
            "description": "Fortified paracetamol with caffeine for fast relief of stubborn headaches, migraines and dental pain.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Panadol CF (Cold & Flu)",
            "generic_name": "Paracetamol + Pseudoephedrine + Chlorpheniramine",
            "category": "Pain, Fever & Cold",
            "price": 98.0,
            "original_price": 110.0,
            "dosage": "Combination Caplet",
            "pack_size": "Strip of 10 Caplets",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 0,
            "stock": 350,
            "description": "Complete formula for blocked nose, sinus headache, sneezing, runny nose, and flu fever.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Disprin 300mg Soluble Tablets",
            "generic_name": "Aspirin (Acetylsalicylic Acid)",
            "category": "Pain, Fever & Cold",
            "price": 65.0,
            "original_price": 75.0,
            "dosage": "300mg Soluble Tablet",
            "pack_size": "Box of 30 Tablets",
            "manufacturer": "Reckitt Benckiser",
            "requires_prescription": 0,
            "stock": 480,
            "description": "Fast-dissolving aspirin for quick relief from acute headache, toothache, and cardiovascular emergency use.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Brufen 400mg Tablets",
            "generic_name": "Ibuprofen",
            "category": "Pain, Fever & Cold",
            "price": 125.0,
            "original_price": 140.0,
            "dosage": "400mg Sugar-Coated Tablet",
            "pack_size": "Box of 30 Tablets",
            "manufacturer": "Abbott Laboratories",
            "requires_prescription": 0,
            "stock": 380,
            "description": "Potent anti-inflammatory analgesic for joint pain, muscle swelling, arthritis, and toothache.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Brufen Syrup 120ml",
            "generic_name": "Ibuprofen 100mg/5ml",
            "category": "Pain, Fever & Cold",
            "price": 120.0,
            "original_price": 135.0,
            "dosage": "100mg/5ml Oral Suspension",
            "pack_size": "120ml Glass Bottle",
            "manufacturer": "Abbott Laboratories",
            "requires_prescription": 0,
            "stock": 250,
            "description": "Pediatric suspension for reducing fever and post-immunization or teething pain in children.",
            "image_url": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Arinac Forte Tablets",
            "generic_name": "Ibuprofen 400mg + Pseudoephedrine 60mg",
            "category": "Pain, Fever & Cold",
            "price": 148.0,
            "original_price": 165.0,
            "dosage": "400mg / 60mg Tablet",
            "pack_size": "Strip of 10 Tablets",
            "manufacturer": "Abbott Laboratories",
            "requires_prescription": 0,
            "stock": 310,
            "description": "Powerful relief for nasal congestion, severe sinus headache, cold and seasonal allergies.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Ponstan Forte 500mg",
            "generic_name": "Mefenamic Acid",
            "category": "Pain, Fever & Cold",
            "price": 65.0,
            "original_price": 75.0,
            "dosage": "500mg Film-Coated Tablet",
            "pack_size": "Strip of 10 Tablets",
            "manufacturer": "Pfizer / Viatris",
            "requires_prescription": 0,
            "stock": 420,
            "description": "Primary pain reliever for dental pain, menstrual cramps (dysmenorrhea), and postoperative muscular pain.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "Buscopan Plus Tablets",
            "generic_name": "Hyoscine Butylbromide + Paracetamol",
            "category": "Stomach & Digestion",
            "price": 125.0,
            "original_price": 140.0,
            "dosage": "10mg / 500mg Tablet",
            "pack_size": "Strip of 10 Tablets",
            "manufacturer": "Sanofi Aventis",
            "requires_prescription": 0,
            "stock": 300,
            "description": "Antispasmodic targeting stomach cramps, abdominal colic, renal pain, and intestinal spasms.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        # Stomach & Digestion Care
        {
            "name": "Risek 20mg Capsules",
            "generic_name": "Omeprazole",
            "category": "Stomach & Digestion",
            "price": 370.0,
            "original_price": 410.0,
            "dosage": "20mg Enteric-Coated Capsule",
            "pack_size": "Pack of 14 Capsules",
            "manufacturer": "Getz Pharma",
            "requires_prescription": 0,
            "stock": 450,
            "description": "Most widely used medicine in Pakistan for acidity, GERD, gas, heartburn, and stomach ulcer healing.",
            "image_url": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Risek 40mg Capsules",
            "generic_name": "Omeprazole 40mg",
            "category": "Stomach & Digestion",
            "price": 520.0,
            "original_price": 580.0,
            "dosage": "40mg Capsule",
            "pack_size": "Pack of 14 Capsules",
            "manufacturer": "Getz Pharma",
            "requires_prescription": 0,
            "stock": 260,
            "description": "High potency proton pump inhibitor for severe gastric reflux and erosive esophagitis.",
            "image_url": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "Gaviscon Liquid Aniseed 120ml",
            "generic_name": "Sodium Alginate + Potassium Bicarbonate",
            "category": "Stomach & Digestion",
            "price": 210.0,
            "original_price": 235.0,
            "dosage": "Oral Suspension 120ml",
            "pack_size": "120ml Bottle",
            "manufacturer": "Reckitt Benckiser",
            "requires_prescription": 0,
            "stock": 180,
            "description": "Instant soothing physical barrier that stops acid reflux and chest burning within 3 minutes.",
            "image_url": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Flagyl 400mg Tablets",
            "generic_name": "Metronidazole",
            "category": "Stomach & Digestion",
            "price": 115.0,
            "original_price": 130.0,
            "dosage": "400mg Tablet",
            "pack_size": "Strip of 20 Tablets",
            "manufacturer": "Sanofi Aventis",
            "requires_prescription": 1,
            "stock": 390,
            "description": "Essential treatment for stomach upset, diarrhea, amoebiasis, and dental infections.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Entox-P Tablets",
            "generic_name": "Di-iodohydroxyquinoline + Phthalylsulfathiazole",
            "category": "Stomach & Digestion",
            "price": 75.0,
            "original_price": 85.0,
            "dosage": "Oral Tablet",
            "pack_size": "Strip of 10 Tablets",
            "manufacturer": "Atco Laboratories",
            "requires_prescription": 0,
            "stock": 320,
            "description": "Traditional Pakistani medical store staple for loose motion, acute diarrhea and gut infections.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "ORS Nimkol Powder (5 Sachets)",
            "generic_name": "Oral Rehydration Salts (WHO Formula)",
            "category": "Stomach & Digestion",
            "price": 80.0,
            "original_price": 95.0,
            "dosage": "Electrolyte Powder",
            "pack_size": "Pack of 5 Sachets",
            "manufacturer": "Ferozsons Laboratories",
            "requires_prescription": 0,
            "stock": 400,
            "description": "Essential electrolyte solution for dehydration caused by diarrhea, vomiting, or summer heat.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        # Antibiotics & Infections (Prescription)
        {
            "name": "Augmentin 625mg Tablets",
            "generic_name": "Co-Amoxiclav (Amoxicillin 500mg + Clavulanate 125mg)",
            "category": "Antibiotics & Infections",
            "price": 345.0,
            "original_price": 380.0,
            "dosage": "625mg Tablet",
            "pack_size": "Pack of 10 Tablets",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 1,
            "stock": 250,
            "description": "Gold standard antibiotic for throat, chest, dental, skin and ear bacterial infections.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Augmentin 1g (1000mg) Tablets",
            "generic_name": "Co-Amoxiclav (Amoxicillin 875mg + Clavulanate 125mg)",
            "category": "Antibiotics & Infections",
            "price": 490.0,
            "original_price": 540.0,
            "dosage": "1g (1000mg) Tablet",
            "pack_size": "Pack of 14 Tablets",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 1,
            "stock": 180,
            "description": "High-strength antibacterial for severe respiratory, urinary tract, and dental infections.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "Leflox 500mg Tablets",
            "generic_name": "Levofloxacin",
            "category": "Antibiotics & Infections",
            "price": 385.0,
            "original_price": 430.0,
            "dosage": "500mg Film-Coated Tablet",
            "pack_size": "Pack of 10 Tablets",
            "manufacturer": "Getz Pharma",
            "requires_prescription": 1,
            "stock": 190,
            "description": "Broad-spectrum fluoroquinolone for bronchitis, pneumonia, sinusitis, and urinary infections.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        # Allergy & Cough Syrups
        {
            "name": "Hydryllin Syrup 120ml",
            "generic_name": "Aminophylline + Diphenhydramine + Ammonium Chloride",
            "category": "Cough & Allergy Care",
            "price": 120.0,
            "original_price": 135.0,
            "dosage": "120ml Expectorant Syrup",
            "pack_size": "120ml Bottle",
            "manufacturer": "The Searle Company",
            "requires_prescription": 0,
            "stock": 290,
            "description": "Trusted cough remedy in Pakistan for chesty cough, throat tickle, asthma and allergy wheezing.",
            "image_url": "https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Rigix 10mg Tablets",
            "generic_name": "Cetirizine Hydrochloride",
            "category": "Cough & Allergy Care",
            "price": 135.0,
            "original_price": 150.0,
            "dosage": "10mg Film-Coated Tablet",
            "pack_size": "Pack of 10 Tablets",
            "manufacturer": "AGP Limited",
            "requires_prescription": 0,
            "stock": 340,
            "description": "Non-sedating antihistamine for seasonal allergic rhinitis, dust allergy, skin hives and itching.",
            "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        # Skin & Eye Ointments
        {
            "name": "Polyfax Skin Ointment 20g",
            "generic_name": "Polymyxin B Sulfate + Bacitracin Zinc",
            "category": "Ointments & First Aid",
            "price": 98.0,
            "original_price": 115.0,
            "dosage": "Topical Antibacterial Ointment",
            "pack_size": "20g Aluminum Tube",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 0,
            "stock": 380,
            "description": "The household antibacterial ointment in every Pakistani home for cuts, burns, scrapes, and wounds.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Polyfax Eye Ointment 6g",
            "generic_name": "Polymyxin B + Bacitracin (Sterile Ophthalmic)",
            "category": "Ointments & First Aid",
            "price": 75.0,
            "original_price": 85.0,
            "dosage": "Sterile Eye Ointment",
            "pack_size": "6g Sterile Tube",
            "manufacturer": "GSK Pakistan",
            "requires_prescription": 0,
            "stock": 270,
            "description": "Special sterile ointment for conjunctivitis, red eye, styes, and superficial ocular bacterial infections.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "Pyodine Solution 10% (60ml)",
            "generic_name": "Povidone Iodine 10%",
            "category": "Ointments & First Aid",
            "price": 110.0,
            "original_price": 125.0,
            "dosage": "Topical Antiseptic Solution",
            "pack_size": "60ml Bottle",
            "manufacturer": "Brookes Pharma",
            "requires_prescription": 0,
            "stock": 250,
            "description": "Antiseptic solution for immediate disinfection of cuts, abrasions, lacerations and surgical wounds.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        {
            "name": "Dettol Antiseptic Liquid 250ml",
            "generic_name": "Chloroxylenol Antiseptic",
            "category": "Ointments & First Aid",
            "price": 285.0,
            "original_price": 320.0,
            "dosage": "Liquid Antiseptic",
            "pack_size": "250ml Bottle",
            "manufacturer": "Reckitt Benckiser",
            "requires_prescription": 0,
            "stock": 200,
            "description": "Standard first-aid antiseptic and hygiene disinfectant protecting against bacteria and germs.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Saniplast Bandages (Box of 100)",
            "generic_name": "Medicated Adhesive Bandages",
            "category": "Ointments & First Aid",
            "price": 250.0,
            "original_price": 280.0,
            "dosage": "Adhesive Dressing",
            "pack_size": "Box of 100 Strips",
            "manufacturer": "English Boot House Pharma",
            "requires_prescription": 0,
            "stock": 350,
            "description": "Waterproof medicated adhesive strips for cuts, minor finger wounds, and daily protection.",
            "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        # Vitamins, Minerals & Immunity
        {
            "name": "Surbex-Z High Potency Tablets",
            "generic_name": "Zinc + Vitamin B-Complex + Vitamin C & E",
            "category": "Vitamins & Supplements",
            "price": 395.0,
            "original_price": 440.0,
            "dosage": "Multivitamin Tablet",
            "pack_size": "Bottle of 30 Tablets",
            "manufacturer": "Abbott Laboratories",
            "requires_prescription": 0,
            "stock": 300,
            "description": "High potency Zinc and Vitamin B complex to boost physical stamina, fight fatigue and improve hair & skin health.",
            "image_url": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "CaC 1000 Plus Effervescent Tablets",
            "generic_name": "Calcium Lactate + Vitamin C, D3 & B6",
            "category": "Vitamins & Supplements",
            "price": 330.0,
            "original_price": 370.0,
            "dosage": "Effervescent Tablet (Orange)",
            "pack_size": "Tube of 10 Tablets",
            "manufacturer": "GSK Consumer Healthcare",
            "requires_prescription": 0,
            "stock": 380,
            "description": "Refreshing orange calcium and Vitamin C drink tablet for strong bones, teeth and immune defense.",
            "image_url": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Sunny D 200,000 IU Oral Ampoule",
            "generic_name": "Cholecalciferol (Vitamin D3)",
            "category": "Vitamins & Supplements",
            "price": 250.0,
            "original_price": 280.0,
            "dosage": "200,000 IU Oral Ampoule (1ml)",
            "pack_size": "Single Dose Ampoule",
            "manufacturer": "PharmEvo",
            "requires_prescription": 0,
            "stock": 210,
            "description": "High-dose oral Vitamin D3 for bone density replenishment, joint stiffness, and deficiency treatment.",
            "image_url": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Evion 400mg Softgel Capsules",
            "generic_name": "Vitamin E (Tocopheryl Acetate)",
            "category": "Vitamins & Supplements",
            "price": 185.0,
            "original_price": 210.0,
            "dosage": "400mg Softgel",
            "pack_size": "Pack of 30 Softgels",
            "manufacturer": "Merck / Martin Dow",
            "requires_prescription": 0,
            "stock": 240,
            "description": "Pure Vitamin E antioxidant for skin glow, acne scar healing, hair nourishment, and muscle repair.",
            "image_url": "https://images.unsplash.com/photo-1577401239170-897942555fb3?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        },
        # Medical Devices & Monitoring
        {
            "name": "Certeza Digital BP Monitor BM-407",
            "generic_name": "Automated Upper Arm Blood Pressure Monitor",
            "category": "Medical Devices",
            "price": 4200.0,
            "original_price": 4800.0,
            "dosage": "Diagnostic Device",
            "pack_size": "1 Unit with Cuff & Adapter",
            "manufacturer": "Certeza Medical Germany",
            "requires_prescription": 0,
            "stock": 40,
            "description": "Accurate European standard upper arm BP machine with WHO hypertension indicator and memory recall.",
            "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Accu-Chek Instant Blood Glucose Meter",
            "generic_name": "Blood Sugar Testing Monitor",
            "category": "Medical Devices",
            "price": 2450.0,
            "original_price": 2800.0,
            "dosage": "Diagnostic Kit",
            "pack_size": "Meter + 10 Strips + Lancets",
            "manufacturer": "Roche Diabetes Care",
            "requires_prescription": 0,
            "stock": 50,
            "description": "World's most popular glucometer with target range indicator and instant 4-second accurate blood sugar reading.",
            "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop&q=60",
            "featured": 1
        },
        {
            "name": "Accu-Chek Instant Test Strips (50 Pack)",
            "generic_name": "Blood Glucose Test Strips",
            "category": "Medical Devices",
            "price": 2250.0,
            "original_price": 2500.0,
            "dosage": "50 Test Strips",
            "pack_size": "Vial of 50 Strips",
            "manufacturer": "Roche Diabetes Care",
            "requires_prescription": 0,
            "stock": 110,
            "description": "Authentic fresh-dated Roche test strips for Accu-Chek Instant meter.",
            "image_url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=500&auto=format&fit=crop&q=60",
            "featured": 0
        }
    ]

    for p in pakistan_medicines:
        cursor.execute('''
            INSERT INTO products (
                name, generic_name, category, price, original_price, dosage,
                pack_size, manufacturer, requires_prescription, stock,
                description, image_url, featured
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p["name"], p["generic_name"], p["category"], p["price"], p["original_price"],
            p["dosage"], p["pack_size"], p["manufacturer"], p["requires_prescription"],
            p["stock"], p["description"], p["image_url"], p["featured"]
        ))

# Initialize database and seed updated authentic products
init_db(reset_products=True)

# ==================== REST API ROUTES ====================

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        "status": "success",
        "pharmacy_name": "Punjab Pharmacy (پنجاب فارمیسی)",
        "location": LOCATION_NAME,
        "admin_phone": ADMIN_PHONE,
        "helpline": HELPLINE_PHONE,
        "whatsapp_url": f"https://wa.me/92{ADMIN_PHONE[1:]}"
    })

@app.route('/api/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    rx_only = request.args.get('rx')
    
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if category and category.lower() != 'all':
        query += " AND category = ?"
        params.append(category)
        
    if search:
        query += " AND (name LIKE ? OR generic_name LIKE ? OR manufacturer LIKE ? OR description LIKE ?)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search, like_search, like_search])
        
    if rx_only is not None and rx_only != '':
        query += " AND requires_prescription = ?"
        params.append(1 if rx_only == 'true' or rx_only == '1' else 0)
        
    query += " ORDER BY featured DESC, id ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    products = [dict(row) for row in rows]
    return jsonify({"status": "success", "count": len(products), "data": products})

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"status": "error", "message": "Product not found"}), 404
        
    return jsonify({"status": "success", "data": dict(row)})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category, count(*) as count FROM products GROUP BY category")
    rows = cursor.fetchall()
    conn.close()
    
    categories = [{"category": row["category"], "count": row["count"]} for row in rows]
    return jsonify({"status": "success", "data": categories})

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload provided"}), 400
        
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    address = data.get('address', '').strip()
    city = data.get('city', 'Kot Sultan, Layyah').strip()
    items = data.get('items', [])
    
    if not customer_name or not customer_phone or not address:
        return jsonify({"status": "error", "message": "Customer name, phone number, and address are required"}), 400
        
    if not items or len(items) == 0:
        return jsonify({"status": "error", "message": "Cart is empty"}), 400
        
    order_id = "PP-" + datetime.now().strftime("%y%m") + "-" + uuid.uuid4().hex[:5].upper()
    subtotal = float(data.get('subtotal', 0))
    discount = float(data.get('discount', 0))
    delivery_fee = 0.0 if subtotal >= 1500 else 150.0
    total = max(0.0, subtotal - discount + delivery_fee)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (
            id, customer_name, customer_phone, customer_email, city, address,
            payment_method, subtotal, discount, delivery_fee, total, status,
            prescription_file, notes, items_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order_id,
        customer_name,
        customer_phone,
        data.get('customer_email', ''),
        city,
        address,
        data.get('payment_method', 'Cash on Delivery'),
        subtotal,
        discount,
        delivery_fee,
        total,
        'Pending Verification',
        data.get('prescription_file', ''),
        data.get('notes', ''),
        json.dumps(items),
        now_str
    ))

    # Fetch configured admin gmail
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_gmail'")
    admin_gmail_row = cursor.fetchone()
    admin_gmail = admin_gmail_row['value'] if (admin_gmail_row and admin_gmail_row['value']) else ADMIN_GMAIL

    # Full itemized medicine list for Gmail & WhatsApp notification
    full_items_lines = []
    for it in items:
        it_name = it.get('name', 'دوا')
        it_qty = it.get('quantity', 1)
        it_price = float(it.get('price', 0)) * int(it_qty)
        full_items_lines.append(f"• {it_name} (x{it_qty}) - Rs. {it_price:.0f}")
    full_items_text = "\n".join(full_items_lines)

    items_summary = ", ".join([f"{it.get('name', 'Item')} (x{it.get('quantity', 1)})" for it in items[:3]])
    if len(items) > 3:
        items_summary += f" + {len(items)-3} more"
        
    # 1. Admin Panel In-App Alert
    admin_alert_msg = f"نیا آرڈر {order_id} گاہک {customer_name} ({customer_phone}) کی جانب سے موصول ہوا ہے۔ کل رقم: Rs. {total:.0f}"
    cursor.execute('''
        INSERT INTO admin_alerts (order_id, alert_type, message, customer_name, customer_phone, total, created_at, seen)
        VALUES (?, 'NEW_ORDER', ?, ?, ?, ?, ?, 0)
    ''', (order_id, admin_alert_msg, customer_name, customer_phone, total, now_str))
    
    # 2. Admin Gmail Notification (hammadfareed876@gmail.com)
    email_subject = f"🚨 نیا آرڈر: {order_id} - {customer_name} (Rs. {total:.0f}) | Punjab Pharmacy Kot Sultan"
    email_body = f"""محترم ایڈمن! (پنجاب فارمیسی کوٹ سلطان، ضلع لیہ)

آپ کی ویب سائٹ پر ایک نیا آرڈر موصول ہو چکا ہے۔

📋 آرڈر کی تفصیلات:
----------------------------------------
آرڈر نمبر: {order_id}
تاریخ و وقت: {now_str}
گاہک کا نام: {customer_name}
موبائل / واٹس ایپ نمبر: {customer_phone}
شہر / علاقہ: {city}
ڈیلیوری پتہ: {address}
طریقہ ادائیگی: {data.get('payment_method', 'Cash on Delivery')}

📦 ادویات کی فہرست:
----------------------------------------
{full_items_text}

----------------------------------------
سب ٹوٹل: Rs. {subtotal:.0f}
رعایت (Discount): Rs. {discount:.0f}
ڈیلیوری چارجز: Rs. {delivery_fee:.0f}
کل قابلِ ادائیگی رقم: Rs. {total:.0f}

⚠️ ضروری نوٹ:
برائے مہربانی ایڈمن پینل سے ادویات کی تصدیق (Verification) فرمائیں۔
ایڈمن رابطہ: {ADMIN_PHONE} | ہیلپ لائن: {HELPLINE_PHONE}
"""

    cursor.execute('''
        INSERT INTO email_logs (order_id, to_email, subject, body, created_at, status)
        VALUES (?, ?, ?, ?, ?, 'Dispatched')
    ''', (order_id, admin_gmail, email_subject, email_body, now_str))

    conn.commit()
    conn.close()
    
    # Pre-formatted Instant WhatsApp notification for Admin 03045518658
    admin_clean_phone = ADMIN_PHONE.replace('-', '').replace(' ', '')
    if admin_clean_phone.startswith('0'):
        admin_clean_phone = '92' + admin_clean_phone[1:]
        
    admin_wa_text = f"*🔔 نیا آرڈر موصول ہوا! (New Order Placed)*\nپنجاب فارمیسی کوٹ سلطان (لیہ)\n\n*آرڈر نمبر:* {order_id}\n*گاہک:* {customer_name}\n*فون:* {customer_phone}\n*شہر:* {city}\n*پتہ:* {address}\n*کل رقم:* Rs. {total:.0f}\n*طریقہ ادائیگی:* {data.get('payment_method')}\n\n*ادویات:*\n{full_items_text}\n\nبرائے مہربانی ادویات ویریفائی کر کے ڈیلیوری کے لیے روانہ فرمائیں۔"
    admin_wa_url = f"https://wa.me/{admin_clean_phone}?text={urllib.parse.quote(admin_wa_text)}"
    
    # Gmail Direct Web Compose URL for instant access
    gmail_compose_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={urllib.parse.quote(admin_gmail)}&su={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"

    return jsonify({
        "status": "success",
        "message": f"Order successfully placed with Punjab Pharmacy ({LOCATION_NAME})!",
        "order_id": order_id,
        "total": total,
        "delivery_fee": delivery_fee,
        "created_at": now_str,
        "admin_contact": ADMIN_PHONE,
        "admin_gmail": admin_gmail,
        "admin_gmail_compose_url": gmail_compose_url,
        "admin_wa_url": admin_wa_url
    }), 201

@app.route('/api/orders/track', methods=['GET'])
def track_order():
    order_id = request.args.get('order_id', '').strip()
    phone = request.args.get('phone', '').strip()
    
    if not order_id and not phone:
        return jsonify({"status": "error", "message": "Please provide an Order ID or Phone number"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    if order_id:
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    else:
        cursor.execute("SELECT * FROM orders WHERE customer_phone = ? ORDER BY created_at DESC LIMIT 1", (phone,))
        
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"status": "error", "message": "No order found matching your inquiry"}), 404
        
    order = dict(row)
    order['items'] = json.loads(order['items_json'])
    del order['items_json']
    
    return jsonify({"status": "success", "data": order})

@app.route('/api/prescriptions/upload', methods=['POST'])
def upload_prescription():
    if 'prescription' not in request.files:
        return jsonify({"status": "error", "message": "No prescription image or file uploaded"}), 400
        
    file = request.files['prescription']
    if file.filename == '':
        return jsonify({"status": "error", "message": "Selected file has no filename"}), 400
        
    patient_name = request.form.get('patient_name', 'Customer').strip()
    phone = request.form.get('phone', '').strip()
    city = request.form.get('city', 'Kot Sultan, Layyah').strip()
    address = request.form.get('address', '').strip()
    notes = request.form.get('notes', '').strip()
    
    if not phone:
        return jsonify({"status": "error", "message": "Contact phone number is required"}), 400
        
    rx_id = "RX-" + datetime.now().strftime("%y%m") + "-" + uuid.uuid4().hex[:4].upper()
    ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{rx_id}{ext}"
    full_path = os.path.join(UPLOAD_FOLDER, saved_filename)
    file.save(full_path)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prescriptions (
            id, patient_name, phone, city, address, notes, file_path, file_name, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        rx_id, patient_name, phone, city, address, notes, saved_filename, file.filename, 'Under Pharmacist Review', now_str
    ))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": f"Prescription received! Punjab Pharmacy Kot Sultan pharmacist will call/WhatsApp you on {phone} within 15 minutes.",
        "rx_id": rx_id,
        "saved_filename": saved_filename
    }), 201

@app.route('/api/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ==================== ADMIN AUTHENTICATION & PORTAL ====================

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    phone = data.get('phone', '').strip().replace('-', '').replace(' ', '')
    pin = data.get('pin', '').strip()
    
    expected_clean_phone = ADMIN_PHONE.replace('-', '').replace(' ', '')
    
    if phone == expected_clean_phone and pin == ADMIN_PIN:
        token = f"admin_auth_{uuid.uuid4().hex[:12]}"
        return jsonify({
            "status": "success",
            "message": f"Welcome Admin ({ADMIN_PHONE}) to Punjab Pharmacy Kot Sultan Dashboard!",
            "token": token,
            "admin_phone": ADMIN_PHONE
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Unauthorized Access! Admin control is strictly reserved for {ADMIN_PHONE}."
        }), 401

@app.route('/api/admin/orders', methods=['GET'])
def admin_orders():
    # Verify Authorization
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_') and request.args.get('token', '') == '':
        return jsonify({"status": "error", "message": f"Unauthorized. Admin login with {ADMIN_PHONE} required."}), 401
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) as total_orders, SUM(total) as total_sales FROM orders")
    stats = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Under Pharmacist Review'")
    pending_rx = cursor.fetchone()[0]
    
    conn.close()
    
    orders = []
    for r in rows:
        od = dict(r)
        od['items'] = json.loads(od['items_json'])
        orders.append(od)
        
    return jsonify({
        "status": "success",
        "total_orders": stats["total_orders"] or 0,
        "total_sales": stats["total_sales"] or 0.0,
        "pending_prescriptions": pending_rx,
        "data": orders
    })

@app.route('/api/admin/orders/<order_id>/status', methods=['POST'])
def update_order_status(order_id):
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_'):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    data = request.json or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({"status": "error", "message": "New status is required"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    
    # Fetch full order details including items, address, total, payment method
    cursor.execute("SELECT customer_name, customer_phone, city, address, payment_method, total, items_json FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    
    if not order_row:
        conn.close()
        return jsonify({"status": "error", "message": "Order not found"}), 404
        
    cust_name = order_row['customer_name']
    cust_phone = order_row['customer_phone']
    cust_city = order_row['city']
    cust_address = order_row['address']
    cust_payment = order_row['payment_method']
    cust_total = order_row['total']
    
    items = []
    try:
        items = json.loads(order_row['items_json'])
    except Exception:
        items = []

    # Build detailed itemized product list
    items_lines = []
    for it in items:
        name = it.get('name', 'دوا')
        qty = it.get('quantity', 1)
        price = float(it.get('price', 0)) * int(qty)
        items_lines.append(f"• {name} (تعداد: {qty}) - Rs. {price:.0f}")
        
    products_detail_str = "\n".join(items_lines) if items_lines else "• تمام منتخب کردہ ادویات"
    
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    
    # Status Message Headline based on status
    status_messages = {
        "Verified by Pharmacist": "آپ کا آرڈر اور تمام ادویات پنجاب فارمیسی کوٹ سلطان (لیہ) کے کوالیفائیڈ فارماسسٹ نے ویریفائی (تصدیق) کر لی ہیں اور تیاری شروع ہو چکی ہے!",
        "Packed in Cold-Box": "آپ کی ادویات محفوظ درجہ حرارت اور پیکنگ میں تیار کر لی گئی ہیں!",
        "Out for Delivery": "آپ کا آرڈر کوٹ سلطان / لیہ رائڈر کو سونپ دیا گیا ہے اور ڈیلیوری کے لیے روانہ ہو چکا ہے!",
        "Delivered": "آپ کا آرڈر کامیابی سے ڈیلیور ہو چکا ہے۔ پنجاب فارمیسی کوٹ سلطان کا انتخاب کرنے کا شکریہ!",
        "Cancelled": "آپ کا آرڈر منسوخ کر دیا گیا ہے۔ مزید معلومات کے لیے 03095518882 پر رابطہ کریں۔"
    }
    status_headline = status_messages.get(new_status, f"آپ کے آرڈر کا اسٹیٹس اپ ڈیٹ ہو گیا ہے: {new_status}")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Comprehensive customer notification with Product Names and Order Information
    customer_notification_msg = (
        f"{status_headline}\n\n"
        f"📦 شامل ادویات کی تفصیل:\n{products_detail_str}\n\n"
        f"💰 کل رقم: Rs. {cust_total:.0f}\n"
        f"💳 طریقہ ادائیگی: {cust_payment}\n"
        f"📍 ڈیلیوری پتہ: {cust_address}, {cust_city}\n"
        f"📞 ہیلپ لائن: {HELPLINE_PHONE}"
    )
    
    # Save notification for customer in database
    cursor.execute('''
        INSERT INTO order_notifications (order_id, phone, status, message, created_at, seen)
        VALUES (?, ?, ?, ?, ?, 0)
    ''', (order_id, cust_phone, new_status, customer_notification_msg, now_str))
    
    conn.commit()
    conn.close()
    
    # Clean phone for WhatsApp notify link
    clean_phone = cust_phone.replace('-', '').replace(' ', '').replace('+', '')
    if clean_phone.startswith('0'):
        clean_phone = '92' + clean_phone[1:]
    elif not clean_phone.startswith('92'):
        clean_phone = '92' + clean_phone
        
    wa_text = (
        f"*محترم {cust_name}!* (پنجاب فارمیسی کوٹ سلطان، ضلع لیہ)\n\n"
        f"آپ کے آرڈر *{order_id}* کی تصدیق و تازہ ترین اپ ڈیٹ:\n"
        f"📍 *اسٹیٹس:* {new_status}\n"
        f"ℹ️ {status_headline}\n\n"
        f"*📦 شامل ادویات:*\n{products_detail_str}\n\n"
        f"*💰 کل رقم:* Rs. {cust_total:.0f}\n"
        f"*💳 طریقہ ادائیگی:* {cust_payment}\n"
        f"*📍 پتہ:* {cust_address}, {cust_city}\n\n"
        f"📞 ہیلپ لائن: {HELPLINE_PHONE} | شکریہ!"
    )
    wa_notify_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_text)}"
    
    return jsonify({
        "status": "success",
        "message": f"Order {order_id} updated to {new_status}. Customer notification created with complete products & order info!",
        "notification_text": customer_notification_msg,
        "order_id": order_id,
        "customer_phone": cust_phone,
        "products": items,
        "total": cust_total,
        "wa_notify_url": wa_notify_url
    })

# Admin Settings API (Gmail Configuration & Preferences)
@app.route('/api/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_') and request.args.get('token', '') == '':
        return jsonify({"status": "error", "message": f"Unauthorized. Admin login with {ADMIN_PHONE} required."}), 401
        
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json or {}
        new_gmail = data.get('admin_gmail', '').strip()
        if new_gmail:
            cursor.execute('''
                INSERT INTO settings (key, value) VALUES ('admin_gmail', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            ''', (new_gmail,))
            conn.commit()
            
    cursor.execute("SELECT value FROM settings WHERE key = 'admin_gmail'")
    row = cursor.fetchone()
    admin_gmail = row['value'] if row else ADMIN_GMAIL
    conn.close()
    
    return jsonify({
        "status": "success",
        "admin_gmail": admin_gmail,
        "admin_phone": ADMIN_PHONE,
        "helpline_phone": HELPLINE_PHONE,
        "location": LOCATION_NAME
    })

# Admin Email Notifications Logs API
@app.route('/api/admin/emails', methods=['GET'])
def get_admin_emails():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_') and request.args.get('token', '') == '':
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_logs ORDER BY id DESC LIMIT 25")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "status": "success",
        "data": [dict(r) for r in rows]
    })

@app.route('/api/orders/<order_id>/notifications', methods=['GET'])
def get_order_notifications(order_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM order_notifications WHERE order_id = ? ORDER BY id DESC LIMIT 5", (order_id,))
    rows = cursor.fetchall()
    
    # Also fetch current status
    cursor.execute("SELECT status FROM orders WHERE id = ?", (order_id,))
    order_row = cursor.fetchone()
    conn.close()
    
    current_status = order_row['status'] if order_row else 'Pending Verification'
    notifications = [dict(r) for r in rows]
    
    return jsonify({
        "status": "success",
        "current_status": current_status,
        "notifications": notifications
    })

@app.route('/api/customer/notifications', methods=['GET'])
def get_customer_live_notifications():
    phone = request.args.get('phone', '').strip()
    if not phone:
        return jsonify({"status": "success", "notifications": []})
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM order_notifications 
        WHERE phone LIKE ? 
        ORDER BY id DESC LIMIT 5
    ''', (f"%{phone.replace('-', '').replace(' ', '')[-7:]}%",))
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "status": "success",
        "notifications": [dict(r) for r in rows]
    })

# 12-Hour Pending Reminders & Instant Admin Alerts
@app.route('/api/admin/pending_reminders', methods=['GET'])
def check_pending_reminders():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_') and request.args.get('token', '') == '':
        return jsonify({"status": "error", "message": f"Unauthorized. Admin login with {ADMIN_PHONE} required."}), 401
        
    simulate = request.args.get('simulate', '0') == '1'
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE status = 'Pending Verification' ORDER BY created_at ASC")
    pending_orders = cursor.fetchall()
    
    now = datetime.now()
    overdue_list = []
    
    for row in pending_orders:
        o = dict(row)
        try:
            created_dt = datetime.strptime(o['created_at'], "%Y-%m-%d %H:%M:%S")
            elapsed_hours = (now - created_dt).total_seconds() / 3600.0
        except Exception:
            elapsed_hours = 0.0
            
        is_overdue = elapsed_hours >= 12.0 or (simulate and len(overdue_list) < 5)
        
        if is_overdue:
            hours_display = round(elapsed_hours, 1) if elapsed_hours >= 1.0 else round(elapsed_hours * 60) # mins or hrs
            unit = "گھنٹے" if elapsed_hours >= 1.0 else "منٹ"
            
            # Formatted 12-Hour Reminder WhatsApp link to Admin 03045518658
            admin_clean_phone = ADMIN_PHONE.replace('-', '').replace(' ', '')
            if admin_clean_phone.startswith('0'):
                admin_clean_phone = '92' + admin_clean_phone[1:]
                
            reminder_msg = f"*⚠️ ارجنٹ ریمائنڈر (12 گھنٹے سے زائد زیرِ التواء)*\nپنجاب فارمیسی کوٹ سلطان\n\n*آرڈر نمبر:* {o['id']}\n*گاہک:* {o['customer_name']} ({o['customer_phone']})\n*شہر:* {o['city']}\n*رقم:* Rs. {o['total']:.0f}\n*گزر چکا وقت:* {hours_display} {unit}\n\nیہ آرڈر ابھی تک ویریفائی نہیں ہوا۔ برائے مہربانی فوری ایڈمن پینل سے پراسیس فرمائیں!"
            reminder_wa_url = f"https://wa.me/{admin_clean_phone}?text={reminder_msg}"
            
            overdue_list.append({
                "id": o['id'],
                "customer_name": o['customer_name'],
                "customer_phone": o['customer_phone'],
                "city": o['city'],
                "total": o['total'],
                "created_at": o['created_at'],
                "elapsed_hours": round(elapsed_hours, 1),
                "reminder_wa_url": reminder_wa_url,
                "reminder_msg": reminder_msg
            })
            
    conn.close()
    
    return jsonify({
        "status": "success",
        "count": len(overdue_list),
        "admin_phone": ADMIN_PHONE,
        "overdue_orders": overdue_list
    })

@app.route('/api/admin/alerts', methods=['GET'])
def get_admin_alerts():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_') and request.args.get('token', '') == '':
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin_alerts ORDER BY id DESC LIMIT 15")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "status": "success",
        "alerts": [dict(r) for r in rows]
    })

@app.route('/api/admin/prescriptions', methods=['GET'])
def admin_prescriptions():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer admin_auth_'):
        return jsonify({"status": "error", "message": f"Unauthorized. Admin login with {ADMIN_PHONE} required."}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prescriptions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return jsonify({
        "status": "success",
        "data": [dict(r) for r in rows]
    })

if __name__ == '__main__':
    print("=================================================================")
    print("       PUNJAB PHARMACY (KOT SULTAN, LAYYAH) - WEB SERVER         ")
    print("       Helpline: 03095518882 | Admin/WhatsApp: 03045518658       ")
    print("       Serving on: http://127.0.0.1:5000                        ")
    print("=================================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
