import asyncio
import time
from sqlalchemy import select
from backend.database import SourceSession, EvalSession, init_db
from backend.models import Chat, Message, Evaluation
from backend.ai_client import AIClient
import json
import datetime

class Orchestrator:
    def __init__(self):
        self.ai_client = AIClient()
        self.running = False

    async def run(self):
        init_db() # Ensure Eval DB exists
        self.running = True
        print("Orchestrator started...")
        while self.running:
            try:
                self.process_batch()
            except Exception as e:
                print(f"Error in orchestrator loop: {e}")
            
            await asyncio.sleep(10) # Run every 10 seconds

    def process_batch(self):
        source_session = SourceSession()
        eval_session = EvalSession()
        
        try:
            # 1. Get OPEN chats from Source DB (Active Monitoring)
            # Legacy logic: Monitor chats that are NOT closed.
            stmt = select(Chat).where(Chat.closedAt == None).order_by(Chat.createdAt.desc()).limit(50)
            chats = source_session.execute(stmt).scalars().all()

            for chat in chats:
                print(f"Monitoring Open Chat ID: {chat.id}")

                # 3. Fetch messages for the chat
                msgs_stmt = select(Message).where(Message.chatId == chat.id).order_by(Message.createdAt)
                messages = source_session.execute(msgs_stmt).scalars().all()
                
                if not messages:
                    # print(f"No messages for Chat {chat.id}, skipping.")
                    continue

                # 4. Format history
                history = []
                for msg in messages:
                    author_data = msg.author if msg.author else {}
                    # Determine role based on author data
                    # Logic: 
                    # 1. If dict and type='customer' -> user
                    # 2. If valid dict and no type='customer' -> agent
                    # 3. If string and cannot parse as dict -> user (Legacy/Fallback)
                    
                    role = "agent" # Default
                    
                    if isinstance(author_data, str):
                        try:
                            parsed = json.loads(author_data)
                            if isinstance(parsed, dict):
                                author_data = parsed
                            else:
                                role = "user"
                        except:
                            role = "user"

                    if isinstance(author_data, dict):
                         if author_data.get('type') == 'customer':
                             role = "user"
                         # else remain agent

                    
                    history.append({
                        "role": role,
                        "content": msg.text if msg.text is not None else "",
                        "timestamp": msg.createdAt.isoformat() if msg.createdAt else None,
                        "author": author_data 
                    })

                # 5. Call AI
                evaluation = self.ai_client.evaluate_chat(history)

                # 6. Save/Update result (Upsert)
                score = evaluation.get("score")
                
                # RETRY LOGIC: If AI fails (returns unknown), DO NOT save/update. 
                # This ensures it gets picked up again in the next cycle.
                if score == "unknown":
                    print(f"Chat {chat.id} returned 'unknown' score (AI failure). Skipping save to retry later.")
                    continue

                existing_eval = eval_session.query(Evaluation).filter_by(chat_id=chat.id).first()
                
                if existing_eval:
                    # Update existing evaluation
                    existing_eval.score = score
                    existing_eval.reason = evaluation.get("reason")
                    existing_eval.improvement = evaluation.get("improvement")
                    existing_eval.key_messages = evaluation.get("key_messages")
                    existing_eval.created_at = datetime.datetime.utcnow() # Update timestamp
                    print(f"Updated Chat {chat.id}: {existing_eval.score}")
                else:
                    # Create new
                    new_eval = Evaluation(
                        chat_id=chat.id,
                        score=score,
                        reason=evaluation.get("reason"),
                        improvement=evaluation.get("improvement"),
                        key_messages=evaluation.get("key_messages")
                    )
                    eval_session.add(new_eval)
                    print(f"Evaluated New Open Chat {chat.id}: {new_eval.score}")
                
                eval_session.commit()

        finally:
            source_session.close()
            eval_session.close()

if __name__ == "__main__":
    orchestrator = Orchestrator()
    try:
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        print("Stopping orchestrator...")
