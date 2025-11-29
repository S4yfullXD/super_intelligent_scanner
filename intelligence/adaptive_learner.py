import time
import re  # ← INI YANG DITAMBAH
import json
import os
from typing import Dict, List, Any
from collections import defaultdict

class AdaptiveLearner:
    def __init__(self):
        self.learning_data = []
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.performance_stats = {
            'total_scans': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'average_response_time': 0,
            'common_success_paths': []
        }
        
    def record_scan_result(self, url: str, path: str, success: bool, 
                         response_time: float, status_code: int, content_length: int):
        """Record scan result for learning"""
        scan_data = {
            'timestamp': time.time(),
            'url': url,
            'path': path,
            'success': success,
            'response_time': response_time,
            'status_code': status_code,
            'content_length': content_length,
            'path_pattern': self.analyze_path_pattern(path)
        }
        
        self.learning_data.append(scan_data)
        self.performance_stats['total_scans'] += 1
        
        if success:
            self.performance_stats['successful_scans'] += 1
            self.success_patterns[scan_data['path_pattern']].append(scan_data)
        else:
            self.performance_stats['failed_scans'] += 1
            self.failure_patterns[scan_data['path_pattern']].append(scan_data)
        
        # Update performance stats
        self.update_performance_stats()
        
        # Keep only recent data for performance
        if len(self.learning_data) > 1000:
            self.learning_data = self.learning_data[-500:]
    
    def analyze_path_pattern(self, path: str) -> str:
        """Analyze path to extract pattern"""
        if not path:
            return 'unknown'
        
        # Replace specific values with patterns
        pattern = path
        
        # Replace numbers with {id}
        pattern = re.sub(r'/\d+', '/{id}', pattern)  # ← FIXED: removed extra backslash
        
        # Replace UUIDs with {uuid}
        pattern = re.sub(r'/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '/{uuid}', pattern, flags=re.IGNORECASE)
        
        # Replace common variable patterns
        pattern = re.sub(r'/[a-z]+_id', '/{param}', pattern)
        pattern = re.sub(r'/[a-z]+_name', '/{param}', pattern)
        
        return pattern
    
    def update_performance_stats(self):
        """Update performance statistics"""
        if not self.learning_data:
            return
        
        # Calculate average response time from recent scans
        recent_scans = self.learning_data[-100:]
        response_times = [scan['response_time'] for scan in recent_scans if scan['response_time'] > 0]
        
        if response_times:
            self.performance_stats['average_response_time'] = sum(response_times) / len(response_times)
        
        # Find common successful paths
        success_paths = [scan['path'] for scan in self.learning_data if scan['success']]
        if success_paths:
            from collections import Counter
            path_counter = Counter(success_paths)
            self.performance_stats['common_success_paths'] = [path for path, count in path_counter.most_common(5)]
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """Get optimization suggestions based on learning"""
        suggestions = {
            'increase_delay': False,
            'decrease_workers': False,
            'focus_paths': [],
            'avoid_paths': []
        }
        
        # Check if we're getting rate limited
        recent_failures = [scan for scan in self.learning_data[-50:] if not scan['success']]
        rate_limit_failures = [scan for scan in recent_failures if scan['status_code'] in [429, 403]]
        
        if len(rate_limit_failures) > len(recent_failures) * 0.3:  # 30% rate limit errors
            suggestions['increase_delay'] = True
            suggestions['decrease_workers'] = True
        
        # Suggest paths to focus on
        successful_patterns = []
        for pattern, scans in self.success_patterns.items():
            success_rate = len(scans) / max(1, len(scans) + len(self.failure_patterns.get(pattern, [])))
            if success_rate > 0.5:  # More than 50% success rate
                successful_patterns.append((pattern, success_rate))
        
        successful_patterns.sort(key=lambda x: x[1], reverse=True)
        suggestions['focus_paths'] = [pattern for pattern, rate in successful_patterns[:5]]
        
        # Suggest paths to avoid
        failure_patterns = []
        for pattern, scans in self.failure_patterns.items():
            failure_rate = len(scans) / max(1, len(scans) + len(self.success_patterns.get(pattern, [])))
            if failure_rate > 0.8:  # More than 80% failure rate
                failure_patterns.append((pattern, failure_rate))
        
        failure_patterns.sort(key=lambda x: x[1], reverse=True)
        suggestions['avoid_paths'] = [pattern for pattern, rate in failure_patterns[:5]]
        
        return suggestions
    
    def save_learning_data(self, filepath: str):
        """Save learning data to file"""
        try:
            data_to_save = {
                'learning_data': self.learning_data[-200:],  # Keep only recent
                'performance_stats': self.performance_stats,
                'timestamp': time.time()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving learning data: {e}")
    
    def load_learning_data(self, filepath: str):
        """Load learning data from file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                self.learning_data = data.get('learning_data', [])
                self.performance_stats = data.get('performance_stats', self.performance_stats)
                
                # Rebuild pattern databases
                for scan in self.learning_data:
                    pattern = scan.get('path_pattern', self.analyze_path_pattern(scan.get('path', '')))
                    if scan.get('success'):
                        self.success_patterns[pattern].append(scan)
                    else:
                        self.failure_patterns[pattern].append(scan)
                        
            except Exception as e:
                print(f"❌ Error loading learning data: {e}")