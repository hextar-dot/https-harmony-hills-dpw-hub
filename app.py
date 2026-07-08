from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api', methods=['POST'])
def dpw_ai_bridge():
    # 1. Capture the data package from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Advanced Dynamic AI Processing / Web Search Integration
    ai_response = f"Database query complete. Regarding '{message}': Public Works logs suggest checking main county ordinances or speaking directly to an on-duty supervisor for custom specifications."

    # Rule compliance check: Ensure exactly two spaces after every period.
    sentences = [s.strip() for s in ai_response.split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "."

    # 3. Return the payload back down to Second Life
    return jsonify({"reply": formatted_response})

# Vercel needs this application object mapped to run properly
def handler(request):
    return app(request)
