import requests
import time
import random
from typing import Dict, Any

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.request_history = []
        self.cookies = {}
        
    def setup_session(self, headers: Dict[str, str] = None):
        """Setup session dengan headers default"""
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        if headers:
            default_headers.update(headers)
            
        self.session.headers.update(default_headers)
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Make request dengan session management"""
        try:
            response = self.session.request(method=method, url=url, **kwargs)
            
            # Record request history
            self.request_history.append({
                'url': url,
                'method': method,
                'status_code': response.status_code,
                'timestamp': time.time()
            })
            
            # Update cookies
            self.cookies.update(self.session.cookies.get_dict())
            
            return response
            
        except requests.RequestException as e:
            print(f"❌ Request failed: {url} - {e}")
            raise
    
    def get_cookies(self) -> Dict[str, str]:
        """Get current cookies"""
        return self.cookies.copy()
    
    def set_cookies(self, cookies: Dict[str, str]):
        """Set cookies untuk session"""
        self.session.cookies.update(cookies)
        self.cookies.update(cookies)
    
    def clear_cookies(self):
        """Clear semua cookies"""
        self.session.cookies.clear()
        self.cookies.clear()
    
    def get_request_count(self) -> int:
        """Get total request count"""
        return len(self.request_history)
    
    def get_recent_requests(self, count: int = 10) -> list:
        """Get recent requests"""
        return self.request_history[-count:]
    
    def reset_session(self):
        """Reset session ke state awal"""
        self.session = requests.Session()
        self.request_history = []
        self.setup_session()