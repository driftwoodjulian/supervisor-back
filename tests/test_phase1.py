import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.security import ReadOnlySession, SecurityAlert
from backend.api import app
from backend.database import SourceBase

class TestPhase1(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_immutability_add(self):
        """Test that ReadOnlySession blocks 'add'"""
        mock_session = MagicMock()
        read_only = ReadOnlySession(mock_session)
        
        print("\n[TEST] Verifying Immutability (add)...")
        with self.assertRaises(SecurityAlert):
            read_only.add("something")
        print("PASS: SecurityAlert raised on 'add'.")

    def test_immutability_commit(self):
        """Test that ReadOnlySession blocks 'commit'"""
        mock_session = MagicMock()
        read_only = ReadOnlySession(mock_session)
        
        print("\n[TEST] Verifying Immutability (commit)...")
        with self.assertRaises(SecurityAlert):
            read_only.commit()
        print("PASS: SecurityAlert raised on 'commit'.")

    @patch('backend.api.SourceSessionLocal')
    def test_curation_endpoint_structure(self, mock_session_cls):
        """Test GET /api/curation/chats returns correct structure"""
        print("\n[TEST] Verifying API Endpoint Structure...")
        
        # Mock Session and Data
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        # Mock Chat
        mock_chat = MagicMock()
        mock_chat.id = 123
        mock_chat.closedAt = None
        mock_chat.createdAt = "2023-01-01T12:00:00"
        
        # Mock Message
        mock_msg = MagicMock()
        mock_msg.chatId = 123
        mock_msg.text = "Hello"
        mock_msg.createdAt = None
        mock_msg.author = "customer" # string means customer in our logic
        
        # Setup Query Returns
        # First query is for Chats
        # Second query is for Messages
        
        # We need to mock the ReadOnlySession wrapping
        # In api.py: session = ReadOnlySession(raw_session)
        # raw_session.query(Chat)...
        
        # Determine strict query return values
        mock_session.query.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [mock_chat]
        
        # Message query simulation is tricky with chained mocks, let's just inspect the response
        # If the endpoint crashes, test fails.
        
        # Needs JWT token mock? @token_required wrapper might block us.
        # Let's mock the token_required decorator or pass headers if we can generate one.
        # Or easier: bypass the decorator for unit testing by accessing the function directly?
        # No, flask routing handles it.
        # Let's patch `backend.api.decode_token` or similar if needed.
        # Actually `token_required` checks `Authorization` header.
        
        # Mocking `jwt.decode` in api.py would be easiest.
        with patch('backend.api.jwt.decode') as mock_jwt:
            mock_jwt.return_value = {'sub': 'testuser'}
            
            # Also mock the message query specifically?
            # The loop does: session.query(Message).filter...
            # We can rely on the fact that mock_session.query returns a mock that eventually returns [mock_chat]
            # When called for Message, it might return [mock_chat] (wrong type) but let's see if code handles it.
            # actually code does: `msgs = session.query(Message)...`
            # We can use side_effect on query()
            
            def query_side_effect(model):
                m = MagicMock()
                if model.__name__ == 'Chat':
                    m.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [mock_chat]
                elif model.__name__ == 'Message':
                    m.filter.return_value.order_by.return_value.all.return_value = [mock_msg]
                return m
                
            mock_session.query.side_effect = query_side_effect
            
            response = self.app.get('/api/curation/chats', headers={'Authorization': 'Bearer mocktoken'})
            
            if response.status_code != 200:
                print(f"FAIL: Endpoint returned {response.status_code}")
                print(response.json)
            
            self.assertEqual(response.status_code, 200)
            data = response.json
            self.assertTrue(isinstance(data, list))
            if len(data) > 0:
                self.assertIn('id', data[0])
                self.assertIn('raw_payload', data[0])
                print("PASS: Endpoint returned valid List[ChatCurationResponse].")

if __name__ == '__main__':
    unittest.main()
