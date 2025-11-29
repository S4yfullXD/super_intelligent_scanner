#!/usr/bin/env python3
"""
Enhanced Quantum Fuzzer dengan Color Integration & Natural Paths Generation
Advanced path fuzzing dengan AI-inspired patterns untuk comprehensive scanning
"""

import random
import hashlib
import base64
from urllib.parse import quote, unquote, urlparse
from typing import List, Set, Dict, Tuple
import re
import itertools
import json

# Import color system yang sudah ada
from utils.colors import term, success, error, warning, info, debug

class QuantumFuzzer:
    def __init__(self):
        self.encoding_methods = ['url', 'base64', 'hex', 'unicode', 'double_url', 'html_entity']
        self.special_chars = ['../', './', '.../', '/./', '//', '/../', '\\..\\', '\\\\.\\\\']
        
        # Natural language paths database
        self.natural_paths = self._load_natural_paths()
        
        # Common patterns dari real-world applications
        self.common_patterns = self._load_common_patterns()
        
        print(debug("🎯 Quantum Fuzzer initialized with natural paths generation"))
    
    def _load_natural_paths(self) -> Dict[str, List[str]]:
        """Load natural language paths untuk realistic path generation"""
        return {
            'admin': [
                '/admin', '/administrator', '/adminpanel', '/admin/login', 
                '/admin/dashboard', '/admin/config', '/admin/settings',
                '/wp-admin', '/administrator/login', '/admincp'
            ],
            'api': [
                '/api', '/api/v1', '/api/v2', '/api/v3', '/graphql', '/rest',
                '/json', '/api/docs', '/api/swagger', '/api/redoc'
            ],
            'auth': [
                '/login', '/signin', '/logout', '/signout', '/register',
                '/signup', '/auth', '/oauth', '/sso', '/password/reset'
            ],
            'files': [
                '/uploads', '/files', '/documents', '/images', '/assets',
                '/static', '/media', '/downloads', '/backups', '/tmp'
            ],
            'config': [
                '/config', '/configuration', '/settings', '/setup',
                '/install', '/initialize', '/env', '/.env', '/config.json'
            ],
            'database': [
                '/db', '/database', '/sql', '/mysql', '/postgres',
                '/mongodb', '/redis', '/phpmyadmin', '/adminer'
            ],
            'development': [
                '/dev', '/development', '/staging', '/test', '/debug',
                '/console', '/shell', '/terminal', '/api/debug'
            ],
            'logs': [
                '/logs', '/log', '/var/log', '/tmp/logs', '/debug/log',
                '/application/logs', '/system/logs'
            ]
        }
    
    def _load_common_patterns(self) -> Dict[str, List[str]]:
        """Load common patterns dari real-world applications"""
        return {
            'wordpress': [
                '/wp-content', '/wp-includes', '/wp-json', '/wp-admin',
                '/xmlrpc.php', '/wp-config.php', '/wp-login.php'
            ],
            'laravel': [
                '/storage', '/bootstrap', '/app', '/resources',
                '/vendor', '/config/app.php', '/.env'
            ],
            'django': [
                '/static', '/media', '/admin', '/api',
                '/accounts', '/docs', '/redoc'
            ],
            'react': [
                '/static/js', '/static/css', '/manifest.json',
                '/service-worker.js', '/precache-manifest'
            ],
            'api_patterns': [
                '/users', '/products', '/orders', '/customers',
                '/auth/token', '/user/profile', '/api/health'
            ]
        }
    
    def generate_quantum_paths(self, base_paths: List[str], max_paths: int = 100) -> List[str]:
        """Generate quantum-inspired path variations dengan enhanced coverage"""
        quantum_paths = set()
        
        print(info(f"🎲 Generating quantum paths from {len(base_paths)} base paths..."))
        
        for i, base_path in enumerate(base_paths[:30]):  # Limit untuk performance
            if i % 10 == 0:
                print(debug(f"   Processing base path {i+1}/{min(30, len(base_paths))}"))
                
            # Generate multiple quantum states untuk setiap path
            quantum_states = self.generate_quantum_states(base_path)
            quantum_paths.update(quantum_states)
            
            # Add natural language variations
            natural_variations = self.generate_natural_variations(base_path)
            quantum_paths.update(natural_variations)
            
            # Jika sudah cukup paths, break early
            if len(quantum_paths) >= max_paths:
                print(warning(f"   Reached max paths limit ({max_paths})"))
                break
        
        final_paths = list(quantum_paths)[:max_paths]
        print(success(f"✅ Generated {len(final_paths)} quantum paths"))
        
        return final_paths
    
    def generate_quantum_states(self, path: str) -> List[str]:
        """Generate multiple quantum state variations untuk sebuah path"""
        states = set()
        
        # Original state
        states.add(path)
        
        # Encoding superposition
        states.update(self.generate_all_encodings(path))
        
        # Path traversal superposition
        states.update(self.generate_traversal_variations(path))
        
        # Case variation superposition
        states.update(self.generate_case_variations(path))
        
        # Parameter superposition (untuk API endpoints)
        if self.looks_like_api(path):
            states.update(self.generate_parameter_variations(path))
        
        # Extension superposition
        states.update(self.generate_extension_variations(path))
        
        # Combined variations (quantum entanglement simulation)
        states.update(self.generate_combined_variations(path))
        
        return list(states)
    
    def generate_natural_variations(self, path: str) -> List[str]:
        """Generate natural language path variations"""
        variations = set()
        
        # Extract keywords dari path
        keywords = self.extract_keywords_from_string(path)
        
        for keyword in keywords[:5]:  # Limit keywords
            if keyword in self.natural_paths:
                variations.update(self.natural_paths[keyword][:3])  # Limit variations
        
        # Add common patterns berdasarkan path characteristics
        if 'api' in path.lower():
            variations.update(self.common_patterns['api_patterns'][:5])
        if 'admin' in path.lower():
            variations.update(self.common_patterns['wordpress'][:3])
        
        return list(variations)
    
    def generate_all_encodings(self, path: str) -> List[str]:
        """Generate semua encoding variations"""
        encoded_paths = []
        
        for encoding in self.encoding_methods:
            try:
                encoded = self.apply_encoding(path, encoding)
                if encoded and encoded != path:
                    encoded_paths.append(encoded)
                    
                    # Double encoding untuk beberapa method
                    if encoding not in ['double_url']:
                        double_encoded = self.apply_encoding(encoded, encoding)
                        if double_encoded:
                            encoded_paths.append(double_encoded)
            except Exception as e:
                debug(f"Encoding error {encoding}: {e}")
                continue
                
        return encoded_paths
    
    def apply_encoding(self, path: str, encoding: str) -> str:
        """Apply different encoding methods"""
        try:
            if encoding == 'url':
                return quote(path)
            elif encoding == 'base64':
                return base64.b64encode(path.encode()).decode()
            elif encoding == 'hex':
                return path.encode().hex()
            elif encoding == 'unicode':
                return ''.join([f'%u{ord(c):04x}' for c in path])
            elif encoding == 'double_url':
                return quote(quote(path))
            elif encoding == 'html_entity':
                return ''.join([f'&#{ord(c)};' for c in path])
            else:
                return path
        except Exception as e:
            debug(f"Encoding failed for {encoding}: {e}")
            return path
    
    def generate_traversal_variations(self, path: str) -> List[str]:
        """Generate path traversal variations"""
        variations = set()
        
        for traversal_char in self.special_chars:
            # Simple append
            variations.add(path + traversal_char)
            variations.add(traversal_char + path)
            
            # Insert at different positions
            if '/' in path:
                parts = path.split('/')
                for i in range(1, len(parts)):
                    new_parts = parts.copy()
                    new_parts.insert(i, traversal_char.strip('/'))
                    variations.add('/'.join(new_parts))
        
        return list(variations)
    
    def generate_case_variations(self, path: str) -> List[str]:
        """Generate case variations"""
        variations = set()
        
        variations.add(path.upper())
        variations.add(path.lower())
        variations.add(path.title())
        variations.add(self.random_case(path))
        
        # Mixed case (every other character)
        mixed = ''.join(
            char.upper() if i % 2 == 0 else char.lower() 
            for i, char in enumerate(path)
        )
        variations.add(mixed)
        
        return list(variations)
    
    def random_case(self, text: str) -> str:
        """Apply random case variation"""
        return ''.join(
            char.upper() if random.random() > 0.5 else char.lower() 
            for char in text
        )
    
    def looks_like_api(self, path: str) -> bool:
        """Check jika path terlihat seperti API endpoint"""
        api_indicators = ['/api/', '/v1/', '/v2/', '/v3/', '/rest/', '/graphql', '/json/']
        return any(indicator in path.lower() for indicator in api_indicators)
    
    def generate_parameter_variations(self, path: str) -> List[str]:
        """Generate parameter variations untuk API paths"""
        variations = set()
        
        parameters = ['id', 'user', 'page', 'limit', 'offset', 'sort', 'filter', 'token']
        values = ['123', 'test', 'admin', '1', 'true', 'false', 'null', 'undefined']
        
        # Add parameters ke path
        base_path = path.split('?')[0]  # Remove existing parameters
        
        for param in parameters[:4]:
            for value in values[:3]:
                # Different parameter formats
                variations.add(f"{base_path}?{param}={value}")
                variations.add(f"{base_path}?{param}[]={value}")
                variations.add(f"{base_path}?{param}={value}&test=1")
                variations.add(f"{base_path}?{param}={value}&{param}={value}")  # Duplicate
        
        # Multiple parameters combinations
        param_combinations = list(itertools.combinations(parameters[:3], 2))[:3]
        for param1, param2 in param_combinations:
            variations.add(f"{base_path}?{param1}=test&{param2}=123")
        
        return list(variations)
    
    def generate_extension_variations(self, path: str) -> List[str]:
        """Generate file extension variations"""
        variations = set()
        
        extensions = ['.json', '.js', '.html', '.xml', '.txt', '.bak', '.old', '.sql']
        no_extension_path = path.split('.')[0]  # Remove existing extension
        
        for ext in extensions:
            variations.add(f"{no_extension_path}{ext}")
            variations.add(f"{path}{ext}")  # Double extension
        
        return list(variations)
    
    def generate_combined_variations(self, path: str) -> List[str]:
        """Generate combined variations (encodings + traversals, etc.)"""
        variations = set()
        
        # Get some base variations
        encoded = self.apply_encoding(path, 'url')
        traversal = path + '../'
        
        # Combine encodings dengan traversals
        if encoded and traversal:
            variations.add(encoded + '../')
            variations.add(self.apply_encoding(traversal, 'url'))
        
        return list(variations)
    
    def extract_keywords_from_string(self, text: str) -> List[str]:
        """Extract keywords dari string"""
        keywords = set()
        
        # Split text into components
        parts = re.split(r'[/\-_.]', text)
        for part in parts:
            if part and len(part) > 2 and not part.isdigit():
                clean_part = re.sub(r'[^a-zA-Z]', '', part)
                if len(clean_part) > 2:
                    keywords.add(clean_part.lower())
        
        return list(keywords)
    
    def smart_fuzzing(self, discovered_paths: List[str], target_url: str) -> List[str]:
        """Smart fuzzing berdasarkan discovered patterns"""
        fuzzed_paths = set()
        
        print(info(f"🧠 Starting smart fuzzing based on {len(discovered_paths)} discovered paths..."))
        
        # Extract keywords dari successful paths
        keywords = self.extract_keywords_from_paths(discovered_paths)
        
        # Generate paths berdasarkan keywords
        for keyword in keywords[:25]:  # Limit keywords
            fuzzed_paths.update(self.generate_keyword_paths(keyword))
        
        # Generate paths berdasarkan URL structure
        domain_keywords = self.extract_domain_keywords(target_url)
        for keyword in domain_keywords:
            fuzzed_paths.update(self.generate_domain_based_paths(keyword))
        
        # Add natural language paths
        fuzzed_paths.update(self.generate_comprehensive_natural_paths())
        
        final_paths = list(fuzzed_paths)[:200]  # Limit output
        print(success(f"✅ Smart fuzzing generated {len(final_paths)} paths"))
        
        return final_paths
    
    def extract_keywords_from_paths(self, paths: List[str]) -> List[str]:
        """Extract meaningful keywords dari paths"""
        keywords = set()
        
        for path in paths:
            path_keywords = self.extract_keywords_from_string(path)
            keywords.update(path_keywords)
        
        return list(keywords)[:30]  # Limit keywords
    
    def extract_domain_keywords(self, url: str) -> List[str]:
        """Extract keywords dari domain name"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            
            keywords = set()
            parts = re.split(r'[.\-]', domain)
            
            for part in parts:
                if part and len(part) > 2 and part not in ['www', 'com', 'org', 'net', 'io']:
                    keywords.add(part.lower())
            
            return list(keywords)
        except Exception as e:
            debug(f"Domain keyword extraction error: {e}")
            return []
    
    def generate_keyword_paths(self, keyword: str) -> List[str]:
        """Generate paths berdasarkan keyword"""
        paths = set()
        
        prefixes = ['/', '/api/', '/static/', '/assets/', '/admin/', '/config/', '/v1/']
        suffixes = ['', '.js', '.json', '.html', '.php', '.xml']
        
        for prefix in prefixes:
            for suffix in suffixes:
                paths.add(f"{prefix}{keyword}{suffix}")
        
        # Add variations
        paths.add(f"/{keyword}/api")
        paths.add(f"/v1/{keyword}")
        paths.add(f"/{keyword}/v1")
        paths.add(f"/{keyword}/admin")
        paths.add(f"/api/{keyword}/list")
        paths.add(f"/api/{keyword}/detail")
        
        return list(paths)
    
    def generate_domain_based_paths(self, keyword: str) -> List[str]:
        """Generate paths berdasarkan domain keywords"""
        paths = set()
        
        paths.add(f"/{keyword}")
        paths.add(f"/{keyword}.js")
        paths.add(f"/{keyword}.json")
        paths.add(f"/api/{keyword}")
        paths.add(f"/static/{keyword}")
        paths.add(f"/assets/{keyword}")
        paths.add(f"/{keyword}/api")
        paths.add(f"/{keyword}/admin")
        
        return list(paths)
    
    def generate_comprehensive_natural_paths(self) -> List[str]:
        """Generate comprehensive natural language paths"""
        natural_paths = set()
        
        # Combine paths dari semua categories
        for category, paths in self.natural_paths.items():
            natural_paths.update(paths[:10])  # Limit per category
        
        # Add common patterns
        for pattern_type, patterns in self.common_patterns.items():
            natural_paths.update(patterns[:5])
        
        return list(natural_paths)

def test_quantum_fuzzer():
    """Test the enhanced quantum fuzzer"""
    print(term.styles.banner("🧪 Testing Quantum Fuzzer"))
    
    fuzzer = QuantumFuzzer()
    
    # Test base paths
    base_paths = [
        "/api/users",
        "/admin/config",
        "/static/js/app.js", 
        "/v1/data",
        "/login"
    ]
    
    print(info(f"Testing with {len(base_paths)} base paths..."))
    
    # Test quantum path generation
    quantum_paths = fuzzer.generate_quantum_paths(base_paths, 50)
    
    print(success(f"Generated {len(quantum_paths)} quantum paths:"))
    for i, path in enumerate(quantum_paths[:15]):
        print(f"  {i+1:2d}. {path}")
    if len(quantum_paths) > 15:
        print(info(f"  ... and {len(quantum_paths) - 15} more paths"))
    
    # Test smart fuzzing
    print(info("Testing smart fuzzing..."))
    discovered_paths = ["/api/v1/users", "/admin/config.json", "/login/auth"]
    smart_paths = fuzzer.smart_fuzzing(discovered_paths, "https://example.com")
    
    print(success(f"Smart fuzzing generated {len(smart_paths)} paths:"))
    for i, path in enumerate(smart_paths[:10]):
        print(f"  {i+1:2d}. {path}")
    
    print(success("🎯 Quantum Fuzzer test completed!"))

if __name__ == "__main__":
    test_quantum_fuzzer()