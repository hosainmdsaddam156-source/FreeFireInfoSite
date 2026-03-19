import asyncio
import time
import httpx
import json
from collections import defaultdict
from functools import wraps
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from cachetools import TTLCache
from typing import Tuple
# তোমার proto import করো — যদি error আসে তাহলে comment করে দাও এবং dummy response দিয়ে টেস্ট করো
# from proto import FreeFire_pb2, main_pb2, AccountPersonalShow_pb2
# from google.protobuf import json_format, message
# from google.protobuf.message import Message
from Crypto.Cipher import AES
import base64
import random
import threading

app = Flask(__name__)
CORS(app)
cache = TTLCache(maxsize=100, ttl=300)
cached_tokens = defaultdict(dict)

# === Settings ===
MAIN_KEY = base64.b64decode('WWcmdGMlREV1aDYlWmNeOA==')
MAIN_IV = base64.b64decode('Nm95WkRyMjJFM3ljaGpNJQ==')
RELEASEVERSION = "OB50"  # OB49 থেকে OB50 করে দিলাম (চেঞ্জ করো যদি লাগে)
USERAGENT = "Dalvik/2.1.0 (Linux; U; Android 14; SM-A546E Build/TP1A.220624.014)"
SUPPORTED_REGIONS = {"IND", "BR", "US", "SAC", "NA", "SG", "RU", "ID", "TW", "VN", "TH", "ME", "PK", "CIS", "BD", "EUROPE"}

def get_account_credentials(region: str) -> str:
    # accounts.txt না থাকায় dummy credential দিলাম — real credential ব্যবহার করলে accounts.txt ফাইল বানিয়ে রাখো
    r = region.upper()
    if r == "BD":
        return "uid=9999999999&password=0000000000000000000000000000000000000000000000000000000000000000"  # dummy
    # অন্য রিজিয়নের জন্যও dummy দাও বা তোমার পুরানো লজিক রাখো
    return "uid=3692279677&password=473AFFEF67F708CBB0962A958BB2809DA0843EA41BDB70D738FD9527EA04B27B"  # default IND

# Token Generation (আপডেটেড headers + error logging)
async def get_access_token(account: str):
    url = "https://ffmconnect.live.gop.garenanow.com/oauth/guest/token/grant"
    payload = account + "&response_type=token&client_type=2&client_secret=2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3&client_id=100067"
    headers = {'User-Agent': USERAGENT, 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip", 'Content-Type': "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=payload, headers=headers)
        print("Access token response status:", resp.status_code)  # log
        try:
            data = resp.json()
            return data.get("access_token", "0"), data.get("open_id", "0")
        except:
            return "0", "0"

async def create_jwt(region: str):
    account = get_account_credentials(region)
    token_val, open_id = await get_access_token(account)
    body = json.dumps({"open_id": open_id, "open_id_type": "4", "login_token": token_val, "orign_platform_type": "4"})
    # proto_bytes = await json_to_proto(body, FreeFire_pb2.LoginReq())  # comment out যদি proto error আসে
    proto_bytes = body.encode()  # temporary dummy — real proto fix করো
    payload = aes_cbc_encrypt(MAIN_KEY, MAIN_IV, proto_bytes)
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {'User-Agent': USERAGENT, 'Connection': "Keep-Alive", 'Accept-Encoding': "gzip",
               'Content-Type': "application/octet-stream", 'Expect': "100-continue", 'X-Unity-Version': "2018.4.11f1",
               'X-GA': "v1 1", 'ReleaseVersion': RELEASEVERSION}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=payload, headers=headers)
        print("Login response status:", resp.status_code)
        print("Raw login response:", resp.content[:300])  # log for debugging
        try:
            # msg = json.loads(json_format.MessageToJson(decode_protobuf(resp.content, FreeFire_pb2.LoginRes)))
            msg = {"token": "dummy_token", "lockRegion": region, "serverUrl": "dummy_url"}  # temporary dummy
            cached_tokens[region] = {
                'token': f"Bearer {msg.get('token','0')}",
                'region': msg.get('lockRegion','0'),
                'server_url': msg.get('serverUrl','0'),
                'expires_at': time.time() + 25200
            }
        except Exception as e:
            print("Parsing error:", str(e))

# ... (তোমার বাকি ফাংশন যেমন initialize_tokens, refresh_tokens_periodically, get_token_info, GetAccountInformation রাখো বা comment করে dummy return দাও)

# Routes
@app.route('/')
def home():
    return render_template_string("""
    <h1 style="color:#ffcc00;">Free Fire Player Info Checker (Demo)</h1>
    <p>এটা শুধুমাত্র পাবলিক প্লেয়ার ইনফো দেখার টুল। কোনো top-up বা hack নেই।</p>
    <p>উদাহরণ: <code>/player-info?region=BD&uid=123456789</code></p>
    <p><a href="/refresh">Tokens Refresh করুন</a></p>
    """)

@app.route('/player-info')
def get_account_info():
    region = request.args.get('region')
    uid = request.args.get('uid')
    if not uid or not region:
        return jsonify({"error": "UID and REGION দরকার"}), 400
    try:
        # return_data = asyncio.run(GetAccountInformation(uid, "7", region, "/GetPlayerPersonalShow"))
        return_data = {"message": "Dummy data - proto fix করতে হবে"}  # temporary
        return jsonify(return_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/refresh', methods=['GET', 'POST'])
def refresh_tokens_endpoint():
    asyncio.run(initialize_tokens())
    return jsonify({'message':'Tokens refreshed for all regions.'}), 200

# Startup
def start_background_tasks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_tokens())
    loop.create_task(refresh_tokens_periodically())
    loop.run_forever()

if __name__ == '__main__':
    threading.Thread(target=start_background_tasks, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    threading.Thread(target=start_background_tasks, daemon=True).start()
