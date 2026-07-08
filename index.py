from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>', methods=['POST'])
def dpw_ai_bridge(path):
    # 1. Capture incoming details from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Extract your hidden Vercel key
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    try:
        # 3. Request layout for the live Google AI text pipeline
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": (
                    "You are the automated AI dispatcher for the Harmony Hills Department of Public Works (DPW) "
                    "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                    f"Answer this prompt directly as the dispatcher. Avatar '{user_name}' asks: {message}"
                )}]
            }],
            "generationConfig": {
                "maxOutputTokens": 100,
                "temperature": 0.7
            }
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
        # Emergency backup fallback so your terminal never breaks
        ai_response = (
            f"Harmony Hills DPW Hub is running on maintenance reserve. "
            f"We are looking into your request regarding '{message}' as quickly as possible."
        )

    # Clean sentence spacing for Second Life display rules
    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    return jsonify({"reply": formatted_response})
