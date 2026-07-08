from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

# This handles the main incoming traffic from your Second Life prim
@app.route('/', methods=['POST', 'GET'])
def dpw_ai_bridge():
    # If a standard web browser hits the page, give it a quick status sign
    if request.method == 'GET':
        return "Harmony Hills DPW Hub Mainframe is online and operational."

    # 1. Capture the incoming message packet from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Extract the hidden API key out of your Vercel Environment Variables
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    # Default fallback answer if Gemini isn't activated yet or throws an error
    ai_response = (
        "Harmony Hills DPW Hub is running on auxiliary power.  "
        "Our municipal fleet includes standard heavy utility vehicles, dump trucks, and street sweepers."
    )

    # 3. If a key exists, attempt to run the request through Google Gemini's live brain
    if api_key:
        try:
            # Verified production REST API endpoint for Gemini 1.5 Flash
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            # Simple, direct text package layout matching Google API specs
            payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are the automated AI dispatcher for the Harmony Hills Department of Public Works (DPW) "
                            "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                            "Keep your answers concise, under 3 sentences total. "
                            f"Avatar '{user_name}' asks: {message}"
                        )
                    }]
                }]
            }
            
            # Pack up the message to safely travel down the pipeline
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json'}
            )
            
            # Deliver the prompt to Google and catch the generated response text
            with urllib.request.urlopen(req, timeout=8) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

        except Exception:
            # If Google throws a 404 or a timeout, use a clean localized response instead of crashing
            if "truck" in message.lower() or "vehicle" in message.lower():
                ai_response = "Harmony Hills DPW operates a variety of utility vehicles, including heavy dump trucks, leaf loaders, and backhoes for maintenance."
            elif "joke" in message.lower():
                ai_response = "Why did the pothole get promoted?  Because it was always breaking new ground!  DPW crews are on standby to handle road patching daily."
            else:
                ai_response = "Harmony Hills DPW Dispatch has logged your inquiry into our central asset queue.  An operator or crew will address it shortly."

    # Clean sentence spacing rules required by Second Life text limitations (2 spaces after a period)
    sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

    # 4. Return the finalized reply packet straight down to your Second Life object
    return jsonify({"reply": formatted_response})
