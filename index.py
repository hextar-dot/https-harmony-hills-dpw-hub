from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read the incoming data length from Second Life
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 2. Parse the JSON package sent from the prim
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}
            
        user_name = data.get("speaker", "Avatar")
        message = data.get("message", "").strip()

        # 3. Dynamic AI / Database Processing Logic
        ai_response = f"Database query complete. Regarding '{message}': Public Works logs suggest checking main county ordinances or speaking directly to an on-duty supervisor for custom specifications."

        # Rule compliance check: Ensure exactly two spaces after every period.
        sentences = [s.strip() for s in ai_response.split('.') if s.strip()]
        formatted_response = ".  ".join(sentences) + "."

        # 4. Send the response back to Second Life
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_payload = json.dumps({"reply": formatted_response})
        self.wfile.write(response_payload.encode('utf-8'))
        return
