import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import validate_url, generate_random_string, sanitize_filename
from utils.file_organizer import detect_content_language

class TestUtils(unittest.TestCase):
    
    def test_url_validation(self):
        """Test URL validation"""
        self.assertTrue(validate_url('https://example.com'))
        self.assertTrue(validate_url('http://localhost:3000'))
        self.assertFalse(validate_url('invalid-url'))
        self.assertFalse(validate_url(''))
    
    def test_random_string(self):
        """Test random string generation"""
        random_str = generate_random_string(10)
        self.assertEqual(len(random_str), 10)
        self.assertTrue(random_str.isalnum())
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        dirty_name = 'file<with>invalid"chars?.txt'
        clean_name = sanitize_filename(dirty_name)
        
        self.assertNotIn('<', clean_name)
        self.assertNotIn('>', clean_name)
        self.assertNotIn('"', clean_name)
        self.assertNotIn('?', clean_name)
    
    def test_content_language_detection(self):
        """Test content language detection"""
        # Test JavaScript detection
        js_content = "function test() { console.log('hello'); }"
        self.assertEqual(detect_content_language(js_content), 'javascript')
        
        # Test HTML detection
        html_content = "<html><body>Hello</body></html>"
        self.assertEqual(detect_content_language(html_content), 'html')
        
        # Test JSON detection
        json_content = '{"name": "test", "value": 123}'
        self.assertEqual(detect_content_language(json_content), 'json')

if __name__ == '__main__':
    unittest.main()