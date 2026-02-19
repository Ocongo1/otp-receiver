# Import the necessary libraries.
import re
from flask import Flask, render_template, request, jsonify
from ai_otp_bot import AIOTPBot

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Create an instance of the AIOTPBot class.
ai_otp_bot = AIOTPBot()

# Define a function that will handle HTTP requests to /api/messages.
@app.route('/api/messages', methods=['GET'])
def api_messages():
    """API for live updates"""
    return jsonify({'messages': messages[-20:]})

# Define a function that will handle HTTP POST requests to /webhook and capture OTP codes.
@app.route('/webhook', methods=['POST'])
def sms_webhook():
    """Twilio SMS webhook"""
    from_number = request.form.get('From')
    body = request.form.get('Body').strip()
    
    # Extract OTP using AI-powered regex patterns.
    ai_result = ai_otp_bot.extract_otp(body)
    
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

# Define a function that will handle HTTP POST requests to /test for testing the OTP extraction functionality.
@app.route('/test', methods=['POST'])
def test_otp():
    """Test AI extraction"""
    sms = request.json.get('sms', '')
    result = ai_otp_bot.extract_otp(sms)
    return jsonify(result)

# Define a function that will handle HTTP requests to the main page.
@app.route('/', methods=['GET', 'POST'])
def index():
    """Main dashboard"""
    if request.method == 'POST':
        sms = request.form.get('sms')
        result = ai_otp_bot.extract_otp(sms)
        return render_template('index.html', messages=messages[-10:], otp=result['otp'], confidence=result['confidence'] * 100)

    return render_template('index.html', messages=messages[-10:])

# Render the main page template.
@app.route('/templates/index.html')
def index_html():
    """Main dashboard"""
    return render_template('index.html')

# Define AI-powered OTP extraction using regex patterns.
class AIOTPBot:
    def __init__(self):
        self.patterns = [
            r'\b\d{4,8}\b',
            r'(?:code|otp|pin|verify)[:\s-]*(\d{4,8})',
            r'(\d{4,8})[\s-]*(?:is|your|code|otp|pin)',
            r'your[\s-]*(?:code|otp|pin)[\s-]*(\d{4,8})',
            r'(\d{6})\s*(?:valid|expires)',
            r'confirmation[:\s]*(\d{4,8})',
            r'(\d{4})\s*(?:digits?|code)'
        ]
        self.compiled = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.patterns]
    
    def confidence_score(self, text: str, otp: str) -> float:
        score = 0.0
        text_lower = text.lower()
        
        keywords = ['code', 'otp', 'pin', 'verify', 'confirm', 'sent', 'message']
        score += min(sum(1 for k in keywords if k in text_lower) * 0.15, 0.4)
        
        pos = text_lower.find(otp.lower())
        if 5 < pos < len(text_lower) - 10:
            score += 0.25
        
        if len(otp) in [4, 6]:
            score += 0.2
        
        if re.search(r'\d{3,}valid|\d{3,}expires', text_lower):
            score += 0.15
        
        return min(score, 1.0)
    
    def extract_otp(self, text: str) -> Dict[str, any]:
        candidates = []
        text_lower = text.lower()
        
        for pattern in self.compiled:
            matches = pattern.findall(text)
            for match in matches:
                if isinstance(match, str) and match.isdigit() and 4 <= len(match) <= 8:
                    conf = self.confidence_score(text, match)
                    candidates.append({'otp': match, 'confidence': conf})
        
        if not candidates:
            return {'otp': None, 'confidence': 0.0, 'method': 'none'}
        
        best = max(candidates, key=lambda x: x['confidence']
        return {
            'otp': best['otp'],
            'confidence': round(best['confidence'], 2),
            'method': 'ai-regex'
        }
