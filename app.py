from flask import Flask, request, jsonify
import httpx

app = Flask(__name__)

# Working third-party FF info API (2026-এ চেক করা, OB50+ compatible)
# উদাহরণ: https://info-ob49.vercel.app/api/account/?uid=193233957&region=BD
EXTERNAL_API_BASE = "https://info-ob49.vercel.app/api/account/"

@app.route('/')
def home():
    return """
    <h1>Free Fire Player Info Checker (Updated 2026)</h1>
    <p>Real data আসছে third-party proxy থেকে।</p>
    <p>উদাহরণ: <a href="/player-info?region=BD&uid=193233957">/player-info?region=BD&uid=193233957</a></p>
    """

@app.route('/player-info')
def get_player_info():
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD').upper()

    if not uid:
        return jsonify({"error": "UID দিন"}), 400

    try:
        url = f"{EXTERNAL_API_BASE}?uid={uid}&region={region}"
        response = httpx.get(url, timeout=15)
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                "error": "External API error",
                "status": response.status_code,
                "message": response.text[:300]
            }), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/refresh')
def dummy_refresh():
    return jsonify({"message": "Refresh not needed in proxy mode"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
