import requests
import random
from typing import List, Dict

class ProxySources:
    def __init__(self):
        self.sources = [
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt',
        ]
    
    def fetch_proxies(self) -> List[str]:
        """Fetch proxies dari berbagai sources"""
        all_proxies = []
        
        for source in self.sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                    all_proxies.extend(proxies)
                    print(f"✅ Got {len(proxies)} proxies from {source.split('/')[-1]}")
            except Exception as e:
                print(f"❌ Failed to fetch from {source}: {e}")
        
        return list(set(all_proxies))  # Remove duplicates
    
    def get_random_proxy(self) -> Dict[str, str]:
        """Get random proxy dari list"""
        proxies = self.fetch_proxies()
        if not proxies:
            return {}
        
        proxy = random.choice(proxies)
        return {
            'http': f"http://{proxy}",
            'https': f"https://{proxy}"
        }