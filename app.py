from flask import Flask, render_template, request, jsonify, session
import re
import requests
from ai_otp_bot import AIOTPBot
from datetime import datetime
import os
from twilio.rest import Client

app = Flask(__name__)
app.secret_key = 'your-super-secret-key-change-this'

# Initialize AI OTP Bot
otp_bot = AIOTPBot()

# Twilio credentials (for receiving SMS in real demo)
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')

# Store received messages
messages = []

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/webhook', methods=['POST'])
def sms_webhook():
    """Twilio SMS webhook - receives OTP SMS"""
    from_number = request.form.get('From')
    message_body = request.form.get('Body')
    
    # Store raw message
    msg_data = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'from_number': from_number,
        'body': message_body,
        'raw_extracted': None,
        'ai_extracted': None
    }
    
    # Traditional regex extraction
    regex_otp = re.findall(r'\b\d{4,8}\b', message_body)
    if regex_otp:
        msg_data['raw_extracted'] = regex_otp[0]
    
    # AI-powered extraction
    ai_otp = otp_bot.extract_otp(message_body)
    msg_data['ai_extracted'] = ai_otp
    
    messages.append(msg_data)
    if len(messages) > 50:  # Keep only last 50
        messages.pop(0)
    
    return 'OK', 200

@app.route('/api/messages')
def get_messages():
    return jsonify(messages[-20:])  # Last 20 messages

@app.route('/test', methods=['POST'])
def test_otp():
    """Test endpoint for demo"""
    test_sms = request.json.get('sms', '')
    return jsonify(otp_bot.extract_otp(test_sms))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)