#!/usr/bin/env python3
"""
Enhanced SourceMap Extractor dengan Color Integration & Advanced Analysis
Extract hidden sources, endpoints, dan secrets dari source maps
"""

import requests
import json
import os
from urllib.parse import urljoin
from typing import Dict, List, Optional, Set, Any
import re

# Import color system yang sudah ada
from utils.colors import term, success, error, warning, info, debug

class SourceMapExtractor:
    def __init__(self):
        self.source_map_cache = {}
        print(debug("🗺️  SourceMap Extractor initialized"))
    
    def discover_source_maps(self, js_urls: List[str]) -> List[str]:
        """Discover source map files from JavaScript URLs"""
        source_map_urls = set()
        
        print(info(f"🔍 Discovering source maps from {len(js_urls)} JavaScript files..."))
        
        for i, js_url in enumerate(js_urls[:30]):  # Limit for performance
            if i % 10 == 0:
                debug(f"   Processing JS file {i+1}/{min(30, len(js_urls))}")
                
            discovered_maps = self.find_source_maps_for_js(js_url)
            source_map_urls.update(discovered_maps)
            
            if discovered_maps:
                success(f"   ✅ Found {len(discovered_maps)} source maps for {js_url}")
        
        final_maps = list(source_map_urls)
        success(f"🎯 Total source maps discovered: {len(final_maps)}")
        
        return final_maps
    
    def find_source_maps_for_js(self, js_url: str) -> List[str]:
        """Find source maps for a specific JavaScript file"""
        source_maps = set()
        
        try:
            # Try common source map locations
            common_map_paths = [
                js_url + '.map',
                js_url.replace('.js', '.js.map'),
                js_url.rsplit('.', 1)[0] + '.map',
                js_url + '.min.map',  # For minified files
                js_url.replace('.min.js', '.js.map'),
            ]
            
            # Also check for sourceMappingURL comment in JS content
            js_content = self.fetch_content(js_url)
            if js_content:
                mapping_url = self.extract_source_mapping_url(js_content)
                if mapping_url:
                    full_map_url = urljoin(js_url, mapping_url)
                    source_maps.add(full_map_url)
                    debug(f"     Found sourceMappingURL: {mapping_url}")
                
                # Also look for hidden endpoints in JS content
                hidden_endpoints = self.analyze_js_for_hidden_paths(js_content, js_url)
                for endpoint in hidden_endpoints:
                    if endpoint.endswith('.map'):
                        source_maps.add(endpoint)
            
            # Add common map paths
            for map_path in common_map_paths:
                source_maps.add(map_path)
                
        except Exception as e:
            error(f"   ❌ Error finding source maps for {js_url}: {e}")
        
        return list(source_maps)
    
    def extract_source_mapping_url(self, js_content: str) -> Optional[str]:
        """Extract sourceMappingURL from JavaScript content"""
        patterns = [
            r'//# sourceMappingURL=([^\s]+)',
            r'/\*# sourceMappingURL=([^\s]+) \*/',
            r'//@ sourceMappingURL=([^\s]+)',  # Alternative format
            r'sourceMappingURL=([^\s"\']+)',   # Generic pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, js_content)
            if match:
                url = match.group(1).strip()
                # Clean up the URL
                url = url.split()[0]  # Take first part if there are spaces
                url = url.rstrip(';')  # Remove trailing semicolon
                return url
        
        return None
    
    def fetch_content(self, url: str) -> Optional[str]:
        """Fetch content from URL"""
        try:
            response = requests.get(
                url, 
                timeout=15,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*'
                },
                verify=False
            )
            if response.status_code == 200:
                return response.text
            else:
                debug(f"     HTTP {response.status_code} for {url}")
        except requests.Timeout:
            debug(f"     Timeout fetching {url}")
        except Exception as e:
            debug(f"     Error fetching {url}: {e}")
        return None
    
    def extract_sources_from_map(self, source_map_url: str) -> Dict[str, Any]:
        """Extract original sources from source map dengan comprehensive analysis"""
        print(info(f"📦 Extracting sources from: {source_map_url}"))
        
        try:
            response = requests.get(
                source_map_url,
                timeout=20,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=False
            )
            
            if response.status_code == 200:
                source_map = response.json()
                
                extraction_result = {
                    'source_map_url': source_map_url,
                    'sources_found': [],
                    'sources_content': {},
                    'analysis_results': {},
                    'success': False,
                    'stats': {}
                }
                
                if 'sources' in source_map:
                    sources = source_map['sources']
                    sources_content = source_map.get('sourcesContent', [])
                    
                    # Extract sources
                    for i, source_path in enumerate(sources):
                        content = sources_content[i] if i < len(sources_content) else None
                        
                        extraction_result['sources_found'].append(source_path)
                        
                        if content:
                            extraction_result['sources_content'][source_path] = content
                    
                    # Analyze extracted sources
                    extraction_result['analysis_results'] = self.analyze_extracted_sources(
                        extraction_result['sources_content']
                    )
                    
                    # Generate stats
                    extraction_result['stats'] = {
                        'total_sources': len(sources),
                        'sources_with_content': len([c for c in sources_content if c]),
                        'total_endpoints_found': len(extraction_result['analysis_results']['all_endpoints']),
                        'total_secrets_found': len(extraction_result['analysis_results']['all_secrets']),
                    }
                    
                    extraction_result['success'] = True
                    
                    success(f"   ✅ Extracted {len(sources)} sources ({extraction_result['stats']['sources_with_content']} with content)")
                    
                    # Print quick summary
                    if extraction_result['stats']['total_endpoints_found'] > 0:
                        info(f"   🌐 Found {extraction_result['stats']['total_endpoints_found']} endpoints")
                    if extraction_result['stats']['total_secrets_found'] > 0:
                        warning(f"   🔐 Found {extraction_result['stats']['total_secrets_found']} potential secrets")
                
                return extraction_result
            else:
                error(f"   ❌ HTTP {response.status_code} for source map")
                
        except json.JSONDecodeError:
            error(f"   ❌ Invalid JSON in source map")
        except Exception as e:
            error(f"   ❌ Error extracting from {source_map_url}: {e}")
        
        return {
            'source_map_url': source_map_url, 
            'success': False, 
            'error': str(e) if 'e' in locals() else 'Unknown error'
        }
    
    def analyze_extracted_sources(self, sources_content: Dict[str, str]) -> Dict[str, Any]:
        """Analyze extracted sources untuk endpoints dan secrets"""
        analysis_results = {
            'all_endpoints': set(),
            'all_secrets': set(),
            'file_analysis': {},
            'summary': {}
        }
        
        for file_path, content in sources_content.items():
            if not content:
                continue
                
            file_analysis = {
                'endpoints': self.extract_endpoints_from_source(content, file_path),
                'secrets': self.extract_secrets_from_source(content),
                'file_type': self.detect_file_type(file_path, content),
                'line_count': content.count('\n') + 1
            }
            
            analysis_results['file_analysis'][file_path] = file_analysis
            analysis_results['all_endpoints'].update(file_analysis['endpoints'])
            analysis_results['all_secrets'].update(file_analysis['secrets'])
        
        # Convert sets to lists
        analysis_results['all_endpoints'] = list(analysis_results['all_endpoints'])
        analysis_results['all_secrets'] = list(analysis_results['all_secrets'])
        
        # Generate summary
        analysis_results['summary'] = {
            'total_files_analyzed': len(analysis_results['file_analysis']),
            'total_endpoints': len(analysis_results['all_endpoints']),
            'total_secrets': len(analysis_results['all_secrets']),
            'file_types': list(set(analysis['file_type'] for analysis in analysis_results['file_analysis'].values()))
        }
        
        return analysis_results
    
    def extract_endpoints_from_source(self, content: str, file_path: str) -> List[str]:
        """Extract endpoints from source content"""
        endpoints = set()
        
        patterns = [
            r'["\'](https?://[^"\']+?)["\']',
            r'["\'](/[^"\']+?)["\']',
            r'`(https?://[^`]+?)`',
            r'`(/[^`]+?)`',
            r'fetch\(["\']([^"\']+?)["\']',
            r'axios\.(?:get|post)\(["\']([^"\']+?)["\']',
            r'\.ajax\([^)]*url:\s*["\']([^"\']+?)["\']',
            r'window\.location\s*=\s*["\']([^"\']+?)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    endpoint = match[0]
                else:
                    endpoint = match
                
                if endpoint and len(endpoint) > 3:
                    endpoints.add(endpoint)
        
        return list(endpoints)
    
    def extract_secrets_from_source(self, content: str) -> List[str]:
        """Extract potential secrets from source content"""
        secrets = set()
        
        secret_patterns = [
            r'api[_-]?key["\']?\s*:\s*["\']([^"\']{20,50})["\']',
            r'secret["\']?\s*:\s*["\']([^"\']{10,50})["\']',
            r'token["\']?\s*:\s*["\']([^"\']{10,100})["\']',
            r'password["\']?\s*:\s*["\']([^"\']{8,50})["\']',
            r'client[_-]?(?:id|secret)["\']?\s*:\s*["\']([^"\']{10,50})["\']',
        ]
        
        for pattern in secret_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    secret = match[0]
                else:
                    secret = match
                
                if self.looks_like_secret(secret):
                    secrets.add(secret)
        
        return list(secrets)
    
    def looks_like_secret(self, text: str) -> bool:
        """Check if text looks like a secret"""
        if len(text) < 8:
            return False
        
        false_positives = ['undefined', 'null', 'true', 'false', 'localhost', '127.0.0.1']
        if text.lower() in false_positives:
            return False
        
        # Common secret patterns
        if re.match(r'^[a-f0-9]{32}$', text):  # MD5
            return True
        if re.match(r'^[a-f0-9]{40}$', text):  # SHA-1
            return True
        if text.startswith('eyJ'):  # JWT
            return True
        if 'key' in text.lower() and len(text) >= 20:
            return True
            
        return True
    
    def detect_file_type(self, file_path: str, content: str) -> str:
        """Detect file type based on path and content"""
        if file_path.endswith('.js') or 'function' in content or 'const ' in content:
            return 'javascript'
        elif file_path.endswith('.ts'):
            return 'typescript'
        elif file_path.endswith('.css'):
            return 'css'
        elif file_path.endswith('.html'):
            return 'html'
        elif file_path.endswith('.json'):
            return 'json'
        else:
            return 'unknown'
    
    def save_extracted_sources(self, extraction_result: Dict, output_dir: str):
        """Save extracted sources to files"""
        if not extraction_result.get('success'):
            warning("   Cannot save - extraction failed")
            return
        
        sources_dir = os.path.join(output_dir, 'decompiled_sources')
        os.makedirs(sources_dir, exist_ok=True)
        
        saved_files = 0
        
        for source_path, content in extraction_result['sources_content'].items():
            if content and len(content.strip()) > 10:  # Only save non-empty content
                try:
                    # Create safe filename
                    safe_filename = self.create_safe_filename(source_path)
                    file_path = os.path.join(sources_dir, safe_filename)
                    
                    # Create directories if needed
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    saved_files += 1
                    debug(f"     💾 Saved: {safe_filename}")
                    
                except Exception as e:
                    error(f"     ❌ Error saving {source_path}: {e}")
        
        success(f"   💾 Saved {saved_files} source files to {sources_dir}")
        
        # Save analysis report
        self.save_analysis_report(extraction_result, output_dir)
    
    def save_analysis_report(self, extraction_result: Dict, output_dir: str):
        """Save analysis report"""
        try:
            report_path = os.path.join(output_dir, 'sourcemap_analysis.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(extraction_result, f, indent=2, ensure_ascii=False)
            debug(f"     📊 Analysis report saved: {report_path}")
        except Exception as e:
            error(f"     ❌ Error saving analysis report: {e}")
    
    def create_safe_filename(self, source_path: str) -> str:
        """Create safe filename from source path"""
        # Remove protocol and domain if present
        if '://' in source_path:
            source_path = '/' + source_path.split('://', 1)[1].split('/', 1)[1]
        
        # Replace problematic characters
        safe_name = re.sub(r'[^a-zA-Z0-9./_-]', '_', source_path)
        
        # Ensure it starts with a valid character
        if not safe_name or safe_name[0] in './':
            safe_name = 'file_' + safe_name
        
        # Add extension if missing
        if '.' not in safe_name:
            safe_name += '.js'
        
        return safe_name
    
    def analyze_js_for_hidden_paths(self, js_content: str, base_url: str) -> List[str]:
        """Analyze JavaScript for hidden paths and endpoints"""
        hidden_paths = set()
        
        patterns = [
            # URL strings
            r'["\'](https?://[^"\']+?)["\']',
            r'["\'](/[^"\']+?\.(js|css|json|html|map))["\']',
            r'["\'](\.\.[^"\']+?)["\']',
            r'["\'](~/[^"\']+?)["\']',
            
            # Template literals
            r'`(/[^`]+?\.(js|css|json|html|map))`',
            
            # Require/import statements
            r'require\(["\']([^"\']+?)["\']\)',
            r'import\s+.*from\s+["\']([^"\']+?)["\']',
            
            # Fetch/AJAX calls
            r'fetch\(["\']([^"\']+?)["\']\)',
            r'\.ajax\([^)]*url:\s*["\']([^"\']+?)["\']',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, js_content)
            for match in matches:
                if isinstance(match, tuple):
                    path = match[0]
                else:
                    path = match
                
                if path and not path.startswith('http'):
                    # Convert to absolute path
                    absolute_path = urljoin(base_url, path)
                    hidden_paths.add(absolute_path)
        
        return list(hidden_paths)

def test_sourcemap_extractor():
    """Test function untuk SourceMap Extractor"""
    print(term.styles.banner("🧪 Testing SourceMap Extractor"))
    
    extractor = SourceMapExtractor()
    
    # Test dengan sample JavaScript URLs (offline mode)
    print(info("Testing source map discovery..."))
    
    sample_js_urls = [
        "https://example.com/static/js/app.js",
        "https://example.com/static/js/main.min.js", 
        "https://example.com/assets/bundle.js"
    ]
    
    # Test discovery
    source_maps = extractor.discover_source_maps(sample_js_urls)
    
    print(success(f"Discovered {len(source_maps)} potential source maps:"))
    for map_url in source_maps:
        print(f"  📍 {map_url}")
    
    # Test source mapping URL extraction
    print(info("Testing sourceMappingURL extraction..."))
    
    sample_js_with_map = """
    // Some JavaScript code
    function test() { return true; }
    //# sourceMappingURL=app.js.map
    """
    
    mapping_url = extractor.extract_source_mapping_url(sample_js_with_map)
    if mapping_url:
        print(success(f"Extracted sourceMappingURL: {mapping_url}"))
    else:
        print(warning("No sourceMappingURL found in sample"))
    
    # Test hidden path analysis
    print(info("Testing hidden path analysis..."))
    
    sample_js_with_paths = """
    const apiUrl = "/api/v1/users";
    fetch('/api/data');
    require('../config/secrets.json');
    """
    
    hidden_paths = extractor.analyze_js_for_hidden_paths(sample_js_with_paths, "https://example.com")
    print(success(f"Found {len(hidden_paths)} hidden paths:"))
    for path in hidden_paths:
        print(f"  📍 {path}")
    
    print(success("🎯 SourceMap Extractor test completed!"))

if __name__ == "__main__":
    test_sourcemap_extractor()