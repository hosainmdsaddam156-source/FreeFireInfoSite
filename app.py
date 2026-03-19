from flask import Flask, request, jsonify
import httpx

app = Flask(__name__)

# কাজ করা API (2026 মার্চে টেস্ট করা)
EXTERNAL_API_BASE = "https://ff-api.vercel.app/api/player"

@app.route('/')
def home():
    return """
    <h1>Free Fire Player Info Checker (2026 Working)</h1>
    <p>Real data third-party API থেকে আসছে।</p>
    <p>উদাহরণ লিংক: <a href="/player-info?region=BD&uid=193233957">BD - UID 193233957</a></p>
    """

@app.route('/player-info')
def get_player_info():
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD').upper()

    if not uid or not uid.isdigit():
        return jsonify({"error": "সঠিক UID দিন"}), 400

    try:
        url = f"{EXTERNAL_API_BASE}?uid={uid}&region={region}"
        response = httpx.get(url, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({
                "error": "API থেকে সমস্যা",
                "status": response.status_code,
                "message": response.text[:400]
            }), response.status_code
    except Exception as e:
        return jsonify({"error": "কানেকশন সমস্যা", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
