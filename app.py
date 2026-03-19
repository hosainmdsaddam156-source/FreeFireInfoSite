from flask import Flask, request, jsonify
import httpx
import random

app = Flask(__name__)

# 10-12 টা alternative API (2026 মার্চে কাজ করার চান্স বেশি)
API_LIST = [
    "https://info-ob49.vercel.app/api/account/?uid={uid}&region={region}",  # PRINCE-lki repo
    "https://ff-api.vercel.app/api/player?uid={uid}&region={region}",
    "https://freefire-api-six.vercel.app/get_player_stats?server={region.lower()}&uid={uid}",
    "https://ffdvinh09-info.vercel.app/player-info?region={region}&uid={uid}",
    "https://free-ff-api-src-5plp.onrender.com/api/v1/account?region={region}&uid={uid}",
    "https://proapis.hlgamingofficial.com/main/games/freefire/account/api?sectionName=AllData&PlayerUid={uid}&region={region}",
    "https://developers.freefirecommunity.com/api/v1/info?region={region}&uid={uid}",
    "https://ff.garena.com/api/player/info?uid={uid}&region={region}",
    "https://ffinfo.vercel.app/player?uid={uid}&region={region}",
    "https://api.ff.garena.com/player/info?uid={uid}&region={region}",
    "https://freefire-api.vercel.app/v1/player?uid={uid}&region={region}",
    "https://ffinfo-api.onrender.com/player?uid={uid}&region={region}"
]

def fetch_player_info(uid, region):
    region = region.upper()
    for api_url_template in API_LIST:
        try:
            url = api_url_template.format(uid=uid, region=region)
            response = httpx.get(url, timeout=15)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and len(data) > 2:  # valid response check
                        return data
                except:
                    pass
            print(f"API failed: {url} - Status {response.status_code}")
        except Exception as e:
            print(f"API error: {str(e)}")
    
    # যদি সব fail করে তাহলে dummy data
    return {
        "uid": uid,
        "region": region,
        "nickname": f"Player_{uid[-4:]} (Dummy)",
        "level": 80,
        "rank": "Heroic",
        "clan": "Demo Clan",
        "message": "Real data আসেনি (সব API down বা changed)। Third-party API চেক করো।"
    }

@app.route('/')
def home():
    return """
    <h1 style="color:#ffcc00;">Free Fire Player Info Checker (2026 Working Demo)</h1>
    <p>এটা শুধুমাত্র পাবলিক প্লেয়ার ইনফো দেখার টুল। কোনো top-up বা hack নেই।</p>
    <p>উদাহরণ: <code>/player-info?region=BD&uid=193233957</code></p>
    <p>API auto চেষ্টা করে যেকোনো একটা চললে data আসবে।</p>
    """

@app.route('/player-info')
def get_player_info():
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD').upper()

    if not uid or not uid.isdigit():
        return jsonify({"error": "সঠিক UID দিন (শুধু নাম্বার)"}), 400

    data = fetch_player_info(uid, region)
    return jsonify(data)

@app.route('/refresh')
def dummy_refresh():
    return jsonify({"message": "Refresh not needed (third-party API)"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
