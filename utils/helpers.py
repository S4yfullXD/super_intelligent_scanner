#!/usr/bin/env python3
"""
Enhanced Helpers Module 
Dengan integrated colors system dan improvements
"""

import os
import sys
import time
import random
import string
from typing import List, Dict, Any
from urllib.parse import urlparse

# Import our centralized color system
from .colors import term, success, error, warning, info, debug

# Dependency availability checking
def check_dependencies():
    """Check availability of optional dependencies dengan styling"""
    missing_deps = []
    optional_features = {}
    
    # Check ML dependencies
    try:
        import sklearn
        optional_features['ml'] = True
    except ImportError:
        optional_features['ml'] = False
        missing_deps.append('scikit-learn')
    
    # Check NLP dependencies
    try:
        import nltk
        optional_features['nlp'] = True
    except ImportError:
        optional_features['nlp'] = False
        missing_deps.append('nltk')
    
    # Check Computer Vision dependencies
    try:
        import cv2
        optional_features['vision'] = True
    except ImportError:
        optional_features['vision'] = False
        missing_deps.append('opencv-python')
    
    # Check async dependencies
    try:
        import aiohttp
        optional_features['async'] = True
    except ImportError:
        optional_features['async'] = False
        missing_deps.append('aiohttp')
    
    # Print results dengan styling
    if missing_deps:
        print(warning("Optional dependencies missing (some features disabled):"))
        for dep in missing_deps:
            print(f"   {term.icons.WARNING} {dep}")
        print(info("Install with: pip install " + " ".join(missing_deps)))
    else:
        print(success("All optional dependencies available!"))
    
    return optional_features

def validate_url(url: str) -> bool:
    """Validate URL format dengan better checking"""
    if not url or not isinstance(url, str):
        return False
        
    try:
        result = urlparse(url)
        has_scheme = result.scheme in ['http', 'https']
        has_netloc = bool(result.netloc)
        has_valid_chars = all(c in string.printable for c in url)
        
        return all([has_scheme, has_netloc, has_valid_chars])
    except Exception:
        return False

def generate_random_string(length: int = 8) -> str:
    """Generate random string untuk various uses"""
    if length <= 0:
        return ""
    chars = string.ascii_lowercase + string.digits + string.ascii_uppercase
    return ''.join(random.choices(chars, k=length))

def get_file_size(filepath: str) -> int:
    """Get file size in bytes dengan error handling"""
    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            return os.path.getsize(filepath)
        return 0
    except (OSError, TypeError):
        return 0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if not isinstance(size_bytes, int) or size_bytes < 0:
        return "0B"
    
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f}{size_names[i]}"

def create_directory(path: str) -> bool:
    """Create directory if it doesn't exist dengan better error handling"""
    if not path or not isinstance(path, str):
        return False
        
    try:
        os.makedirs(path, exist_ok=True)
        # Verify directory was created
        if os.path.exists(path) and os.path.isdir(path):
            return True
        return False
    except Exception as e:
        print(error(f"Error creating directory {path}: {e}"))
        return False

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe saving dengan comprehensive cleaning"""
    if not filename:
        return "unknown_file"
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*\''
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Limit length (255 chars max for most filesystems)
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:250-len(ext)] + "_truncated" + ext
    
    # Ensure filename is not empty
    if not filename:
        filename = f"file_{generate_random_string(8)}"
    
    return filename

def print_banner():
    """Print application banner dengan styling keren"""
    banner = term.styles.banner(f"""
{term.icons.BANNER} SUPER INTELLIGENT SCANNER
==================================================
   Advanced Web Security Scanner
   with AI-Powered Intelligence
   
{term.icons.SCAN} Smart Discovery • {term.icons.INTELLIGENCE} Machine Learning  
{term.icons.STEALTH} Stealth Technology • {term.icons.REPORT} Advanced Reporting
==================================================
    """)
    print(banner)

def calculate_scan_duration(start_time: float) -> str:
    """Calculate and format scan duration dengan precision"""
    if not isinstance(start_time, (int, float)) or start_time <= 0:
        return "0s"
    
    duration = time.time() - start_time
    
    if duration < 1:
        return f"{duration*1000:.0f}ms"
    elif duration < 60:
        return f"{duration:.1f}s"
    elif duration < 3600:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        return f"{minutes}m {seconds}s"
    else:
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        return f"{hours}h {minutes}m"

def is_termux_environment() -> bool:
    """Check if running in Termux environment"""
    termux_paths = [
        '/data/data/com.termux/files/usr',
        '/data/data/com.termux/files/home',
        '/usr/bin/termux-info'
    ]
    return any(os.path.exists(path) for path in termux_paths)

def get_resource_path(relative_path: str) -> str:
    """Get absolute path for resource file dengan cross-platform support"""
    if not relative_path:
        return ""
        
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            base_path = sys._MEIPASS
        else:
            # Normal execution - cari root project directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(current_dir)  # Naik ke parent directory
        
        full_path = os.path.join(base_path, relative_path)
        return os.path.normpath(full_path)
        
    except Exception:
        return relative_path  # Fallback ke path relative

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries dengan recursive merge untuk nested dicts"""
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2 or dict1 or {}
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if (key in result and 
            isinstance(result[key], dict) and 
            isinstance(value, dict)):
            # Recursive merge untuk nested dictionaries
            result[key] = merge_dicts(result[key], value)
        else:
            # Replace atau add value
            result[key] = value
    
    return result

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks dengan validation"""
    if not lst or not isinstance(lst, list):
        return []
    
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        chunk_size = 1
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def progress_bar(iteration: int, total: int, prefix: str = "", length: int = 30) -> str:
    """Create progress bar string dengan styling"""
    if total <= 0:
        return f"{prefix} |{'░' * length}| 0% (0/0)"
    
    iteration = max(0, min(iteration, total))  # Clamp value
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    
    bar = '█' * filled_length + '░' * (length - filled_length)
    return f"{term.colors.BRIGHT_CYAN}{prefix} |{bar}| {percent}% ({iteration}/{total}){term.colors.RESET}"

def print_scan_status(current: int, total: int, found: int, errors: int):
    """Print real-time scan status dengan formatting bagus"""
    status = (
        f"{term.colors.BRIGHT_BLUE}Scan Progress: "
        f"{term.colors.BRIGHT_CYAN}{current}/{total} "
        f"{term.colors.BRIGHT_GREEN}Found: {found} "
        f"{term.colors.BRIGHT_RED}Errors: {errors}"
        f"{term.colors.RESET}"
    )
    print(f"\r{status}", end='', flush=True)

def cleanup_old_scans(max_age_hours: int = 24):
    """Clean up old scan results to save space"""
    try:
        scans_dir = get_resource_path("results")
        if not os.path.exists(scans_dir):
            return
            
        current_time = time.time()
        max_age = max_age_hours * 3600
        
        for item in os.listdir(scans_dir):
            item_path = os.path.join(scans_dir, item)
            if os.path.isdir(item_path):
                # Check directory age
                dir_time = os.path.getctime(item_path)
                if current_time - dir_time > max_age:
                    import shutil
                    shutil.rmtree(item_path)
                    print(info(f"Cleaned up old scan: {item}"))
                    
    except Exception as e:
        print(debug(f"Cleanup skipped: {e}"))

# Test functions untuk development
def _test_helpers():
    """Test semua helper functions"""
    print(success("Testing helper functions..."))
    
    # Test URL validation
    test_urls = [
        "https://example.com",
        "http://localhost:3000", 
        "invalid-url",
        ""
    ]
    
    for url in test_urls:
        valid = validate_url(url)
        status = success("VALID") if valid else error("INVALID")
        print(f"URL: {url} -> {status}")
    
    # Test file size formatting
    test_sizes = [0, 1024, 1048576, 1073741824]
    for size in test_sizes:
        print(f"Size {size} -> {format_file_size(size)}")
    
    print(success("Helper functions test completed!"))

if __name__ == "__main__":
    _test_helpers()