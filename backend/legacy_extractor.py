import pymysql
import json
import os

DB_HOST = 'mysql.towebs.com'
DB_USER = 'julian'
DB_PASS = 'jul23789ian'
DB_NAME = 'twchat'

VICTOR_OPERATOR_ID = 146
VICTOR_ALIAS = 'Victor.c'

def extract_victor_chats():
    print(f"Connecting to {DB_HOST} to extract Victor's chats (ID: {VICTOR_OPERATOR_ID})...")
    
    # We will build a list of Q&A pairs
    qa_pairs = []
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 1. Get all chats handled by Victor
            # Limit to recent or successful ones if there are too many, but let's grab up to 5000 chats for a good dataset
            chat_query = f"SELECT id FROM chat_chat WHERE operator_id = {VICTOR_OPERATOR_ID} ORDER BY id DESC LIMIT 5000;"
            cursor.execute(chat_query)
            chats = cursor.fetchall()
            print(f"Found {len(chats)} chats handled by Victor.")
            
            chat_ids = [str(c['id']) for c in chats]
            
            if not chat_ids:
                print("No chats found.")
                return
                
            # 2. Get messages for these chats
            # We batch the query to avoid huge memory spikes
            batch_size = 500
            for i in range(0, len(chat_ids), batch_size):
                batch_ids = chat_ids[i:i + batch_size]
                ids_str = ",".join(batch_ids)
                
                msg_query = f"""
                    SELECT chat_id_id, user_alias, user_role, message_type, message_text, message_date
                    FROM chat_message 
                    WHERE chat_id_id IN ({ids_str})
                      AND message_type = '1'
                    ORDER BY chat_id_id, message_date ASC;
                """
                cursor.execute(msg_query)
                messages = cursor.fetchall()
                
                # Group messages by chat
                chat_threads = {}
                for msg in messages:
                    cid = msg['chat_id_id']
                    if cid not in chat_threads:
                        chat_threads[cid] = []
                    
                    # Clean the html/text if needed (twchat might store raw HTML)
                    text = msg['message_text']
                    if not text: continue
                    text = text.strip().replace('<br>', '\\n').replace('<br/>', '\\n')
                    
                    alias = (msg['user_alias'] or '').lower()
                    chat_threads[cid].append({
                        'role': 'agent' if alias == VICTOR_ALIAS.lower() else 'customer',
                        'text': text
                    })
                
                # Process threads into QA pairs
                for cid, thread in chat_threads.items():
                    current_question = []
                    current_answer = []
                    state = 'customer' # expecting customer first
                    
                    for m in thread:
                        if m['role'] == 'customer':
                            if state == 'agent' and current_answer:
                                # We finished an answer, save the pair
                                if current_question:
                                    qa_pairs.append({
                                        'chat_id': cid,
                                        'question': "\\n".join(current_question),
                                        'answer': "\\n".join(current_answer)
                                    })
                                # Reset for next question
                                current_question = [m['text']]
                                current_answer = []
                                state = 'customer'
                            else:
                                current_question.append(m['text'])
                                
                        elif m['role'] == 'agent':
                            state = 'agent'
                            current_answer.append(m['text'])
                    
                    # Flush last pair
                    if current_question and current_answer:
                        qa_pairs.append({
                            'chat_id': cid,
                            'question': "\\n".join(current_question),
                            'answer': "\\n".join(current_answer)
                        })

                print(f"Processed batch {i} - {i + batch_size}. Total Q&A pairs: {len(qa_pairs)}")

    except Exception as e:
        print(f"Extraction Error: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()
            
    # Save to disk
    out_file = 'backend/victor_chats.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully saved {len(qa_pairs)} specific interactions to {out_file}!")

if __name__ == "__main__":
    extract_victor_chats()
