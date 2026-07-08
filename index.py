from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read incoming data from Second Life
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}
            
        user_name = data.get("speaker", "Avatar")
        message = data.get("message", "").strip()

        # 2. Grab the secret API Key from Vercel's environment
        api_key = os.environ.get("GEMINI_API_KEY", "")

        if not api_key:
            ai_response = "Error: Gemini API Key is missing in Vercel settings."
        else:
            try:
                # 3. Formulate the system persona and instructions for the AI
                system_instruction = (
                    ""You are the amazing automated AI dispatcher for the Harmony Hills Department of Public Works..."
                    "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                    "Keep your responses concise, under 3 sentences, and localized to a municipal DPW environment."
                )

                # Prepare the web request to Google's AI servers
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                # Format the prompt payload
                payload = {
                    "contents": [{
                        "parts": [{"text": f"{system_instruction}\n\nAvatar '{user_name}' asks: {message}"}]
                    }]
                }
                
                req = urllib.request.Request(
                    url, 
                    data=json.dumps(payload).encode('utf-8'), 
                    headers={'Content-Type': 'application/json'}
                )
                
                # Shoot the text over to Google and catch the AI response
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    ai_response = res_data['candidates'][0]['content']['parts'][0]['text'].strip()

            except Exception as e:
                ai_response = f"Database query timeout.  Please re-submit your inquiry to DPW Dispatch.  (Error: {str(e)})"

        # Rule compliance check: Ensure exactly two spaces after every period.
        # This automatically formats the raw AI text to your DPW guidelines.
        sentences = [s.strip() for s in ai_response.replace('\n', ' ').split('.') if s.strip()]
        formatted_response = ".  ".join(sentences) + "." if sentences else ai_response

        # 4. Package up the response and send it right back down to Second Life
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_payload = json.dumps({"reply": formatted_response})
        self.wfile.write(response_payload.encode('utf-8'))
        return
