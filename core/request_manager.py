#!/usr/bin/env python3
"""
Advanced Request Manager dengan Evasion Techniques
Heart of the scanner - handles all HTTP requests dengan smart bypass
"""

import requests
import time
import random
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urljoin
from fake_useragent import UserAgent

# Import our color system
from utils.colors import term, success, error, warning, info, debug

class RequestManager:
    def __init__(self, max_retries: int = 3, timeout: int = 15, enable_evasion: bool = True):
        self.max_retries = max_retries
        self.timeout = timeout
        self.enable_evasion = enable_evasion
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # Setup session dengan evasion defaults
        self._setup_evasion_session()
        
    def _setup_evasion_session(self):
        """Setup session dengan evasion techniques"""
        # Default headers yang natural
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # SSL verification disabled untuk testing (bisa di-enable di production)
        self.session.verify = False
        
        # Handle redirects secara smart
        self.session.max_redirects = 5
        
    def _get_evasion_headers(self) -> Dict[str, str]:
        """Generate stealth headers untuk bypass WAF"""
        if not self.enable_evasion:
            return {}
            
        return {
            'User-Agent': self.ua.random,
            'X-Requested-With': 'XMLHttpRequest',
            'X-Forwarded-For': self._generate_random_ip(),
            'CF-Connecting-IP': self._generate_random_ip(),
            'Referer': 'https://www.google.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
    
    def _generate_random_ip(self) -> str:
        """Generate random IP address untuk header spoofing"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def _smart_delay(self, base_delay: float = 2.0):
        """Random delay antara requests untuk avoid rate limiting"""
        if self.enable_evasion:
            delay = base_delay + random.uniform(0.5, 3.0)
            time.sleep(delay)
    
    def _should_retry(self, response: requests.Response, attempt: int) -> Tuple[bool, float]:
        """Determine if request should be retried dan berapa lama delaynya"""
        if response is None:
            return True, (attempt + 1) * 2  # Increase delay setiap attempt
            
        status_code = response.status_code
        
        # Rate limiting - wait longer
        if status_code in [429, 420]:
            wait_time = (attempt + 1) * 5  # Exponential backoff
            print(warning(f"Rate limited (429), waiting {wait_time}s..."))
            return True, wait_time
            
        # Server errors - retry with delay
        if status_code >= 500:
            wait_time = (attempt + 1) * 3
            print(warning(f"Server error {status_code}, waiting {wait_time}s..."))
            return True, wait_time
            
        # Cloudflare/WAF challenges
        if status_code in [403, 406] and any(indicator in response.text.lower() for indicator in 
                                           ['cloudflare', 'waf', 'challenge', 'captcha', 'security']):
            wait_time = (attempt + 1) * 4
            print(warning(f"WAF/Cloudflare detected, waiting {wait_time}s..."))
            return True, wait_time
            
        return False, 0
    
    def smart_request(self, url: str, method: str = 'GET', 
                     use_evasion: bool = True, **kwargs) -> Optional[requests.Response]:
        """
        Advanced smart request dengan evasion & retry logic
        """
        evasion_headers = self._get_evasion_headers() if (use_evasion and self.enable_evasion) else {}
        
        # Merge headers
        headers = kwargs.pop('headers', {})
        headers.update(evasion_headers)
        
        for attempt in range(self.max_retries):
            try:
                print(debug(f"Attempt {attempt + 1}/{self.max_retries}: {method} {url}"))
                
                response = self.session.request(
                    method=method.upper(),
                    url=url,
                    timeout=self.timeout,
                    headers=headers,
                    allow_redirects=True,
                    **kwargs
                )
                
                # Check if we should retry
                should_retry, wait_time = self._should_retry(response, attempt)
                
                if should_retry and attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue
                
                # Log result berdasarkan status code
                if response.status_code == 200:
                    print(success(f"SUCCESS: {url} (200)"))
                elif response.status_code in [301, 302]:
                    print(info(f"REDIRECT: {url} -> {response.url}"))
                elif response.status_code == 403:
                    print(warning(f"FORBIDDEN: {url}"))
                elif response.status_code == 404:
                    # Jangan log 404 untuk avoid spam
                    pass
                else:
                    print(warning(f"HTTP {response.status_code}: {url}"))
                
                return response
                    
            except requests.Timeout:
                print(error(f"Timeout attempt {attempt + 1}/{self.max_retries}"))
                if attempt < self.max_retries - 1:
                    self._smart_delay(1.0)
                    continue
                    
            except requests.ConnectionError as e:
                print(error(f"Connection error: {e}"))
                if attempt < self.max_retries - 1:
                    self._smart_delay(3.0)
                    continue
                    
            except requests.RequestException as e:
                print(error(f"Request error: {e}"))
                if attempt < self.max_retries - 1:
                    self._smart_delay(2.0)
                    continue
            
            except Exception as e:
                print(error(f"Unexpected error: {e}"))
                if attempt < self.max_retries - 1:
                    self._smart_delay(2.0)
                    continue
        
        print(error(f"All {self.max_retries} attempts failed for: {url}"))
        return None
    
    def check_url_exists(self, url: str, use_evasion: bool = True) -> Tuple[bool, int]:
        """Check jika URL exists, return (exists, status_code)"""
        try:
            response = self.smart_request(url, method='HEAD', use_evasion=use_evasion)
            if response:
                return (response.status_code == 200, response.status_code)
            return (False, 0)
        except Exception as e:
            print(debug(f"URL check failed: {e}"))
            return (False, 0)
    
    def get_final_url(self, url: str, use_evasion: bool = True) -> str:
        """Get final URL setelah redirect"""
        try:
            response = self.smart_request(url, use_evasion=use_evasion, allow_redirects=True)
            return response.url if response else url
        except Exception as e:
            print(debug(f"Get final URL failed: {e}"))
            return url
    
    def get_content_type(self, url: str, use_evasion: bool = True) -> str:
        """Get content type dari URL"""
        try:
            response = self.smart_request(url, method='HEAD', use_evasion=use_evasion)
            return response.headers.get('content-type', '') if response else ''
        except Exception as e:
            print(debug(f"Get content type failed: {e}"))
            return ''
    
    def get_page_title(self, url: str, use_evasion: bool = True) -> str:
        """Extract page title dari HTML"""
        try:
            response = self.smart_request(url, use_evasion=use_evasion)
            if response and response.status_code == 200:
                # Simple title extraction
                import re
                title_match = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
                return title_match.group(1).strip() if title_match else ''
            return ''
        except Exception:
            return ''
    
    def test_connection(self, url: str = "https://httpbin.org/json") -> bool:
        """Test connection dan evasion capabilities"""
        print(info("Testing request manager connection..."))
        
        try:
            response = self.smart_request(url, use_evasion=True)
            if response and response.status_code == 200:
                print(success("Request manager working perfectly!"))
                print(debug(f"User-Agent: {self.session.headers.get('User-Agent', 'Default')}"))
                return True
            else:
                print(error(f"Test failed with status: {response.status_code if response else 'No response'}"))
                return False
                
        except Exception as e:
            print(error(f"Test failed with error: {e}"))
            return False
    
    def set_proxy(self, proxy_url: str):
        """Set proxy untuk requests"""
        try:
            if proxy_url:
                self.session.proxies.update({
                    'http': proxy_url,
                    'https': proxy_url,
                })
                print(info(f"Proxy set: {proxy_url}"))
            else:
                self.session.proxies.clear()
                print(info("Proxy cleared"))
        except Exception as e:
            print(error(f"Failed to set proxy: {e}"))

# Quick test function
def test_request_manager():
    """Test the request manager"""
    print(term.styles.banner("Testing Request Manager"))
    
    rm = RequestManager(max_retries=2, enable_evasion=True)
    
    # Test connection
    if rm.test_connection():
        # Test various URLs
        test_urls = [
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/404", 
            "https://httpbin.org/status/403"
        ]
        
        for url in test_urls:
            exists, status = rm.check_url_exists(url)
            print(f"{url} -> Exists: {exists}, Status: {status}")

if __name__ == "__main__":
    test_request_manager()