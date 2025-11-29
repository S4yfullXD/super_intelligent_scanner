#!/usr/bin/env python3
"""
Enhanced Endpoint Discoverer dengan Color Integration
Advanced API endpoint discovery dari berbagai sources
"""

import re
import requests
from urllib.parse import urljoin, urlparse
from typing import List, Set, Dict, Any
import json

# Import color system yang sudah ada
from utils.colors import term, success, error, warning, info, debug

class EndpointDiscoverer:
    def __init__(self):
        self.common_endpoints = self.load_common_endpoints()
        self.api_patterns = self.load_api_patterns()
        
        print(debug("🔍 Endpoint Discoverer initialized"))
    
    def load_common_endpoints(self) -> List[str]:
        """Load common API endpoints"""
        return [
            '/api/', '/api/v1/', '/api/v2/', '/api/v3/', '/api/v4/',
            '/graphql', '/graphql/api', '/gql',
            '/rest/', '/rest/api/', '/rest/v1/',
            '/json/', '/json/api/',
            '/ajax/', '/ajax/api/',
            '/oauth/', '/oauth2/', '/auth/', '/authentication/',
            '/users/', '/user/', '/account/', '/profile/',
            '/admin/', '/administrator/', '/dashboard/', '/panel/',
            '/config/', '/configuration/', '/settings/', '/setup/',
            '/database/', '/db/', '/data/', '/storage/',
            '/files/', '/upload/', '/download/', '/media/',
            '/search/', '/query/', '/filter/', '/sort/',
            '/create/', '/update/', '/delete/', '/remove/',
            '/list/', '/get/', '/post/', '/put/', '/patch/', '/delete/'
        ]
    
    def load_api_patterns(self) -> Dict[str, str]:
        """Load API endpoint patterns"""
        return {
            'restful': r'/(?:api|v[1-9])/[a-z]+(?:/[a-z]+)*/?',
            'graphql': r'/(?:graphql|gql)(?:\?.*)?',
            'action_based': r'/[a-z]+/(?:get|post|put|delete|update|create|list)[A-Za-z]*',
            'resource_based': r'/[a-z]+/(?:\d+|[a-f0-9-]+)',
            'parameterized': r'/[a-z]+\?[a-zA-Z0-9&=]+',
        }
    
    def discover_from_html(self, html_content: str, base_url: str) -> List[str]:
        """Discover endpoints from HTML content"""
        endpoints = set()
        
        print(info(f"📄 Analyzing HTML content for endpoints..."))
        
        # Forms action attributes
        form_actions = re.findall(r'<form[^>]*action=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        for action in form_actions:
            if action and not action.startswith(('javascript:', 'mailto:')):
                full_url = urljoin(base_url, action)
                endpoints.add(full_url)
                debug(f"   Found form action: {action}")
        
        # JavaScript data attributes
        data_endpoints = re.findall(r'data-(?:api|url|endpoint)=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        for endpoint in data_endpoints:
            if endpoint:
                full_url = urljoin(base_url, endpoint)
                endpoints.add(full_url)
                debug(f"   Found data endpoint: {endpoint}")
        
        # Meta tags
        meta_urls = re.findall(r'<meta[^>]*(?:content|url)=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        for url in meta_urls:
            if url and url.startswith('/'):
                full_url = urljoin(base_url, url)
                endpoints.add(full_url)
                debug(f"   Found meta URL: {url}")
        
        # Link tags dengan API rel
        api_links = re.findall(r'<link[^>]*rel=["\'](?:api|service)["\'][^>]*href=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
        for link in api_links:
            if link:
                full_url = urljoin(base_url, link)
                endpoints.add(full_url)
                debug(f"   Found API link: {link}")
        
        success(f"✅ Found {len(endpoints)} endpoints from HTML")
        return list(endpoints)
    
    def discover_from_js(self, js_content: str, base_url: str) -> List[str]:
        """Discover endpoints from JavaScript content"""
        endpoints = set()
        
        print(info(f"📜 Analyzing JavaScript content for endpoints..."))
        
        # API call patterns
        api_patterns = [
            # Fetch API
            r'fetch\(["\']([^"\']+?)["\']\)',
            r'fetch\(`([^`]+?)`\)',
            
            # XMLHttpRequest
            r'\.open\(["\'](?:GET|POST|PUT|DELETE)["\']\s*,\s*["\']([^"\']+?)["\']',
            
            # Axios
            r'axios\.(?:get|post|put|delete)\(["\']([^"\']+?)["\']',
            r'axios\([^)]*url:\s*["\']([^"\']+?)["\']',
            
            # jQuery AJAX
            r'\$\.(?:get|post|ajax)\([^)]*url:\s*["\']([^"\']+?)["\']',
            r'\$\.(?:get|post|ajax)\(["\']([^"\']+?)["\']',
            
            # Angular HTTP
            r'http\.(?:get|post|put|delete)\(["\']([^"\']+?)["\']',
            
            # Vue.js resource
            r'this\.\$http\.(?:get|post|put|delete)\(["\']([^"\']+?)["\']',
            
            # Modern frameworks
            r'useFetch\(["\']([^"\']+?)["\']',
            r'fetchAPI\(["\']([^"\']+?)["\']',
        ]
        
        found_count = 0
        for pattern in api_patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[0]
                else:
                    endpoint = match
                
                if endpoint and not endpoint.startswith(('http', '//')):
                    full_url = urljoin(base_url, endpoint)
                    if full_url not in endpoints:
                        endpoints.add(full_url)
                        found_count += 1
                        debug(f"   Found JS endpoint: {endpoint}")
        
        # URL strings that look like endpoints
        endpoint_like = re.findall(r'["\'](/[a-zA-Z0-9/_-]+(?:/v[1-9])?/[a-zA-Z0-9/_-]*)["\']', js_content)
        for endpoint in endpoint_like:
            if self.looks_like_api_endpoint(endpoint):
                full_url = urljoin(base_url, endpoint)
                if full_url not in endpoints:
                    endpoints.add(full_url)
                    found_count += 1
                    debug(f"   Found endpoint-like: {endpoint}")
        
        success(f"✅ Found {found_count} endpoints from JavaScript")
        return list(endpoints)
    
    def looks_like_api_endpoint(self, path: str) -> bool:
        """Check if a path looks like an API endpoint"""
        api_indicators = ['/api/', '/v1/', '/v2/', '/v3/', '/rest/', '/graphql', '/oauth']
        
        if any(indicator in path for indicator in api_indicators):
            return True
        
        # Check for common API patterns
        for pattern_name, pattern in self.api_patterns.items():
            if re.match(pattern, path):
                return True
        
        return False
    
    def discover_from_json(self, json_content: str, base_url: str) -> List[str]:
        """Discover endpoints from JSON content"""
        endpoints = set()
        
        print(info(f"📊 Analyzing JSON content for endpoints..."))
        
        try:
            data = json.loads(json_content)
            extracted_urls = self.extract_urls_from_json(data, base_url)
            endpoints.update(extracted_urls)
            success(f"✅ Found {len(extracted_urls)} endpoints from JSON")
        except json.JSONDecodeError:
            # If not valid JSON, try to find URL patterns
            warning("   Content is not valid JSON, using pattern matching")
            url_patterns = re.findall(r'"(https?://[^"]+)"', json_content)
            endpoints.update(url_patterns)
            success(f"✅ Found {len(url_patterns)} URL patterns from content")
        except Exception as e:
            error(f"   JSON analysis error: {e}")
        
        return list(endpoints)
    
    def extract_urls_from_json(self, data, base_url: str, current_path: str = "") -> Set[str]:
        """Recursively extract URLs from JSON data"""
        urls = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                # Check if key suggests it's a URL
                url_keys = ['url', 'endpoint', 'api', 'link', 'href', 'uri', 'path']
                if any(url_key in key.lower() for url_key in url_keys):
                    if isinstance(value, str) and value.startswith('/'):
                        full_url = urljoin(base_url, value)
                        urls.add(full_url)
                        debug(f"   Found JSON URL: {key} -> {value}")
                
                # Recursively check nested objects
                urls.update(self.extract_urls_from_json(value, base_url, f"{current_path}.{key}"))
        
        elif isinstance(data, list):
            for index, item in enumerate(data):
                urls.update(self.extract_urls_from_json(item, base_url, f"{current_path}[{index}]"))
        
        elif isinstance(data, str) and data.startswith('/') and len(data) > 3:
            # String that looks like a path
            if self.looks_like_api_endpoint(data):
                full_url = urljoin(base_url, data)
                urls.add(full_url)
                debug(f"   Found path in JSON: {data}")
        
        return urls
    
    def discover_from_url(self, url: str) -> List[str]:
        """Discover endpoints from a specific URL"""
        endpoints = set()
        
        print(info(f"🌐 Discovering endpoints from: {url}"))
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/html, application/xhtml+xml, */*'
            })
            
            response = session.get(url, timeout=15, verify=False)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                
                if 'html' in content_type:
                    endpoints.update(self.discover_from_html(response.text, url))
                elif 'javascript' in content_type or response.text.strip().startswith(('function', 'var ', 'const ', 'let ')):
                    endpoints.update(self.discover_from_js(response.text, url))
                elif 'json' in content_type:
                    endpoints.update(self.discover_from_json(response.text, url))
                else:
                    # Try all methods for unknown content types
                    endpoints.update(self.discover_from_html(response.text, url))
                    endpoints.update(self.discover_from_js(response.text, url))
                    endpoints.update(self.discover_from_json(response.text, url))
            else:
                warning(f"   HTTP {response.status_code} for {url}")
                
        except requests.RequestException as e:
            error(f"   Request failed: {e}")
        except Exception as e:
            error(f"   Unexpected error: {e}")
        
        return list(endpoints)
    
    def generate_endpoint_variations(self, base_endpoints: List[str]) -> List[str]:
        """Generate variations of discovered endpoints"""
        variations = set()
        
        print(info(f"🎲 Generating variations for {len(base_endpoints)} endpoints..."))
        
        for i, endpoint in enumerate(base_endpoints[:50]):  # Limit for performance
            if i % 10 == 0:
                debug(f"   Processing endpoint {i+1}/{min(50, len(base_endpoints))}")
                
            endpoint_variations = self.generate_single_endpoint_variations(endpoint)
            variations.update(endpoint_variations)
        
        success(f"✅ Generated {len(variations)} endpoint variations")
        return list(variations)
    
    def generate_single_endpoint_variations(self, endpoint: str) -> List[str]:
        """Generate variations for a single endpoint"""
        variations = set()
        
        # HTTP method variations
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
        
        # Parameter variations
        parameters = {
            'format': ['json', 'xml', 'html', 'txt'],
            'page': ['1', '0', '10', '100'],
            'limit': ['10', '20', '50', '100'],
            'sort': ['asc', 'desc', 'name', 'date'],
            'filter': ['active', 'inactive', 'all'],
            'token': ['test', 'demo', '123456']
        }
        
        # Add original
        variations.add(endpoint)
        
        # Add method variations as comments (for documentation discovery)
        for method in methods[:3]:
            variations.add(f"{endpoint}#{method}")
            variations.add(f"{endpoint}?__method={method}")
        
        # Add parameter variations
        base_url = endpoint.split('?')[0]
        for param_name, param_values in parameters.items():
            for value in param_values[:2]:
                variations.add(f"{base_url}?{param_name}={value}")
        
        # Add multiple parameters
        variations.add(f"{base_url}?page=1&limit=10")
        variations.add(f"{base_url}?format=json&pretty=true")
        variations.add(f"{base_url}?sort=desc&filter=active")
        
        # Add trailing slash variations
        if not endpoint.endswith('/'):
            variations.add(endpoint + '/')
        else:
            variations.add(endpoint.rstrip('/'))
        
        # Add common endpoint extensions
        extensions = ['.json', '.xml', '.html', '.txt']
        for ext in extensions:
            variations.add(f"{base_url}{ext}")
        
        return list(variations)
    
    def comprehensive_discovery(self, target_url: str, max_endpoints: int = 100) -> List[str]:
        """Comprehensive endpoint discovery dari berbagai sources"""
        all_endpoints = set()
        
        print(term.styles.banner(f"🎯 Starting Comprehensive Endpoint Discovery"))
        print(info(f"Target: {target_url}"))
        
        # Step 1: Discover dari main page
        print(info("Step 1: Discovering from main page..."))
        main_page_endpoints = self.discover_from_url(target_url)
        all_endpoints.update(main_page_endpoints)
        
        # Step 2: Generate variations dari common endpoints
        print(info("Step 2: Generating common endpoint variations..."))
        common_variations = self.generate_endpoint_variations(self.common_endpoints)
        all_endpoints.update(common_variations)
        
        # Step 3: Generate variations dari discovered endpoints
        if main_page_endpoints:
            print(info("Step 3: Generating variations from discovered endpoints..."))
            discovered_variations = self.generate_endpoint_variations(main_page_endpoints)
            all_endpoints.update(discovered_variations)
        
        # Step 4: Add common API patterns
        print(info("Step 4: Adding common API patterns..."))
        all_endpoints.update(self.common_endpoints)
        
        # Convert to relative paths dan filter
        final_endpoints = self.filter_and_convert_endpoints(list(all_endpoints), target_url)
        final_endpoints = final_endpoints[:max_endpoints]
        
        success(f"🎯 Comprehensive discovery completed! Found {len(final_endpoints)} endpoints")
        
        return final_endpoints
    
    def filter_and_convert_endpoints(self, endpoints: List[str], base_url: str) -> List[str]:
        """Filter dan convert endpoints ke format yang konsisten"""
        filtered = set()
        base_domain = urlparse(base_url).netloc
        
        for endpoint in endpoints:
            try:
                parsed = urlparse(endpoint)
                
                # Filter hanya endpoints dari domain yang sama
                if base_domain in parsed.netloc:
                    # Ambil path dan query
                    path_with_query = parsed.path
                    if parsed.query:
                        path_with_query += f"?{parsed.query}"
                    if parsed.fragment:
                        path_with_query += f"#{parsed.fragment}"
                    
                    if path_with_query and path_with_query != '/':
                        filtered.add(path_with_query)
                        
            except Exception as e:
                debug(f"Endpoint filtering error: {e}")
        
        return list(filtered)

def test_endpoint_discoverer():
    """Test function untuk endpoint discoverer"""
    print(term.styles.banner("🧪 Testing Endpoint Discoverer"))
    
    discoverer = EndpointDiscoverer()
    
    # Test dengan sample data
    print(info("Testing with sample HTML content..."))
    
    # Sample HTML untuk testing
    sample_html = """
    <html>
        <form action="/api/login" method="post">
            <input type="text" name="username">
        </form>
        <form action="/api/register" method="post">
            <input type="email" name="email">
        </form>
        <a href="/api/users">Users</a>
        <link rel="api" href="/api/docs">
        <meta content="/api/metadata">
        <div data-api="/api/data" data-url="/api/info"></div>
    </html>
    """
    
    # Test HTML discovery
    html_endpoints = discoverer.discover_from_html(sample_html, "https://example.com")
    print(success(f"HTML discovery found {len(html_endpoints)} endpoints:"))
    for endpoint in html_endpoints:
        print(f"  📍 {endpoint}")
    
    # Test JavaScript discovery
    print(info("Testing with sample JavaScript content..."))
    
    sample_js = """
    // API calls
    fetch('/api/users')
        .then(response => response.json());
    
    axios.get('/api/posts')
        .then(data => console.log(data));
    
    $.ajax({
        url: '/api/comments',
        method: 'GET'
    });
    
    var userEndpoint = '/api/user/profile';
    const settingsUrl = '/api/settings';
    """
    
    js_endpoints = discoverer.discover_from_js(sample_js, "https://example.com")
    print(success(f"JavaScript discovery found {len(js_endpoints)} endpoints:"))
    for endpoint in js_endpoints:
        print(f"  📍 {endpoint}")
    
    # Test JSON discovery
    print(info("Testing with sample JSON content..."))
    
    sample_json = """
    {
        "api": {
            "users": "/api/users",
            "posts": "/api/posts",
            "settings": {
                "url": "/api/settings",
                "endpoint": "/api/config"
            }
        },
        "links": [
            "/api/link1",
            "/api/link2"
        ]
    }
    """
    
    json_endpoints = discoverer.discover_from_json(sample_json, "https://example.com")
    print(success(f"JSON discovery found {len(json_endpoints)} endpoints:"))
    for endpoint in json_endpoints:
        print(f"  📍 {endpoint}")
    
    # Test endpoint variations
    print(info("Testing endpoint variations..."))
    
    base_endpoints = ["/api/users", "/api/posts"]
    variations = discoverer.generate_endpoint_variations(base_endpoints)
    print(success(f"Generated {len(variations)} variations:"))
    for i, variation in enumerate(variations[:10]):  # Show first 10
        print(f"  {i+1:2d}. {variation}")
    if len(variations) > 10:
        print(info(f"  ... and {len(variations) - 10} more variations"))
    
    # Test comprehensive discovery (offline mode)
    print(info("Testing comprehensive discovery (offline mode)..."))
    
    # Gunakan base URL dummy untuk testing offline
    test_url = "https://example.com"
    endpoints = discoverer.comprehensive_discovery(test_url, 20)
    
    print(success(f"Comprehensive discovery found {len(endpoints)} endpoints:"))
    for i, endpoint in enumerate(endpoints[:15]):
        print(f"  {i+1:2d}. {endpoint}")
    
    print(success("🎯 Endpoint Discoverer test completed!"))

if __name__ == "__main__":
    test_endpoint_discoverer()