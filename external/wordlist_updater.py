import requests
import os
from typing import List

class WordlistUpdater:
    def __init__(self):
        self.wordlist_sources = {
            'common_paths': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt',
            'big_wordlist': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/big.txt',
            'api_endpoints': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/api/api-endpoints.txt',
        }
        self.local_dir = "resources/data"
    
    def update_all_wordlists(self):
        """Update semua wordlists dari GitHub"""
        print("🔄 Updating wordlists from GitHub...")
        
        for name, url in self.wordlist_sources.items():
            self.download_wordlist(name, url)
    
    def download_wordlist(self, name: str, url: str):
        """Download wordlist tertentu"""
        local_path = os.path.join(self.local_dir, f"{name}.txt")
        
        try:
            print(f"📥 Downloading {name}...")
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ Updated: {name}")
            else:
                print(f"❌ Failed to download {name}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error downloading {name}: {e}")
    
    def load_wordlist(self, name: str) -> List[str]:
        """Load wordlist dari file local"""
        local_path = os.path.join(self.local_dir, f"{name}.txt")
        
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        
        return []