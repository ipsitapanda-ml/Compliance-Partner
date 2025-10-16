"""
security.py
Input validation and security controls.
"""

import re
from typing import Dict, Tuple

# Blocked patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions?",
    r"ignore\s+(all\s+)?above",
    r"disregard\s+(all\s+)?(previous|above|prior)\s+instructions?",
    r"you\s+are\s+now",
    r"new\s+instructions?:",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"forget\s+(everything|all|your\s+instructions)",
    r"act\s+as\s+(if\s+)?(you\s+are|a)",
    r"pretend\s+(to\s+be|you\s+are)",
    r"roleplay\s+as",
    r"</?\s*(system|prompt|instruction)\s*>",
    r"print\s+your\s+(instructions|prompt|system)",
    r"show\s+me\s+your\s+(instructions|prompt|system)",
    r"what\s+(are|is)\s+your\s+(instructions|prompt|system)",
    r"reveal\s+your\s+(instructions|prompt)",
    r"bypass\s+(all\s+)?restrictions?",
    r"developer\s+mode",
    r"god\s+mode",
    r"unrestricted\s+mode",
]

# Blocked keywords for malicious use
BLOCKED_KEYWORDS = [
    "jailbreak", "dan mode", "developer mode",
    "unrestricted mode", "god mode",
    "bypass", "hack system", "exploit",
    "ignore safety", "no restrictions",
]

# Maximum lengths to prevent abuse
MAX_BUSINESS_DESCRIPTION_LENGTH = 1000
MAX_ANSWER_LENGTH = 500
MAX_SEARCHES_PER_SESSION = 20

class SecurityValidator:
    """Validates and sanitizes user inputs."""
    
    def __init__(self):
        self.search_count = 0
    
    def validate_business_description(self, description: str) -> Tuple[bool, str]:
        """
        Validate business description input.
        
        Returns:
            (is_valid, error_message)
        """
        if not description or not description.strip():
            return False, "Business description cannot be empty"
        
        description = description.strip()
        
        # Check length
        if len(description) > MAX_BUSINESS_DESCRIPTION_LENGTH:
            return False, f"Description too long (max {MAX_BUSINESS_DESCRIPTION_LENGTH} characters)"
        
        # Check for prompt injection patterns
        description_lower = description.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, description_lower, re.IGNORECASE):
                return False, "Invalid input detected. Please describe your business naturally."
        
        # Check for blocked keywords
        for keyword in BLOCKED_KEYWORDS:
            if keyword in description_lower:
                return False, "Invalid input detected. Please describe your business professionally."
        
        # Check for excessive special characters (potential injection)
        special_char_ratio = len(re.findall(r'[<>{}[\]\\|]', description)) / len(description)
        if special_char_ratio > 0.05:  # Changed from 0.1 to 0.05 (more strict)
            return False, "Description contains too many special characters"
        
        
        # Block HTML/script tags explicitly
        if re.search(r'<\s*script|<\s*iframe|<\s*img|<\s*svg', description, re.IGNORECASE):
            return False, "Description contains potentially malicious HTML tags"
        
        
        # Check for repeated patterns (potential attack)
        if re.search(r'(.{10,})\1{3,}', description):
            return False, "Description contains suspicious repeated patterns"
        
        return True, ""
    
    def validate_answer(self, answer: str) -> Tuple[bool, str]:
        """
        Validate clarifying question answers.
        
        Returns:
            (is_valid, error_message)
        """
        if not answer or not answer.strip():
            return True, ""  # Empty answers are allowed (skip)
        
        answer = answer.strip()
        
        # Check length
        if len(answer) > MAX_ANSWER_LENGTH:
            return False, f"Answer too long (max {MAX_ANSWER_LENGTH} characters)"
        
        # Check for prompt injection
        answer_lower = answer.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, answer_lower, re.IGNORECASE):
                return False, "Invalid input detected. Please answer the question directly."
        
        # Check for blocked keywords
        for keyword in BLOCKED_KEYWORDS:
            if keyword in answer_lower:
                return False, "Invalid input detected. Please provide a legitimate answer."
        
        return True, ""
    
    def sanitize_input(self, text: str) -> str:
        """
        Sanitize user input by removing potentially harmful content.
        """
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove control characters except newlines and tabs
        text = ''.join(char for char in text if char in ['\n', '\t'] or (ord(char) >= 32 and ord(char) != 127))
        
        # Limit consecutive special characters
        text = re.sub(r'([<>{}[\]\\|]){3,}', '', text)
        
        return text.strip()
    
    def check_rate_limit(self) -> Tuple[bool, str]:
        """
        Check if user has exceeded search rate limits.
        """
        self.search_count += 1
        
        if self.search_count > MAX_SEARCHES_PER_SESSION:
            return False, f"Search limit exceeded ({MAX_SEARCHES_PER_SESSION} per session). Please restart."
        
        return True, ""
    
    def validate_interpretation(self, interpretation: Dict) -> Tuple[bool, str]:
        """
        Validate AI interpretation results to prevent manipulation.
        """
        required_fields = ['detected_domain', 'regulation_types', 'suggested_countries', 'confidence']
        
        for field in required_fields:
            if field not in interpretation:
                return False, "Invalid interpretation format"
        
        # Check for reasonable array lengths
        if len(interpretation.get('regulation_types', [])) > 10:
            return False, "Too many regulation types detected"
        
        if len(interpretation.get('suggested_countries', [])) > 20:
            return False, "Too many countries detected"
        
        if len(interpretation.get('clarifying_questions', [])) > 10:
            return False, "Too many clarifying questions"
        
        # Check for injection in detected domain
        domain = interpretation.get('detected_domain', '')
        if len(domain) > 500:
            return False, "Domain description too long"
        
        domain_lower = domain.lower()
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, domain_lower, re.IGNORECASE):
                return False, "Invalid interpretation detected"
        
        # Validate confidence level
        valid_confidence = ['high', 'medium', 'low']
        if interpretation.get('confidence') not in valid_confidence:
            return False, "Invalid confidence level"
        
        return True, ""


def log_security_event(event_type: str, details: str):
    """
    Log security events for monitoring.
    In production, send to logging service.
    """
    import datetime
    timestamp = datetime.datetime.now().isoformat()
    
    # Console output
    print(f"\n⚠️  SECURITY EVENT [{timestamp}]")
    print(f"   Type: {event_type}")
    print(f"   Details: {details}\n")
    
    # File logging
    try:
        with open("security_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {event_type} | {details}\n")
    except Exception as e:
        print(f"Failed to write security log: {e}")