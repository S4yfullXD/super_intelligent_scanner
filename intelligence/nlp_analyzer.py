import re
import json
from typing import Dict, List, Set, Tuple

class NLPAnalyzer:
    def __init__(self):
        self.secret_patterns = self.load_secret_patterns()
        self.tech_indicators = self.load_tech_indicators()
    
    def load_secret_patterns(self) -> Dict[str, str]:
        """Load patterns for detecting secrets"""
        return {
            'api_key': r'["\']?(api[_-]?key|access[_-]?key|secret[_-]?key)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_-]{20,50})["\']',
            'jwt_token': r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'private_key': r'-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            'password': r'["\']?(password|pwd|pass)["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            'database_url': r'["\']?(mysql|postgres|mongodb)://[^"\']+["\']?',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        }
    
    def load_tech_indicators(self) -> Dict[str, List[str]]:
        """Load technology detection patterns"""
        return {
            'react': ['react', 'react-dom', 'jsx', 'createElement'],
            'vue': ['vue', 'v-model', 'v-for', 'v-if'],
            'angular': ['angular', 'ng-', '@angular'],
            'nodejs': ['require(', 'module.exports', 'express', 'mongoose'],
            'python': ['def ', 'import ', 'from ', 'class ', 'print('],
            'php': ['<?php', '$_GET', '$_POST', '->'],
            'jquery': ['jQuery', '$('],
            'bootstrap': ['bootstrap', 'btn-', 'col-'],
        }
    
    def analyze_content(self, content: str, url: str) -> Dict:
        """Analyze content for secrets and intelligence"""
        if not content or len(content) < 50:
            return {}
        
        analysis = {
            'secrets_found': [],
            'technologies_detected': [],
            'endpoints_found': [],
            'keywords': [],
            'content_type': 'unknown'
        }
        
        # Detect secrets
        analysis['secrets_found'] = self.detect_secrets(content)
        
        # Detect technologies
        analysis['technologies_detected'] = self.detect_technologies(content)
        
        # Find endpoints
        analysis['endpoints_found'] = self.find_endpoints(content, url)
        
        # Extract keywords
        analysis['keywords'] = self.extract_keywords(content)
        
        # Detect content type
        analysis['content_type'] = self.detect_content_type(content)
        
        return analysis
    
    def detect_secrets(self, content: str) -> List[Dict]:
        """Detect secrets and sensitive information"""
        secrets = []
        
        for secret_type, pattern in self.secret_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    secret_value = match[1] if len(match) > 1 else match[0]
                else:
                    secret_value = match
                
                # Basic validation
                if self.validate_secret(secret_type, secret_value):
                    secrets.append({
                        'type': secret_type,
                        'value': secret_value[:50] + '...' if len(secret_value) > 50 else secret_value,
                        'risk_level': self.get_risk_level(secret_type)
                    })
        
        return secrets
    
    def validate_secret(self, secret_type: str, value: str) -> bool:
        """Validate if detected secret is likely real"""
        if secret_type == 'api_key' and len(value) < 10:
            return False
        if secret_type == 'email' and 'example.com' in value:
            return False
        if secret_type == 'ip_address' and value.startswith('192.168.'):
            return False
        return True
    
    def get_risk_level(self, secret_type: str) -> str:
        """Get risk level for secret type"""
        high_risk = ['api_key', 'aws_key', 'private_key', 'password']
        medium_risk = ['jwt_token', 'database_url']
        
        if secret_type in high_risk:
            return 'high'
        elif secret_type in medium_risk:
            return 'medium'
        else:
            return 'low'
    
    def detect_technologies(self, content: str) -> List[str]:
        """Detect technologies used"""
        detected_tech = []
        content_lower = content.lower()
        
        for tech, indicators in self.tech_indicators.items():
            for indicator in indicators:
                if indicator.lower() in content_lower:
                    detected_tech.append(tech)
                    break
        
        return list(set(detected_tech))
    
    def find_endpoints(self, content: str, base_url: str) -> List[str]:
        """Find API endpoints in content"""
        endpoints = set()
        
        endpoint_patterns = [
            r'["\'](/api/[^"\']+?)["\']',
            r'["\'](/v[1-9]/[^"\']+?)["\']',
            r'["\'](/graphql[^"\']*?)["\']',
            r'["\'](/rest/[^"\']+?)["\']',
            r'fetch\(["\']([^"\']+?)["\']\)',
            r'axios\.(?:get|post|put|delete)\(["\']([^"\']+?)["\']\)',
        ]
        
        for pattern in endpoint_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[0]
                else:
                    endpoint = match
                
                if endpoint and not endpoint.startswith(('http', '//')):
                    endpoints.add(endpoint)
        
        return list(endpoints)
    
    def extract_keywords(self, content: str) -> List[str]:
        """Extract meaningful keywords from content"""
        words = re.findall(r'\b[a-zA-Z]{4,15}\b', content.lower())
        
        # Filter common words
        common_words = {'this', 'that', 'with', 'from', 'have', 'were', 'their', 'there'}
        meaningful_words = [word for word in words if word not in common_words]
        
        # Get most frequent words
        from collections import Counter
        word_freq = Counter(meaningful_words)
        
        return [word for word, count in word_freq.most_common(10)]
    
    def detect_content_type(self, content: str) -> str:
        """Detect content type based on patterns"""
        if not content:
            return 'unknown'
        
        content_lower = content.lower()
        
        if any(pattern in content_lower for pattern in ['<html', '<!doctype', '<head']):
            return 'html'
        elif any(pattern in content_lower for pattern in ['function', 'const ', 'let ', 'var ']):
            return 'javascript'
        elif content.strip().startswith('{') or content.strip().startswith('['):
            return 'json'
        elif any(pattern in content_lower for pattern in ['import ', 'def ', 'class ']):
            return 'python'
        elif '<?php' in content_lower:
            return 'php'
        elif any(pattern in content_lower for pattern in ['{', '}', ':']):
            return 'css'
        else:
            return 'text'