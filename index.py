from flask import Flask, request, jsonify
import os
import urllib.request
import json

app = Flask(__name__)

@app.route('/', methods=['POST', 'GET'])
def dpw_ai_bridge():
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

    # 3. If a key exists, process it through Google Gemini's live brain
    if api_key:
        try:
            # Using the fully supported production 2.0-flash model endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": (
                            "You are the automated AI dispatcher for the Harmony Hills Department of Public Works (DPW) "
                            "in Second Life. You are helpful, professional, and knowledgeable about municipal operations. "
                            "Keep your answers concise, under 3 sentences
