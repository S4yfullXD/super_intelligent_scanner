#!/usr/bin/env python3
"""
Centralized Color & Styling System
Untuk semua output terminal yang keren!
"""

class Colors:
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
    # Normal Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    GRAY = '\033[90m'
    
    # Bright Colors  
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Backgrounds
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class Icons:
    # Status Icons
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠️'
    INFO = 'ℹ️'
    DEBUG = '🐛'
    LOADING = '🔄'
    
    # Scanner Icons
    SCAN = '🔍'
    TARGET = '🎯'
    BANNER = '🧠🚀'
    STEALTH = '🛡️'
    INTELLIGENCE = '🤖'
    REPORT = '📊'
    
    # File Icons
    FOLDER = '📁'
    FILE = '📄'
    SAVE = '💾'
    
    # Time Icons
    TIME = '⏱️'
    HOURGLASS = '⏳'
    
    # Network Icons
    NETWORK = '🌐'
    SERVER = '🖥️'
    LOCK = '🔒'
    UNLOCK = '🔓'
    
    # Action Icons
    START = '🚀'
    STOP = '🛑'
    SETTINGS = '⚙️'
    DOWNLOAD = '📥'
    UPLOAD = '📤'

class Styles:
    """Pre-defined styled messages"""
    
    @staticmethod
    def banner(text):
        return f"{Colors.BRIGHT_CYAN}{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text):
        return f"{Colors.BRIGHT_GREEN}{Icons.SUCCESS} {text}{Colors.RESET}"
    
    @staticmethod
    def error(text):
        return f"{Colors.BRIGHT_RED}{Icons.ERROR} {text}{Colors.RESET}"
    
    @staticmethod
    def warning(text):
        return f"{Colors.BRIGHT_YELLOW}{Icons.WARNING} {text}{Colors.RESET}"
    
    @staticmethod
    def info(text):
        return f"{Colors.BRIGHT_BLUE}{Icons.INFO} {text}{Colors.RESET}"
    
    @staticmethod
    def debug(text):
        return f"{Colors.GRAY}{Icons.DEBUG} {text}{Colors.RESET}"
    
    @staticmethod
    def scan(text):
        return f"{Colors.BRIGHT_MAGENTA}{Icons.SCAN} {text}{Colors.RESET}"
    
    @staticmethod
    def target(text):
        return f"{Colors.BRIGHT_CYAN}{Icons.TARGET} {text}{Colors.RESET}"

class ScannerMessages:
    """Scanner-specific message templates"""
    
    @staticmethod
    def scan_start(target):
        return f"{Styles.scan('STARTING SCAN')} {Styles.target(target)}"
    
    @staticmethod
    def found(url, status=200, details=""):
        base = f"{Colors.BRIGHT_GREEN}{Icons.SUCCESS} FOUND: {url} (Status: {status}){Colors.RESET}"
        if details:
            base += f"\n   {Colors.GRAY}{details}{Colors.RESET}"
        return base
    
    @staticmethod
    def forbidden(url, details=""):
        base = f"{Colors.BRIGHT_YELLOW}{Icons.LOCK} FORBIDDEN: {url}{Colors.RESET}"
        if details:
            base += f"\n   {Colors.GRAY}{details}{Colors.RESET}"
        return base
    
    @staticmethod
    def blocked(url, details=""):
        base = f"{Colors.BRIGHT_RED}{Icons.ERROR} BLOCKED: {url}{Colors.RESET}"
        if details:
            base += f"\n   {Colors.GRAY}{details}{Colors.RESET}"
        return base
    
    @staticmethod
    def error(url, error_msg):
        return f"{Colors.RED}{Icons.ERROR} ERROR: {url} - {error_msg}{Colors.RESET}"
    
    @staticmethod
    def progress(current, total, prefix=""):
        percent = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        return f"{Colors.BRIGHT_CYAN}{prefix} |{bar}| {current}/{total} ({percent:.1f}%){Colors.RESET}"

# Quick access functions
def success(text): return Styles.success(text)
def error(text): return Styles.error(text)
def warning(text): return Styles.warning(text)
def info(text): return Styles.info(text)
def debug(text): return Styles.debug(text)
def scan(text): return Styles.scan(text)
def target(text): return Styles.target(text)

# Global instance for easy access
class Terminal:
    colors = Colors
    icons = Icons
    styles = Styles
    scan_msg = ScannerMessages

# Short alias
term = Terminal()