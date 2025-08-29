"""
PII Detection Utility
Scans text for potential personally identifiable information
"""

import re
import string
from typing import List, Dict
from app.config import settings
import structlog

logger = structlog.get_logger()

def detect_pii(text: str) -> bool:
    """
    Detect potential PII in text
    
    Args:
        text: Text to scan for PII
        
    Returns:
        bool: True if PII is detected, False otherwise
    """
    if not settings.pii_detection_enabled:
        return False
    
    if not text or not isinstance(text, str):
        return False
    
    text = text.strip()
    if len(text) < 3:  # Too short to be meaningful PII
        return False
    
    # Check for common PII patterns
    for pattern in settings.pii_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            logger.warning("PII pattern detected", pattern=pattern, text_sample=text[:50])
            return True
    
    # Check for high entropy strings (likely random tokens, not PII)
    if is_high_entropy(text):
        return False
    
    # Check for specific PII indicators
    if contains_pii_indicators(text):
        logger.warning("PII indicators detected", text_sample=text[:50])
        return True
    
    return False

def contains_pii_indicators(text: str) -> bool:
    """
    Check for specific PII indicators in text
    """
    text_lower = text.lower()
    
    # Common PII keywords
    pii_keywords = [
        'ssn', 'social security', 'social security number',
        'phone', 'telephone', 'cell', 'mobile',
        'email', 'e-mail', 'mail',
        'name', 'first name', 'last name', 'full name',
        'address', 'street', 'city', 'state', 'zip',
        'birth', 'born', 'date of birth', 'dob',
        'driver license', 'drivers license', 'license number',
        'passport', 'passport number',
        'account number', 'account #', 'acct #',
        'credit card', 'debit card', 'card number'
    ]
    
    for keyword in pii_keywords:
        if keyword in text_lower:
            return True
    
    # Check for name-like patterns (two words that could be first/last name)
    words = text.split()
    if len(words) >= 2:
        for i in range(len(words) - 1):
            word_pair = f"{words[i]} {words[i+1]}"
            if (re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', word_pair) and
                len(words[i]) > 1 and len(words[i+1]) > 1):
                return True
    
    return False

def is_high_entropy(text: str) -> bool:
    """
    Check if text has high entropy (likely a random token, not PII)
    """
    if len(text) < 8:
        return False
    
    # Count character types
    has_upper = bool(re.search(r'[A-Z]', text))
    has_lower = bool(re.search(r'[a-z]', text))
    has_digit = bool(re.search(r'\d', text))
    has_special = bool(re.search(r'[^A-Za-z0-9]', text))
    
    # High entropy indicators
    char_types = sum([has_upper, has_lower, has_digit, has_special])
    
    # If text has 3+ character types and is long, likely high entropy
    if char_types >= 3 and len(text) >= 12:
        return True
    
    # Check for UUID-like patterns
    if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', text.lower()):
        return True
    
    # Check for base64-like patterns
    if re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', text):
        return True
    
    return False

def scan_csv_for_pii(csv_content: str) -> Dict[str, List[str]]:
    """
    Scan CSV content for PII and return detailed results
    
    Args:
        csv_content: CSV content as string
        
    Returns:
        Dict with 'pii_detected' and 'suspicious_rows' lists
    """
    results = {
        'pii_detected': [],
        'suspicious_rows': []
    }
    
    lines = csv_content.split('\n')
    
    for line_num, line in enumerate(lines, 1):
        if not line.strip():
            continue
            
        if detect_pii(line):
            results['pii_detected'].append(f"Line {line_num}: {line[:100]}...")
        
        # Check for suspicious patterns
        if is_suspicious_line(line):
            results['suspicious_rows'].append(f"Line {line_num}: {line[:100]}...")
    
    return results

def is_suspicious_line(line: str) -> bool:
    """
    Check if a CSV line has suspicious characteristics
    """
    # Check for unusually long lines
    if len(line) > 1000:
        return True
    
    # Check for too many commas (potential data injection)
    comma_count = line.count(',')
    if comma_count > 20:
        return True
    
    # Check for potential SQL injection patterns
    sql_patterns = [
        'union select', 'drop table', 'insert into', 'delete from',
        'update set', 'exec(', 'execute(', 'script>', '<script'
    ]
    
    line_lower = line.lower()
    for pattern in sql_patterns:
        if pattern in line_lower:
            return True
    
    return False
