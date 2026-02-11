import unittest
from unittest.mock import MagicMock, patch
import json
from flask import Flask
from backend.api import app
from backend.schemas import ScoreEnum

class TestPhase4(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('backend.database.EvalSession')
    @patch('backend.api.jwt.decode')
    def test_submit_success(self, mock_jwt, mock_session_cls):
        # Mock Auth
        mock_jwt.return_value = {'user': 'testuser'}
        
        # Mock DB Session
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        payload = {
            "chat_id": 123,
            "score": "good",
            "reason": "Buena atencion rapida",
            "improvement": "Nada que mejorar por ahora",
            "key_messages": []
        }
        
        headers = {'Authorization': 'Bearer token'}
        response = self.app.post('/api/curation/submit', 
                               data=json.dumps(payload),
                               content_type='application/json',
                               headers=headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn("success", response.json['status'])
        
        # Verify Session Add/Commit
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('backend.database.EvalSession')
    @patch('backend.api.jwt.decode')
    def test_submit_validation_fail(self, mock_jwt, mock_session_cls):
        # Mock Auth
        mock_jwt.return_value = {'user': 'testuser'}
        
        payload = {
            "chat_id": 123,
            "score": "bad", # Bad score requires key_messages
            "reason": "Mala atencion",
            "improvement": "Mejorar todo",
            "key_messages": [] # Empty!
        }
        
        headers = {'Authorization': 'Bearer token'}
        response = self.app.post('/api/curation/submit', 
                               data=json.dumps(payload),
                               content_type='application/json',
                               headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation Failed", response.json.get('details', ''))

if __name__ == '__main__':
    unittest.main()
