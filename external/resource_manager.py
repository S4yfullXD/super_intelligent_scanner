import os
import json
from typing import Dict, List, Any

class ResourceManager:
    def __init__(self):
        self.resource_dir = "resources/data"
        self.loaded_resources = {}
    
    def load_resource(self, resource_name: str) -> Any:
        """Load resource from file"""
        if resource_name in self.loaded_resources:
            return self.loaded_resources[resource_name]
        
        file_path = os.path.join(self.resource_dir, f"{resource_name}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.loaded_resources[resource_name] = data
                    return data
            except Exception as e:
                print(f"❌ Error loading resource {resource_name}: {e}")
        
        return None
    
    def save_resource(self, resource_name: str, data: Any):
        """Save resource to file"""
        file_path = os.path.join(self.resource_dir, f"{resource_name}.json")
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.loaded_resources[resource_name] = data
            return True
        except Exception as e:
            print(f"❌ Error saving resource {resource_name}: {e}")
            return False
    
    def get_available_resources(self) -> List[str]:
        """Get list of available resources"""
        resources = []
        if os.path.exists(self.resource_dir):
            for file in os.listdir(self.resource_dir):
                if file.endswith('.json'):
                    resources.append(file[:-5])  # Remove .json extension
        return resources
    
    def clear_cache(self):
        """Clear resource cache"""
        self.loaded_resources.clear()