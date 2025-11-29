#!/usr/bin/env python3
"""
Adaptive Engine - Deteksi jenis target & apply strategy yang tepat
"""

import requests
import re
from utils.colors import term

class AdaptiveEngine:
    def __init__(self):
        self.platform_patterns = {
            'vercel': ['vercel', 'x-vercel', '_next/static'],
            'firebase': ['firebase', '__/firebase'],
            'netlify': ['netlify', '_redirects', '_headers'],
            'aws': ['aws', 'x-amz', 'amazon'],
            'azure': ['azure', 'x-ms-'],
            'heroku': ['heroku', 'x-heroku'],
            'wordpress': ['wp-', 'wordpress', 'wp-includes'],
            'laravel': ['laravel', 'x-laravel'],
            'nodejs': ['express', 'x-powered-by: express'],
            'python': ['python', 'django', 'flask'],
        }
    
    def detect_platform(self, target_url):
        """Deteksi platform target"""
        try:
            response = requests.get(target_url, timeout=10, verify=False)
            headers = response.headers
            body = response.text.lower()
            
            detected_platforms = []
            
            # Check headers
            for platform, patterns in self.platform_patterns.items():
                for pattern in patterns:
                    if pattern in str(headers).lower() or pattern in body:
                        detected_platforms.append(platform)
                        break
            
            return list(set(detected_platforms)) or ['unknown']
            
        except Exception as e:
            return ['unknown']
    
    def get_scan_strategy(self, platform):
        """Dapatkan strategy berdasarkan platform"""
        strategies = {
            'vercel': {
                'paths': self.vercel_paths(),
                'evasion': 'stealth',
                'delay': (3, 8),
                'headers': 'stealth_headers'
            },
            'firebase': {
                'paths': self.firebase_paths(), 
                'evasion': 'moderate',
                'delay': (2, 5),
                'headers': 'mobile_headers'
            },
            'netlify': {
                'paths': self.netlify_paths(),
                'evasion': 'light',
                'delay': (1, 3),
                'headers': 'standard_headers'
            },
            'wordpress': {
                'paths': self.wordpress_paths(),
                'evasion': 'aggressive', 
                'delay': (1, 2),
                'headers': 'wordpress_headers'
            },
            'unknown': {
                'paths': self.universal_paths(),
                'evasion': 'moderate',
                'delay': (2, 4),
                'headers': 'standard_headers'
            }
        }
        
        return strategies.get(platform, strategies['unknown'])
    
    def vercel_paths(self):
        """Paths khusus Vercel/Next.js"""
        return [
            '/api', '/api/', '/api/auth', '/api/users', '/api/data',
            '/_next/static', '/_next/data', '/_next/image',
            '/auth', '/login', '/dashboard', '/profile'
        ]
    
    def firebase_paths(self):
        """Paths khusus Firebase"""
        return [
            '/__/firebase', '/__/auth', '/__/config',
            '/api', '/v1', '/rest/v1',
            '/users', '/posts', '/data'
        ]
    
    def wordpress_paths(self):
        """Paths khusus WordPress"""
        return [
            '/wp-admin', '/wp-login.php', '/wp-content',
            '/wp-includes', '/xmlrpc.php', '/wp-json',
            '/admin', '/login', '/dashboard'
        ]
    
    def universal_paths(self):
        """Universal paths untuk semua platform"""
        return [
            # API endpoints
            '/api', '/api/v1', '/api/v2', '/graphql', '/rest', '/json',
            
            # Auth endpoints  
            '/auth', '/login', '/register', '/signin', '/signup',
            '/oauth', '/token', '/refresh',
            
            # Common directories
            '/admin', '/dashboard', '/panel', '/control',
            '/user', '/users', '/profile', '/account',
            '/data', '/files', '/uploads', '/storage',
            '/config', '/settings', '/setup',
            
            # File endpoints
            '/robots.txt', '/sitemap.xml', '/.env', '/config.json',
            '/package.json', '/composer.json',
            
            # Well-known
            '/.well-known/security.txt', '/.well-known/jwks.json'
        ]