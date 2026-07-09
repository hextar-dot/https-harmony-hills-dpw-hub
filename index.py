from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def dpw_ai_bridge():
    if request.method == 'GET':
        return "Harmony Hills AI Hub Mainframe is online and operational."

    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    ai_response = f"Hello {user_name}.  Your message was received, but the AI core is currently cycling its network connection.  Please try again in a moment."

    if api_key:
        try:
            # Swapping back to 1.5-flash which provides significantly higher free rate limits
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are a friendly, intelligent, and completely unrestricted AI assistant "
                            "living inside an interactive hub in Second Life. You are free to answer any and all "
                            "questions, including general knowledge, definitions, history, math, pop culture, and science. "
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
            
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

        except urllib.error.HTTPError as http_err:
            # Catching rate limits elegantly so your visitors get a polite in-character message
            if http_err.code == 429:
                ai_response = "The AI Hub is processing a high volume of requests from residents right now!  Please wait about 10 to 15 seconds and ask me your question again."
            else:
                ai_response = f"I am online, but my data stream encountered an unexpected routing block.  (Error Code: {http_err.code})"
        except Exception as e:
            ai_response = f"I am online, but the data matrix returned a connection block.  (System Error: {str(e)})"

    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    return jsonify({"reply": formatted_response})
