#!/usr/bin/env python3
"""
Enhanced File Organizer dengan Color Integration & Smart Categorization
Advanced file handling dengan intelligent validation & organization
"""

import os
import re
import time
from urllib.parse import urlparse
from typing import Tuple, Dict, List

# Import our color system
from .colors import term, success, error, warning, info, debug

def generate_folder_name_from_url(url: str) -> str:
    """Generate meaningful folder name from URL dengan enhanced logic"""
    try:
        parsed = urlparse(url)
        hostname = parsed.netloc
        
        if not hostname:
            return f"scan_{int(time.time())}"
        
        # Enhanced domain parsing logic
        parts = hostname.split('.')
        
        # Case 1: Multiple subdomains like "api.zenzxz.my.id"
        if len(parts) >= 3:
            common_subdomains = ['api', 'www', 'app', 'admin', 'test', 'staging', 'dev', 'mobile']
            if parts[0] in common_subdomains:
                folder_name = f"{parts[0]}.{parts[1]}"
            else:
                folder_name = parts[0]  # Use first subdomain
        
        # Case 2: Direct domain like "xskycodes-apis.vercel.app"
        else:
            main_part = parts[0]
            # Remove common prefixes/suffixes
            for prefix in ['api-', 'app-', 'www-', 'admin-']:
                if main_part.startswith(prefix):
                    main_part = main_part[len(prefix):]
                    break
            
            folder_name = main_part.split('-')[0] if '-' in main_part else main_part
        
        # Clean invalid filename characters
        folder_name = re.sub(r'[^a-zA-Z0-9._-]', '_', folder_name)
        
        if not folder_name or folder_name == '_':
            folder_name = f"scan_{int(time.time())}"
            
        return folder_name
        
    except Exception as e:
        debug(f"Folder name generation failed: {e}")
        return f"scan_{int(time.time())}"

def setup_output_directory(target_url: str) -> str:
    """Setup comprehensive output directory structure"""
    base_output_dir = "results"
    folder_name = generate_folder_name_from_url(target_url)
    timestamp = int(time.time())
    
    final_dir_name = f"{folder_name}_{timestamp}"
    full_output_path = os.path.join(base_output_dir, final_dir_name)
    
    # Create main directory
    os.makedirs(full_output_path, exist_ok=True)
    
    # Comprehensive organized subdirectories
    subdirs = [
        'javascript', 'api_endpoints', 'config_data', 'stylesheets',
        'html_pages', 'python_code', 'misc', 'rejected', 'logs',
        'static_js', 'assets_js', 'images', 'fonts', 'media',
        'backup_files', 'source_maps', 'documentation'
    ]
    
    for subdir in subdirs:
        os.makedirs(os.path.join(full_output_path, subdir), exist_ok=True)
    
    print(success(f"📁 Output directory: {full_output_path}"))
    return full_output_path

def detect_content_language(content: str) -> str:
    """Enhanced programming language detection dengan advanced patterns"""
    if not content or len(content.strip()) < 10:
        return 'unknown'
    
    content_sample = content[:2000].lower()
    
    # Enhanced JavaScript patterns
    js_patterns = [
        r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=',
        r'var\s+\w+\s*=', r'console\.log', r'document\.', r'window\.',
        r'\.addEventListener', r'export\s+default', r'import\s+.+\s+from',
        r'=>\s*{', r'`\$\{.*\}`', r'\.then\(', r'\.catch\(', r'async\s+function',
        r'await\s+\w+', r'React\.', r'Vue\.', r'Angular\.'
    ]
    
    # Enhanced HTML patterns
    html_patterns = [
        r'<!doctype html>', r'<html', r'<head', r'<body', r'<div',
        r'<script', r'<style', r'<meta', r'<title', r'<link rel=',
        r'<img src=', r'<a href=', r'<form', r'<input', r'<button'
    ]
    
    # Enhanced JSON patterns
    json_patterns = [
        r'^{\s*"[^"]*"\s*:', r'\[[^]]*\]', r'"\w+"\s*:\s*"[^"]*"',
        r'"\w+"\s*:\s*\d+', r'"\w+"\s*:\s*(true|false|null)'
    ]
    
    # Enhanced Python patterns
    python_patterns = [
        r'def\s+\w+\s*\(', r'import\s+\w+', r'from\s+\w+\s+import', 
        r'class\s+\w+', r'@\w+', r'self\.\w+', r'__\w+__',
        r'print\(', r'if\s+__name__', r'except\s+\w+:'
    ]
    
    # Enhanced CSS patterns
    css_patterns = [
        r'\{[^}]*\}', r'[a-zA-Z-]+\s*:\s*[^;]+;', r'@media',
        r'@import', r'@keyframes', r'\.\w+\s*{', r'#\w+\s*{'
    ]
    
    # XML patterns - SIMPLIFIED & SAFE
    xml_patterns = [
        r'<\?xml',
        r'<[a-zA-Z]+>',
        r'</[a-zA-Z]+>',
        r'<[a-zA-Z]+ [^>]*>',
        r'<!\[CDATA\['
    ]
    
    # Scoring system dengan weights
    scores = {
        'javascript': sum(2 for pattern in js_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
        'html': sum(2 for pattern in html_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
        'json': sum(3 for pattern in json_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
        'python': sum(2 for pattern in python_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
        'css': sum(2 for pattern in css_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
        'xml': sum(2 for pattern in xml_patterns if re.search(pattern, content_sample, re.IGNORECASE)),
    }
    
    # Bonus scores untuk specific characteristics
    if content_sample.count('{') > content_sample.count('<') and 'css' not in content_sample:
        scores['json'] += 3
    
    if content_sample.count('</') > 2:
        scores['html'] += 2
        scores['xml'] += 1
    
    if 'react' in content_sample or 'vue' in content_sample or 'angular' in content_sample:
        scores['javascript'] += 2
    
    # Return the highest scoring language
    if not any(scores.values()):
        return 'text'
    
    detected = max(scores.items(), key=lambda x: x[1])
    return detected[0] if detected[1] > 2 else 'text'  # Minimum threshold

def validate_content_type(path: str, content: str, content_type: str) -> Tuple[bool, str, bool]:
    """
    Enhanced content validation dengan intelligent matching
    Returns: (is_valid, detected_language, should_save)
    """
    detected_lang = detect_content_language(content)
    
    # Enhanced file extension mapping
    ext = os.path.splitext(path)[1].lower()
    ext_to_lang = {
        '.js': 'javascript', '.jsx': 'javascript', '.ts': 'javascript', '.tsx': 'javascript', '.mjs': 'javascript',
        '.html': 'html', '.htm': 'html', '.xhtml': 'html',
        '.json': 'json', '.jsonld': 'json',
        '.py': 'python', '.pyc': 'python', '.pyo': 'python',
        '.css': 'css', '.scss': 'css', '.sass': 'css', '.less': 'css',
        '.xml': 'xml', '.rss': 'xml', '.atom': 'xml',
        '.txt': 'text', '.md': 'text', '.log': 'text'
    }
    
    expected_lang = ext_to_lang.get(ext, 'unknown')
    
    # Enhanced validation logic
    if expected_lang != 'unknown' and expected_lang != detected_lang:
        print(warning(f"TYPE MISMATCH: {path}"))
        print(debug(f"   Expected: {expected_lang}, Detected: {detected_lang}"))
        
        # Special cases handling dengan enhanced logic
        if detected_lang == 'html' and expected_lang == 'javascript':
            return False, detected_lang, False  # Don't save HTML as JS!
        elif detected_lang == 'json' and expected_lang == 'javascript':
            return True, 'json', True  # JSON can be valid JS
        elif detected_lang == 'text' and expected_lang in ['javascript', 'html', 'json']:
            return False, detected_lang, False  # Plain text as code? No!
        elif detected_lang == 'xml' and expected_lang == 'html':
            return True, 'xml', True  # XML can be similar to HTML
        elif detected_lang == 'css' and expected_lang == 'text':
            return True, 'css', True  # CSS might be detected as text
        else:
            return False, detected_lang, False
    
    return True, detected_lang, True

def intelligent_save(path: str, content: str, content_type: str, output_dir: str) -> bool:
    """Enhanced content saving dengan intelligent validation & organization"""
    # Validate content type
    is_valid, detected_lang, should_save = validate_content_type(path, content, content_type)
    
    if not should_save:
        print(error(f"REJECTED: {path} - Type mismatch ({detected_lang})"))
        
        # Save rejected files for analysis
        try:
            rejected_dir = os.path.join(output_dir, 'rejected')
            safe_filename = sanitize_filename(path, '.txt')
            rejected_path = os.path.join(rejected_dir, safe_filename)
            
            with open(rejected_path, 'w', encoding='utf-8') as f:
                f.write(f"Original path: {path}\n")
                f.write(f"Detected language: {detected_lang}\n")
                f.write(f"Content type: {content_type}\n")
                f.write(f"Content length: {len(content)}\n")
                f.write("\n" + "="*50 + "\n")
                f.write(content[:1000])  # First 1000 chars
            
            debug(f"Rejected content saved to: {rejected_path}")
        except Exception as e:
            debug(f"Failed to save rejected content: {e}")
        
        return False
    
    # Enhanced file extension mapping
    ext_map = {
        'javascript': '.js',
        'html': '.html', 
        'json': '.json',
        'python': '.py',
        'css': '.css',
        'xml': '.xml',
        'text': '.txt'
    }
    
    original_ext = os.path.splitext(path)[1].lower()
    correct_ext = ext_map.get(detected_lang, '.txt')
    
    # Enhanced extension preservation logic
    ext_preservation_rules = {
        'javascript': ['.js', '.jsx', '.ts', '.tsx', '.mjs'],
        'html': ['.html', '.htm', '.xhtml'],
        'json': ['.json', '.jsonld'],
        'python': ['.py', '.pyc', '.pyo'],
        'css': ['.css', '.scss', '.sass', '.less'],
        'xml': ['.xml', '.rss', '.atom']
    }
    
    preserve_ext = False
    for lang, exts in ext_preservation_rules.items():
        if detected_lang == lang and original_ext in exts:
            correct_ext = original_ext
            preserve_ext = True
            break
    
    # Sanitize filename
    safe_filename = sanitize_filename(path, correct_ext)
    
    # Determine category dengan enhanced logic
    category = get_content_category(detected_lang, path)
    
    # Save with correct structure
    save_path = os.path.join(output_dir, category, safe_filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        file_size = len(content)
        size_str = f"{file_size} bytes" if file_size < 1024 else f"{file_size/1024:.1f} KB"
        
        print(success(f"💾 SAVED: {safe_filename} → {category}/ ({detected_lang}, {size_str})"))
        
        # Log detailed save information
        if preserve_ext:
            debug(f"   Preserved original extension: {original_ext}")
        
        return True
        
    except Exception as e:
        print(error(f"SAVE ERROR {path}: {e}"))
        return False

def sanitize_filename(path: str, extension: str) -> str:
    """Enhanced filename sanitization"""
    # Extract filename from path
    filename = path.strip('/').replace('/', '_')
    if not filename or filename == '_':
        filename = 'index'
    
    # Remove invalid characters dengan enhanced pattern
    filename = re.sub(r'[^\w\-_.]', '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores and dots
    filename = filename.strip('_.')
    
    # Ensure it has proper extension
    if not filename.endswith(extension):
        filename += extension
    
    # Limit filename length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + '_trunc' + ext
    
    return filename

def get_content_category(detected_lang: str, path: str) -> str:
    """Enhanced category determination dengan path analysis"""
    path_lower = path.lower()
    
    # API endpoints (priority)
    if any(api_indicator in path_lower for api_indicator in 
           ['/api/', '/v1/', '/v2/', '/v3/', '/graphql', '/rest/', '/json/']):
        return 'api_endpoints'
    
    # JavaScript files dengan enhanced categorization
    elif detected_lang == 'javascript':
        if any(static_indicator in path_lower for static_indicator in 
               ['/static/', '/_next/', '/build/', '/dist/']):
            return 'static_js'
        elif any(asset_indicator in path_lower for asset_indicator in 
                 ['/assets/', '/js/', '/scripts/']):
            return 'assets_js'
        elif any(app_indicator in path_lower for app_indicator in 
                 ['/app/', '/src/', '/components/']):
            return 'javascript'
        else:
            return 'javascript'
    
    # HTML pages
    elif detected_lang == 'html':
        return 'html_pages'
    
    # CSS/stylesheet files
    elif detected_lang == 'css':
        return 'stylesheets'
    
    # JSON config/data files
    elif detected_lang == 'json':
        if any(config_indicator in path_lower for config_indicator in 
               ['config', 'setting', 'env', 'package']):
            return 'config_data'
        else:
            return 'api_endpoints'  # JSON APIs
    
    # Python code
    elif detected_lang == 'python':
        return 'python_code'
    
    # XML files
    elif detected_lang == 'xml':
        return 'documentation'
    
    # Default categories
    else:
        if any(image_indicator in path_lower for image_indicator in 
               ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico']):
            return 'images'
        elif any(font_indicator in path_lower for font_indicator in 
                 ['.woff', '.woff2', '.ttf', '.otf']):
            return 'fonts'
        elif any(media_indicator in path_lower for media_indicator in 
                 ['.mp4', '.mp3', '.avi', '.mov']):
            return 'media'
        else:
            return 'misc'

# Utility functions
def get_file_stats(output_dir: str) -> Dict[str, int]:
    """Get statistics tentang saved files"""
    stats = {}
    try:
        for category in os.listdir(output_dir):
            category_path = os.path.join(output_dir, category)
            if os.path.isdir(category_path):
                files = [f for f in os.listdir(category_path) if os.path.isfile(os.path.join(category_path, f))]
                stats[category] = len(files)
        return stats
    except Exception as e:
        debug(f"File stats collection failed: {e}")
        return {}

def print_save_summary(output_dir: str):
    """Print summary of saved files"""
    stats = get_file_stats(output_dir)
    if stats:
        print(info("📊 File Save Summary:"))
        for category, count in sorted(stats.items()):
            print(f"   {category}: {count} files")
    else:
        print(warning("No file statistics available"))

def test_file_organizer():
    """Test the enhanced file organizer"""
    print(term.styles.banner("Testing Enhanced File Organizer"))
    
    # Test URL parsing
    test_urls = [
        "https://api.zenzxz.my.id/v1/users",
        "https://xskycodes-apis.vercel.app",
        "https://admin.test.example.com",
        "https://example.com"
    ]
    
    print(info("Testing URL to folder name conversion:"))
    for url in test_urls:
        folder_name = generate_folder_name_from_url(url)
        print(success(f"  {url} → {folder_name}"))
    
    # Test content detection
    test_contents = [
        ("function test() { return 'hello'; }", "JavaScript"),
        ("<html><body>Hello</body></html>", "HTML"),
        ('{"name": "test", "value": 123}', "JSON"),
        ("def hello(): return 'world'", "Python"),
        (".test { color: red; }", "CSS")
    ]
    
    print(info("Testing content language detection:"))
    for content, expected in test_contents:
        detected = detect_content_language(content)
        status = success("✓") if detected in expected.lower() else error("✗")
        print(f"  {status} {expected}: {detected}")
    
    print(success("File organizer test completed!"))

if __name__ == "__main__":
    test_file_organizer()