import string
import random
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# SENİN SHOPIER PAT (PERSONAL ACCESS TOKEN) ANAHTARIN
SHOPIER_PAT_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiJlZWVjZTBiZTNjYmRjNTlkNTMzYjJmYTg2MzRmMjM1MSIsImp0aSI6ImZhZTdiOTdiOTk2NjFiZGRkNzEyZjQ5YjU4OWY3ZTBmZWIyZWVlNTc4YmFiZDc4MDliNjI0ZDMxODA4MmVmZTM2ZWQ0MjVlNzBhMTg1YTNjN2JhNDQwMzQ1YzU5YjNlMmIwMDM1OTVhMjU0ZDc4ZWE1NWVmMTY2YjNjMzU1YmNlYWM4ZmE5OTUxNTBhNzk5NTI4YmI3YjAyZTFiNWU1OWUiLCJpYXQiOjE3ODk4NTA0MTksIm5iZiI6MTc4OTg1MDQxOSwiZXhwIjoxOTQ3NjM1MTc5LCJzdWIiOjE4ODAxODgsInNjb3BlcyI6WyJvcmRlcnM6cmVhZCIsIm9yZGVyczp3cml0ZSIsInByb2R1Y3RzOnJlYWQiLCJwcm9kdWN0czp3cml0ZSIsInNoaXBwaW5nczpyZWFkIiwic2hpcHBpbmdzOndyaXRlIiwiZGlzY291bnRzOnJlYWQiLCJkaXNjb3VudHM6d3JpdGUiLCJwYXlvdXRzOnJlYWQiLCJyZWZ1bmRzOnJlYWQiLCJyZWZ1bmRzOndyaXRlIiwic2hvcDpyZWFkIiwic2hvcDp3cml0ZSJdfQ.Kv-ss-mXsRgqw8Tvzwg_Mrj_CG4hndNQaxRYxiFGcfvM0VrP_Nr3vQkJlI652gnsRjk8yNOsqcwep8qyQ6rXwOpB9GCaNa4f7nPThGp7L6WmpMkB9Gy2qx6IhnM03Fk_5JLQYSYCntpVq0xh9I6T_yJNGXxAW-RBmTkkL-khCpgKRB2T-ZQDKsf5KzI1dK9BLoRXtBeKDxVuM9um66nlsQsl94wcttsD2JJsDdwYSRf00Ex08b8QfJ4Rr44QkOzl8GHrwJt7iw-xjthQVE2TF4bRrYPhi3prRuksV4NOGqTT8aTq600R1GHB_gTTy_NVfwaXYK5W1OKNemo7sUQ1Zg"

# FİRESTORE REST API BİLGİLERİ
PROJECT_ID = "sensisoftware-a3ae2"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def generate_key(product_name):
    prefix = "SENS"
    if "GUI" in product_name: prefix = "SENS-GUI"
    elif "Radar" in product_name: prefix = "SENS-RDR"
    elif "Simulator" in product_name: prefix = "SENS-SIM"
    
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{part1}-{part2}"

@app.route('/', methods=['GET'])
def home():
    return "SensiSoftware Backend Calisiyor!", 200

@app.route('/shopier-webhook', methods=['POST'])
def shopier_webhook():
    data = request.form
    
    # Test bildirimlerinde veya eksik gönderimlerde patlamaması için esnek tutuldu
    status = data.get('status', 'success')
    email = data.get('email', 'test_musteri@mail.com')
    product_name = data.get('product_name', 'Sensi Test Ürünü')
    price = data.get('price', '100')

    duration = "lifetime"
    if "Günlük" in product_name: duration = "daily"
    elif "Aylık" in product_name: duration = "monthly"

    new_key = generate_key(product_name)

    # 1. Lisans olarak Firestore'a ekle
    license_payload = {
        "fields": {
            "userId": {"stringValue": "shopier_alici"},
            "userEmail": {"stringValue": email},
            "productName": {"stringValue": product_name},
            "type": {"stringValue": duration},
            "keyType": {"stringValue": "user"},
            "hwid": {"stringValue": ""},
            "status": {"stringValue": "active"}
        }
    }
    requests.post(f"{FIRESTORE_URL}/licenses?documentId={new_key}", json=license_payload)

    # 2. Sipariş olarak Firestore'a ekle (Admin paneli canlı görsün diye)
    order_payload = {
        "fields": {
            "buyerEmail": {"stringValue": email},
            "productName": {"stringValue": product_name},
            "price": {"stringValue": str(price)},
            "licenseKey": {"stringValue": new_key},
            "shopierApiRef": {"stringValue": SHOPIER_PAT_TOKEN[:20] + "..."}
        }
    }
    requests.post(f"{FIRESTORE_URL}/orders", json=order_payload)

    return jsonify({"status": "success", "key": new_key}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
