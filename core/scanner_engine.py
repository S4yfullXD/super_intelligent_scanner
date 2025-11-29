#!/usr/bin/env python3
"""
Super Intelligent Scanner Engine dengan NATURAL PATHS Strategy
Optimized untuk bypass WAF & avoid detection
"""

import requests
import time
import threading
import random
import sys
import os
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# Import our enhanced systems
from utils.colors import term, success, error, warning, info, debug
from utils.config_loader import ConfigLoader
from utils.file_organizer import setup_output_directory, intelligent_save
from utils.logger import ScannerLogger
from utils.report_generator import ReportGenerator

# Import core modules dengan error handling
try:
    from intelligence.ml_predictor import MLPredictor
    from intelligence.nlp_analyzer import NLPAnalyzer
    from intelligence.adaptive_learner import AdaptiveLearner
    from intelligence.pattern_recognizer import PatternRecognizer
    INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    print(warning(f"Some intelligence modules not available: {e}"))
    INTELLIGENCE_AVAILABLE = False

try:
    from core.evasion_engine import EvasionEngine
    from core.healing_engine import HealingEngine
    from core.request_manager import RequestManager
    CORE_AVAILABLE = True
except ImportError as e:
    print(warning(f"Some core modules not available: {e}"))
    CORE_AVAILABLE = False

try:
    from external.github_resources import GitHubResourceManager
    EXTERNAL_AVAILABLE = True
except ImportError as e:
    print(warning(f"External modules not available: {e}"))
    EXTERNAL_AVAILABLE = False

class ScannerEngine:
    def __init__(self, discovery_modules=None):
        """
        Initialize Scanner Engine
        
        Args:
            discovery_modules: Dictionary berisi discovery modules dari main.py
                Format: {
                    'intelligent_crawler': function,
                    'quantum_fuzzer': QuantumFuzzer instance, 
                    'endpoint_discoverer': EndpointDiscoverer instance,
                    'js_analyzer': JSAnalyzer instance,
                    'sourcemap_extractor': SourceMapExtractor instance
                }
        """
        self.config = ConfigLoader.load_config()
        
        # Initialize modules dengan error handling
        self.evasion_engine = EvasionEngine() if CORE_AVAILABLE else None
        self.healing_engine = HealingEngine() if CORE_AVAILABLE else None
        self.request_manager = RequestManager() if CORE_AVAILABLE else None
        self.resource_manager = GitHubResourceManager() if EXTERNAL_AVAILABLE else None
        
        # Intelligence modules
        if INTELLIGENCE_AVAILABLE:
            self.ml_predictor = MLPredictor()
            self.nlp_analyzer = NLPAnalyzer()
            self.adaptive_learner = AdaptiveLearner()
            self.pattern_recognizer = PatternRecognizer()
        else:
            self.ml_predictor = self.nlp_analyzer = self.adaptive_learner = self.pattern_recognizer = None
            
        # Discovery modules - DITERIMA DARI MAIN.PY  
        if discovery_modules:
            self.intelligent_crawler = discovery_modules.get('intelligent_crawler')
            self.quantum_fuzzer = discovery_modules.get('quantum_fuzzer')
            self.endpoint_discoverer = discovery_modules.get('endpoint_discoverer')
            self.js_analyzer = discovery_modules.get('js_analyzer')
            self.sourcemap_extractor = discovery_modules.get('sourcemap_extractor')
            self.DISCOVERY_AVAILABLE = True
        else:
            self.intelligent_crawler = None
            self.quantum_fuzzer = None
            self.endpoint_discoverer = None
            self.js_analyzer = None
            self.sourcemap_extractor = None
            self.DISCOVERY_AVAILABLE = False
            
        self.report_generator = ReportGenerator()
        self.logger = None
        self.setup_session()
        
        # Animation control
        self._spinner_running = False
        self._spinner_thread = None
    
    def setup_session(self):
        """Setup session dengan default headers"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _start_loading_animation(self, message: str):
        """Start loading animation untuk long-running processes"""
        if self._spinner_running:
            self._stop_loading_animation()
            
        self._spinner_running = True
        spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        
        def animate():
            i = 0
            while self._spinner_running:
                sys.stdout.write(f'\r{term.colors.BRIGHT_CYAN}{spinner_chars[i]} {message}{term.colors.RESET}')
                sys.stdout.flush()
                time.sleep(0.1)
                i = (i + 1) % len(spinner_chars)
            sys.stdout.write('\r' + ' ' * (len(message) + 2) + '\r')
            sys.stdout.flush()
        
        self._spinner_thread = threading.Thread(target=animate)
        self._spinner_thread.daemon = True
        self._spinner_thread.start()
    
    def _stop_loading_animation(self):
        """Stop loading animation"""
        self._spinner_running = False
        if self._spinner_thread:
            self._spinner_thread.join(timeout=1.0)
    
    def _print_phase_header(self, phase_num: int, phase_name: str, description: str = ""):
        """Print phase header yang keren"""
        print(f"\n{term.colors.BRIGHT_MAGENTA}{term.colors.BOLD}🔍 PHASE {phase_num}: {phase_name}{term.colors.RESET}")
        if description:
            print(f"{term.colors.GRAY}   {description}{term.colors.RESET}")
        print(f"{term.colors.GRAY}   {'=' * 50}{term.colors.RESET}")
    
    def _is_suspicious_path(self, path: str) -> bool:
        """Check if path is suspicious dan akan trigger WAF"""
        suspicious_patterns = [
            '..', '...', '////', '.bak', '.old', '.txt', '.xml', 
            '.json', '.js.map', '.css.map', '.env', 'config.json',
            'package.json', 'composer.json', 'wp-', 'laravel/',
            '//', '....', '.sql', '.zip', '.tar', '.gz',
            '.log', '.tmp', '.temp', '.swp', '.swo'
        ]
        return any(pattern in path for pattern in suspicious_patterns)
    
    def get_common_paths(self) -> List[str]:
        """Get SMART common paths yang natural & tidak suspicious"""
        return [
            # ✅ NATURAL API PATHS (tidak suspicious)
            '/api', '/api/', '/api/v1', '/api/v1/', '/api/v2', '/api/v2/',
            '/api/v3', '/api/v3/', '/graphql', '/graphql/', '/rest', '/rest/', 
            '/json', '/json/', '/v1', '/v1/', '/v2', '/v2/', '/v3', '/v3/',
            
            # ✅ NATURAL AUTH PATHS  
            '/auth', '/auth/', '/login', '/login/', '/register', '/register/',
            '/signin', '/signin/', '/signup', '/signup/', '/oauth', '/oauth/',
            '/token', '/token/', '/refresh', '/refresh/', '/logout', '/logout/',
            
            # ✅ NATURAL APP PATHS
            '/app', '/app/', '/dashboard', '/dashboard/', '/admin', '/admin/',
            '/profile', '/profile/', '/settings', '/settings/', '/account', '/account/',
            '/user', '/user/', '/users', '/users/', '/me', '/me/', '/home', '/home/',
            
            # ✅ NATURAL STATIC PATHS (tanpa extensions suspicious)
            '/static', '/static/', '/assets', '/assets/', '/public', '/public/',
            '/media', '/media/', '/uploads', '/uploads/', '/files', '/files/',
            '/images', '/images/', '/img', '/img/', '/css', '/css/', '/js', '/js/',
            '/fonts', '/fonts/', '/icons', '/icons/', '/svg', '/svg/',
            
            # ✅ NATURAL DOCUMENT PATHS
            '/docs', '/docs/', '/documentation', '/documentation/', 
            '/api-docs', '/api-docs/', '/swagger', '/swagger/', '/openapi', '/openapi/',
            
            # ✅ WELL-KNOWN STANDARD PATHS (aman)
            '/robots.txt', '/sitemap.xml', '/favicon.ico', 
            '/humans.txt', '/security.txt',
            
            # ✅ HEALTH & STATUS PATHS
            '/health', '/health/', '/status', '/status/', '/ping', '/ping/',
            '/ready', '/ready/', '/live', '/live/', '/healthcheck', '/healthcheck/',
            
            # ✅ MODERN FRAMEWORK PATHS
            '/_next', '/_next/', '/_next/data', '/_next/data/',
            '/__nuxt', '/__nuxt/', '/_nuxt', '/_nuxt/',
            '/_astro', '/_astro/', '/build', '/build/', '/dist', '/dist/',
            
            # ✅ SEARCH & DATA PATHS
            '/search', '/search/', '/query', '/query/', '/data', '/data/',
            '/list', '/list/', '/items', '/items/', '/products', '/products/',
            '/catalog', '/catalog/', '/store', '/store/', '/shop', '/shop/',
            
            # ✅ MINIMAL CONFIG PATHS (tanpa .json yang obvious)
            '/config', '/config/', '/settings', '/settings/', 
            '/configuration', '/configuration/', '/options', '/options/',
            
            # ✅ CONTENT PATHS
            '/blog', '/blog/', '/posts', '/posts/', '/articles', '/articles/',
            '/news', '/news/', '/updates', '/updates/', '/feed', '/feed/',
            
            # ✅ CONTACT & SUPPORT PATHS
            '/contact', '/contact/', '/about', '/about/', '/support', '/support/',
            '/help', '/help/', '/faq', '/faq/', '/terms', '/terms/', '/privacy', '/privacy/'
        ]
    
    def generate_natural_variations(self, base_paths: List[str]) -> List[str]:
        """Generate natural variations yang tidak trigger WAF"""
        natural_paths = set()
        
        for path in base_paths:
            # Skip obviously suspicious paths
            if self._is_suspicious_path(path):
                continue
                
            # Base paths
            natural_paths.add(path)
            
            # Natural variations dengan parameters yang realistic
            variations = [
                path,
                path + '/',
                path + '?v=1',
                path + '?version=1', 
                path + '?format=json',
                path + '?callback=jsonp' + str(random.randint(1000, 9999)),
                path + '?_=' + str(random.randint(1000000000, 9999999999)),
                path + '?cache=true',
                path + '?preview=1',
                path + '?debug=true',
                path + '?api_key=test',
                path + '?token=abc123',
                path + '?auth=true',
                path + '?source=web',
                path + '?platform=desktop',
                path + '?lang=en',
                path + '?locale=en_US',
            ]
            
            natural_paths.update(variations)
        
        return list(natural_paths)
    
    def start_scan(self, target_url: str) -> Dict[str, Any]:
        """Start the intelligent scanning process dengan NATURAL paths strategy"""
        start_time = time.time()
        
        print(term.scan_msg.scan_start(target_url))
        
        # Setup output directory and logger
        output_dir = setup_output_directory(target_url)
        self.logger = ScannerLogger(output_dir)
        self.logger.info(f"Scan started for: {target_url}")
        
        # Download resources if enabled
        if self.config['resources']['auto_download'] and EXTERNAL_AVAILABLE:
            self.logger.info("Downloading resources from GitHub...")
            self._start_loading_animation("Downloading resources from GitHub...")
            try:
                self.resource_manager.download_resources()
                self._stop_loading_animation()
                print(success("Resources downloaded successfully"))
            except Exception as e:
                self._stop_loading_animation()
                print(warning(f"Resource download failed: {e}"))
        
        try:
            # Phase 1: Advanced Discovery dengan NATURAL PATHS
            self._print_phase_header(1, "Natural Path Discovery", "Discovering endpoints using natural patterns only")
            discovered_paths = self.advanced_discovery_phase(target_url)
            
            # Phase 2: Intelligent Scanning  
            self._print_phase_header(2, "Intelligent Path Scanning", f"Scanning {len(discovered_paths)} natural paths")
            scan_results = self.scan_paths(target_url, discovered_paths, output_dir)
            
            # Phase 3: Intelligence Analysis
            self._print_phase_header(3, "Intelligence Analysis", "Analyzing findings with AI-powered techniques")
            intelligence_data = self.intelligence_analysis_phase(target_url, output_dir, scan_results)
            
            # Phase 4: Reporting
            self._print_phase_header(4, "Generating Reports", "Creating comprehensive scan reports")
            final_report = self.final_reporting_phase(target_url, output_dir, scan_results, intelligence_data, start_time)
            
            return final_report
            
        except Exception as e:
            self._stop_loading_animation()  # Pastikan animation stop kalau error
            self.logger.error(f"Scan failed: {e}")
            print(error(f"Scan failed: {e}"))
            raise
        finally:
            self._stop_loading_animation()  # Cleanup
    
    def advanced_discovery_phase(self, target_url: str) -> List[str]:
        """Advanced path discovery dengan NATURAL paths only"""
        all_paths = set()
        
        # Method 1: Get natural base paths
        self._start_loading_animation("Generating natural base paths...")
        base_paths = self.get_common_paths()
        all_paths.update(base_paths)
        self._stop_loading_animation()
        print(info(f"Generated {len(base_paths)} natural base paths"))
        
        # Method 2: Generate natural variations
        self._start_loading_animation("Creating natural variations...")
        natural_paths = self.generate_natural_variations(base_paths)
        all_paths.update(natural_paths)
        self._stop_loading_animation()
        print(info(f"Created {len(natural_paths)} natural path variations"))
        
        # Method 3: Intelligent crawling (jika available)
        if self.DISCOVERY_AVAILABLE and self.intelligent_crawler:
            self._start_loading_animation("Crawling for natural endpoints...")
            try:
                crawled_paths = self.intelligent_crawler(target_url, max_pages=10)
                # Filter crawled paths untuk yang natural saja
                natural_crawled = [p for p in crawled_paths if not self._is_suspicious_path(p)]
                all_paths.update(natural_crawled)
                self._stop_loading_animation()
                print(info(f"Crawling discovered {len(natural_crawled)} natural paths"))
            except Exception as e:
                self._stop_loading_animation()
                print(warning(f"Crawling failed: {e}"))
        
        # Method 4: GitHub resources (filtered)
        if EXTERNAL_AVAILABLE and self.config['resources']['auto_download']:
            self._start_loading_animation("Loading filtered GitHub resources...")
            try:
                github_paths = self.resource_manager.load_common_paths()
                # Filter GitHub paths untuk yang natural
                natural_github = [p for p in github_paths if not self._is_suspicious_path(p)]
                all_paths.update(natural_github)
                self._stop_loading_animation()
                print(info(f"Added {len(natural_github)} natural paths from GitHub"))
            except Exception as e:
                self._stop_loading_animation()
                print(warning(f"GitHub resources failed: {e}"))
        
        # Final filtering untuk pastikan semua paths natural
        final_paths = [p for p in all_paths if not self._is_suspicious_path(p)]
        
        print(success(f"Total NATURAL paths to scan: {len(final_paths)}"))
        self.logger.info(f"Total natural paths discovered: {len(final_paths)}")
        return final_paths
    
    def fetch_initial_content(self, url: str) -> str:
        """Fetch initial content untuk analysis"""
        try:
            # Gunakan request manager untuk better evasion
            if self.request_manager:
                response = self.request_manager.smart_request(url, use_evasion=True)
                if response and response.status_code == 200:
                    return response.text
            else:
                # Fallback ke regular session
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            print(debug(f"Initial content fetch failed: {e}"))
        return ""
    
    def scan_paths(self, base_url: str, paths: List[str], output_dir: str) -> List[Dict]:
        """Scan all discovered paths dengan progress tracking"""
        scan_config = self.config['scanning']
        results = []
        found_count = 0
        error_count = 0
        
        def scan_single_path(path: str):
            """Scan a single path dengan natural approach"""
            nonlocal found_count, error_count
            target_url = urljoin(base_url, path)
            
            try:
                # Gunakan request manager untuk better evasion & natural requests
                if self.request_manager:
                    response = self.request_manager.smart_request(target_url, use_evasion=True)
                else:
                    # Fallback ke evasion engine atau regular session
                    if self.config['evasion']['stealth_mode'] and self.evasion_engine:
                        response = self.evasion_engine.stealth_request(target_url, timeout=scan_config['timeout'])
                    else:
                        response = self.session.get(target_url, timeout=scan_config['timeout'], allow_redirects=False)
                
                if response is None:
                    error_count += 1
                    return {'url': target_url, 'path': path, 'error': 'request_failed'}
                
                result = {
                    'url': target_url,
                    'path': path,
                    'status_code': response.status_code,
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', ''),
                    'success': False,
                }
                
                # Check if this is a valid finding - relaxed criteria untuk natural paths
                if (response.status_code == 200 and 
                    result['content_length'] > 20 and  # Very relaxed threshold untuk natural paths
                    any(text_type in result['content_type'].lower() for text_type in ['text', 'json', 'javascript', 'html', 'xml'])):
                    
                    result['success'] = True
                    found_count += 1
                    
                    # Save content
                    try:
                        save_success = intelligent_save(path, response.text, result['content_type'], output_dir)
                        result['saved'] = save_success
                        
                        if save_success:
                            print(term.scan_msg.found(path, response.status_code, f"{result['content_length']} bytes"))
                        else:
                            print(warning(f"Found but rejected: {path}"))
                    except Exception as e:
                        result['saved'] = False
                        print(debug(f"Save failed for {path}: {e}"))
                
                elif response.status_code == 403:
                    print(term.scan_msg.forbidden(path))
                elif response.status_code == 404:
                    pass  # Silent for 404 - common untuk natural paths
                else:
                    # Only log non-404 errors untuk avoid spam
                    if response.status_code != 400:  # 400 juga common
                        print(warning(f"HTTP {response.status_code}: {path}"))
                
                return result
                
            except Exception as e:
                error_count += 1
                print(term.scan_msg.error(path, str(e)))
                return {'url': target_url, 'path': path, 'error': str(e)}
        
        # Multi-threaded scanning dengan progress
        total_paths = len(paths)
        print(info(f"Starting scan of {total_paths} NATURAL paths with {scan_config['max_workers']} workers..."))
        
        completed = 0
        with ThreadPoolExecutor(max_workers=scan_config['max_workers']) as executor:
            # Submit semua tasks
            future_to_path = {executor.submit(scan_single_path, path): path for path in paths}
            
            # Process results dengan progress tracking
            for future in as_completed(future_to_path):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    
                    completed += 1
                    # Update progress setiap 10 paths atau di akhir
                    if completed % 10 == 0 or completed == total_paths:
                        progress = term.scan_msg.progress(completed, total_paths, "Scanning Natural Paths")
                        print(f"\r{progress}", end='', flush=True)
                        
                except Exception as e:
                    path = future_to_path[future]
                    error_result = {'url': urljoin(base_url, path), 'path': path, 'error': str(e)}
                    results.append(error_result)
                    error_count += 1
                    self.logger.error(f"Failed to scan {path}: {e}")
        
        print()  # New line setelah progress
        print(success(f"Natural paths scanning completed! Found: {found_count}, Errors: {error_count}"))
        return results
    
    def intelligence_analysis_phase(self, target_url: str, output_dir: str, scan_results: List[Dict]) -> Dict[str, Any]:
        """Perform advanced intelligence analysis dengan progress"""
        intelligence_data = {
            'secrets_found': [],
            'technologies_detected': [],
            'endpoints_analyzed': [],
            'pattern_analysis': {},
            'risk_assessment': {}
        }
        
        if not INTELLIGENCE_AVAILABLE:
            print(warning("Intelligence modules not available - skipping advanced analysis"))
            return intelligence_data
        
        # Analyze successful findings
        successful_scans = [r for r in scan_results if r.get('success') and r.get('saved')]
        
        if not successful_scans:
            print(info("No successful scans to analyze"))
            return intelligence_data
        
        print(info(f"Analyzing {len(successful_scans)} successful findings..."))
        
        analyzed = 0
        for scan in successful_scans:
            try:
                self._start_loading_animation(f"Analyzing {scan['path']}...")
                
                content = self.load_saved_content(scan['path'], output_dir)
                if content:
                    # NLP analysis
                    if self.nlp_analyzer:
                        nlp_analysis = self.nlp_analyzer.analyze_content(content, target_url)
                        intelligence_data['secrets_found'].extend(nlp_analysis.get('secrets_found', []))
                        intelligence_data['technologies_detected'].extend(nlp_analysis.get('technologies_detected', []))
                    
                    # JS analysis untuk JavaScript files
                    if scan['path'].endswith('.js') and self.js_analyzer:
                        js_analysis = self.js_analyzer.analyze_javascript(content, target_url)
                        intelligence_data['endpoints_analyzed'].extend(js_analysis.get('endpoints_found', []))
                
                analyzed += 1
                self._stop_loading_animation()
                print(f"\r{term.scan_msg.progress(analyzed, len(successful_scans), 'Analysis')}", end='', flush=True)
                
            except Exception as e:
                self._stop_loading_animation()
                print(debug(f"Analysis failed for {scan['path']}: {e}"))
        
        print()  # New line setelah progress
        
        # Remove duplicates
        intelligence_data['secrets_found'] = list(set(intelligence_data['secrets_found']))
        intelligence_data['technologies_detected'] = list(set(intelligence_data['technologies_detected']))
        
        # Pattern analysis
        if self.pattern_recognizer:
            self._start_loading_animation("Analyzing response patterns...")
            intelligence_data['pattern_analysis'] = self.pattern_recognizer.analyze_response_patterns(scan_results)
            self._stop_loading_animation()
        
        # Risk assessment
        intelligence_data['risk_assessment'] = {
            'total_secrets': len(intelligence_data['secrets_found']),
            'sensitive_files': len([s for s in successful_scans if self.is_sensitive_path(s['path'])]),
            'recommendations': self.adaptive_learner.get_optimization_suggestions() if self.adaptive_learner else []
        }
        
        print(success(f"Intelligence analysis completed! Secrets: {len(intelligence_data['secrets_found'])}"))
        return intelligence_data
    
    def load_saved_content(self, path: str, output_dir: str) -> str:
        """Load saved content untuk analysis"""
        try:
            # Simplified file loading - you might need proper implementation
            import os
            sanitized_name = path.replace('/', '_').replace('..', '').strip('_')
            
            # Cari file di berbagai可能的 locations
            possible_locations = [
                os.path.join(output_dir, 'files', sanitized_name + '.txt'),
                os.path.join(output_dir, 'files', sanitized_name),
                os.path.join(output_dir, sanitized_name + '.txt'),
                os.path.join(output_dir, sanitized_name),
            ]
            
            for file_path in possible_locations:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read()
            return ""
        except Exception as e:
            print(debug(f"Content loading failed: {e}"))
            return ""
    
    def is_sensitive_path(self, path: str) -> bool:
        """Check if path is sensitive"""
        sensitive_indicators = ['.env', 'config', 'secret', 'password', 'key', 'admin', 'database']
        return any(indicator in path.lower() for indicator in sensitive_indicators)
    
    def final_reporting_phase(self, target_url: str, output_dir: str, scan_results: List[Dict], 
                            intelligence_data: Dict, start_time: float) -> Dict[str, Any]:
        """Generate final reports dan summary"""
        successful_scans = [r for r in scan_results if r.get('success')]
        saved_files = [r for r in successful_scans if r.get('saved')]
        errors = [r for r in scan_results if 'error' in r]
        
        final_report = {
            'target_url': target_url,
            'scan_timestamp': int(time.time()),
            'scan_duration': time.time() - start_time,
            'total_paths_scanned': len(scan_results),
            'successful_finds': len(successful_scans),
            'saved_files': len(saved_files),
            'errors_count': len(errors),
            'successful_paths': [r['path'] for r in successful_scans],
            'intelligence_data': intelligence_data,
            'config_used': self.config
        }
        
        # Save JSON report
        self._start_loading_animation("Generating JSON report...")
        report_path = f"{output_dir}/scan_report.json"
        try:
            import json
            with open(report_path, 'w') as f:
                json.dump(final_report, f, indent=2)
            self._stop_loading_animation()
            print(success(f"JSON Report saved: {report_path}"))
            self.logger.info(f"Scan report saved: {report_path}")
        except Exception as e:
            self._stop_loading_animation()
            print(error(f"Error saving JSON report: {e}"))
        
        # Generate HTML report
        self._start_loading_animation("Generating HTML report...")
        try:
            html_report_path = self.report_generator.generate_html_report(final_report, output_dir)
            self._stop_loading_animation()
            print(success(f"HTML Report saved: {html_report_path}"))
        except Exception as e:
            self._stop_loading_animation()
            print(error(f"Error generating HTML report: {e}"))
        
        # Save learning data
        if self.adaptive_learner:
            try:
                learning_path = f"{output_dir}/learning_data.json"
                self.adaptive_learner.save_learning_data(learning_path)
            except Exception as e:
                print(debug(f"Failed to save learning data: {e}"))
        
        duration_str = f"{final_report['scan_duration']:.1f}s" if final_report['scan_duration'] < 60 else f"{final_report['scan_duration']/60:.1f}m"
        
        print(success(f"\n🎉 SCAN COMPLETED SUCCESSFULLY!"))
        print(info(f"📊 Results: {len(successful_scans)} successful finds, {len(saved_files)} files saved"))
        print(info(f"📁 Output: {output_dir}"))
        print(info(f"⏱️  Duration: {duration_str}"))
        
        return final_report

# Test function untuk natural paths
def test_natural_paths():
    """Test natural paths strategy"""
    print(term.styles.banner("Testing Natural Paths Strategy"))
    
    # Test tanpa discovery modules
    scanner = ScannerEngine()
    
    # Test natural paths generation
    natural_paths = scanner.get_common_paths()
    print(success(f"Generated {len(natural_paths)} natural paths"))
    
    # Show some examples
    print(info("Example natural paths:"))
    for path in natural_paths[:15]:
        print(f"  {path}")
    
    # Test path filtering
    test_paths = ['/api/v2/', '/..///api/v2/', '/config.json', '/api/v2/.bak', '/health/']
    print(info("\nTesting path filtering:"))
    for path in test_paths:
        is_suspicious = scanner._is_suspicious_path(path)
        status = warning("SUSPICIOUS") if is_suspicious else success("NATURAL")
        print(f"  {path} -> {status}")

if __name__ == "__main__":
    test_natural_paths()