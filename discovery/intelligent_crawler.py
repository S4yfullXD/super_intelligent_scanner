#!/usr/bin/env python3
"""
Enhanced Intelligent Crawler dengan Color Integration & Advanced Discovery
Smart website crawling dengan comprehensive path discovery
"""

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
import time
from typing import List, Set, Dict, Any
from collections import deque

# Import our color system
from utils.colors import term, success, error, warning, info, debug

def intelligent_crawler(base_url: str, max_pages: int = 15, delay: float = 1.0) -> List[str]:
    """
    Enhanced intelligent crawler untuk discover website structure
    
    Args:
        base_url: Starting URL untuk crawling
        max_pages: Maximum pages untuk crawl
        delay: Delay antara requests (seconds)
        
    Returns:
        List of discovered relative paths
    """
    discovered_paths: Set[str] = set()
    visited: Set[str] = set()
    to_visit = deque([base_url])
    
    print(info(f"🕷️  Starting intelligent crawl: {base_url}"))
    print(debug(f"   Max pages: {max_pages}, Delay: {delay}s"))
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
    })
    session.verify = False  # Skip SSL verification
    
    crawl_stats = {
        'total_pages': 0,
        'successful_pages': 0,
        'failed_pages': 0,
        'paths_discovered': 0,
        'api_endpoints_found': 0
    }
    
    while to_visit and len(visited) < max_pages:
        current_url = to_visit.popleft()
        
        if current_url in visited:
            continue
            
        crawl_stats['total_pages'] += 1
        
        try:
            debug(f"Crawling: {current_url}")
            response = session.get(current_url, timeout=15)
            visited.add(current_url)
            
            if response.status_code == 200:
                crawl_stats['successful_pages'] += 1
                
                # Enhanced path extraction
                extraction_result = extract_paths_from_html(response.text, base_url)
                new_paths = extraction_result['paths']
                api_endpoints = extraction_result['api_endpoints']
                
                # Add discovered paths
                for path in new_paths:
                    if path not in discovered_paths:
                        discovered_paths.add(path)
                        crawl_stats['paths_discovered'] += 1
                        
                        # Add to queue jika dari domain yang sama
                        if is_same_domain(path, base_url) and path not in visited:
                            to_visit.append(path)
                
                # Track API endpoints
                crawl_stats['api_endpoints_found'] += len(api_endpoints)
                
                if new_paths:
                    success(f"   ✅ {current_url} - Found {len(new_paths)} paths, {len(api_endpoints)} APIs")
                else:
                    debug(f"   📄 {current_url} - No new paths found")
                
            else:
                crawl_stats['failed_pages'] += 1
                warning(f"   ⚠️  {current_url} - HTTP {response.status_code}")
                
        except requests.Timeout:
            crawl_stats['failed_pages'] += 1
            error(f"   ⏰ {current_url} - Timeout")
        except requests.RequestException as e:
            crawl_stats['failed_pages'] += 1
            error(f"   ❌ {current_url} - {e}")
        except Exception as e:
            crawl_stats['failed_pages'] += 1
            error(f"   💥 {current_url} - Unexpected error: {e}")
        
        # Polite delay
        time.sleep(delay)
    
    # Convert to relative paths dengan filtering
    relative_paths = convert_to_relative_paths(discovered_paths, base_url)
    
    # Print crawl summary
    print(success(f"🎯 Crawling completed!"))
    print(info(f"   📊 Pages: {crawl_stats['successful_pages']}/{crawl_stats['total_pages']} successful"))
    print(info(f"   🔍 Paths discovered: {len(relative_paths)}"))
    print(info(f"   🌐 API endpoints: {crawl_stats['api_endpoints_found']}"))
    print(info(f"   ⏱️  Total visited: {len(visited)} pages"))
    
    return relative_paths

def extract_paths_from_html(html_content: str, base_url: str) -> Dict[str, Any]:
    """
    Enhanced path extraction dari HTML content
    
    Returns:
        Dictionary dengan paths dan api_endpoints
    """
    paths = set()
    api_endpoints = set()
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract dari <a href>
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if is_valid_url(href):
                full_url = urljoin(base_url, href)
                paths.add(full_url)
        
        # Extract dari <script src>
        for script in soup.find_all('script', src=True):
            src = script['src']
            if is_valid_url(src):
                full_url = urljoin(base_url, src)
                paths.add(full_url)
        
        # Extract dari <link href>
        for link in soup.find_all('link', href=True):
            href = link['href']
            if is_valid_url(href):
                full_url = urljoin(base_url, href)
                paths.add(full_url)
        
        # Extract dari <img src>
        for img in soup.find_all('img', src=True):
            src = img['src']
            if is_valid_url(src):
                full_url = urljoin(base_url, src)
                paths.add(full_url)
        
        # Extract dari <form action>
        for form in soup.find_all('form', action=True):
            action = form['action']
            if is_valid_url(action):
                full_url = urljoin(base_url, action)
                paths.add(full_url)
        
        # Extract dari <meta> tags
        for meta in soup.find_all('meta', content=True):
            content = meta.get('content', '')
            if 'url=' in content.lower():
                url_match = re.search(r'url=([^\s,]+)', content)
                if url_match:
                    url = url_match.group(1)
                    if is_valid_url(url):
                        full_url = urljoin(base_url, url)
                        paths.add(full_url)
        
        # Discover API endpoints dari JavaScript content
        api_endpoints = discover_api_endpoints(html_content, base_url)
        
    except Exception as e:
        debug(f"HTML parsing error: {e}")
    
    return {
        'paths': list(paths),
        'api_endpoints': list(api_endpoints)
    }

def is_valid_url(url: str) -> bool:
    """Check jika URL valid untuk crawling"""
    if not url or url.strip() == '':
        return False
    
    # Skip invalid protocols
    if url.startswith(('javascript:', 'mailto:', 'tel:', '#', 'data:')):
        return False
    
    # Skip common non-content URLs
    if any(skip in url.lower() for skip in ['cdn.', 'fonts.', 'googleapis.', 'gstatic.']):
        return False
    
    return True

def is_same_domain(url: str, base_url: str) -> bool:
    """Check jika URL dari domain yang sama"""
    try:
        url_domain = urlparse(url).netloc
        base_domain = urlparse(base_url).netloc
        return url_domain == base_domain
    except Exception:
        return False

def convert_to_relative_paths(full_urls: Set[str], base_url: str) -> List[str]:
    """Convert full URLs ke relative paths dengan enhanced filtering"""
    relative_paths = set()
    base_domain = urlparse(base_url).netloc
    
    for url in full_urls:
        try:
            if base_domain in url:
                parsed = urlparse(url)
                if parsed.path and parsed.path != '/':  # Only add jika ada path dan bukan root
                    # Clean dan normalize path
                    clean_path = clean_and_normalize_path(parsed.path)
                    if clean_path and is_interesting_path(clean_path):
                        relative_paths.add(clean_path)
                        
        except Exception as e:
            debug(f"URL conversion error: {e}")
    
    return list(relative_paths)

def clean_and_normalize_path(path: str) -> str:
    """Clean dan normalize path"""
    if not path:
        return ""
    
    # Remove fragments dan queries
    path = path.split('#')[0].split('?')[0]
    
    # Ensure starts with slash
    if not path.startswith('/'):
        path = '/' + path
    
    # Remove duplicate slashes
    path = re.sub(r'/+', '/', path)
    
    return path

def is_interesting_path(path: str) -> bool:
    """Check jika path interesting untuk scanning"""
    if not path or path == '/':
        return False
    
    # Skip common static files yang kurang interesting
    static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
    if any(path.lower().endswith(ext) for ext in static_extensions):
        return False
    
    # Skip common CDN paths
    cdn_indicators = ['/cdn-cgi/', '/_next/static/', '/wp-content/cache/', '/static/cache/']
    if any(indicator in path for indicator in cdn_indicators):
        return False
    
    return True

def discover_api_endpoints(html_content: str, base_url: str) -> Set[str]:
    """Discover API endpoints dari JavaScript dan HTML content"""
    endpoints = set()
    
    # Enhanced patterns untuk API endpoints
    patterns = [
        # Fetch API
        r'fetch\(["\']([^"\']+?)["\']\)',
        r'fetch\(`([^`]+?)`\)',
        
        # Axios
        r'axios\.(?:get|post|put|delete|patch)\(["\']([^"\']+?)["\']\)',
        r'axios\([^)]*url:\s*["\']([^"\']+?)["\']',
        
        # jQuery AJAX
        r'\$\.(?:ajax|get|post)\([^)]*url:\s*["\']([^"\']+?)["\']',
        r'\$\.(?:ajax|get|post)\(["\']([^"\']+?)["\']',
        
        # XMLHttpRequest
        r'\.open\(["\'](?:GET|POST|PUT|DELETE)["\'],\s*["\']([^"\']+?)["\']',
        
        # Common API patterns
        r'["\'](/api/[^"\']+?)["\']',
        r'["\'](/v[1-9]/[^"\']+?)["\']',
        r'["\'](/graphql[^"\']*?)["\']',
        r'["\'](/rest/[^"\']+?)["\']',
        r'["\'](/json/[^"\']+?)["\']',
        
        # Modern frameworks
        r'["\'](/_next/data/[^"\']+?)["\']',
        r'["\'](/_api/[^"\']+?)["\']',
    ]
    
    for pattern in patterns:
        try:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[0]
                else:
                    endpoint = match
                
                if endpoint and not endpoint.startswith('http'):
                    # Clean endpoint
                    endpoint = endpoint.split('?')[0].split('#')[0]
                    
                    # Skip obvious non-API paths
                    if not any(api_indicator in endpoint.lower() for api_indicator in 
                              ['/api/', '/v1/', '/v2/', '/graphql', '/rest/', '/json/']):
                        continue
                    
                    full_url = urljoin(base_url, endpoint)
                    endpoints.add(full_url)
                    
        except Exception as e:
            debug(f"API endpoint pattern error: {e}")
    
    return endpoints

def get_crawl_config() -> Dict[str, Any]:
    """Get default crawl configuration"""
    return {
        'max_pages': 15,
        'delay': 1.0,
        'timeout': 15,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'respect_robots_txt': False
    }

# Test function
def test_intelligent_crawler():
    """Test the enhanced intelligent crawler"""
    print(term.styles.banner("Testing Intelligent Crawler"))
    
    # Test dengan website yang aman untuk crawling
    test_url = "https://httpbin.org/html"
    
    try:
        print(info(f"Testing crawl on: {test_url}"))
        paths = intelligent_crawler(test_url, max_pages=5, delay=0.5)
        
        if paths:
            print(success(f"Crawling successful! Found {len(paths)} paths:"))
            for path in paths[:10]:  # Show first 10 paths
                print(f"  📍 {path}")
            if len(paths) > 10:
                print(info(f"  ... and {len(paths) - 10} more paths"))
        else:
            print(warning("No paths discovered - this is normal for some sites"))
            
        print(success("Intelligent crawler test completed!"))
        
    except Exception as e:
        print(error(f"Crawler test failed: {e}"))

if __name__ == "__main__":
    test_intelligent_crawler()