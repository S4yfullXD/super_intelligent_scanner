#!/usr/bin/env python3
"""
Enhanced Configuration Loader dengan Validation & Color Integration
Advanced configuration system dengan comprehensive error handling
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import our color system
from .colors import term, success, error, warning, info, debug

class ConfigLoader:
    """Advanced configuration loader dengan validation & smart defaults"""
    
    # Comprehensive default configuration
    DEFAULT_CONFIG = {
        'scanning': {
            'max_workers': 10,
            'timeout': 15,
            'max_retries': 3,
            'rate_limit_delay': 1.0,
            'max_paths_per_scan': 1000,
            'concurrent_requests': 5,
            'respect_robots_txt': False
        },
        'evasion': {
            'rotate_user_agents': True,
            'use_proxies': False,
            'random_delays': True,
            'stealth_mode': True,
            'delay_min': 2.0,
            'delay_max': 5.0,
            'max_redirects': 5,
            'verify_ssl': False
        },
        'intelligence': {
            'enable_ml': False,
            'enable_nlp': True,
            'enable_vision': False,
            'adaptive_learning': True,
            'pattern_recognition': True,
            'risk_assessment': True,
            'confidence_threshold': 0.7
        },
        'discovery': {
            'max_crawl_pages': 15,
            'crawl_depth': 3,
            'follow_links': True,
            'extract_js_endpoints': True,
            'analyze_sourcemaps': True,
            'quantum_fuzzing': True
        },
        'resources': {
            'auto_download': True,
            'update_interval_days': 7,
            'github_backup': True,
            'local_cache': True,
            'cache_expiry_hours': 24
        },
        'output': {
            'organized_saving': True,
            'generate_reports': True,
            'save_full_content': True,
            'compress_output': False,
            'log_level': 'INFO',
            'max_file_size_mb': 10
        },
        'security': {
            'max_request_size': 10485760,  # 10MB
            'blacklisted_paths': ['/etc/passwd', '/etc/shadow', '/proc/'],
            'sensitive_keywords': ['password', 'secret', 'key', 'token'],
            'enable_sandbox': False
        }
    }
    
    # Configuration validation rules
    VALIDATION_RULES = {
        'scanning.max_workers': {'type': int, 'min': 1, 'max': 50},
        'scanning.timeout': {'type': int, 'min': 5, 'max': 60},
        'scanning.max_retries': {'type': int, 'min': 1, 'max': 10},
        'scanning.rate_limit_delay': {'type': (int, float), 'min': 0.1, 'max': 10.0},
        'evasion.delay_min': {'type': (int, float), 'min': 0.5, 'max': 30.0},
        'evasion.delay_max': {'type': (int, float), 'min': 1.0, 'max': 60.0},
        'output.max_file_size_mb': {'type': int, 'min': 1, 'max': 100},
        'intelligence.confidence_threshold': {'type': float, 'min': 0.1, 'max': 1.0}
    }
    
    @staticmethod
    def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
        """
        Load configuration dengan comprehensive validation & error handling
        
        Args:
            config_path: Path ke configuration file
            
        Returns:
            Validated configuration dictionary
        """
        print(info("Loading configuration..."))
        
        # Check jika config file exists
        if not os.path.exists(config_path):
            print(warning(f"Config file not found: {config_path}"))
            print(info("Using comprehensive default configuration"))
            return ConfigLoader.DEFAULT_CONFIG.copy()
        
        try:
            # Load user configuration
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f) or {}
            
            print(success(f"Configuration loaded from: {config_path}"))
            
            # Deep merge dengan defaults
            final_config = ConfigLoader._deep_merge(
                ConfigLoader.DEFAULT_CONFIG.copy(), 
                user_config
            )
            
            # Validate configuration
            validation_errors = ConfigLoader._validate_config(final_config)
            
            if validation_errors:
                print(warning(f"Configuration validation issues found:"))
                for error_msg in validation_errors:
                    print(f"  ⚠️  {error_msg}")
                print(info("Using default values for invalid settings"))
            else:
                print(success("Configuration validation passed!"))
            
            # Print configuration summary
            ConfigLoader._print_config_summary(final_config)
            
            return final_config
            
        except yaml.YAMLError as e:
            print(error(f"YAML parsing error in {config_path}: {e}"))
            print(warning("Using default configuration due to YAML error"))
            return ConfigLoader.DEFAULT_CONFIG.copy()
            
        except Exception as e:
            print(error(f"Unexpected error loading config: {e}"))
            print(warning("Using default configuration"))
            return ConfigLoader.DEFAULT_CONFIG.copy()
    
    @staticmethod
    def _deep_merge(base: Dict, update: Dict) -> Dict:
        """Deep merge two dictionaries dengan preservation of structure"""
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and 
                isinstance(result[key], dict) and 
                isinstance(value, dict)):
                # Recursive merge untuk nested dictionaries
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                # Replace atau add value
                result[key] = value
        
        return result
    
    @staticmethod
    def _validate_config(config: Dict) -> List[str]:
        """Validate configuration values"""
        errors = []
        
        for key_path, rules in ConfigLoader.VALIDATION_RULES.items():
            try:
                # Get value dari nested path
                value = ConfigLoader._get_nested_value(config, key_path)
                if value is None:
                    continue  # Skip jika key tidak ada
                
                # Type validation
                expected_types = rules['type']
                if not isinstance(expected_types, tuple):
                    expected_types = (expected_types,)
                
                if not isinstance(value, expected_types):
                    errors.append(f"{key_path}: Expected type {expected_types}, got {type(value).__name__}")
                    continue
                
                # Range validation
                if 'min' in rules and value < rules['min']:
                    errors.append(f"{key_path}: Value {value} below minimum {rules['min']}")
                
                if 'max' in rules and value > rules['max']:
                    errors.append(f"{key_path}: Value {value} above maximum {rules['max']}")
                    
            except Exception as e:
                errors.append(f"{key_path}: Validation error - {e}")
        
        return errors
    
    @staticmethod
    def _get_nested_value(config: Dict, key_path: str) -> Any:
        """Get value dari nested dictionary path"""
        keys = key_path.split('.')
        value = config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
    
    @staticmethod
    def _print_config_summary(config: Dict):
        """Print configuration summary"""
        print(info("Configuration Summary:"))
        
        summary = [
            f"  🔧 Scanning: {config['scanning']['max_workers']} workers, "
            f"{config['scanning']['timeout']}s timeout",
            
            f"  🛡️  Evasion: {'Stealth' if config['evasion']['stealth_mode'] else 'Normal'} mode, "
            f"{'Random delays' if config['evasion']['random_delays'] else 'No delays'}",
            
            f"  🤖 Intelligence: "
            f"{'ML' if config['intelligence']['enable_ml'] else 'No-ML'}, "
            f"{'NLP' if config['intelligence']['enable_nlp'] else 'No-NLP'}, "
            f"{'Vision' if config['intelligence']['enable_vision'] else 'No-Vision'}",
            
            f"  📁 Output: {'Organized' if config['output']['organized_saving'] else 'Flat'}, "
            f"{'Reports' if config['output']['generate_reports'] else 'No-Reports'}"
        ]
        
        for line in summary:
            print(line)
    
    @staticmethod
    def create_default_config(config_path: str = "config.yaml") -> bool:
        """
        Create default configuration file
        
        Args:
            config_path: Path dimana config file akan dibuat
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            # Check jika file sudah ada
            if os.path.exists(config_path):
                print(warning(f"Config file already exists: {config_path}"))
                overwrite = input("Overwrite? (y/N): ").strip().lower()
                if overwrite not in ['y', 'yes']:
                    print(info("Config creation cancelled"))
                    return False
            
            # Create directory jika perlu
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Write default config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(ConfigLoader.DEFAULT_CONFIG, f, 
                         default_flow_style=False, 
                         indent=2,
                         allow_unicode=True)
            
            print(success(f"Default configuration created: {config_path}"))
            print(info("You can now customize the configuration file"))
            return True
            
        except Exception as e:
            print(error(f"Failed to create config file: {e}"))
            return False
    
    @staticmethod
    def get_config_value(config: Dict, key_path: str, default: Any = None) -> Any:
        """
        Safely get configuration value dari nested path
        
        Args:
            config: Configuration dictionary
            key_path: Dot-separated path (e.g., 'scanning.max_workers')
            default: Default value jika key tidak ditemukan
            
        Returns:
            Configuration value atau default
        """
        value = ConfigLoader._get_nested_value(config, key_path)
        return value if value is not None else default
    
    @staticmethod
    def update_config(config: Dict, updates: Dict) -> Dict:
        """
        Update configuration dengan new values
        
        Args:
            config: Current configuration
            updates: Dictionary dengan updates
            
        Returns:
            Updated configuration
        """
        return ConfigLoader._deep_merge(config.copy(), updates)

# Convenience function
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Convenience function untuk quick config loading"""
    return ConfigLoader.load_config(config_path)

def test_config_loader():
    """Test the enhanced configuration loader"""
    print(term.styles.banner("Testing Configuration Loader"))
    
    # Test 1: Load default config
    print(info("Test 1: Loading default configuration..."))
    config = ConfigLoader.load_config("non_existent_config.yaml")
    print(success("Default config loaded successfully"))
    
    # Test 2: Validate config values
    print(info("Test 2: Testing config validation..."))
    test_config = config.copy()
    test_config['scanning']['max_workers'] = 100  # Invalid value
    test_config['scanning']['timeout'] = "invalid"  # Wrong type
    
    errors = ConfigLoader._validate_config(test_config)
    if errors:
        print(warning("Validation errors detected (expected):"))
        for error in errors:
            print(f"  {error}")
    
    # Test 3: Test config value retrieval
    print(info("Test 3: Testing config value retrieval..."))
    workers = ConfigLoader.get_config_value(config, 'scanning.max_workers', 5)
    nonexistent = ConfigLoader.get_config_value(config, 'nonexistent.key', 'default')
    
    print(success(f"Max workers: {workers}"))
    print(success(f"Nonexistent key with default: {nonexistent}"))
    
    print(success("Configuration loader test completed!"))

if __name__ == "__main__":
    test_config_loader()