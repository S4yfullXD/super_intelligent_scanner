import re
import random
from typing import List, Set
from collections import Counter

class MLPredictor:
    def __init__(self):
        self.learned_patterns = {
            'api_patterns': set(),
            'static_patterns': set(),
            'config_patterns': set(),
            'admin_patterns': set()
        }
        self.path_frequency = Counter()
        
    def train_on_successful_paths(self, successful_paths: List[str]):
        """Train ML model on successful paths"""
        if not successful_paths:
            return
            
        print("🤖 Training ML model on successful paths...")
        
        for path in successful_paths:
            # Extract path components
            parts = self.extract_path_components(path)
            
            # Learn patterns based on path structure
            if '/api/' in path or path.startswith('/api'):
                self.learned_patterns['api_patterns'].update(parts)
            elif '/static/' in path or '/assets/' in path:
                self.learned_patterns['static_patterns'].update(parts)
            elif any(ext in path for ext in ['.json', '.config', '.env']):
                self.learned_patterns['config_patterns'].update(parts)
            elif any(keyword in path for keyword in ['admin', 'dashboard', 'login']):
                self.learned_patterns['admin_patterns'].update(parts)
            
            # Update frequency
            self.path_frequency.update(parts)
    
    def extract_path_components(self, path: str) -> List[str]:
        """Extract meaningful components from path"""
        components = []
        
        # Split by common separators
        parts = re.split(r'[/\-_.]', path)
        
        for part in parts:
            if part and len(part) > 2 and not part.isdigit():
                # Clean the component
                clean_part = re.sub(r'[^a-zA-Z0-9]', '', part)
                if len(clean_part) > 2:
                    components.append(clean_part.lower())
        
        return components
    
    def predict_new_paths(self, base_words: List[str], count: int = 50) -> List[str]:
        """Predict new paths based on learned patterns"""
        if not any(self.learned_patterns.values()):
            return self.fallback_prediction(base_words, count)
        
        predicted_paths = set()
        
        # Generate paths based on learned patterns
        for pattern_type, patterns in self.learned_patterns.items():
            if patterns:
                if pattern_type == 'api_patterns':
                    predicted_paths.update(self.generate_api_paths(patterns, base_words))
                elif pattern_type == 'static_patterns':
                    predicted_paths.update(self.generate_static_paths(patterns, base_words))
                elif pattern_type == 'config_patterns':
                    predicted_paths.update(self.generate_config_paths(patterns, base_words))
                elif pattern_type == 'admin_patterns':
                    predicted_paths.update(self.generate_admin_paths(patterns, base_words))
        
        # If not enough predictions, use fallback
        if len(predicted_paths) < count // 2:
            predicted_paths.update(self.fallback_prediction(base_words, count // 2))
        
        return list(predicted_paths)[:count]
    
    def generate_api_paths(self, patterns: Set[str], base_words: List[str]) -> List[str]:
        """Generate API paths"""
        paths = set()
        
        for pattern in list(patterns)[:10]:
            for word in base_words[:5]:
                paths.add(f"/api/v1/{word}")
                paths.add(f"/api/{pattern}/{word}")
                paths.add(f"/{word}/api/{pattern}")
                paths.add(f"/{pattern}/v1/{word}")
        
        return list(paths)
    
    def generate_static_paths(self, patterns: Set[str], base_words: List[str]) -> List[str]:
        """Generate static resource paths"""
        paths = set()
        
        for pattern in list(patterns)[:10]:
            for word in base_words[:5]:
                paths.add(f"/static/{pattern}/{word}.js")
                paths.add(f"/assets/{word}/{pattern}.css")
                paths.add(f"/public/{pattern}/{word}")
        
        return list(paths)
    
    def generate_config_paths(self, patterns: Set[str], base_words: List[str]) -> List[str]:
        """Generate configuration paths"""
        paths = set()
        
        extensions = ['.json', '.config', '.yml', '.yaml', '.env']
        for pattern in list(patterns)[:10]:
            for ext in extensions:
                paths.add(f"/config/{pattern}{ext}")
                paths.add(f"/{pattern}/settings{ext}")
        
        return list(paths)
    
    def generate_admin_paths(self, patterns: Set[str], base_words: List[str]) -> List[str]:
        """Generate admin paths"""
        paths = set()
        
        admin_keywords = ['admin', 'dashboard', 'panel', 'control', 'manage']
        for pattern in list(patterns)[:10]:
            for keyword in admin_keywords:
                paths.add(f"/{keyword}/{pattern}")
                paths.add(f"/{pattern}/{keyword}")
        
        return list(paths)
    
    def fallback_prediction(self, base_words: List[str], count: int) -> List[str]:
        """Fallback prediction when no patterns learned"""
        paths = set()
        
        common_prefixes = ['/api/', '/static/', '/assets/', '/admin/', '/config/']
        common_suffixes = ['.js', '.json', '.css', '.html', '.php']
        
        for word in base_words[:20]:
            for prefix in common_prefixes:
                paths.add(f"{prefix}{word}")
                for suffix in common_suffixes:
                    paths.add(f"{prefix}{word}{suffix}")
            
            # Add some variations
            paths.add(f"/{word}/api")
            paths.add(f"/v1/{word}")
            paths.add(f"/{word}/v1")
        
        return list(paths)[:count]