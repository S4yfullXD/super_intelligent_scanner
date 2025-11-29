import unittest
from unittest.mock import Mock, patch
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discovery.intelligent_crawler import intelligent_crawler
from discovery.quantum_fuzzer import QuantumFuzzer

class TestDiscovery(unittest.TestCase):
    
    def setUp(self):
        self.quantum_fuzzer = QuantumFuzzer()
    
    def test_quantum_fuzzing(self):
        """Test quantum fuzzing functionality"""
        base_paths = ['/api/users', '/static/main.js']
        quantum_paths = self.quantum_fuzzer.generate_quantum_paths(base_paths, 10)
        
        self.assertIsInstance(quantum_paths, list)
        self.assertLessEqual(len(quantum_paths), 10)
    
    def test_path_encoding(self):
        """Test path encoding methods"""
        test_path = '/api/v1/users'
        
        encoded_url = self.quantum_fuzzer.apply_encoding(test_path, 'url')
        self.assertIn('%', encoded_url)  # Should be URL encoded
        
        encoded_base64 = self.quantum_fuzzer.apply_encoding(test_path, 'base64')
        self.assertTrue(len(encoded_base64) > 0)
    
    def test_api_detection(self):
        """Test API endpoint detection"""
        self.assertTrue(self.quantum_fuzzer.looks_like_api('/api/v1/users'))
        self.assertTrue(self.quantum_fuzzer.looks_like_api('/graphql'))
        self.assertFalse(self.quantum_fuzzer.looks_like_api('/static/main.js'))

if __name__ == '__main__':
    unittest.main()