import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, ConfigSession
from backend.models import SystemPrompt, Manual, ActiveConfig
from backend.encryption import encrypt_text

def seed_defaults():
    init_db()
    session = ConfigSession()
    
    try:
        # Load Manual
        base_dir = os.path.dirname(os.path.abspath(__file__))
        manual_path = os.path.join(base_dir, 'manual.txt')
        with open(manual_path, 'r', encoding='utf-8') as f:
            manual_content = f.read()
            
        # Hardcoded Prompt
        system_prompt = (
            "You are a B2C/B2B satisfaction expert. Evaluate the support agent's performance.\n"
            "- OUTPUT: Strictly a valid JSON object.\n"
            "- SCORE: Must be EXACTLY ONE of: 'horrible', 'bad', 'neutral', 'good', 'great'.\n"
            "- LANGUAGE: The 'reason' and 'improvement' fields MUST be in SPANISH.\n"
            "- CONTEXT: Use the provided QUALITY MANUAL to judge compliance (greetings, empathy, efficiency, etc).\n\n"
            "### OUTPUT JSON SCHEMA:\n"
            "{\n"
            "  \"score\": \"string (exactly one of: horrible, bad, neutral, good, great)\",\n"
            "  \"reason\": \"Spanish text (max 500 chars) explaining the choice.\",\n"
            "  \"improvement\": \"Spanish text (max 800 chars) on how the operator can improve.\",\n"
            "  \"key_messages\": [int, int] // INDICES of Support Agent messages that directly TRIGGERED this score.\n"
            "  // CRITICAL: If score is 'bad' or 'horrible', 'key_messages' MUST contain at least one message index.\n"
            "  // IMPORTANT: The indices must point to lines where the sender is explicitly the Support Agent (NOT the User).\n"
            "}\n"
        )
        
        # Insert them
        p = SystemPrompt(title="V1 - Original Strict JSON Logic", content=encrypt_text(system_prompt))
        m = Manual(title="V1 - Quality Assurance Manual", content=encrypt_text(manual_content))
        session.add(p)
        session.add(m)
        session.commit()
        
        # Set them as active
        active = session.query(ActiveConfig).filter_by(id=1).first()
        if not active:
            active = ActiveConfig(id=1, active_prompt_id=p.id, active_manual_id=m.id)
            session.add(active)
        else:
            active.active_prompt_id = p.id
            active.active_manual_id = m.id
        session.commit()
        
        print("Successfully seeded the default configurations into config.db")
        
    except Exception as e:
        print(f"Error seeding defaults: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    seed_defaults()
