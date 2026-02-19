import re
from typing import Optional, Dict

class AIOTPBot:
    def __init__(self):
        self.otp_patterns = [
            r'\b\d{4,8}\b',
            r'(?:code|otp|pin|verify)[:\s]*(\d{4,8})',
            r'(\d{4,8})[\s\-]*(?:is|your|code|otp)',
            r'your[\s\-]*(?:code|otp|pin)[\s\-]*(\d{4,8})',
            r'(\d{6})\s*valid', r'(\d{4})\s*confirm'
        ]
        self.compiled_patterns = [re.compile(p, re.IGNORECASE | re.DOTALL) for p in self.otp_patterns]
    
    def contextual_score(self, text: str, otp: str) -> float:
        """AI-like confidence scoring"""
        score = 0.0
        text_lower = text.lower()
        
        # OTP keywords boost
        keywords = ['code', 'otp', 'pin', 'verify', 'confirm', 'sent', 'message']
        score += sum(1 for kw in keywords if kw in text_lower) * 0.15
        
        # Position (middle = better)
        pos = text_lower.find(otp.lower())
        if 10 < pos < len(text) - 20:
            score += 0.25
        
        # Length preference
        if len(otp) in [4, 6]:
            score += 0.2
        
        # Repeated digits penalty
        if len(set(otp)) < 2:
            score -= 0.3
        
        return min(max(score, 0.0), 1.0)
    
    def extract_otp(self, sms_text: str) -> Dict[str, str]:
        """Advanced regex + AI scoring"""
        candidates = []
        
        for pattern in self.compiled_patterns:
            matches = pattern.findall(sms_text)
            for match in matches:
                if 4 <= len(match) <= 8 and match.isdigit():
                    confidence = self.contextual_score(sms_text, match)
                    candidates.append({
                        'otp': match,
                        'confidence': confidence,
                        'method': 'pattern'
                    })
        
        if not candidates:
            return {'otp': None, 'confidence': 0.0, 'method': 'none'}
        
        # Best candidate
        best = max(candidates, key=lambda x: x['confidence'])
        return {
            'otp': best['otp'],
            'confidence': round(best['confidence'], 2),
            'method': best['method']
        }