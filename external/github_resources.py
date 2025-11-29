import requests
import os
import json
from typing import List, Dict

class GitHubResourceManager:
    def __init__(self):
        self.resource_urls = {
            'user_agents': 'https://raw.githubusercontent.com/monperrus/crawler-user-agents/master/crawler-user-agents.json',
            'common_paths': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt',
        }
        self.local_dir = "resources/data"
        
    def download_resources(self, force_update: bool = False):
        """Download resources from GitHub"""
        print("🌐 Downloading resources from GitHub...")
        
        for resource_name, url in self.resource_urls.items():
            local_path = os.path.join(self.local_dir, f"{resource_name}.json")
            
            if not os.path.exists(local_path) or force_update:
                try:
                    print(f"   📥 Downloading {resource_name}...")
                    response = requests.get(url, timeout=30)
                    
                    if response.status_code == 200:
                        # Process based on resource type
                        if resource_name == 'user_agents':
                            processed_data = self.process_user_agents(response.json())
                        else:
                            processed_data = response.text
                        
                        self.save_resource(local_path, processed_data)
                        print(f"   ✅ Downloaded: {resource_name}")
                    else:
                        print(f"   ❌ Failed: {resource_name} - Status {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {resource_name} - {e}")
            else:
                print(f"   ✅ Already exists: {resource_name}")
    
    def process_user_agents(self, raw_data: List[Dict]) -> List[str]:
        """Process user agents data"""
        user_agents = []
        for item in raw_data:
            if 'pattern' in item:
                user_agents.append(item['pattern'])
        return user_agents[:50]  # Limit to 50 for performance
    
    def save_resource(self, path: str, data):
        """Save resource to file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        if isinstance(data, list):
            with open(path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(data)
    
    def load_user_agents(self) -> List[str]:
        """Load user agents from local file"""
        ua_path = os.path.join(self.local_dir, "user_agents.json")
        fallback_ua = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        ]
        
        if os.path.exists(ua_path):
            try:
                with open(ua_path, 'r') as f:
                    return json.load(f)
            except:
                return fallback_ua
        return fallback_ua
    
    def load_common_paths(self) -> List[str]:
        """Load common paths from local file"""
        paths_path = os.path.join(self.local_dir, "common_paths.json")
        default_paths = [
            '/api/', '/admin/', '/static/', '/assets/', '/config.json',
            '/.env', '/package.json', '/composer.json'
        ]
        
        if os.path.exists(paths_path):
            try:
                with open(paths_path, 'r') as f:
                    data = json.load(f)
                    # If it's a list of paths, return it
                    if isinstance(data, list):
                        return data[:100]  # Limit to 100 paths
                    else:
                        return default_paths
            except:
                return default_paths
        return default_paths