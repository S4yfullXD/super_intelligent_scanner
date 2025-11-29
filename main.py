#!/usr/bin/env python3
"""
Super Intelligent Web Scanner - Main Entry Point
Advanced AI-powered web security scanner with intelligent discovery
"""

import os
import sys
import argparse
import time
import signal
import re
from typing import Optional, Dict, Any

# Add current directory to path for module imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.scanner_engine import ScannerEngine
from utils.helpers import (
    print_banner, 
    validate_url, 
    is_termux_environment, 
    check_dependencies,
    calculate_scan_duration
)
from utils.config_loader import ConfigLoader
from external.github_resources import GitHubResourceManager

# Global variable untuk handle interrupt
current_scanner = None

def signal_handler(signum, frame):
    """Handle interrupt signals gracefully"""
    print(f"\n\n⚠️  Received interrupt signal. Shutting down gracefully...")
    if current_scanner and hasattr(current_scanner, 'stop_scan'):
        current_scanner.stop_scan()
    sys.exit(1)

def setup_environment() -> Dict[str, bool]:
    """Setup application environment and check dependencies"""
    print("🔧 Setting up environment...")
    
    # Create necessary directories
    directories = ["results", "resources/data", "resources/models", "outputs/scans", "outputs/reports", "outputs/logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    available_features = check_dependencies()
    
    # Update config based on available dependencies
    config = ConfigLoader.load_config()
    
    # Apply dependency-based feature toggling
    if not available_features.get('ml', False):
        config['intelligence']['enable_ml'] = False
        print("   ⚠️  ML features disabled (scikit-learn not available)")
    else:
        print("   ✅ ML features enabled")
    
    if not available_features.get('nlp', False):
        config['intelligence']['enable_nlp'] = False
        print("   ⚠️  NLP features disabled (nltk not available)")
    else:
        print("   ✅ NLP features enabled")
    
    if not available_features.get('vision', False):
        config['intelligence']['enable_vision'] = False
        print("   ⚠️  Vision features disabled (opencv not available)")
    else:
        print("   ✅ Vision features enabled")
    
    if not available_features.get('async', False):
        print("   ⚠️  Async features disabled (aiohttp not available)")
    else:
        print("   ✅ Async features enabled")
    
    return available_features

def download_resources_if_needed():
    """Download resources if auto-download is enabled"""
    config = ConfigLoader.load_config()
    if config['resources']['auto_download']:
        print("🌐 Checking for resource updates...")
        try:
            resource_manager = GitHubResourceManager()
            resource_manager.download_resources()
            print("   ✅ Resources updated successfully")
        except Exception as e:
            print(f"   ⚠️  Resource download failed: {e}")
            print("   💡 Continuing with local resources...")
    else:
        print("   ℹ️  Auto-download disabled in config")

def display_system_info():
    """Display system and environment information"""
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    
    # Environment
    if is_termux_environment():
        print("📱 Environment: Termux (Mobile Optimized)")
    else:
        print("💻 Environment: Standard")
    
    # Python version
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    # Config info
    config = ConfigLoader.load_config()
    print(f"🔧 Workers: {config['scanning']['max_workers']}")
    print(f"⏱️  Timeout: {config['scanning']['timeout']}s")
    print(f"🛡️  Stealth: {'Enabled' if config['evasion']['stealth_mode'] else 'Disabled'}")
    
    # Feature status
    print(f"🤖 ML: {'Enabled' if config['intelligence']['enable_ml'] else 'Disabled'}")
    print(f"📝 NLP: {'Enabled' if config['intelligence']['enable_nlp'] else 'Disabled'}")
    print(f"👁️  Vision: {'Enabled' if config['intelligence']['enable_vision'] else 'Disabled'}")
    
    print("="*60)

def validate_and_fix_url(target_url: str) -> Optional[str]:
    """Validate URL and attempt to fix common issues"""
    if not target_url:
        return None
    
    # Basic cleaning
    target_url = target_url.strip()
    
    # Remove any leading -- from URLs (fix for argument parsing issue)
    if target_url.startswith('--'):
        target_url = target_url[2:]
        print(f"   🔧 Fixed URL: removed leading '--'")
    
    # Check if it's already a valid URL
    if validate_url(target_url):
        return target_url
    
    # Try to fix common issues
    fixes_attempted = []
    
    # Add protocol if missing
    if not target_url.startswith(('http://', 'https://')):
        target_url = 'https://' + target_url
        fixes_attempted.append("Added HTTPS protocol")
    
    # Validate again after fixes
    if validate_url(target_url):
        if fixes_attempted:
            print("   🔧 Applied fixes:", " | ".join(fixes_attempted))
        return target_url
    
    # If still invalid, show error
    print("   ❌ Invalid URL format. Please use:")
    print("      https://example.com")
    print("      http://localhost:3000")
    print("      https://subdomain.example.com")
    return None

def interactive_mode():
    """Run scanner in interactive mode"""
    print_banner()
    display_system_info()
    
    scan_count = 0
    
    while True:
        try:
            scan_count += 1
            print(f"\n🎯 SCAN SESSION #{scan_count}")
            print("-" * 40)
            
            # Get target URL
            target_url = input("\n🎯 Enter target URL (or 'quit' to exit): ").strip()
            
            if target_url.lower() in ['quit', 'exit', 'q', '']:
                print("\n👋 Thank you for using Super Intelligent Scanner!")
                break
            
            # Validate and fix URL
            validated_url = validate_and_fix_url(target_url)
            if not validated_url:
                continue
            
            # Confirm scan
            print(f"\n🔍 Ready to scan: {validated_url}")
            print("   This will:")
            print("   - Discover website structure and endpoints")
            print("   - Analyze content for security insights") 
            print("   - Generate comprehensive reports")
            print("   - Save findings to organized folders")
            
            confirm = input("\n✅ Proceed with scan? (y/N): ").strip().lower()
            
            if confirm not in ['y', 'yes']:
                print("   ⏹️  Scan cancelled")
                continue
            
            # Download resources if needed
            download_resources_if_needed()
            
            # Initialize and start scanner
            start_time = time.time()
            global current_scanner
            scanner = ScannerEngine()
            current_scanner = scanner
            
            print(f"\n🚀 STARTING INTELLIGENT SCAN...")
            print("=" * 60)
            
            results = scanner.start_scan(validated_url)
            current_scanner = None
            
            # Display comprehensive results
            scan_duration = time.time() - start_time
            display_scan_results(results, scan_duration, validated_url)
            
            # Ask if user wants to scan another target
            another = input("\n🔄 Scan another target? (y/N): ").strip().lower()
            if another not in ['y', 'yes']:
                print("\n👋 Thank you for using Super Intelligent Scanner!")
                print("   Check the 'results/' folder for your scan outputs.")
                break
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Scan interrupted by user")
            current_scanner = None
            break
        except Exception as e:
            print(f"\n❌ Scan failed: {e}")
            import traceback
            traceback.print_exc()
            current_scanner = None
            
            # Ask if user wants to try again
            retry = input("\n🔄 Try again? (y/N): ").strip().lower()
            if retry not in ['y', 'yes']:
                break

def display_scan_results(results: Dict[str, Any], scan_duration: float, target_url: str):
    """Display comprehensive scan results"""
    print(f"\n🎉 SCAN COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    # Basic statistics
    print("📊 SCAN STATISTICS:")
    print(f"   🎯 Target: {results['target_url']}")
    print(f"   ⏱️  Duration: {calculate_scan_duration(scan_duration)}")
    print(f"   📁 Files Saved: {results['saved_files']}")
    print(f"   ✅ Successful Finds: {results['successful_finds']}")
    print(f"   📋 Paths Scanned: {results['total_paths_scanned']}")
    print(f"   ❌ Errors: {results['errors_count']}")
    
    # Intelligence insights
    if 'intelligence_data' in results:
        intel = results['intelligence_data']
        
        # Secrets found
        secrets_count = len(intel.get('secrets_found', []))
        if secrets_count > 0:
            print(f"\n🔐 SECURITY FINDINGS:")
            print(f"   🚨 Secrets Found: {secrets_count}")
            for secret in intel.get('secrets_found', [])[:3]:  # Show first 3
                print(f"      - {secret.get('type', 'Unknown')}: {secret.get('value', 'N/A')}")
            if secrets_count > 3:
                print(f"      ... and {secrets_count - 3} more")
        
        # Technologies detected
        technologies = intel.get('technologies_detected', [])
        if technologies:
            print(f"   🛠️  Technologies: {', '.join(technologies[:5])}")
            if len(technologies) > 5:
                print(f"      ... and {len(technologies) - 5} more")
    
    # Risk assessment
    if 'intelligence_data' in results and 'risk_assessment' in results['intelligence_data']:
        risk_data = results['intelligence_data']['risk_assessment']
        total_secrets = risk_data.get('total_secrets', 0)
        sensitive_files = risk_data.get('sensitive_files', 0)
        
        if total_secrets > 0 or sensitive_files > 0:
            print(f"\n⚠️  RISK ASSESSMENT:")
            if total_secrets > 0:
                print(f"   🔴 {total_secrets} secrets exposed - HIGH RISK")
            if sensitive_files > 0:
                print(f"   🟡 {sensitive_files} sensitive files exposed - MEDIUM RISK")
    
    # Output information
    print(f"\n📄 OUTPUT FILES:")
    print(f"   📋 JSON Report: scan_report.json (Detailed data)")
    print(f"   🌐 HTML Report: detailed_report.html (Visual report)")
    print(f"   📁 Saved Files: Organized in categorized folders")
    print(f"   📊 Scan Logs: scanner.log (Execution details)")
    
    # Output location
    output_dir = f"results/{target_url.split('//')[1].split('/')[0]}" if '//' in target_url else "results/unknown"
    print(f"\n📁 OUTPUT LOCATION:")
    print(f"   {output_dir}_*/")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if results['saved_files'] > 0:
        print("   1. Review saved files in categorized folders")
        print("   2. Check for exposed credentials and secrets")
        print("   3. Analyze API endpoints for security issues")
    else:
        print("   1. Target appears well-secured")
        print("   2. Consider testing with different configurations")
        print("   3. Verify target is accessible and scanable")
    
    print("   4. Implement security recommendations from HTML report")

def quick_scan_mode(target_url: str, quick_mode: bool = False):
    """Run scanner in quick mode with provided URL"""
    print_banner()
    mode_label = "🚀 QUICK SCAN MODE" if quick_mode else "🔍 STANDARD SCAN MODE"
    print(f"{mode_label}")
    print("=" * 50)
    
    # Validate URL
    validated_url = validate_and_fix_url(target_url)
    if not validated_url:
        print("❌ Invalid URL provided")
        return
    
    print(f"🎯 Target: {validated_url}")
    print("⏰ Starting scan...")
    
    try:
        # Download resources if needed
        download_resources_if_needed()
        
        # Start scan
        start_time = time.time()
        global current_scanner
        scanner = ScannerEngine()
        current_scanner = scanner
        
        # Apply quick scan settings if requested
        if quick_mode:
            config = ConfigLoader.load_config()
            config['scanning']['max_workers'] = min(config['scanning']['max_workers'], 5)
            config['discovery']['max_depth'] = min(config['discovery']['max_depth'], 2)
            print("   ⚡ Quick scan optimizations applied")
        
        results = scanner.start_scan(validated_url)
        current_scanner = None
        
        # Display quick summary
        scan_duration = time.time() - start_time
        print(f"\n✅ Scan completed in {calculate_scan_duration(scan_duration)}")
        print(f"📁 {results['saved_files']} files saved")
        print(f"✅ {results['successful_finds']} successful finds")
        print(f"📋 {results['total_paths_scanned']} paths scanned")
        
        # Quick security alert
        if 'intelligence_data' in results:
            secrets_count = len(results['intelligence_data'].get('secrets_found', []))
            if secrets_count > 0:
                print(f"🚨 {secrets_count} SECRETS FOUND - Check reports!")
        
    except KeyboardInterrupt:
        print(f"\n⏹️  Scan interrupted by user")
        current_scanner = None
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        current_scanner = None

def batch_scan_mode(file_path: str, quick_mode: bool = False):
    """Run scanner in batch mode with URLs from file"""
    print_banner()
    mode_label = "📁 BATCH QUICK SCAN MODE" if quick_mode else "📁 BATCH SCAN MODE"
    print(f"{mode_label}")
    print("=" * 50)
    
    try:
        with open(file_path, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        print(f"📋 Found {len(urls)} URLs to scan")
        download_resources_if_needed()
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Scanning: {url}")
            
            validated_url = validate_and_fix_url(url)
            if not validated_url:
                print("   ❌ Skipping invalid URL")
                continue
            
            try:
                start_time = time.time()
                scanner = ScannerEngine()
                
                # Apply quick scan settings if requested
                if quick_mode:
                    config = ConfigLoader.load_config()
                    config['scanning']['max_workers'] = min(config['scanning']['max_workers'], 3)
                    config['discovery']['max_depth'] = 1
                
                results = scanner.start_scan(validated_url)
                
                duration = time.time() - start_time
                print(f"   ✅ Completed in {duration:.1f}s - {results['saved_files']} files saved")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
    
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
    except Exception as e:
        print(f"❌ Batch scan failed: {e}")

def main():
    """Main entry point with command line support"""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Pre-process arguments to handle URLs with -- prefix
    processed_args = []
    for arg in sys.argv[1:]:
        if arg.startswith('--http'):
            # Convert --https://example.com to https://example.com
            processed_args.append(arg[2:])
        else:
            processed_args.append(arg)
    
    parser = argparse.ArgumentParser(
        description='🧠🚀 Super Intelligent Scanner - Advanced AI-powered web security scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Interactive mode
  %(prog)s https://example.com # Quick scan
  %(prog)s -i                 # Interactive mode  
  %(prog)s -b urls.txt        # Batch scan from file
  %(prog)s -u https://example.com --quick-scan  # Quick scan with URL
  %(prog)s --help             # Show this help

For more information, see the documentation in docs/ folder.
        """
    )
    
    # FIXED ARGUMENT DEFINITIONS
    parser.add_argument('url', nargs='?', help='Target URL for quick scan (positional)')
    parser.add_argument('--url', '-u', help='Target URL for scanning (alternative)')
    parser.add_argument('--quick-scan', '-q', action='store_true', help='Run quick scan mode')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--batch', '-b', metavar='FILE', help='Batch scan URLs from file')
    parser.add_argument('--version', '-v', action='store_true', help='Show version information')
    
    # Use processed arguments instead of sys.argv
    args = parser.parse_args(processed_args)
    
    # Show version
    if args.version:
        print("Super Intelligent Scanner v1.0.0")
        print("Advanced AI-powered web security scanner")
        return
    
    # Setup environment
    available_features = setup_environment()
    
    try:
        # Determine which URL to use (positional or --url)
        target_url = args.url if args.url else args.url
        
        if args.batch:
            # Batch scan mode
            batch_scan_mode(args.batch, args.quick_scan)
        elif target_url:
            # Quick scan mode with provided URL
            quick_scan_mode(target_url, args.quick_scan)
        elif args.interactive:
            # Interactive mode
            interactive_mode()
        else:
            # Default to interactive mode
            interactive_mode()
            
    except KeyboardInterrupt:
        print(f"\n\n👋 Scanner stopped by user")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()