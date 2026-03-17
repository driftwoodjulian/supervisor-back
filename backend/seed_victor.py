import sys
import os
from datetime import datetime

# Ensure we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import ConfigSession
from backend.models import SystemPrompt, ActiveConfig
from backend.encryption import encrypt_text

def seed_victor():
    session = ConfigSession()
    try:
        # Check if it already exists
        existing = session.query(SystemPrompt).filter_by(title="Victor AI (Classic)").first()
        if not existing:
            prompt_text = "You are Victor, an elite technical support agent. You speak ONLY in Spanish.\nYou are helpful, concise, and professional.\n"
            new_prompt = SystemPrompt(
                title="Victor AI (Classic)",
                content=encrypt_text(prompt_text),
                created_at=datetime.utcnow()
            )
            session.add(new_prompt)
            session.commit()
            
            # Set it as the active prompt for Victor if none is set
            active = session.query(ActiveConfig).filter_by(id=1).first()
            if active and not active.victor_prompt_id:
                active.victor_prompt_id = new_prompt.id
                session.commit()
                print("Victor AI (Classic) prompt added and set as active for Victor.")
            else:
                print("Victor AI (Classic) prompt added.")
        else:
            print("Victor AI (Classic) prompt already exists.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed_victor()
