import re
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import numpy as np
from typing import Optional, List

class AIOTPBot:
    def __init__(self):
        # Load spaCy for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("spaCy model not found. Install: python -m spacy download en_core_web_sm")
            self.nlp = None
            
        # Load regex patterns for OTP
        self.otp_patterns = [
            r'\b\d{4,8}\b',  # 4-8 digits
            r'code[:\s]*(\d{4,8})',
            r'otp[:\s]*(\d{4,8})',
            r'pin[:\s]*(\d{4,8})',
            r'(\d{4,8})[\s\-]*is your',
            r'your[\s\-]*(\d{4,8})[\s\-]*code'
        ]
        
        # Initialize regex compiler
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.otp_patterns]
    
    def extract_with_regex(self, text: str) -> Optional[str]:
        """Traditional regex OTP extraction"""
        text_lower = text.lower()
        for pattern in self.compiled_patterns:
            matches = pattern.findall(text_lower)
            if matches:
                return matches[0]
        return None
    
    def extract_with_nlp(self, text: str) -> Optional[str]:
        """NLP-based extraction using spaCy"""
        if not self.nlp:
            return None
            
        doc = self.nlp(text)
        numbers = []
        
        for ent in doc.ents:
            if ent.label_ in ['CARDINAL', 'MONEY', 'QUANTITY', 'ORDINAL']:
                numbers.extend(re.findall(r'\b\d{4,8}\b', ent.text))
        
        # Extract numbers from tokens
        for token in doc:
            if token.like_num and 4 <= len(token.text) <= 8:
                numbers.append(token.text)
        
        return numbers[0] if numbers else None
    
    def contextual_confidence(self, text: str, otp_candidate: str) -> float:
        """Calculate confidence score based on context"""
        context_score = 0.0
        
        # Keywords that suggest OTP
        otp_keywords = ['code', 'otp', 'verify', 'confirm', 'security', 'login', 
                       'account', 'password', 'pin', 'sent', 'message']
        
        text_lower = text.lower()
        keyword_hits = sum(1 for kw in otp_keywords if kw in text_lower)
        context_score += min(keyword_hits * 0.1, 0.5)
        
        # Position scoring (middle of message = higher confidence)
        otp_pos = text_lower.find(otp_candidate.lower())
        if otp_pos > 0 and otp_pos < len(text_lower) - 10:
            context_score += 0.3
        
        # Length scoring (6-digit most common)
        if len(otp_candidate) == 6:
            context_score += 0.2
        
        return min(context_score, 1.0)
    
    def extract_otp(self, sms_text: str) -> dict:
        """Main AI-powered OTP extraction"""
        candidates = []
        
        # Regex candidates
        regex_otp = self.extract_with_regex(sms_text)
        if regex_otp:
            confidence = self.contextual_confidence(sms_text, regex_otp)
            candidates.append({
                'otp': regex_otp,
                'method': 'regex',
                'confidence': confidence
            })
        
        # NLP candidates
        nlp_otp = self.extract_with_nlp(sms_text)
        if nlp_otp and nlp_otp != regex_otp:
            confidence = self.contextual_confidence(sms_text, nlp_otp)
            candidates.append({
                'otp': nlp_otp,
                'method': 'nlp',
                'confidence': confidence
            })
        
        if not candidates:
            return {'otp': None, 'confidence': 0.0, 'method': 'none'}
        
        # Return highest confidence candidate
        best = max(candidates, key=lambda x: x['confidence'])
        return {
            'otp': best['otp'],
            'confidence': round(best['confidence'], 2),
            'method': best['method'],
            'all_candidates': candidates
        }