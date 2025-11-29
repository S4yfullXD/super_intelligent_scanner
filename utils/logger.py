#!/usr/bin/env python3
"""
Enhanced Logger System dengan Color Integration & Advanced Features
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

# Import our color system
from .colors import term, success, error, warning, info, debug

class ColorFormatter(logging.Formatter):
    """Custom formatter dengan colors untuk console output"""
    
    # Color mapping untuk different log levels
    COLOR_MAP = {
        logging.DEBUG: term.colors.GRAY,
        logging.INFO: term.colors.BRIGHT_BLUE,
        logging.WARNING: term.colors.BRIGHT_YELLOW,
        logging.ERROR: term.colors.BRIGHT_RED,
        logging.CRITICAL: term.colors.BRIGHT_RED + term.colors.BOLD
    }
    
    # Icon mapping untuk different log levels
    ICON_MAP = {
        logging.DEBUG: term.icons.DEBUG,
        logging.INFO: term.icons.INFO,
        logging.WARNING: term.icons.WARNING,
        logging.ERROR: term.icons.ERROR,
        logging.CRITICAL: term.icons.ERROR
    }
    
    def format(self, record):
        """Format log record dengan colors dan icons"""
        # Save original levelname
        original_levelname = record.levelname
        
        # Add color dan icon ke levelname
        color = self.COLOR_MAP.get(record.levelno, term.colors.RESET)
        icon = self.ICON_MAP.get(record.levelno, '')
        
        # Format untuk console (dengan color)
        if self.is_console_handler(record):
            record.levelname = f"{color}{icon} {original_levelname}{term.colors.RESET}"
            record.msg = f"{color}{record.msg}{term.colors.RESET}"
        else:
            # Format untuk file (tanpa color)
            record.levelname = f"{icon} {original_levelname}"
        
        return super().format(record)
    
    def is_console_handler(self, record) -> bool:
        """Check jika handler adalah console handler"""
        if hasattr(record, 'handler_name'):
            return 'console' in record.handler_name
        return any('StreamHandler' in str(h) for h in logging.getLogger().handlers)

def setup_logging(output_dir: str, log_level: str = 'INFO') -> logging.Logger:
    """
    Setup comprehensive logging system dengan color support
    
    Args:
        output_dir: Directory untuk log files
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory
    log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Log file dengan timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'scanner_{timestamp}.log')
    
    # Get logger
    logger = logging.getLogger('super_intelligent_scanner')
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler - detailed format untuk file
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(file_formatter)
    file_handler.set_name('file_handler')
    
    # Console handler - clean format dengan colors
    console_formatter = ColorFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.set_name('console_handler')
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup information
    logger.info(f"Logging system initialized - Level: {log_level}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Output directory: {output_dir}")
    
    return logger

class ScannerLogger:
    """
    Enhanced logger class dengan convenience methods dan color integration
    """
    
    def __init__(self, output_dir: str, log_level: str = 'INFO'):
        self.output_dir = output_dir
        self.logger = setup_logging(output_dir, log_level)
        self.log_file = self._get_latest_log_file(output_dir)
    
    def _get_latest_log_file(self, output_dir: str) -> str:
        """Get path ke latest log file"""
        log_dir = os.path.join(output_dir, 'logs')
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.startswith('scanner_') and f.endswith('.log')]
            if log_files:
                latest = sorted(log_files)[-1]
                return os.path.join(log_dir, latest)
        return "Unknown"
    
    def info(self, message: str, color: bool = True):
        """Log info message"""
        if color:
            # Also print ke console dengan styling
            print(info(message))
        self.logger.info(message)
    
    def warning(self, message: str, color: bool = True):
        """Log warning message"""
        if color:
            print(warning(message))
        self.logger.warning(message)
    
    def error(self, message: str, color: bool = True):
        """Log error message"""
        if color:
            print(error(message))
        self.logger.error(message)
    
    def critical(self, message: str, color: bool = True):
        """Log critical message"""
        if color:
            print(error(f"🚨 CRITICAL: {message}"))
        self.logger.critical(message)
    
    def debug(self, message: str, color: bool = True):
        """Log debug message"""
        if color:
            print(debug(message))
        self.logger.debug(message)
    
    def success(self, message: str, color: bool = True):
        """Log success message (custom level)"""
        if color:
            print(success(message))
        self.logger.info(f"SUCCESS: {message}")
    
    def scan_start(self, target_url: str):
        """Log scan start dengan formatting khusus"""
        self.info(f"🚀 Scan started for: {target_url}")
        self.info(f"📁 Output directory: {self.output_dir}")
        self.info(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def scan_complete(self, duration: float, found_count: int, total_scanned: int):
        """Log scan completion dengan statistics"""
        self.success(f"Scan completed successfully!")
        self.info(f"⏱️  Duration: {duration:.2f} seconds")
        self.info(f"📊 Results: {found_count} found out of {total_scanned} scanned")
        self.info(f"💾 Log file: {self.log_file}")
    
    def phase_start(self, phase_name: str, description: str = ""):
        """Log phase start"""
        message = f"Starting phase: {phase_name}"
        if description:
            message += f" - {description}"
        self.info(message)
    
    def module_status(self, module_name: str, status: bool, details: str = ""):
        """Log module status"""
        status_text = "✅ Enabled" if status else "❌ Disabled"
        message = f"Module {module_name}: {status_text}"
        if details:
            message += f" - {details}"
        
        if status:
            self.info(message)
        else:
            self.warning(message)
    
    def security_finding(self, finding_type: str, path: str, details: str = ""):
        """Log security finding dengan formatting khusus"""
        message = f"🔍 {finding_type.upper()} found: {path}"
        if details:
            message += f" - {details}"
        self.warning(message)
    
    def config_loaded(self, config_path: str):
        """Log configuration load"""
        self.info(f"⚙️  Configuration loaded from: {config_path}")
    
    def get_log_file_path(self) -> str:
        """Get path ke current log file"""
        return self.log_file
    
    def cleanup_old_logs(self, max_age_days: int = 7):
        """Clean up old log files"""
        try:
            log_dir = os.path.join(self.output_dir, 'logs')
            if not os.path.exists(log_dir):
                return
            
            current_time = datetime.now().timestamp()
            max_age_seconds = max_age_days * 24 * 3600
            
            for log_file in os.listdir(log_dir):
                if log_file.startswith('scanner_') and log_file.endswith('.log'):
                    file_path = os.path.join(log_dir, log_file)
                    file_time = os.path.getctime(file_path)
                    
                    if current_time - file_time > max_age_seconds:
                        os.remove(file_path)
                        self.debug(f"Cleaned up old log file: {log_file}")
                        
        except Exception as e:
            self.debug(f"Log cleanup failed: {e}")

# Convenience functions untuk quick logging
def get_logger(output_dir: str, log_level: str = 'INFO') -> ScannerLogger:
    """Quick function untuk get logger instance"""
    return ScannerLogger(output_dir, log_level)

def test_logger():
    """Test the enhanced logger system"""
    print(term.styles.banner("Testing Enhanced Logger System"))
    
    # Test dengan directory di current location (Termux compatible)
    test_dir = "./test_logs"
    os.makedirs(test_dir, exist_ok=True)
    
    try:
        logger = ScannerLogger(test_dir, 'DEBUG')
        
        # Test semua log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message") 
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.success("This is a success message!")
        
        # Test specialized methods
        logger.scan_start("https://example.com")
        logger.phase_start("Discovery", "Finding endpoints")
        logger.module_status("ML Predictor", True, "All features available")
        logger.security_finding("API Key", "/api/config", "Hardcoded key found")
        logger.scan_complete(125.5, 15, 200)
        
        print(success("Logger test completed!"))
        print(info(f"Log file: {logger.get_log_file_path()}"))
        
        # Cleanup test directory
        import shutil
        shutil.rmtree(test_dir)
        print(info("Test directory cleaned up"))
        
    except Exception as e:
        print(error(f"Logger test failed: {e}"))

if __name__ == "__main__":
    test_logger()