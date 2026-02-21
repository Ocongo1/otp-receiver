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
