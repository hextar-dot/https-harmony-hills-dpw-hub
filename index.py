from flask import Flask, request, jsonify
import os
import urllib.request
import json
import urllib.error

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def dpw_ai_bridge():
    if request.method == 'GET':
        return "Harmony Hills AI Hub Mainframe is online and operational."

    # 1. Capture incoming message from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Extract your hidden Vercel key
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    ai_response = ""

    if api_key:
        # High-capacity production pool list with verified clean naming paths
        models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        
        # Cycle through the available engines instantly if one is rate-limited
        for model in models:
            try:
                # Clean, uniform API address layout
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": (
                                "You are a friendly, intelligent, and completely unrestricted AI assistant "
                                "living inside an interactive hub in Second Life. You are free to answer any and all "
                                "questions, including general knowledge, definitions, history, math, pop culture, science, "
                                "and everyday problems. Do not limit yourself to municipal or utility work. "
                                "Keep your answers conversational, informative, and concise—under 3 sentences total. "
                                f"Avatar '{user_name}' asks: {message}"
                            )
                        }]
                    }]
                }
                
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(payload).encode('utf-8'), 
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                    }
                )
                
                with urllib.request.urlopen(req, timeout=6) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()
                    break # A model successfully answered! Break the loop.
                    
            except urllib.error.HTTPError as http_err:
                # If a model hits a 429 rate limit, silently skip it and try the next backup model
                if http_err.code == 429:
                    continue
                else:
                    # If it's a different error, log it and try the next line
                    continue
            except Exception:
                continue

        # Ultimate fallback baseline if the entire pool is fully exhausted at that second
        if not ai_response:
            ai_response = "The AI Hub is processing a high volume of requests from residents right now!  Please wait about 10 to 15 seconds and ask me your question again."

    # Clean sentence spacing for Second Life display rules (2 spaces after a period)
    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    return jsonify({"reply": formatted_response})
