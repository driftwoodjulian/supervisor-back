import unittest
from unittest.mock import MagicMock, patch
import json
import sqlite3
import os
from datetime import datetime

# Adjust path to import backend
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import app
from backend.models import Evaluation, Chat
from backend.database import eval_engine, source_engine

class TestHITLSimulation(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.headers = None

    @patch('backend.api.check_password_hash')
    @patch('backend.database.SourceSessionLocal') # Mock Source DB for read
    @patch('backend.database.EvalSession')        # Mock Eval DB for write
    def test_end_to_end_hitl_flow(self, mock_eval_session_cls, mock_source_session_cls, mock_check_pw):
        print("\n--- STARTING HITL ZERO-TOUCH SIMULATION ---")
        
        # 1. Simulate Login
        print("[Step 1] Simulating Login...")
        mock_check_pw.return_value = True
        
        # Mock User Query for Login
        mock_source_session = MagicMock()
        mock_source_session_cls.return_value = mock_source_session
        
        mock_user = MagicMock()
        mock_user.username = 'admin'
        mock_user.password_hash = 'hashed_secret'
        mock_source_session.query.return_value.filter_by.return_value.first.return_value = mock_user

        login_payload = {'username': 'admin', 'password': 'password'}
        resp = self.app.post('/api/login', json=login_payload)
        self.assertEqual(resp.status_code, 200)
        token = resp.json['token']
        self.headers = {'Authorization': f'Bearer {token}'}
        print(" -> Login Successful. Token acquired.")

        # 2. Fetch Pending Chats
        print("[Step 2] Fetching Pending Chats...")
        
        # Mock Chat Data
        mock_chat = MagicMock()
        mock_chat.id = 999
        mock_chat.closedAt = datetime.now()
        mock_chat.msg_metadata = {}
        
        # Mock Query Results
        mock_source_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.offset.return_value.all.return_value = [mock_chat]
        # Mock Messages for Context
        mock_source_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [] 
        
        resp = self.app.get('/api/curation/chats?page=1', headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        chats = resp.json
        self.assertGreater(len(chats), 0)
        target_chat_id = chats[0]['id']
        print(f" -> Fetched {len(chats)} chats. Target Chat ID: {target_chat_id}")

        # 3. Submit Evaluation (Good Score)
        print(f"[Step 3] Submitting Evaluation for Chat {target_chat_id}...")
        
        # Mock Eval DB
        mock_eval_session = MagicMock()
        mock_eval_session_cls.return_value = mock_eval_session
        
        eval_payload = {
            "chat_id": target_chat_id,
            "score": "good",
            "reason": "Buena simulacion",
            "improvement": "Ninguna mejora necesaria por ahora",
            "key_messages": []
        }
        
        resp = self.app.post('/api/curation/submit', 
                             json=eval_payload,
                             headers=self.headers)
        
        self.assertEqual(resp.status_code, 201)
        print(" -> Evaluation Submitted Successfully.")

        # 4. Verify DB Interactions
        print("[Step 4] Verifying Database Constraints...")
        
        # Check Eval DB Write
        mock_eval_session.add.assert_called_once()
        mock_eval_session.commit.assert_called_once()
        print(" -> Verified: Write to Evaluations DB (SQLite).")
        
        # Check Source DB Immutability
        # We can verify that 'commit' or 'add' was NEVER called on source_session
        mock_source_session.add.assert_not_called()
        mock_source_session.commit.assert_not_called()
        print(" -> Verified: NO Write to Source DB (Postgres).")

        print("--- SIMULATION COMPLETE: SUCCESS ---")

if __name__ == '__main__':
    unittest.main()
