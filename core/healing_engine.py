#!/usr/bin/env python3
"""
Enhanced Healing Engine dengan Color Integration & Adaptive Recovery
Intelligent error recovery system dengan learning capabilities
"""

import time
import random
from typing import Callable, Any, Dict, Optional
from datetime import datetime

# Import our color system
from utils.colors import term, success, error, warning, info, debug

class HealingEngine:
    def __init__(self, max_retries: int = 3, enable_learning: bool = True):
        self.max_retries = max_retries
        self.enable_learning = enable_learning
        self.retry_count = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        self.error_patterns = {}
        self.recovery_strategies = self._initialize_strategies()
        self.learning_data = {
            'total_operations': 0,
            'successful_operations': 0,
            'recovery_attempts': 0,
            'common_errors': {}
        }
    
    def _initialize_strategies(self) -> Dict[str, Callable]:
        """Initialize comprehensive healing strategies"""
        return {
            'ConnectionError': self.heal_connection,
            'TimeoutError': self.heal_timeout,
            'Timeout': self.heal_timeout,
            'TooManyRedirects': self.heal_redirects,
            'SSLError': self.heal_ssl,
            'ProxyError': self.heal_proxy,
            'ConnectionRefusedError': self.heal_connection_refused,
            'HTTPError': self.heal_http,
            'RequestException': self.heal_request,
            'BlockedByWAF': self.heal_waf,
            'RateLimited': self.heal_rate_limit
        }
    
    def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function dengan intelligent retry and adaptive healing
        
        Args:
            func: Function untuk execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result jika successful
            
        Raises:
            Original exception jika semua attempts failed
        """
        self.learning_data['total_operations'] += 1
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                debug(f"Healing attempt {attempt + 1}/{self.max_retries} for {func.__name__}")
                
                result = func(*args, **kwargs)
                
                # Success - update learning data
                self.learning_data['successful_operations'] += 1
                self.retry_count = 0
                
                if attempt > 0:  # Jika berhasil setelah retry
                    self.successful_recoveries += 1
                    success(f"✅ Recovery successful on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_exception = e
                self.retry_count += 1
                self.learning_data['recovery_attempts'] += 1
                
                error_type = type(e).__name__
                error_msg = str(e)
                
                # Update error patterns untuk learning
                self._update_error_patterns(error_type, error_msg)
                
                warning(f"Attempt {attempt + 1}/{self.max_retries} failed: {error_type} - {error_msg}")
                
                if attempt < self.max_retries - 1:
                    # Apply intelligent healing strategy
                    healing_applied = self._apply_healing_strategy(error_type, attempt, error_msg)
                    
                    if healing_applied:
                        info(f"🔧 Applied healing strategy for {error_type}")
                    else:
                        debug(f"No specific healing strategy for {error_type}, using generic")
                    
                    continue
                else:
                    # Final attempt failed
                    self.failed_recoveries += 1
                    error(f"❌ All {self.max_retries} recovery attempts failed for {func.__name__}")
                    break
        
        # Jika semua attempts failed, raise original exception
        if last_exception:
            self._learn_from_failure(func.__name__, last_exception)
            raise last_exception
        
        return None
    
    def _apply_healing_strategy(self, error_type: str, attempt: int, error_msg: str) -> bool:
        """Apply appropriate healing strategy berdasarkan error type"""
        self.learning_data['recovery_attempts'] += 1
        
        # Get healing strategy
        strategy = self.recovery_strategies.get(error_type, self.heal_generic)
        
        # Apply strategy dengan attempt-aware parameters
        try:
            strategy(attempt, error_msg)
            return True
        except Exception as e:
            debug(f"Healing strategy failed: {e}")
            # Fallback ke generic healing
            self.heal_generic(attempt, error_msg)
            return False
    
    def _update_error_patterns(self, error_type: str, error_msg: str):
        """Update error patterns untuk adaptive learning"""
        if self.enable_learning:
            if error_type not in self.learning_data['common_errors']:
                self.learning_data['common_errors'][error_type] = {
                    'count': 0,
                    'last_occurred': datetime.now().isoformat(),
                    'sample_messages': set()
                }
            
            self.learning_data['common_errors'][error_type]['count'] += 1
            self.learning_data['common_errors'][error_type]['last_occurred'] = datetime.now().isoformat()
            
            # Keep sample messages (max 5)
            messages = self.learning_data['common_errors'][error_type]['sample_messages']
            if len(messages) < 5:
                messages.add(error_msg[:100])  # Truncate long messages
    
    def _learn_from_failure(self, function_name: str, exception: Exception):
        """Learn from final failures untuk future improvements"""
        if self.enable_learning:
            error_type = type(exception).__name__
            debug(f"Learning from failure: {function_name} -> {error_type}")
            
            # Bisa extend ini untuk lebih sophisticated learning
            # Contoh: adjust strategies based on failure patterns
    
    def heal_connection(self, attempt: int, error_msg: str = ""):
        """Heal connection-related issues dengan adaptive backoff"""
        base_delay = 2.0
        delay = base_delay * (attempt + 1) + random.uniform(0.5, 2.0)
        
        info(f"🔌 Healing connection issue... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_timeout(self, attempt: int, error_msg: str = ""):
        """Heal timeout issues dengan progressive delays"""
        base_delay = 3.0
        delay = base_delay * (attempt + 1) * 1.5  # More aggressive untuk timeouts
        
        info(f"⏰ Healing timeout... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_redirects(self, attempt: int, error_msg: str = ""):
        """Heal redirect issues"""
        delay = 1.0 + attempt * 0.5
        
        info(f"🔄 Healing redirect issue... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_ssl(self, attempt: int, error_msg: str = ""):
        """Heal SSL-related issues"""
        delay = 2.0 + attempt
        
        warning(f"🔒 Healing SSL issue... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_proxy(self, attempt: int, error_msg: str = ""):
        """Heal proxy-related issues"""
        delay = 3.0 + attempt * 2
        
        info(f"🌐 Healing proxy issue... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_connection_refused(self, attempt: int, error_msg: str = ""):
        """Heal connection refused errors"""
        delay = 5.0 + attempt * 3  # Longer delays untuk connection refused
        
        warning(f"🚫 Healing connection refused... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_http(self, attempt: int, error_msg: str = ""):
        """Heal HTTP error responses"""
        delay = 2.0 + attempt * 1.5
        
        info(f"🌍 Healing HTTP error... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_request(self, attempt: int, error_msg: str = ""):
        """Heal general request exceptions"""
        delay = 1.5 + attempt
        
        info(f"📡 Healing request exception... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_waf(self, attempt: int, error_msg: str = ""):
        """Heal WAF blocking issues"""
        delay = 10.0 + attempt * 5  # Significant delays untuk WAF
        
        warning(f"🛡️  Healing WAF block... waiting {delay:.1f}s (consider rotating IP)")
        time.sleep(delay)
    
    def heal_rate_limit(self, attempt: int, error_msg: str = ""):
        """Heal rate limiting issues"""
        delay = 15.0 + attempt * 10  # Very long delays untuk rate limits
        
        warning(f"🚦 Healing rate limit... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def heal_generic(self, attempt: int, error_msg: str = ""):
        """Generic healing strategy dengan jitter"""
        base_delay = 2.0
        delay = base_delay * (attempt + 1) + random.uniform(0.1, 1.5)
        
        debug(f"⚕️  Applying generic healing... waiting {delay:.1f}s")
        time.sleep(delay)
    
    def get_healing_stats(self) -> Dict[str, Any]:
        """Get comprehensive healing statistics"""
        total_recoveries = self.successful_recoveries + self.failed_recoveries
        success_rate = (self.successful_recoveries / total_recoveries * 100) if total_recoveries > 0 else 0
        
        return {
            'total_operations': self.learning_data['total_operations'],
            'successful_operations': self.learning_data['successful_operations'],
            'success_rate': f"{success_rate:.1f}%",
            'successful_recoveries': self.successful_recoveries,
            'failed_recoveries': self.failed_recoveries,
            'total_recovery_attempts': self.learning_data['recovery_attempts'],
            'common_errors': dict(sorted(
                self.learning_data['common_errors'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )),
            'learning_enabled': self.enable_learning,
            'available_strategies': list(self.recovery_strategies.keys())
        }
    
    def reset_learning(self):
        """Reset learning data"""
        self.learning_data = {
            'total_operations': 0,
            'successful_operations': 0,
            'recovery_attempts': 0,
            'common_errors': {}
        }
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        info("Healing engine learning data reset")
    
    def optimize_strategies(self):
        """Optimize healing strategies based on learned data"""
        if not self.enable_learning:
            return
        
        # Analyze common errors dan adjust strategies
        common_errors = self.learning_data['common_errors']
        
        if common_errors:
            info("Optimizing healing strategies based on learned patterns...")
            
            for error_type, data in common_errors.items():
                if data['count'] > 5:  # Jika error sering terjadi
                    debug(f"Frequent error: {error_type} ({data['count']} occurrences)")
                    # Bisa implement strategy adjustments di sini
    
    def test_healing_engine(self):
        """Test the healing engine dengan simulated failures"""
        info("Testing healing engine...")
        
        def failing_function(attempts_to_succeed: int = 2):
            """Test function yang fails beberapa kali sebelum success"""
            if not hasattr(failing_function, 'call_count'):
                failing_function.call_count = 0
            
            failing_function.call_count += 1
            
            if failing_function.call_count < attempts_to_succeed:
                raise ConnectionError(f"Simulated failure #{failing_function.call_count}")
            
            return f"Success after {failing_function.call_count} attempts"
        
        try:
            result = self.execute_with_retry(failing_function, 3)
            success(f"Healing test result: {result}")
            
            # Show stats
            stats = self.get_healing_stats()
            print(info("Healing Statistics:"))
            for key, value in stats.items():
                if key != 'common_errors':  # Skip detailed errors untuk display
                    print(f"  {key}: {value}")
            
            return True
            
        except Exception as e:
            error(f"Healing test failed: {e}")
            return False

# Quick test function
def test_healing_engine():
    """Test the enhanced healing engine"""
    print(term.styles.banner("Testing Enhanced Healing Engine"))
    
    healer = HealingEngine(max_retries=4, enable_learning=True)
    
    if healer.test_healing_engine():
        print(success("Healing engine test completed successfully!"))
    else:
        print(error("Healing engine test failed!"))

if __name__ == "__main__":
    test_healing_engine()