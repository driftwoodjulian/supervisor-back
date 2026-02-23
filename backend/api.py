from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from backend.database import EvalSession, SourceSession, init_db, SessionLocal, SourceSessionLocal
from backend.models import Evaluation, Chat, User, Account, Message
import os
import jwt
import datetime
from functools import wraps
from werkzeug.security import check_password_hash
from sqlalchemy import func
import requests

app = Flask(__name__)
CORS(app)

SECRET_KEY = "super_secret_key" # In production, this goes in .env
app.config['SECRET_KEY'] = SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            token = token.split(" ")[1] # Bearer <token>
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as e:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/chats/<int:chat_id>', methods=['GET'])
@token_required
def get_chat_details(chat_id):
    session = SessionLocal()
    # In a real app with two DBs (Postgres and SQLite), this is tricky.
    # The Chat/Message data is in Postgres (Source), but we are in the Backend which connects to both.
    # backend/database.py handles this.
    
    # Logic:
    # 1. Fetch Chat metadata from Source DB (Postgres)
    # 2. Fetch Messages from Source DB (Postgres)
    
    # We need a new Session for the Source DB.
    # See backend/database.py for how to do this.
    # For now, let's look at how orchestrator does it, or if we need to expose SourceSession.
    
    from backend.database import SourceSessionLocal
    import json
    # Local import to avoid circular dependency if any, though likely fine at top too.
    from backend.models import Message
    source_session = SourceSessionLocal()
    
    chat = source_session.query(Chat).filter(Chat.id == chat_id).first()
    # Correct column name is chatId, and order by createdAt
    messages = source_session.query(Message).filter(Message.chatId == chat_id).order_by(Message.createdAt).all()
    
    source_session.close()
    session.close()
    
    if not chat:
        return jsonify({"error": "Chat not found"}), 404
        
    # Helper to determine role from author JSON
    formatted_messages = []
    
    # 1. Identify Transfer Index (Logic matching ai_client.py)
    last_agent_name = None
    transfer_index = 0
    
    # Pre-scan for transfers
    for i, m in enumerate(messages):
        author_data = m.author
        role = "agent"
        if isinstance(author_data, str):
            role = "customer"
        
        if role == "agent":
            # Extract name
            name = author_data.get('pushName') if isinstance(author_data, dict) else None
            if name:
                if last_agent_name and name != last_agent_name:
                    transfer_index = i
                last_agent_name = name

    # 2. Format Messages
    for i, m in enumerate(messages):
        author_data = m.author
        
        # Logic from legacy 'get_messages.py':
        # dict -> support operator (agent)
        # str -> customer
        role = "agent"
        if isinstance(author_data, str):
            role = "customer"
        
        # Calculate UI Index
        # Only assign index 1..N if message is at or after transfer_index
        ui_index = None
        if i >= transfer_index:
             ui_index = i - transfer_index + 1

        content = m.text or ""

        # [NEW] Image Handling
        # If message has attachmentId, fetch the path and append reference tag
        # Use simple query since we are in a loop (optimization: eager load if performance issues arise)
        if getattr(m, 'attachmentId', None):
             # We need to use source_session (Postgres) to query Attachment, but we closed it above!
             # We must keep source_session open or re-open it. 
             # Re-opening is safer for now to minimise code grouping changes, though inefficient.
             # Better: Use the `Attachment` model import.
             from backend.models import Attachment
             
             # Re-open session briefly (inefficient but safe)
             # Actually, let's just do it cleanly: Re-open session once.
             # OR, we can fetch all attachments in one go before closing session?
             # Let's adjust the logic to keep session open until after processing.
             pass
        
        # We need to re-structure this function to keep session open.
        # But `replace_file_content` is limited to a block.
        # I will do a quick dirty re-open for now or rewrite the block to include session logic if I can.
        # The surrounding code closes session at line 59.
        # Accessing `m.text` works because objects are loaded/detached or simple types?
        # If `m` is detached, `m.attachmentId` is available.
        # But I can't query `Attachment` without a session.
        # I will use a local session for this block.
        
        attachment_path = None
        if getattr(m, 'attachmentId', None):
             local_session = SourceSessionLocal()
             from backend.models import Attachment
             try:
                 att = local_session.query(Attachment).filter(Attachment.id == m.attachmentId).first()
                 if att and att.path:
                     attachment_path = att.path
             finally:
                 local_session.close()
        
        if attachment_path:
             content += f"\n[IMAGE_REF: {attachment_path}]"

        formatted_messages.append({
            "index": ui_index, # None if pre-transfer, 1..N if post-transfer
            "role": role,
            "content": content,
            "created_at": m.createdAt.isoformat() if m.createdAt else None,
            "author_name": author_data.get('pushName') if isinstance(author_data, dict) else author_data
        })

    return jsonify({
        "chat": {
            "id": chat.id,
            "created_at": chat.createdAt.isoformat() if chat.createdAt else None,
            "closed_at": chat.closedAt.isoformat() if chat.closedAt else None,
            "display_name": chat.displayName,
            "metadata": chat.msg_metadata # Directly pass JSON metadata
        },
        "messages": formatted_messages
    })

@app.route('/api/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('username') or not auth.get('password'):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    session = SessionLocal()
    user = session.query(User).filter_by(username=auth.get('username')).first()
    session.close()

    if not user:
         return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password_hash, auth.get('password')):
        token = jwt.encode({
            'user': user.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({'token': token})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

@app.route('/api/evaluations', methods=['GET'])
@token_required
def get_evaluations():
    session = EvalSession()
    source_session = SourceSessionLocal() # Need to check open status
    
    try:
        # 1. Get IDs of currently OPEN chats from Source DB
        # User Requirement: "if a displayed chat is closed then it is eliminated"
        open_chats = source_session.query(Chat.id).filter(Chat.closedAt == None).all()
        open_chat_ids = [c.id for c in open_chats]
        
        # 2. Fetch latest evaluations, but FILTER by open_chat_ids
        if not open_chat_ids:
             return jsonify([])

        # Using IN clause to filter
        evals = session.query(Evaluation)\
            .filter(Evaluation.chat_id.in_(open_chat_ids))\
            .order_by(Evaluation.created_at.desc())\
            .limit(50).all()
            
        result = []
        for e in evals:
            result.append({
                "chat_id": e.chat_id,
                "score": e.score,
                "reason": e.reason,
                "improvement": e.improvement,
                "key_messages": e.key_messages,
                "created_at": e.created_at.isoformat() + "Z"
            })
        return jsonify(result)
    finally:
        session.close()
        source_session.close()

@app.route('/api/admin/switch-model', methods=['POST'])
@token_required
def switch_model():
    try:
        # Proxy to AI Manager
        host = os.getenv('HOST_B_IP', '127.0.0.1')
        url = f"http://{host}:5002/switch"
        print(f"DEBUG: Connecting to {url} with {request.json}")
        resp = requests.post(url, json=request.json, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return jsonify({"error": f"Failed to contact AI Manager: {str(e)}"}), 500

@app.route('/api/admin/model-status', methods=['GET'])
@token_required
def get_model_status():
    try:
        # Proxy to AI Manager
        resp = requests.get(f"http://{os.getenv('HOST_B_IP', '127.0.0.1')}:5002/status", timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"model": "unknown", "status": "error", "error": str(e)}), 500

@app.route('/api/stats/agents', methods=['GET'])
@token_required
def get_agent_stats():
    eval_session = SessionLocal()
    source_session = SourceSessionLocal()

    try:
        filter_type = request.args.get('filter', 'current') # 'current' or 'historical'

        # 1. Fetch all evaluations
        evaluations = eval_session.query(Evaluation).all()
        if not evaluations:
            return jsonify([])

        # 2. Gather Chat IDs to resolve Agent
        chat_ids = [e.chat_id for e in evaluations]
        
        # 3. Fetch Chats from Source DB to get assignedToId
        # Note: In a large system, we might chunk this
        query = source_session.query(Chat).filter(Chat.id.in_(chat_ids))
        
        if filter_type == 'current':
             query = query.filter(Chat.closedAt == None)
        elif filter_type == 'historical':
             query = query.filter(Chat.closedAt != None)
             
        chats = query.all()
        
        chat_agent_map = {c.id: c.assignedToId for c in chats}
        
        # Filter evaluations to only those belonging to the filtered chats
        # Re-build set of valid chat IDs after filtering
        valid_chat_ids = set(c.id for c in chats)
        evaluations_filtered = [e for e in evaluations if e.chat_id in valid_chat_ids]
        evaluations = evaluations_filtered
        
        # 4. Gather Agent IDs & Fallback for Unassigned
        agent_ids = set()
        unassigned_chat_ids = []
        
        for c in chats:
            if c.assignedToId:
                agent_ids.add(c.assignedToId)
            else:
                unassigned_chat_ids.append(c.id)

        # 5. Fetch Account Names
        accounts = source_session.query(Account).filter(Account.id.in_(agent_ids)).all()
        agent_name_map = {str(a.id): a.pushName for a in accounts} 
        
        # 5b. Fallback: Resolve Unassigned via Messages
        if unassigned_chat_ids:
            # We need to find ONE message from an agent for each unassigned chat to get the name
            # This can be N+1 if we are not careful, but expected volume of *displayed* stats is manageable (all history might be large)
            # Optimization: Fetch one agent message per chat.
            # Since we can't easily do "lateral join" in simple ORM without complexity, let's just loop for now OR do a distinct query.
            # Let's try to get distinct authors for these chats.
            
            # Efficient approach: Fetch distinct author JSON/Dict where chatId in unassigned
            # But checking JSON type in SQL is dialect specific (Postgres).
            # Let's just iterate unassigned chats if count is reasonable, or fetch all messages (too big).
            # Compromise: Check first 5 messages of each unassigned chat (similar to debug script logic)
            # Actually, `debug_stats` showed it works. 
            
            import json # Ensure json is available
            
            for cid in unassigned_chat_ids:
                # Get the first message that has a dict author (agent)
                # We order by createdAt to get the first interaction or any interaction
                msgs = source_session.query(Message).filter(Message.chatId == cid).limit(10).all()
                for m in msgs:
                     if isinstance(m.author, dict):
                         push_name = m.author.get('pushName')
                         if push_name:
                             # We map the CHAT ID directly to the name for these cases?
                             # Or we map a fake "agent_id" -> name?
                             # The stats loop joins on chat_agent_map.get(e.chat_id). 
                             # So we can update chat_agent_map to point to a temporary ID or just use the logic below.
                             # Actually `chat.assignedToId` is None.
                             # So `chat_agent_map[cid]` is None.
                             
                             # Let's update chat_agent_map to use a "virtual" ID or just handle it in the stats loop.
                             # Better: Update `agent_name_map` with a key "fallback_{cid}" and set `chat_agent_map[cid]` to "fallback_{cid}"
                             
                             virtual_id = f"fallback_{cid}"
                             chat_agent_map[cid] = virtual_id
                             agent_name_map[virtual_id] = push_name
                             break

        # 6. Aggregate Data
        # Structure: { agent_name: { total: 0, scores: { 'great': 0 ... } } }
        stats = {}
        
        for e in evaluations:
            agent_id = chat_agent_map.get(e.chat_id)
            if not agent_id:
                agent_name = "Unassigned"
            else:
                agent_name = agent_name_map.get(str(agent_id), "Unknown Agent")

            if agent_name not in stats:
                stats[agent_name] = {
                    "agent": agent_name,
                    "total": 0,
                    "scores": {"great": 0, "good": 0, "neutral": 0, "bad": 0, "horrible": 0, "unknown": 0}
                }
            
            stats[agent_name]["total"] += 1
            score_key = e.score.lower() if e.score else "unknown"
            if score_key not in stats[agent_name]["scores"]:
                 score_key = "unknown" # Safety net
            stats[agent_name]["scores"][score_key] += 1

        # 7. Calculate Percentages and Format List
        result = []
        for agent_name, data in stats.items():
            total = data["total"]
            row = {
                "agent": agent_name,
                "total": total,
                "pct_great": round((data["scores"]["great"] / total) * 100, 1),
                "pct_good": round((data["scores"]["good"] / total) * 100, 1),
                "pct_neutral": round((data["scores"]["neutral"] / total) * 100, 1),
                "pct_bad": round((data["scores"]["bad"] / total) * 100, 1),
                "pct_horrible": round((data["scores"]["horrible"] / total) * 100, 1)
            }
            result.append(row)
        
        # Sort by total chats desc
        result.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify(result)

    except Exception as e:
        print(f"Stats Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        eval_session.close()
        source_session.close()

@app.route('/api/curation/chats', methods=['GET'])
@token_required
def get_curation_chats():
    from backend.security import ReadOnlySession, SecurityAlert
    from backend.ai_client import AIClient
    from sqlalchemy import desc
    import json
    # Import Attachment model locally to avoid circular imports if any, or ensures it's available
    from backend.models import Attachment 
    
    # 1. Initialize Read-Only Session
    # Wraps the SourceSessionLocal to enforce immutability
    raw_session = SourceSessionLocal()
    session = ReadOnlySession(raw_session)
    
    try:
        # 2. Parse Query Params
        page = request.args.get('page', 1, type=int)
        per_page = 50
        chat_id = request.args.get('chat_id', type=int)
        
        # 3. Build Query
        query = session.query(Chat)
        
        if chat_id:
            query = query.filter(Chat.id == chat_id)
        else:
            # Default sort by most recent closed or created
            query = query.order_by(desc(Chat.createdAt))
            
        # Pagination
        offset = (page - 1) * per_page
        chats = query.limit(per_page).offset(offset).all()
        
        results = []
        ai_client = AIClient() # Used for payload construction
        
        for chat in chats:
            # 4. Fetch Messages for Context
            msgs = session.query(Message).filter(Message.chatId == chat.id).order_by(Message.createdAt).all()
            
            # Format history for AIClient
            history = []
            for m in msgs:
                author_data = m.author
                role = "agent"
                if isinstance(author_data, str):
                    role = "customer"
                
                content = m.text or ""
                
                # [NEW] Image Handling
                # If message has attachmentId, fetch the path and append reference tag
                if getattr(m, 'attachmentId', None): # Safely access if column exists in mapped model (it does in DB, need to insure model has it)
                     # Wait, Message model might not have attachmentId defined in models.py yet? 
                     # Let's check models.py from previous read... It wasn't in the definition I read earlier!
                     # I need to update Message model first or use getattr fallback if I didn't update it?
                     # Actually, to use it in query, I should update Message model. 
                     # But for now let's assume I can query it or if it's missing from model I might have issues.
                     # Let's quickly verify Message model in previous step... 
                     # It had: chatId, text, createdAt, author. attachmentId was NOT in the class Message(SourceBase)!
                     # I MUST UPDATE MESSAGE MODEL TOO. 
                     # I will add it in this same replacement if possible or separate. 
                     # Since this is `api.py`, I can't update `models.py` here. 
                     # I will proceed assuming I will update `models.py` in next step (or previous task step I missed it).
                     # Actually I missed adding `attachmentId` to `Message` in `models.py`.
                     # I will do a quick fix to `models.py` via `multi_replace` or just use raw sql here?
                     # Better to update `models.py`. I will pause this edit and update `models.py` first?
                     # No, I can't pause mid-tool-call sequence easily without returning.
                     # I'll rely on `getattr(m, 'attachmentId')` failing/returning None if not in model, 
                     # BUT SQLAlchemy won't fetch it if not in model.
                     # So I MUST update `models.py` first. 
                     
                     # Wait, I just updated `models.py` to add `Attachment`. 
                     # I should have added `attachmentId` to `Message` at the same time.
                     # I will assume I can do another tool call relative to `models.py` immediately.
                     pass

                # Re-do logic assuming models are correct:
                # We need to manually fetch attachment if we don't have a relationship
                if hasattr(m, 'attachmentId') and m.attachmentId:
                     att = session.query(Attachment).filter(Attachment.id == m.attachmentId).first()
                     if att and att.path:
                         # Append tag
                         content += f"\n[IMAGE_REF: {att.path}]"

                
                # We need to construct the dict format AIClient expects
                history.append({
                    "role": role,
                    "content": content,
                    "timestamp": m.createdAt.isoformat() if m.createdAt else None,
                    "author": author_data
                })
            
            # 5. Generate Raw Payload (Context-Faithful)
            payload = ai_client.build_payload(history)
            
            results.append({
                "id": chat.id,
                "finished_at": chat.closedAt.isoformat() if chat.closedAt else None,
                "raw_payload": json.dumps(payload, ensure_ascii=False)
            })
            
        return jsonify(results)

    except SecurityAlert as e:
        print(f"CRITICAL SECURITY ALERT CAUGHT: {e}")
        return jsonify({"error": "Security Violation: Write attempt on Read-Only DB"}), 500
    except Exception as e:
        print(f"Curation API Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        session.close() # Closes the underlying session

@app.route('/api/curation/submit', methods=['POST'])
@token_required
def submit_curation():
    from backend.schemas import EvaluationSubmission
    from backend.database import EvalSession
    import json
    
    try:
        # 1. Validate Payload
        data = request.json
        submission = EvaluationSubmission(**data)
        
        # 2. Save to DB
        session = EvalSession()
        try:
            # Check if already evaluated? (Optional constraints, but good practice)
            # existing = session.query(Evaluation).filter_by(chat_id=submission.chat_id).first()
            # if existing: return jsonify({"error": "Already evaluated"}), 409

            # Create Evaluation Record
            eval_record = Evaluation(
                chat_id=submission.chat_id,
                score=submission.score.value, # Enum to string
                reason=submission.reason,
                improvement=submission.improvement,
                # Store key_messages as JSON string or relation?
                # The model `Evaluation` has `key_messages` as... let's check model.
                # Assuming it's a JSON column or text.
                # For SQLite, it's likely Text.
                key_messages=json.dumps(submission.key_messages),
                created_at=datetime.datetime.utcnow()
            )
            
            session.add(eval_record)
            session.commit()
            
            return jsonify({"status": "success", "id": eval_record.id}), 201
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    except ValueError as e:
        return jsonify({"error": str(e), "details": "Validation Failed"}), 400
    except Exception as e:
        print(f"Submission Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.getenv('BACKEND_PORT', 5001)))
