import json
from queue import Empty
from sqlite3.dbapi2 import Timestamp
import time
from flask import request
from datetime import datetime

from sockets.sock_extention import sock


from service.get_chat import get_current_chats
from controllers.satisfaction_controller import set_satisfaction

scores = []

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


def query_scores():
    

    while True:
        chats = get_current_chats()
        chat_ids = [chat.id for chat in chats]
        
        if not chat_ids:
            scores.clear()
            sock.send(json.dumps({"data": "No current chats"}))
        else:
            #do a while loop that looks to match the id of the scores in the scores array and matches them with the ids in the chats_ids array, if no match is found in chats_ids then the score must be eliminated from the array
            eliminate_old_scores(chat_ids=chat_ids)

            for chat_id in chat_ids:
                try:
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



