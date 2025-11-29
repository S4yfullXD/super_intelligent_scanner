import re
from typing import List, Dict, Set
from collections import Counter

class PatternRecognizer:
    def __init__(self):
        self.content_patterns = {}
        self.structure_patterns = {}
        
    def analyze_response_patterns(self, responses: List[Dict]) -> Dict:
        """Analyze patterns across multiple responses"""
        analysis = {
            'common_headers': {},
            'content_patterns': {},
            'size_distribution': {},
            'type_categories': {}
        }
        
        if not responses:
            return analysis
        
        # Analyze headers
        analysis['common_headers'] = self.analyze_common_headers(responses)
        
        # Analyze content patterns
        analysis['content_patterns'] = self.analyze_content_patterns(responses)
        
        # Analyze size distribution
        analysis['size_distribution'] = self.analyze_size_distribution(responses)
        
        # Categorize by type
        analysis['type_categories'] = self.categorize_responses(responses)
        
        return analysis
    
    def analyze_common_headers(self, responses: List[Dict]) -> Dict:
        """Find common headers across responses"""
        header_counter = Counter()
        
        for response in responses:
            if 'headers' in response:
                for header_name in response['headers']:
                    header_counter[header_name.lower()] += 1
        
        return dict(header_counter.most_common(10))
    
    def analyze_content_patterns(self, responses: List[Dict]) -> Dict:
        """Analyze patterns in response content"""
        patterns = {
            'common_strings': [],
            'framework_indicators': [],
            'api_indicators': []
        }
        
        all_content = " ".join([r.get('content', '') for r in responses if r.get('content')])
        
        if not all_content:
            return patterns
        
        # Find common strings
        words = re.findall(r'[a-zA-Z]{5,}', all_content)
        word_freq = Counter(words)
        patterns['common_strings'] = [word for word, count in word_freq.most_common(10)]
        
        # Framework detection
        framework_keywords = {
            'react': ['react', 'createElement', 'component'],
            'vue': ['vue', 'v-model', 'v-for'],
            'angular': ['angular', 'ng-'],
            'jquery': ['jQuery', '$'],
            'express': ['express', 'middleware'],
            'django': ['django', 'csrf'],
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in all_content.lower() for keyword in keywords):
                patterns['framework_indicators'].append(framework)
        
        # API indicators
        api_patterns = [r'api[_-]?key', r'endpoint', r'base[_-]?url', r'fetch', r'axios']
        for pattern in api_patterns:
            if re.search(pattern, all_content, re.IGNORECASE):
                patterns['api_indicators'].append(pattern)
        
        return patterns
    
    def analyze_size_distribution(self, responses: List[Dict]) -> Dict:
        """Analyze distribution of response sizes"""
        sizes = [r.get('content_length', 0) for r in responses]
        
        if not sizes:
            return {}
        
        return {
            'min_size': min(sizes),
            'max_size': max(sizes),
            'avg_size': sum(sizes) / len(sizes),
            'total_size': sum(sizes)
        }
    
    def categorize_responses(self, responses: List[Dict]) -> Dict:
        """Categorize responses by type"""
        categories = {
            'javascript': 0,
            'html': 0,
            'json': 0,
            'css': 0,
            'other': 0
        }
        
        for response in responses:
            content_type = response.get('content_type', '').lower()
            content = response.get('content', '')
            
            if 'javascript' in content_type or self.looks_like_javascript(content):
                categories['javascript'] += 1
            elif 'html' in content_type or self.looks_like_html(content):
                categories['html'] += 1
            elif 'json' in content_type or self.looks_like_json(content):
                categories['json'] += 1
            elif 'css' in content_type:
                categories['css'] += 1
            else:
                categories['other'] += 1
        
        return categories
    
    def looks_like_javascript(self, content: str) -> bool:
        """Check if content looks like JavaScript"""
        js_patterns = [r'function\s*\w*\s*\(', r'const\s+\w+\s*=', r'console\.log']
        return any(re.search(pattern, content) for pattern in js_patterns)
    
    def looks_like_html(self, content: str) -> bool:
        """Check if content looks like HTML"""
        return any(tag in content.lower() for tag in ['<html', '<div', '<head', '<body'])
    
    def looks_like_json(self, content: str) -> bool:
        """Check if content looks like JSON"""
        content = content.strip()
        return (content.startswith('{') and content.endswith('}')) or \
               (content.startswith('[') and content.endswith(']'))