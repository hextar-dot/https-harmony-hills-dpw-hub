from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def dpw_ai_bridge(path):
    # 1. Read what your Second Life prim is sending
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Grab the hidden Vercel key
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    # 3. Try to reach out to Gemini using the current 2026 stable engine
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": f"You are a DPW automated dispatcher. Keep it brief. Avatar asks: {message}"}]}]
        }
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

    except Exception as e:
        # If Gemini fails, DO NOT CRASH. Provide an interactive smart fallback!
        key_length = len(api_key)
        ai_response = (
            f"Harmony Hills DPW Hub is online.  "
            f"Our fleet uses standard municipal utility vehicles, dump trucks, and sweepers.  "
            f"(Diagnostic Mode: Gemini failed via error '{str(e)}'. Key character count is {key_length}.)"
        )

    # Clean sentence spacing for Second Life display rules
    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    return jsonify({"reply": formatted_response})
