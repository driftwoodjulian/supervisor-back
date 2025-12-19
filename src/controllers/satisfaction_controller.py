import json
from entity.chat import Chat
from service.get_chat import get_chat
from service.get_messages import get_messages
from flask import Blueprint, jsonify, request
from service.harmony_convertion import convert_to_harmony
from service.get_chat import get_current_chats
import requests
from decorators.auth import preauth


api_endpoint ="http://10.10.1.8:5040/ai/ai"
satisfaction_bp = Blueprint("satisfaction_controller", __name__)

def set_satisfaction(chat_id):
    print("getting score for: " + str(chat_id))

    messages = get_messages(chat_id)
    chat = get_chat(chat_id)
    
    info = {
        "conversation": messages["conversation"],
        "chat_and_customer_info": chat
    }

    data=convert_to_harmony(full_chat=info)

    #send data to ai
    print("sending data to ai")
    print(data)
    ai_response = requests.post(api_endpoint, json=data)

    #return serializable response content
    try:
        print("got a response from ai")
        print(ai_response.json())
        return ai_response.json()
    except Exception as e:
        print(e)
        message = {"error": "from ai for chat {}".format(chat_id)}
        return  message.json()


#turn in to a socket
@satisfaction_bp.route("/satisfaction", methods=["GET"])
@preauth
def satisfaction_controller():
    response = None
    scores = []
    #add a while true

    

    try:
        chats = get_current_chats()
        chat_ids = []
        if len(chats) == 0:
            response= jsonify({"data": "No current chats"}), 200
        else:
            for chat in chats:
                print("current chat id: "+ str(chat.id) )
                chat_ids.append(chat.id)
            for id in chat_ids:
                try:
                    score =set_satisfaction(id)
                    scores.append({
                        "chat_id": id,
                        "score": score
                    })
                except Exception as e:
                    print(e)
            # ensure a valid response is always returned
            response = jsonify({"scores": scores}), 200
                
    except Exception as e:
        print(e)
        response = jsonify({"error": "error in satisfaction controller"}), 500
    return response








    