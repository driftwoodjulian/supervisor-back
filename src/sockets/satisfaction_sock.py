import json
from queue import Empty
from sqlite3.dbapi2 import Timestamp
import time
from flask import request
from datetime import datetime

from sockets.sock_extention import sock


from service.get_chat import get_current_chats
from controllers.satisfaction_controller import set_satisfaction


import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

scores = []
scores_lock = threading.Lock()

def is_score_present(message):
    
    is_present = False

    if message["chat_id"] and len(scores)>0:
        i=0
        for score in scores:
            if score["chat_id"] and message["chat_id"]== score["chat_id"]:
                is_present=True
                print("updating chat id " + str(score["chat_id"]))
                scores[i] = message
                print(scores[i])
                break
            i+=1
    
    return is_present



    


def eliminate_old_scores(chat_ids):
    global score

    i = 0
    while i < len(scores) and len(scores)>0:
        try:
            score_id = scores[i]["chat_id"]
            is_found = False
            for chat_id in chat_ids:
                if chat_id == score_id:
                    is_found = True
                    break

            if not is_found:
                scores.pop(i)
            else:
                i += 1
        except Exception as e:
            print("error eliminating old scores: " + e)


def batch_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def query_scores():
    """
    Processes chat_ids in batches of 3. The global `scores` list grows cumulatively:
    after finishing each batch, new scored chat entries are appended (or existing ones updated).
    """
    # Reuse a single ThreadPoolExecutor across iterations to avoid re-creating threads too often.
    executor = ThreadPoolExecutor(max_workers=3)

    while True:
        try:
            chats = get_current_chats()
            chat_ids = [chat.id for chat in chats]

            if not chat_ids:
                with scores_lock:
                    scores.clear()
                    # Keep the same behavior you had before (a single JSON string entry)
                    scores.append(json.dumps({"data": "No current chats"}))
            else:
                # Remove scores that belong to chats that are no longer current
                eliminate_old_scores(chat_ids=chat_ids)

                # Process chat ids in batches of 3
                for batch in batch_list(chat_ids, 3):
                    # Submit the set_satisfaction calls for this batch
                    futures = {executor.submit(set_satisfaction, chat_id): chat_id for chat_id in batch}

                    # As each future completes, append/update the global scores list.
                    for future in as_completed(futures):
                        chat_id = futures[future]
                        try:
                            score = future.result()

                            # If the API sometimes returns an explicit error dict, retry here
                            # (mirrors your previous retry loop)
                            retry_attempts = 0
                            while score == {'error': 'error with the score query'} and retry_attempts < 5:
                                print(f"error detected for chat {chat_id}, requerying (attempt {retry_attempts+1})")
                                score = set_satisfaction(chat_id)
                                retry_attempts += 1

                            # Build message
                            message = {
                                "chat_id": chat_id,
                                "score": score,
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }

                            # Append or update in a thread-safe way.
                            # IMPORTANT: we must append new items so the array grows cumulatively.
                            if not is_score_present(message):
                                with scores_lock:
                                    print(f"appending new score: {message['chat_id']}")
                                    scores.append(message)
                                    # print current list for debugging
                                    for s in scores:
                                        print(f"{s} --- in list")
                            else:
                                print(f"updated score of chat {chat_id}")

                        except Exception as e:
                            # keep the error message informative
                            print(f"error fetching score for chat {chat_id}: {e}")

            # small sleep before next full iteration
            time.sleep(3)
        except Exception as top_level_exc:
            # protect the loop from crashing
            print(f"unexpected error in query_scores loop: {top_level_exc}")
            time.sleep(3)

'''
def query_scores():
    

    while True:
        chats = get_current_chats()
        chat_ids = [chat.id for chat in chats]
        
        if not chat_ids:
            scores.clear()
            scores.append(json.dumps({"data": "No current chats"}))
        else:
            #do a while loop that looks to match the id of the scores in the scores array and matches them with the ids in the chats_ids array, if no match is found in chats_ids then the score must be eliminated from the array
            eliminate_old_scores(chat_ids=chat_ids)



            for chat_id in chat_ids:
                try:
                    score_an_error= True
                    score= None
                    while score_an_error:
                        print()
                        score = set_satisfaction(chat_id) 
                        print("------------------")
                        print(str(score) + " ---- "+ str(chat_id) + " -----")
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        message = {
                            "chat_id": chat_id,
                            "score": score,
                            "timestamp": timestamp
                        }
                        print(message)
                        #chech if score it an error json here if not set score_not_an_error to True
                        if score =={'error': 'error with the score query'}:
                            print("error detected, requering")
                        else:
                            score_an_error= False 
                    try:
                        if not is_score_present(message=message):
                            print("appending new score: " + str(message["chat_id"]))

                            scores.append(message)
                            for scoree in scores:
                                print(str(scoree) +'--- in list')
                        else:
                            print("updated score of chat " + str(chat_id))
                    except:
                        print("error appending")   
                except Exception as e:
                    print(e)
                    print(f"error, we did get a score for chat {chat_id}: " + e)

        time.sleep(3)
'''

@sock.route("/ws/satisfaction")
def satisfaction_ws(sock):
    """
    token = request.args.get("token")
    if token != "valid_token_123":
        sock.send(json.dumps({"error": "Unauthorized"}))
        sock.close()
        return
    """
    while True:
        
        if len(scores) == 0:
            #sock.send(json.dumps({"chat_id": 0, "score": "neutral", "timestamp": "None"}))
            time.sleep(5)
        else:
            sock.send(json.dumps(scores))
            time.sleep(5)
        time.sleep(3)



