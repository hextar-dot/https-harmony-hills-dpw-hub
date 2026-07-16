from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read incoming data safely
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}
            
        user_name = data.get("speaker", "Avatar")
        message = data.get("message", "").strip()

        # 2. Grab API settings
        api_key = os.environ.get("GEMINI_API_KEY", "")

        if not api_key:
            ai_response = "Error: Gemini API Key is missing in Vercel settings."
        elif not message:
            ai_response = "System Alert: No message content detected in the transmission."
        else:
            try:
                # 3. Use systemInstruction properly in the Gemini API payload
                system_instruction = (
                    "You are the automated AI dispatcher for the Harmony Hills Department of Public Works (DPW) "
                    "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                    "Keep your responses concise, under 3 sentences, and localized to a municipal DPW environment."
                )

                # Use v1beta or v1 endpoint
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                # Correct API structure: Pass instructions in 'systemInstruction' rather than appending to prompt
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Avatar '{user_name}' asks: {message}"}]
                    }],
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    }
                }
                
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(payload).encode('utf-8'), 
                    headers={'Content-Type': 'application/json'}
                )
                
                # Shoot the text over to Google with a defined timeout (essential for LSL and Vercel)
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    
                    # Safely dig out the response text
                    candidates = res_data.get('candidates', [])
                    if candidates and 'content' in candidates[0]:
                        parts = candidates[0]['content'].get('parts', [])
                        if parts:
                            ai_response = parts[0].get('text', '').strip()
                        else:
                            ai_response = "DPW Dispatch System idle. No content was generated."
                    else:
                        ai_response = "DPW Dispatch System idle. Processing stalled."

            except Exception as e:
                ai_response = f"Database query timeout. Please re-submit your inquiry to DPW Dispatch. (Error: {str(e)})"

        # Rule compliance: Format to exactly two spaces after every period.
        sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
        formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

        # 4. Return the payload to Second Life
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_payload = json.dumps({"reply": formatted_response})
        self.wfile.write(response_payload.encode('utf-8'))
        return
