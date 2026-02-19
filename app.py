from flask import Flask, render_template, request, jsonify
from ai_otp_bot import AIOTPBot
from datetime import datetime
import os
import re

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'otp-demo-railway-2026'

# Global storage
messages = []
otp_bot = AIOTPBot()

@app.route('/')
@app.route('/index.html')
def index():
    """Main dashboard"""
    return render_template('index.html', messages=messages[-10:])

@app.route('/api/messages')
def api_messages():
    """API for live updates"""
    return jsonify({'messages': messages[-20:]})

@app.route('/webhook', methods=['POST'])
def sms_webhook():
    """Twilio SMS webhook"""
    from_number = request.form.get('From', 'unknown')
    body = request.form.get('Body', '').strip()
    
    # Extract OTP
    ai_result = otp_bot.extract_otp(body)
    
    msg = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'from_number': from_number,
        'body': body,
        'ai_extracted': ai_result
    }
    
    messages.append(msg)
    if len(messages) > 100:
        messages.pop(0)
    
    return 'OK', 200

@app.route('/test', methods=['POST'])
def test_otp():
    """Test AI extraction"""
    sms = request.json.get('sms', '')
    result = otp_bot.extract_otp(sms)
    return jsonify(result)

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', messages=messages[-10:]), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)