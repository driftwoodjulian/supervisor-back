import sys
import os

# Add root project dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db
from backend.ai_client import AIClient
from backend.database import ConfigSession
from backend.models import SystemPrompt, Manual, ActiveConfig
from backend.encryption import encrypt_text

def test_stuff():
    print("Initialize DBs...")
    init_db()
    
    # Pre-populate some config
    session = ConfigSession()
    try:
        p = SystemPrompt(title="Test Prompt", content=encrypt_text("This is my dynamic test prompt"))
        m = Manual(title="Test Manual", content=encrypt_text("Rule 1: Always be testing."))
        session.add(p)
        session.add(m)
        session.commit()
        
        active = ActiveConfig(id=1, active_prompt_id=p.id, active_manual_id=m.id)
        session.add(active)
        session.commit()
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        session.close()

    print("\nTesting AIClient build_payload()...")
    client = AIClient()
    dummy_history = [
        {"role": "user", "content": "Hello", "timestamp": "2024-01-01T12:00:00"},
        {"role": "agent", "content": "Hi", "timestamp": "2024-01-01T12:00:10"}
    ]
    
    payload = client.build_payload(dummy_history)
    import json
    print("\nResult Payload:")
    print(json.dumps(payload, indent=2))

if __name__ == "__main__":
    test_stuff()
