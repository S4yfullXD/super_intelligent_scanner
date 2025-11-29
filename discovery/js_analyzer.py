#!/usr/bin/env python3
"""
Enhanced JavaScript Analyzer dengan Color Integration & Advanced Analysis
Comprehensive JS analysis untuk extract endpoints, secrets, dan patterns
"""

import re
import ast
import requests
from urllib.parse import urljoin
from typing import List, Dict, Set, Any
import json

# Import color system yang sudah ada
from utils.colors import term, success, error, warning, info, debug

class JSAnalyzer:
    def __init__(self):
        self.analysis_patterns = self.load_analysis_patterns()
        
        print(debug("🔍 JavaScript Analyzer initialized"))
    
    def load_analysis_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for JavaScript analysis"""
        return {
            'endpoints': [
                r'["\'](https?://[^"\']+?)["\']',
                r'["\'](/[^"\']+?)["\']',
                r'`(https?://[^`]+?)`',
                r'`(/[^`]+?)`',
                r'fetch\(["\']([^"\']+?)["\']',
                r'axios\.(?:get|post)\(["\']([^"\']+?)["\']',
                r'\.ajax\([^)]*url:\s*["\']([^"\']+?)["\']',
            ],
            'secrets': [
                r'api[_-]?key["\']?\s*:\s*["\']([^"\']{20,50})["\']',
                r'secret["\']?\s*:\s*["\']([^"\']{10,50})["\']',
                r'password["\']?\s*:\s*["\']([^"\']{3,50})["\']',
                r'token["\']?\s*:\s*["\']([^"\']{10,100})["\']',
                r'client[_-]?(?:id|secret)["\']?\s*:\s*["\']([^"\']{10,50})["\']',
                r'authorization["\']?\s*:\s*["\'](Bearer\s+[^"\']+)["\']',
            ],
            'functions': [
                r'function\s+(\w+)\s*\(',
                r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                r'let\s+(\w+)\s*=\s*\([^)]*\)\s*=>',
                r'(\w+)\s*\([^)]*\)\s*{',
                r'class\s+(\w+)',
            ],
            'variables': [
                r'const\s+(\w+)\s*=',
                r'let\s+(\w+)\s*=',
                r'var\s+(\w+)\s*=',
            ],
            'api_patterns': [
                r'["\'](/api/[^"\']+?)["\']',
                r'["\'](/v[1-9]/[^"\']+?)["\']',
                r'["\'](/graphql[^"\']*?)["\']',
                r'["\'](/rest/[^"\']+?)["\']',
            ]
        }
    
    def analyze_javascript(self, js_content: str, base_url: str = "") -> Dict[str, Any]:
        """Comprehensive JavaScript analysis dengan detailed reporting"""
        analysis = {
            'endpoints_found': [],
            'secrets_detected': [],
            'functions_identified': [],
            'variables_identified': [],
            'imports_found': [],
            'api_endpoints': [],
            'analysis_summary': {},
            'ast_analysis': {}
        }
        
        print(info(f"📜 Analyzing JavaScript content ({len(js_content)} characters)..."))
        
        if not js_content or len(js_content.strip()) < 10:
            warning("   JavaScript content too short or empty")
            return analysis
        
        # Basic pattern analysis
        analysis['endpoints_found'] = self.extract_endpoints(js_content, base_url)
        analysis['secrets_detected'] = self.extract_secrets(js_content)
        analysis['functions_identified'] = self.extract_functions(js_content)
        analysis['variables_identified'] = self.extract_variables(js_content)
        analysis['imports_found'] = self.extract_imports(js_content)
        analysis['api_endpoints'] = self.extract_api_endpoints(js_content, base_url)
        
        # Advanced AST analysis (if possible)
        try:
            analysis['ast_analysis'] = self.ast_analyze(js_content)
            debug("   AST analysis completed successfully")
        except Exception as e:
            analysis['ast_analysis'] = {'error': f'AST parsing failed: {e}'}
            debug(f"   AST analysis skipped: {e}")
        
        # Generate summary
        analysis['analysis_summary'] = self.generate_summary(analysis)
        
        # Print analysis results
        self.print_analysis_results(analysis)
        
        return analysis
    
    def extract_endpoints(self, js_content: str, base_url: str) -> List[Dict]:
        """Extract endpoints from JavaScript"""
        endpoints = []
        
        print(debug("   Extracting endpoints..."))
        
        for pattern in self.analysis_patterns['endpoints']:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[0]
                else:
                    url = match
                
                if url and not url.startswith(('javascript:', 'mailto:', 'data:')):
                    # Make URL absolute if it's relative
                    if url.startswith('/') and base_url:
                        full_url = urljoin(base_url, url)
                    else:
                        full_url = url
                    
                    endpoint_info = {
                        'url': full_url,
                        'original': url,
                        'type': self.classify_endpoint(url),
                        'pattern': pattern[:30] + '...' if len(pattern) > 30 else pattern
                    }
                    
                    # Avoid duplicates
                    if not any(e['url'] == endpoint_info['url'] for e in endpoints):
                        endpoints.append(endpoint_info)
                        debug(f"     Found endpoint: {url}")
        
        success(f"   ✅ Found {len(endpoints)} endpoints")
        return endpoints
    
    def extract_api_endpoints(self, js_content: str, base_url: str) -> List[Dict]:
        """Extract specific API endpoints from JavaScript"""
        api_endpoints = []
        
        print(debug("   Extracting API endpoints..."))
        
        for pattern in self.analysis_patterns['api_patterns']:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[0]
                else:
                    endpoint = match
                
                if endpoint:
                    # Make URL absolute if it's relative
                    if endpoint.startswith('/') and base_url:
                        full_url = urljoin(base_url, endpoint)
                    else:
                        full_url = endpoint
                    
                    api_info = {
                        'url': full_url,
                        'original': endpoint,
                        'type': 'api',
                        'pattern': 'api_specific'
                    }
                    
                    if not any(e['url'] == api_info['url'] for e in api_endpoints):
                        api_endpoints.append(api_info)
                        debug(f"     Found API endpoint: {endpoint}")
        
        success(f"   ✅ Found {len(api_endpoints)} API-specific endpoints")
        return api_endpoints
    
    def classify_endpoint(self, endpoint: str) -> str:
        """Classify endpoint type"""
        if endpoint.startswith('/api/') or '/v1/' in endpoint or '/v2/' in endpoint:
            return 'api'
        elif endpoint.endswith(('.js', '.css', '.woff', '.ttf')):
            return 'static'
        elif endpoint.endswith(('.json', '.xml')):
            return 'data'
        elif endpoint.endswith(('.html', '.php', '.jsp')):
            return 'page'
        elif 'cdn' in endpoint.lower() or 'cloudfront' in endpoint.lower():
            return 'cdn'
        else:
            return 'unknown'
    
    def extract_secrets(self, js_content: str) -> List[Dict]:
        """Extract potential secrets from JavaScript"""
        secrets = []
        
        print(debug("   Scanning for secrets..."))
        
        for pattern in self.analysis_patterns['secrets']:
            matches = re.findall(pattern, js_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    secret = match[0]
                else:
                    secret = match
                
                if self.looks_like_secret(secret):
                    secret_info = {
                        'value': secret[:50] + '...' if len(secret) > 50 else secret,
                        'full_value': secret,
                        'type': self.classify_secret(secret),
                        'confidence': self.secret_confidence(secret),
                        'pattern': pattern[:30] + '...' if len(pattern) > 30 else pattern
                    }
                    
                    # Avoid duplicates
                    if not any(s['full_value'] == secret_info['full_value'] for s in secrets):
                        secrets.append(secret_info)
                        
                        if secret_info['confidence'] == 'high':
                            warning(f"     ⚠️  High confidence secret found: {secret_info['type']}")
                        else:
                            debug(f"     Potential secret: {secret_info['type']}")
        
        if secrets:
            warning(f"   ⚠️  Found {len(secrets)} potential secrets")
        else:
            debug("   No secrets detected")
        
        return secrets
    
    def looks_like_secret(self, text: str) -> bool:
        """Check if text looks like a secret"""
        if len(text) < 8:
            return False
        
        # Common false positives
        false_positives = ['undefined', 'null', 'true', 'false', 'function', 'localhost']
        if text.lower() in false_positives:
            return False
        
        # Check for common patterns
        if re.match(r'^[a-f0-9]{32}$', text):  # MD5 hash
            return True
        if re.match(r'^[a-f0-9]{40}$', text):  # SHA-1 hash
            return True
        if text.startswith('eyJ') and len(text) > 50:  # JWT token
            return True
        
        return True
    
    def classify_secret(self, secret: str) -> str:
        """Classify secret type"""
        secret_lower = secret.lower()
        
        if 'key' in secret_lower or len(secret) in [20, 32, 40, 64]:
            return 'api_key'
        elif 'token' in secret_lower or secret.startswith('eyJ'):
            return 'jwt_token'
        elif 'secret' in secret_lower:
            return 'secret'
        elif 'password' in secret_lower or 'pass' in secret_lower:
            return 'password'
        elif 'client' in secret_lower and ('id' in secret_lower or 'secret' in secret_lower):
            return 'oauth_credential'
        elif 'bearer' in secret_lower:
            return 'bearer_token'
        else:
            return 'unknown'
    
    def secret_confidence(self, secret: str) -> str:
        """Calculate confidence level for secret"""
        # High confidence patterns
        if (len(secret) >= 20 and 
            any(c.isupper() for c in secret) and 
            any(c.islower() for c in secret) and
            any(c.isdigit() for c in secret)):
            return 'high'
        elif (secret.startswith('eyJ') or  # JWT
              re.match(r'^[a-f0-9]{32,64}$', secret) or  # Hashes
              'bearer' in secret.lower()):
            return 'high'
        elif len(secret) >= 15:
            return 'medium'
        else:
            return 'low'
    
    def extract_functions(self, js_content: str) -> List[str]:
        """Extract function names from JavaScript"""
        functions = set()
        
        for pattern in self.analysis_patterns['functions']:
            matches = re.findall(pattern, js_content)
            functions.update(matches)
        
        return sorted(list(functions))
    
    def extract_variables(self, js_content: str) -> List[str]:
        """Extract variable names from JavaScript"""
        variables = set()
        
        for pattern in self.analysis_patterns['variables']:
            matches = re.findall(pattern, js_content)
            variables.update(matches)
        
        return sorted(list(variables))
    
    def extract_imports(self, js_content: str) -> List[Dict]:
        """Extract import statements from JavaScript"""
        imports = []
        
        import_patterns = [
            r'import\s+(?:\{[^}]*\}|\* as \w+|\w+)\s+from\s+["\']([^"\']+)["\']',
            r'require\(["\']([^"\']+)["\']\)',
            r'import\(["\']([^"\']+)["\']\)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                import_info = {
                    'module': match,
                    'type': 'es6' if 'import' in pattern else 'commonjs'
                }
                
                if not any(i['module'] == import_info['module'] for i in imports):
                    imports.append(import_info)
        
        return imports
    
    def ast_analyze(self, js_content: str) -> Dict[str, Any]:
        """Advanced AST analysis of JavaScript"""
        analysis = {
            'function_calls': [],
            'object_access': [],
            'string_literals': [],
            'complexity_metrics': {},
            'analysis_notes': []
        }
        
        try:
            # Extract function calls
            function_calls = re.findall(r'(\w+)\([^)]*\)', js_content)
            analysis['function_calls'] = sorted(list(set(function_calls)))[:20]
            
            # Extract object property access
            object_access = re.findall(r'(\w+)\.(\w+)', js_content)
            analysis['object_access'] = list(set(object_access))[:20]
            
            # Extract string literals (potential endpoints/config)
            string_literals = re.findall(r'["\']([^"\']{10,100})["\']', js_content)
            analysis['string_literals'] = list(set(string_literals))[:15]
            
            # Basic complexity metrics
            analysis['complexity_metrics'] = {
                'line_count': js_content.count('\n') + 1,
                'function_count': len(re.findall(r'function\s+\w', js_content)),
                'variable_count': len(re.findall(r'(const|let|var)\s+\w', js_content)),
                'import_count': len(re.findall(r'(import|require)', js_content)),
                'class_count': len(re.findall(r'class\s+\w', js_content)),
            }
            
            # Analysis notes
            if analysis['complexity_metrics']['function_count'] > 50:
                analysis['analysis_notes'].append('High function complexity')
            if analysis['complexity_metrics']['import_count'] > 10:
                analysis['analysis_notes'].append('Many external dependencies')
                
        except Exception as e:
            analysis['analysis_notes'].append(f'AST analysis error: {e}')
        
        return analysis
    
    def generate_summary(self, analysis: Dict) -> Dict[str, Any]:
        """Generate analysis summary"""
        high_confidence_secrets = len([s for s in analysis['secrets_detected'] if s['confidence'] == 'high'])
        medium_confidence_secrets = len([s for s in analysis['secrets_detected'] if s['confidence'] == 'medium'])
        
        return {
            'total_endpoints': len(analysis['endpoints_found']),
            'total_secrets': len(analysis['secrets_detected']),
            'high_confidence_secrets': high_confidence_secrets,
            'medium_confidence_secrets': medium_confidence_secrets,
            'total_functions': len(analysis['functions_identified']),
            'total_variables': len(analysis['variables_identified']),
            'api_endpoints': len(analysis['api_endpoints']),
            'imports_count': len(analysis['imports_found']),
            'ast_complexity': analysis['ast_analysis'].get('complexity_metrics', {}).get('function_count', 0)
        }
    
    def print_analysis_results(self, analysis: Dict):
        """Print analysis results dengan color formatting"""
        summary = analysis['analysis_summary']
        
        print(success(f"🎯 JavaScript Analysis Completed!"))
        print(info(f"   📊 Summary:"))
        print(f"      • Endpoints found: {summary['total_endpoints']}")
        print(f"      • API endpoints: {summary['api_endpoints']}")
        print(f"      • Secrets detected: {summary['total_secrets']}")
        
        if summary['high_confidence_secrets'] > 0:
            print(warning(f"      • High confidence secrets: {summary['high_confidence_secrets']}"))
        
        print(f"      • Functions: {summary['total_functions']}")
        print(f"      • Variables: {summary['total_variables']}")
        print(f"      • Imports: {summary['imports_count']}")
        
        # Print notable findings
        if analysis['secrets_detected']:
            print(warning(f"   🔐 Secrets Found:"))
            for secret in analysis['secrets_detected'][:3]:  # Show first 3
                confidence_color = term.colors.BRIGHT_RED if secret['confidence'] == 'high' else term.colors.BRIGHT_YELLOW
                print(f"      {confidence_color}{secret['type']}: {secret['value']}{term.colors.RESET}")
        
        if analysis['api_endpoints']:
            print(info(f"   🌐 API Endpoints:"))
            for endpoint in analysis['api_endpoints'][:5]:  # Show first 5
                print(f"      • {endpoint['url']}")

def test_js_analyzer():
    """Test function untuk JS Analyzer"""
    print(term.styles.banner("🧪 Testing JavaScript Analyzer"))
    
    analyzer = JSAnalyzer()
    
    # Sample JavaScript content untuk testing
    sample_js = """
    // Sample JavaScript dengan berbagai patterns
    const apiBase = "https://api.example.com";
    
    function fetchUserData(userId) {
        return fetch(apiBase + '/v1/users/' + userId)
            .then(response => response.json());
    }
    
    const config = {
        apiUrl: "/api/v2/config",
        secretToken: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        clientId: "client_12345",
        clientSecret: "secret_67890"
    };
    
    axios.get('/api/graphql', {
        headers: {
            'Authorization': 'Bearer ' + config.secretToken
        }
    });
    
    // Import statements
    import { useState, useEffect } from 'react';
    const express = require('express');
    
    // More endpoints
    $.ajax({
        url: '/api/search',
        method: 'POST',
        data: { query: 'test' }
    });
    """
    
    print(info("Analyzing sample JavaScript content..."))
    
    # Run analysis
    analysis = analyzer.analyze_javascript(sample_js, "https://example.com")
    
    # Detailed results
    print(info("Detailed Analysis Results:"))
    
    if analysis['endpoints_found']:
        print(success(f"📍 Endpoints ({len(analysis['endpoints_found'])}):"))
        for endpoint in analysis['endpoints_found'][:5]:
            print(f"   • {endpoint['url']} ({endpoint['type']})")
    
    if analysis['functions_identified']:
        print(info(f"🔧 Functions ({len(analysis['functions_identified'])}):"))
        print(f"   {', '.join(analysis['functions_identified'][:10])}")
    
    print(success("🎯 JavaScript Analyzer test completed!"))

if __name__ == "__main__":
    test_js_analyzer()