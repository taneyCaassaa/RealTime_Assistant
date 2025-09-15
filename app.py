from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)

# Configure CORS - Allow all origins for development
# In production, replace "*" with your actual frontend domain
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

# Get OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY environment variable not set")

@app.route('/api/token', methods=['GET', 'OPTIONS'])
def get_ephemeral_token():
    """
    Generate an ephemeral token for client-side WebRTC connection
    """
    if request.method == 'OPTIONS':
        return '', 200
        
    if not OPENAI_API_KEY:
        return jsonify({"error": "OPENAI_API_KEY not configured"}), 500
    
    session_config = {
        "session": {
            "type": "realtime",
            "model": "gpt-realtime",
            "audio": {
                "output": {
                    "voice": "marin"  # Options: marin, lara, echo, onyx
                }
            },
            "instructions": "You are a helpful voice assistant. Be conversational and friendly."
        }
    }
    
    try:
        print(f"Making request to OpenAI with session config: {json.dumps(session_config, indent=2)}")
        
        response = requests.post(
            "https://api.openai.com/v1/realtime/client_secrets",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            },
            json=session_config,
            timeout=30
        )
        
        print(f"OpenAI Response Status: {response.status_code}")
        print(f"OpenAI Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Token generated successfully. Expires at: {data.get('expires_at', 'unknown')}")
            return jsonify(data)
        else:
            error_text = response.text
            print(f"OpenAI API Error: {response.status_code} - {error_text}")
            return jsonify({
                "error": "Failed to generate token",
                "details": error_text,
                "status_code": response.status_code
            }), 500
            
    except requests.exceptions.Timeout:
        print("Request to OpenAI timed out")
        return jsonify({"error": "Request timeout"}), 500
    except requests.exceptions.ConnectionError:
        print("Connection error to OpenAI API")
        return jsonify({"error": "Connection error"}), 500
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return jsonify({"error": f"Request failed: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "openai-realtime-backend",
        "version": "1.0.0",
        "api_key_configured": bool(OPENAI_API_KEY)
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        "message": "Backend is working!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/api/health",
            "token": "/api/token",
            "test": "/api/test"
        }
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "service": "OpenAI Realtime API Backend",
        "status": "running",
        "endpoints": {
            "health": "/api/health - Health check",
            "token": "/api/token - Get ephemeral token",
            "test": "/api/test - Test endpoint"
        },
        "cors": "Enabled for all origins",
        "deployment": "Ready for Render"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/api/health", "/api/token", "/api/test"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "message": "Something went wrong on the server"
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting server on port {port}")
    print(f"Debug mode: {debug_mode}")
    print(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)





# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# import json
# import os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# load_dotenv(".env")
# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # You need to set your OpenAI API key as an environment variable
# # export OPENAI_API_KEY=your_api_key_here
# OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# if not OPENAI_API_KEY:
#     raise ValueError("Please set the OPENAI_API_KEY environment variable")

# @app.route('/token', methods=['GET'])
# def get_ephemeral_token():
#     """
#     Generate an ephemeral token for client-side WebRTC connection
#     """
#     session_config = {
#         "session": {
#             "type": "realtime",
#             "model": "gpt-realtime",
#             "audio": {
#                 "output": {
#                     "voice": "marin"  # Options: marin, lara, echo, onyx
#                 }
#             },
#             "instructions": "You are a helpful voice assistant. Be conversational and friendly."
#         }
#     }
    
#     try:
#         response = requests.post(
#             "https://api.openai.com/v1/realtime/client_secrets",
#             headers={
#                 "Authorization": f"Bearer {OPENAI_API_KEY}",
#                 "Content-Type": "application/json"
#             },
#             json=session_config,
#             timeout=30
#         )
        
#         if response.status_code == 200:
#             data = response.json()
#             return jsonify(data)
#         else:
#             print(f"OpenAI API Error: {response.status_code} - {response.text}")
#             return jsonify({"error": "Failed to generate token"}), 500
            
#     except requests.exceptions.RequestException as e:
#         print(f"Request error: {e}")
#         return jsonify({"error": "Failed to generate token"}), 500

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# @app.route('/', methods=['GET'])
# def index():
#     """Serve the main HTML page"""
#     return '''
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>OpenAI Realtime Voice Assistant</title>
#         <style>
#             body {
#                 font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#                 max-width: 800px;
#                 margin: 0 auto;
#                 padding: 20px;
#                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#                 min-height: 100vh;
#                 display: flex;
#                 flex-direction: column;
#                 justify-content: center;
#                 align-items: center;
#             }
            
#             .container {
#                 background: white;
#                 padding: 40px;
#                 border-radius: 20px;
#                 box-shadow: 0 20px 40px rgba(0,0,0,0.1);
#                 text-align: center;
#                 width: 100%;
#                 max-width: 600px;
#             }
            
#             h1 {
#                 color: #333;
#                 margin-bottom: 30px;
#                 font-size: 2.5em;
#                 background: linear-gradient(45deg, #667eea, #764ba2);
#                 -webkit-background-clip: text;
#                 -webkit-text-fill-color: transparent;
#                 background-clip: text;
#             }
            
#             .status {
#                 font-size: 18px;
#                 margin: 20px 0;
#                 padding: 15px;
#                 border-radius: 10px;
#                 font-weight: 500;
#             }
            
#             .status.disconnected {
#                 background-color: #fee2e2;
#                 color: #dc2626;
#                 border: 1px solid #fecaca;
#             }
            
#             .status.connecting {
#                 background-color: #fef3c7;
#                 color: #d97706;
#                 border: 1px solid #fed7aa;
#             }
            
#             .status.connected {
#                 background-color: #dcfce7;
#                 color: #16a34a;
#                 border: 1px solid #bbf7d0;
#             }
            
#             .status.listening {
#                 background-color: #dbeafe;
#                 color: #2563eb;
#                 border: 1px solid #bfdbfe;
#                 animation: pulse 2s infinite;
#             }
            
#             @keyframes pulse {
#                 0%, 100% { opacity: 1; }
#                 50% { opacity: 0.7; }
#             }
            
#             button {
#                 background: linear-gradient(45deg, #667eea, #764ba2);
#                 color: white;
#                 border: none;
#                 padding: 15px 30px;
#                 font-size: 16px;
#                 border-radius: 50px;
#                 cursor: pointer;
#                 margin: 10px;
#                 transition: all 0.3s ease;
#                 font-weight: 600;
#                 min-width: 120px;
#             }
            
#             button:hover:not(:disabled) {
#                 transform: translateY(-2px);
#                 box-shadow: 0 10px 20px rgba(0,0,0,0.2);
#             }
            
#             button:disabled {
#                 background: #ccc;
#                 cursor: not-allowed;
#                 transform: none;
#                 box-shadow: none;
#             }
            
#             .controls {
#                 margin: 30px 0;
#             }
            
#             .log {
#                 background-color: #f8f9fa;
#                 border: 1px solid #e9ecef;
#                 border-radius: 10px;
#                 padding: 20px;
#                 margin-top: 20px;
#                 height: 200px;
#                 overflow-y: auto;
#                 text-align: left;
#                 font-family: monospace;
#                 font-size: 14px;
#             }
            
#             .log-entry {
#                 margin: 5px 0;
#                 padding: 5px;
#                 border-radius: 5px;
#             }
            
#             .log-entry.info {
#                 background-color: #e3f2fd;
#                 color: #1976d2;
#             }
            
#             .log-entry.error {
#                 background-color: #ffebee;
#                 color: #c62828;
#             }
            
#             .log-entry.success {
#                 background-color: #e8f5e8;
#                 color: #2e7d32;
#             }
            
#             .microphone-icon {
#                 font-size: 2em;
#                 margin: 20px 0;
#             }
            
#             .speaking {
#                 animation: speak 0.5s infinite alternate;
#             }
            
#             @keyframes speak {
#                 0% { transform: scale(1); }
#                 100% { transform: scale(1.1); }
#             }
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <h1>🎙️ Voice Assistant</h1>
#             <div class="microphone-icon" id="microphoneIcon">🎤</div>
#             <div class="status disconnected" id="status">Disconnected</div>
#             <div class="controls">
#                 <button id="connectBtn">Connect</button>
#                 <button id="disconnectBtn" disabled>Disconnect</button>
#             </div>
#             <div class="log" id="log">
#                 <div class="log-entry info">Ready to connect...</div>
#             </div>
#         </div>
        
#         <script src="/static/app.js"></script>
#     </body>
#     </html>
#     '''

# if __name__ == '__main__':
#     print("Starting OpenAI Realtime Voice Assistant Server...")
#     print("Make sure to set OPENAI_API_KEY environment variable")
#     print("Server will be available at: http://localhost:5000")
#     app.run(debug=True, host='0.0.0.0', port=5000)