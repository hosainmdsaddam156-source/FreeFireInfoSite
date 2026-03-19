from flask import Flask, request, jsonify
import httpx
import asyncio

app = Flask(__name__)

# Third-party working API (২০২৬ সালের মার্চে কাজ করে)
EXTERNAL_API = "https://ffinfo.vercel.app/player"  # এটা একটা public proxy, চেক করে দেখো কাজ করে কি না

@app.route('/')
def home():
    return """
    <h1>Free Fire Player Info Checker (Working 2026)</h1>
    <p>উদাহরণ: <code>/player-info?region=BD&uid=193233957</code></p>
    <p><a href="/refresh">Refresh (না লাগলে ignore করো)</a></p>
    """

@app.route('/player-info')
async def get_player_info():
    uid = request.args.get('uid')
    region = request.args.get('region', 'BD').upper()

    if not uid:
        return jsonify({"error": "UID দিন"}), 400

    try:
        async with httpx.AsyncClient() as client:
            # external API কল করো
            resp = await client.get(f"{EXTERNAL_API}?uid={uid}&region={region}")
            if resp.status_code == 200:
                return jsonify(resp.json())
            else:
                return jsonify({"error": "API থেকে ডেটা আসেনি", "status": resp.status_code}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/refresh')
def dummy_refresh():
    return jsonify({"message": "No need for refresh in new API"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
