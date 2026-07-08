from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def dpw_ai_bridge():
    # 1. Capture the data package from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Grab the secret API Key from Vercel's environment settings
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        ai_response = "Error: Gemini API Key is missing in Vercel settings."
    else:
        try:
            # 3. Formulate the system persona and instructions for the AI
            system_instruction = (
                "You are the automated AI dispatcher for the Harmony Hills Department of Public Works (DPW) "
                "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                "Keep your responses concise, under 3 sentences, and localized to a municipal DPW environment."
            )

            # Updated secure endpoint path
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
            
            # Format the prompt payload
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_instruction}\n\nAvatar '{user_name}' asks: {message}"}]
                }]
            }
            
            # Pass the API key securely inside the HTTP header rather than the URL string
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={
                    'Content-Type': 'application/json',
                    'x-goog-api-key': api_key
                }
            )
            
            # Shoot the text over to Google and catch the AI response
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

        except Exception as e:
            ai_response = f"Database query timeout.  Please re-submit your inquiry to DPW Dispatch.  (Error: {str(e)})"

    # Rule compliance check: Ensure exactly two spaces after every period.
    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    # 4. Return the payload back down to Second Life
    return jsonify({"reply": formatted_response})
