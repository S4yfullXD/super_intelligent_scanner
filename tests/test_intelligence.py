import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intelligence.nlp_analyzer import NLPAnalyzer
from intelligence.ml_predictor import MLPredictor

class TestIntelligence(unittest.TestCase):
    
    def setUp(self):
        self.nlp_analyzer = NLPAnalyzer()
        self.ml_predictor = MLPredictor()
    
    def test_secret_detection(self):
        """Test secret detection functionality"""
        test_content = """
        const api_key = "AKIAIOSFODNN7EXAMPLE";
        const password = "secret123";
        """
        
        analysis = self.nlp_analyzer.analyze_content(test_content, 'https://example.com')
        secrets = analysis['secrets_found']
        
        self.assertGreaterEqual(len(secrets), 1)
    
    def test_technology_detection(self):
        """Test technology detection"""
        test_content = """
        React.createElement('div', null, 'Hello World');
        const app = express();
        """
        
        analysis = self.nlp_analyzer.analyze_content(test_content, 'https://example.com')
        technologies = analysis['technologies_detected']
        
        self.assertIn('react', technologies)
        self.assertIn('nodejs', technologies)
    
    def test_ml_training(self):
        """Test ML model training"""
        successful_paths = ['/api/v1/users', '/static/js/main.js', '/api/v2/config']
        self.ml_predictor.train_on_successful_paths(successful_paths)
        
        # Should be able to generate predictions after training
        predictions = self.ml_predictor.predict_new_paths(['users', 'config'], 5)
        self.assertIsInstance(predictions, list)

if __name__ == '__main__':
    unittest.main()