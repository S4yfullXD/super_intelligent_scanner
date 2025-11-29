import requests
import random
import time
from typing import List, Dict, Optional

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_index = 0
        self.last_refresh = 0
        self.refresh_interval = 3600  # 1 hour
    
    def load_proxies_from_file(self, filepath: str) -> bool:
        """Load proxies from file"""
        try:
            with open(filepath, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            print(f"✅ Loaded {len(self.proxies)} proxies from {filepath}")
            return True
        except Exception as e:
            print(f"❌ Error loading proxies: {e}")
            return False
    
    def add_proxy(self, proxy: str):
        """Add a single proxy"""
        if proxy and proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy with rotation"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
        return {
            'http': f"http://{proxy}",
            'https': f"https://{proxy}"
        }
    
    def validate_proxy(self, proxy: str, test_url: str = "http://httpbin.org/ip") -> bool:
        """Validate if proxy is working"""
        try:
            response = requests.get(
                test_url,
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def validate_all_proxies(self, max_test: int = 20) -> List[str]:
        """Validate all proxies and return working ones"""
        working_proxies = []
        test_count = min(max_test, len(self.proxies))
        
        print(f"🔍 Validating {test_count} proxies...")
        
        for i, proxy in enumerate(self.proxies[:test_count]):
            print(f"   Testing proxy {i+1}/{test_count}...", end=' ')
            if self.validate_proxy(proxy):
                working_proxies.append(proxy)
                print("✅ Working")
            else:
                print("❌ Failed")
            
            time.sleep(0.5)  # Be polite
        
        self.proxies = working_proxies
        print(f"🎯 {len(working_proxies)} working proxies remaining")
        return working_proxies
    
    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get random proxy"""
        if not self.proxies:
            return None
        
        proxy = random.choice(self.proxies)
        return {
            'http': f"http://{proxy}",
            'https': f"https://{proxy}"
        }
    
    def get_proxy_count(self) -> int:
        """Get number of available proxies"""
        return len(self.proxies)
    
    def clear_proxies(self):
        """Clear all proxies"""
        self.proxies = []
        self.current_index = 0