#!/usr/bin/env python3
"""
Enhanced Evasion Engine dengan Color Integration & Advanced Bypass Techniques
Advanced evasion system untuk bypass WAF & avoid detection
"""

import random
import time
import requests
from typing import Dict, List, Optional
from fake_useragent import UserAgent

# Import our color system
from utils.colors import term, success, error, warning, info, debug

class EvasionEngine:
    def __init__(self):
        self.ua = UserAgent()
        self.request_count = 0
        self.session = requests.Session()
        
        # Setup session dengan evasion defaults
        self._setup_evasion_session()
        
    def _setup_evasion_session(self):
        """Setup session dengan evasion techniques"""
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.session.verify = False  # Skip SSL verification
    
    def get_evasion_headers(self) -> Dict[str, str]:
        """Generate advanced evasion headers"""
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
            'Pragma': 'no-cache',
            'TE': 'trailers'
        }
    
    def _generate_random_ip(self) -> str:
        """Generate random IP address untuk header spoofing"""
        return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
    
    def smart_delay(self, base_delay: float = 2.0):
        """Intelligent random delay antara requests"""
        delay = base_delay + random.uniform(0.5, 3.0)
        time.sleep(delay)
    
    def is_blocked(self, response: requests.Response) -> bool:
        """Enhanced blocking detection dengan WAF identification"""
        if not response:
            return False
            
        # Normal responses yang jelas NOT blocking
        if response.status_code in [200, 201, 301, 302, 404]:
            return False
        
        # Only consider real blocking pada specific status codes
        if response.status_code not in [403, 429, 503, 406]:
            return False
        
        response_text = response.text.lower()[:1000]
        response_headers = str(response.headers).lower()
        
        # Enhanced blocking indicators
        blocking_indicators = [
            # Cloudflare
            response.status_code == 403 and any(indicator in response_text for indicator in 
                                             ['cloudflare', 'captcha', 'challenge', 'waf']),
            # Rate limiting
            response.status_code == 429 and any(indicator in response_text for indicator in 
                                              ['rate limit', 'too many requests']),
            # WAF blocks
            any(waf in response_headers for waf in ['cloudflare', 'akamai', 'imperva', 'aws']),
            response.status_code == 403 and 'access denied' in response_text,
            'your ip has been blocked' in response_text,
            'security policy' in response_text,
            'bot detected' in response_text,
            'suspicious activity' in response_text,
        ]
        
        if any(blocking_indicators):
            debug(f"Blocking detected: Status {response.status_code}, Indicators: {blocking_indicators}")
            return True
            
        return False
    
    def stealth_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Advanced stealth request dengan comprehensive evasion techniques"""
        self.request_count += 1
        
        # Apply smart delay
        self.smart_delay()
        
        # Use advanced evasion headers
        headers = kwargs.get('headers', {})
        headers.update(self.get_evasion_headers())
        
        try:
            timeout = kwargs.get('timeout', 15)
            
            # Prepare request parameters
            request_params = {
                'method': method.upper(),
                'url': url,
                'headers': headers,
                'timeout': timeout,
                'allow_redirects': kwargs.get('allow_redirects', True),
                'verify': False
            }
            
            # Remove any None values
            request_params = {k: v for k, v in request_params.items() if v is not None}
            
            debug(f"Evasion request #{self.request_count}: {method} {url}")
            
            response = self.session.request(**request_params)
            
            # Enhanced blocking detection
            if self.is_blocked(response):
                warning(f"WAF/Blocking detected: {url} (Status: {response.status_code})")
                return None
                
            # Log successful requests
            if response.status_code == 200:
                debug(f"Evasion success: {url}")
            elif response.status_code in [403, 429]:
                warning(f"Access issue: {url} (Status: {response.status_code})")
                
            return response
            
        except requests.Timeout:
            error(f"Evasion timeout: {url}")
            return None
        except requests.ConnectionError as e:
            error(f"Evasion connection error: {url} - {e}")
            return None
        except requests.RequestException as e:
            error(f"Evasion request failed: {url} - {e}")
            return None
        except Exception as e:
            error(f"Evasion unexpected error: {url} - {e}")
            return None
    
    def advanced_stealth_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Advanced stealth request dengan retry logic & exponential backoff"""
        max_retries = kwargs.get('max_retries', 3)
        
        for attempt in range(max_retries):
            response = self.stealth_request(url, method, **kwargs)
            
            if response and not self.is_blocked(response):
                if response.status_code == 200:
                    debug(f"Advanced evasion success on attempt {attempt + 1}: {url}")
                return response
            
            # Exponential backoff dengan jitter
            backoff_time = (attempt + 1) * 2 + random.uniform(0.1, 1.0)
            warning(f"Evasion retry {attempt + 1}/{max_retries} after {backoff_time:.1f}s...")
            time.sleep(backoff_time)
        
        error(f"All evasion attempts failed for: {url}")
        return None
    
    def rotate_session(self):
        """Rotate session untuk avoid fingerprinting"""
        self.session.close()
        self.session = requests.Session()
        self._setup_evasion_session()
        debug("Session rotated for evasion")
    
    def get_evasion_stats(self) -> Dict[str, any]:
        """Get evasion statistics"""
        return {
            'total_requests': self.request_count,
            'current_session_requests': self.request_count,
            'user_agent_rotation': 'Enabled',
            'ip_spoofing': 'Enabled',
            'random_delays': 'Enabled'
        }
    
    def test_evasion(self, test_url: str = "https://httpbin.org/user-agent") -> bool:
        """Test evasion capabilities"""
        info("Testing evasion engine...")
        
        try:
            response = self.stealth_request(test_url)
            if response and response.status_code == 200:
                user_agent = response.json().get('user-agent', 'Unknown')
                success(f"Evasion test successful! User-Agent: {user_agent}")
                return True
            else:
                error(f"Evasion test failed: Status {response.status_code if response else 'No response'}")
                return False
                
        except Exception as e:
            error(f"Evasion test error: {e}")
            return False

# Quick test function
def test_evasion_engine():
    """Test the enhanced evasion engine"""
    print(term.styles.banner("Testing Enhanced Evasion Engine"))
    
    evasion = EvasionEngine()
    
    # Test basic functionality
    if evasion.test_evasion():
        # Test multiple requests
        test_urls = [
            "https://httpbin.org/headers",
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent"
        ]
        
        for url in test_urls:
            response = evasion.stealth_request(url)
            if response and response.status_code == 200:
                success(f"✓ {url} - Success")
            else:
                error(f"✗ {url} - Failed")
        
        # Show evasion stats
        stats = evasion.get_evasion_stats()
        print(info("Evasion Statistics:"))
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print(success("Evasion engine test completed!"))

if __name__ == "__main__":
    test_evasion_engine()