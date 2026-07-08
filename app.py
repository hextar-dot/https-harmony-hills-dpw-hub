from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def dpw_ai_bridge():
    # 1. Capture the data package from Second Life
    data = request.get_json(force=True, silent=True) or {}
    user_name = data.get("speaker", "Avatar")
    message = data.get("message", "").strip()

    # 2. Advanced Dynamic AI Processing / Web Search Integration
    # (For production, you can replace this template with an open AI API package or custom scraper)
    ai_response = f"Database query complete. Regarding '{message}': Public Works logs suggest checking main county ordinances or speaking directly to an on-duty supervisor for custom specifications."

    # Rule compliance check: Ensure exactly two spaces after every period.
    # This automatically splits sentences and reformats them to your DPW layout rules.
    sentences = [s.strip() for s in ai_response.split('.') if s.strip()]
    formatted_response = ".  ".join(sentences) + "."

    # 3. Return the payload back down to Second Life
    return jsonify({"reply": formatted_response})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)