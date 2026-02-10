import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.models import Evaluation
from backend.ai_client import AIClient

def test_evaluation_model():
    eval = Evaluation(
        chat_id=123,
        score="good",
        reason="Test reason",
        improvement="Test improvement"
    )
    assert eval.chat_id == 123
    assert eval.score == "good"
    assert eval.reason == "Test reason"

def test_ai_client_mock():
    client = AIClient()
    response = client.evaluate_chat([])
    assert "score" in response
    assert response["score"] in ["horrible", "bad", "neutral", "good", "great"]
    assert "reason" in response
    assert "improvement" in response

def test_conversation_formatting():
    client = AIClient()
    history = [
        {"role": "user", "content": "Hello", "timestamp": "2023-01-01T10:00:00", "author": {"name": "Client", "type": "customer"}},
        {"role": "agent", "content": "Hi there", "timestamp": "2023-01-01T10:00:30", "author": {"name": "Franco", "type": "agent"}}
    ]
    formatted = client._format_conversation_with_time(history)
    print(formatted)
    assert "1 - User: Hello" in formatted
    assert "2 - Support agent (Franco) (+30s): Hi there" in formatted
