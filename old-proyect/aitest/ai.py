from werkzeug.wrappers import response
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
from flask import Blueprint, jsonify, request

available= False
score_request_counter = 0

model_path = "/home/juli/gptoss/gpt-oss-20b"


tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True, padding_side="left")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    local_files_only=True,
    device_map="auto",
)
system_prompt4 = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words. "
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters, and an 'improvement' key which must be your suggestion for improving the score that you chose in a maximum of 800 characters. "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' and 'improvement' keys. DO NOT output anything else, only the json score."
    "Take into account that the support agent is comunicating with the client in monitorized and safe environment for exchange of sensitive data like username and passwords."
    "If the score is bad or horrible, the improvement key must include the number of the key messages from the support agent that might have lead to the bad or horrible score."
    """the final answer must be inside a json such as this example: {"score": "neutral", 
    "reason": "Califiqué la interacción como neutral porque el agente de soporte dio la información correcta, 
    pero el tono fue algo impersonal y poco empático. El problema se resolvió, pero el cliente no pareció 
    completamente tranquilo, y faltó una actitud proactiva para asegurar su satisfacción.", 
    "improvement": "El operador veo que se llama Franco  segun la conversacion en este caso. 
    Dio informacion correcta pero veo que pidio los datos de ingreso del panel de control del cliente sin explicarle que 
    estan en un medio seguro. El cliente fue migrado de el area de pagos a soporte y luego de soporte a pagos de nuevo para solucionar el problema, eso puede aportar a la frustracion. Deberia empatizar con la situacion del cliente atendiendo su situacion emocional y ofreciendo soluciones proactivas 
    aun que la solucion no sea inmediata. Mesajes clave de agente de soporte que aportaron a la calificacion: 4, 6, 7, 12  ",
    "key_messages": "4, 6, 7, 12"
     }"""

)


system_prompt4_2 = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words. "
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters, and an 'improvement' key which must be your suggestion for improving the score that you chose in a maximum of 800 characters. "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' and 'improvement' keys. DO NOT output anything else, only the json score."
    "Take into account that the support agent is comunicating with the client in monitorized and safe environment for exchange of sensitive data like username and passwords."
    "If the score is bad or horrible, the improvement key must include the number of the key messages from the support agent that might have lead to the bad or horrible score."
    """the final answer must be inside a json such as this example: {"score": "neutral", 
    "reason": "Califiqué la interacción como neutral porque el agente de soporte dio la información correcta, 
    pero el tono fue algo impersonal y poco empático. El problema se resolvió, pero el cliente no pareció 
    completamente tranquilo, y faltó una actitud proactiva para asegurar su satisfacción.", 
    "improvement": " El operador dio informacion correcta pero veo que pidio los datos de ingreso del panel de control del cliente sin explicarle que 
    estan en un medio seguro. El cliente fue migrado de el area de pagos a soporte y luego de soporte a pagos de nuevo para solucionar el problema, eso puede aportar a la frustracion pero no parecio molestarse. Deberia empatizar con la situacion del cliente atendiendo su situacion emocional y ofreciendo soluciones proactivas 
    aun que la solucion no sea inmediata. El operador no tardo mas de 5 minutos en responder al cliente y cuando lo hizo pidio mas tiempo o se disculpo por la demora en la respuesta. Mesajes clave de agente de soporte que aportaron a la calificacion: 4, 6, 7, 12  ",
    "key_messages": ["4", "6", "7", "12"]
     }"""

)


system_prompt3 = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words. "
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters, and an 'improvement' key which must be your suggestion for improving the score that you chose in a maximum of 800 characters. "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' and 'improvement' keys. DO NOT output anything else, only the json score."
    "Take into account that the support agent is comunicating with the client in monitorized and safe environment for exchange of sensitive data like username and passwords."
    "If the score is bad or horrible, the improvement key must include the number of the key messages from the support agent that might have lead to the bad or horrible score."
    """the final answer must be inside a json such as this example: {"score": "neutral", 
    "reason": "Califiqué la interacción como neutral porque el agente de soporte dio la información correcta, 
    pero el tono fue algo impersonal y poco empático. El problema se resolvió, pero el cliente no pareció 
    completamente tranquilo, y faltó una actitud proactiva para asegurar su satisfacción.", 
    "improvement": "El operador veo que se llama Franco  segun la conversacion en este caso. 
    Dio informacion correcta pero veo que pidio los datos de ingreso del panel de control del cliente sin explicarle que 
    estan en un medio seguro. El cliente fue migrado de el area de pagos a soporte y luego de soporte a pagos de nuevo para solucionar el problema, eso puede aportar a la frustracion. Deberia empatizar con la situacion del cliente atendiendo su situacion emocional y ofreciendo soluciones proactivas 
    aun que la solucion no sea inmediata. Mesajes clave de agente de soporte que aportaron a la calificacion: 4, 6, 7, 12  " }"""

)






system_prompt = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words. "
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters, and an 'improvement' key which must be your suggestion for improving the score that you chose in a maximum of 800 characters. "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' and 'improvement' keys. DO NOT output anything else, only the json score."
    """the final answer must be inside a json such as this example: {"score": "neutral", 
    "reason": "Califiqué la interacción como neutral porque el agente de soporte dio la información correcta, 
    pero el tono fue algo impersonal y poco empático. El problema se resolvió, pero el cliente no pareció 
    completamente tranquilo, y faltó una actitud proactiva para asegurar su satisfacción.", 
    "improvement": "El operador veo que se llama Franco  segun la conversacion en este caso. 
    Dio informacion correcta pero veo que pidio los datos de ingreso del panel de control del cliente sin explicarle que 
    estan en un medio seguro como vemos en este text que envio el agente de soporte: Por favor paseme los datos del cpanel. 
    Deberia empatizar con la situacion del cliente atendiendo su situacion emocional y ofreciendo soluciones proactivas 
    aun que la solucion no sea inmediata" }"""
)


system_prompt2 = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words"
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters and an 'improvement' key which must give an explanation of how to improve the score that you chose in a maximum of 800 characters  . "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' key. DO NOT output anything else, only the json score."
    """the final answer must be inside a json similar to this example but not using the same word as this example: {
  "score": "neutral",
  "reason": "La interacción fue correcta desde el punto de vista informativo, pero 
  la experiencia del cliente puede verse afectada cuando la resolución no es inmediata. 
  La falta de una solución instantánea, ya sea por problemas de servidor o por políticas internas, genera incertidumbre y 
  frustración. Aunque el agente comunicó la situación, faltó reforzar el acompañamiento emocional y la sensación de 
  seguimiento continuo. El cliente recibió respuestas válidas, pero no percibió un compromiso activo con su tranquilidad 
  ni con la gestión del problema a lo largo del tiempo.",
  "improvement": "Para mejorar el score de satisfacción del cliente, el agente debe priorizar la empatía y
   la proactividad. Es clave validar explícitamente la molestia del cliente y explicar con claridad por qué
    la resolución no puede ser inmediata, usando un lenguaje simple y cercano. Ofrecer pasos concretos, 
    como plazos estimados, alternativas temporales o la promesa de un seguimiento, ayuda a reducir la ansiedad. 
    Mantener informado al cliente, incluso sin novedades técnicas, refuerza la confianza. Un cierre empático, 
    agradeciendo la paciencia y reafirmando el compromiso de la empresa con la resolución, permite transformar una 
    limitación operativa en una experiencia de atención más humana y satisfactoria."}"""

)

available= True


from datetime import datetime

def format_time_diff(prev_time, curr_time):
    if not prev_time or not curr_time:
        return ""
    try:
        dt1 = datetime.fromisoformat(prev_time)
        dt2 = datetime.fromisoformat(curr_time)
        diff = dt2 - dt1
        seconds = diff.total_seconds()
        
        prefix = "+"
        if seconds < 0:
            prefix = "-"
            seconds = abs(seconds)
            
        if seconds < 60:
            return f" ({prefix}{int(seconds)}s)"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f" ({prefix}{minutes}m)"
        else:
            hours = int(seconds / 3600)
            return f" ({prefix}{hours}h)"
    except Exception:
        return ""

def format_conversation_with_time(messages_list):
    formatted_lines = []
    last_time = None
    last_operator_name = None
    
    for i, m in enumerate(messages_list):
        current_time = m.get("timestamp")
        author_name = m.get("author_name")
        role = m['role']
        
        # calculate time diff
        time_str = ""
        if last_time and current_time:
            time_str = format_time_diff(last_time, current_time)
            
        # Detect transfer or identify operator
        role_label = role.capitalize()
        
        # If it's a support agent and has a name
        if role == "support agent" and author_name:
            role_label = f"Support agent ({author_name})"
            
            # Check for transfer
            if last_operator_name and last_operator_name != author_name:
                 formatted_lines.append(f"[System: Conversation transferred from {last_operator_name} to {author_name}]")
            
            last_operator_name = author_name
            
        content = m['content']
        line = f"{i+1} - {role_label}{time_str}: {content}"
        formatted_lines.append(line)
        
        if current_time:
            last_time = current_time
            
    return "\n".join(formatted_lines)

def get_score(prompt):
    conversation_text = format_conversation_with_time(prompt["messages"])

    messages =[
                {"role": "developer", "content": system_prompt},
                {"role": "user" , "content": conversation_text},
                {"role": "assistant", "thinking": "null", "content":"json score of: 'horrible', 'bad', 'neutral', 'good', 'great'..."},
            ] 

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        padding=True,
        
    ).to(model.device)

    output_ids = model.generate(input_ids, max_new_tokens=512, attention_mask=input_ids.ne(tokenizer.pad_token_id),do_sample=False)
    response = tokenizer.batch_decode(output_ids)[0]
    final = json.loads(response.split("<|end|>".strip())[5].replace("<|start|>assistant<|channel|>final<|message|>", "").replace("<|return|>",""))
    print(response)
    print("<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>")
    print( final, final['score'] )
    print("<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>")
    print()
    return final


def extract_last_json_from_response(response_text):
    """
    Finds and parses the LAST complete JSON object in a string.
    This is necessary because the system prompt contains an example JSON.
    """
    json_objects = []
    
    # Simple counting approach to find potential JSON boundaries
    start_brace_index = -1
    
    for i, char in enumerate(response_text):
        if char == '{':
            start_brace_index = i
        elif char == '}' and start_brace_index != -1:
            try:
                # Attempt to extract and parse the potential JSON string
                json_string = response_text[start_brace_index : i + 1].strip()
                
                # Check if the string actually looks like a valid score JSON 
                # (A simple heuristic to filter out random braces)
                if 'score' in json_string and 'reason' in json_string:
                    parsed_json = json.loads(json_string)
                    json_objects.append(parsed_json)
                    
                # Reset start_brace_index after finding a potential object boundary
                # This helps find subsequent, separate objects.
                start_brace_index = -1
            except json.JSONDecodeError:
                # If parsing fails, just continue the search
                start_brace_index = -1
            except Exception:
                # Other errors, continue
                pass

    if not json_objects:
        raise ValueError("No valid score JSON object could be found in the response.")

    # 🟢 CRITICAL FIX: Return the last successfully parsed object
    return json_objects[-1]

def get_scores_batch(prompts_list):
    """
    Accepts a LIST of prompts (conversations) and processes them in parallel on the GPU.
    """
    all_messages = []
    
    # 1. Prepare all prompts for the tokenizer
    for prompt in prompts_list:
        # NOTE: Your prompt structure from the client has a key 'messages' inside the 'data'
        # The data being sent is the output of convert_to_harmony, which contains the messages list.
        # Assuming the input to get_scores_batch is a list of dictionaries, where each dict 
        # has a 'messages' key containing the conversation:
        
        conversation_text = format_conversation_with_time(prompt["messages"])
        
        # Wrap the conversation string with the system prompt template
        messages =[
             {"role": "developer", "content": system_prompt},
             {"role": "user" , "content": conversation_text},
             {"role": "assistant", "thinking": "null", "content":"json score of: 'horrible', 'bad', 'neutral', 'good', 'great'..."},
        ]
        all_messages.append(messages)

    # 2. 🟢 CRITICAL: TOKENIZE THE ENTIRE BATCH WITH PADDING=TRUE
    # This creates the single, rectangular tensor for parallel processing.
    input_ids = tokenizer.apply_chat_template(
        all_messages, # <<< List of separate conversations
        add_generation_prompt=True,
        return_tensors="pt",
        padding=True, # <<< THIS ACTIVATES GPU PARALLELISM
         
    ).to(model.device)
    
    attention_mask = input_ids.ne(tokenizer.pad_token_id)
    
    # 3. Parallel Inference (One model.generate call for the whole batch)
    output_ids = model.generate(
        input_ids,
        max_new_tokens=512,
        attention_mask=attention_mask,
        do_sample=False
    )
    
    # 4. Decode the batch results
    responses = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    
    # 5. Extract and parse the JSON score for each response
    print(responses)
    final_scores = []
    for i, response in enumerate(responses):
        try:
             # Your custom JSON parsing logic
             final = extract_last_json_from_response(response)
             final_scores.append(final)
        except Exception as e:
            print(f"Error parsing response {i}: {e}")
            final_scores.append({"score": "error", "reason": "Parsing failed on server."})
            
    return final_scores

ai_bp = Blueprint('ai_score', __name__)


@ai_bp.route("/ai/check_gpu", methods=["GET"])
def check_gpu():
    return jsonify({"gpu": available}), 200


@ai_bp.route("/ai/batch_score", methods=["POST"])
def batch_chat_controller():
    # Expects a list of prompt objects: data = [ {prompt_1}, {prompt_2}, ... ]
    available = False
    data = request.get_json()

    if not isinstance(data, list) or not data:
        available = True
        return jsonify({"error": "Invalid batch data format, expecting a list of prompts"}), 400

    try:
        results = get_scores_batch(data)
        # The response MUST be a list of results corresponding to the input list
        print(results)
        available = True
        return jsonify(results), 200
    except Exception as e:
        print(f"Error during batch inference: {e}")
        available = True
        return jsonify({"error": "error with the batch score query"}), 500

#have to feed it the current conversations


@ai_bp.route("/ai", methods=["POST"])
def chat_controller():
    response = None
    if not available:
        response = jsonify({"error":"service temporarily unavailable"}), 503
    else:
            
        data = request.get_json()
        if not data:
            response = jsonify({"error": "insuficient data"}), 400
            
        else:
            try:
                #score_request_counter += 1
                score = get_score(data)
                #score_request_counter -= 1
                response = jsonify(score), 200
            except Exception as e:
                #score_request_counter -= 1
                print(e)
                response =  jsonify({"error": "error with the score query"}), 500
    return response


'''
from werkzeug.wrappers import response
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from flask import Blueprint, jsonify, request
available= False
score_request_counter = 0

model_path = "/home/juli/gptoss/gpt-oss-20b"

tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    local_files_only=True,
    device_map="auto"
)


system_prompt = (
    "You are a concise AI assistant. That can view a user's messages of an ongoing chat(chat is currently ongoing thus is still not finished) and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words. "
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention, a 'reason' key which must give an explanation of why you gave it the score that you chose in a maximum of 500 characters, and a 'chat_eval' key. "
    "The 'chat_eval' key must be a list of objects representing the conversation, where each object has 'text' (the message content), 'role' (the sender), and an 'eval' key (only for the support agent, classifying the message as horrible, bad, neutral, good, or great). "
    "Do NOT explain or justify the rating outside of the json's 'reason' key and do not used any language other than spanish in the 'reason' key. DO NOT output anything else, only the json score."
    'the final answer must be inside a json such as this example: {"score": "neutral", "reason": "Califiqué la interacción como neutral porque el agente de soporte dio la información correcta, pero el tono fue algo impersonal y poco empático. El problema se resolvió, pero el cliente no pareció completamente tranquilo, y faltó una actitud proactiva para asegurar su satisfacción.", "chat_eval": [{"text": "Que tal buenas tardes", "role": "Support agent", "eval": "Good"}, {"text": "Hola Franco, una consulta", "role": "Client"}] }'
)

available= True


def get_score(prompt):
  conversation_text = "\n".join(
      [f"{m['role'].capitalize()}: {m['content']}" for m in prompt["messages"]]
  )

  messages =[
              {"role": "developer", "content": system_prompt},
              {"role": "user" , "content": conversation_text},
              {"role": "assistant", "thinking": "null", "content":"json score of: 'horrible', 'bad', 'neutral', 'good', 'great'..."},
          ] 

  input_ids = tokenizer.apply_chat_template(
      messages,
      add_generation_prompt=True,
      return_tensors="pt",
      padding=True,
      
  ).to(model.device)

  output_ids = model.generate(input_ids, max_new_tokens=512,attention_mask=input_ids.ne(tokenizer.pad_token_id) , do_sample=False)
  response = tokenizer.batch_decode(output_ids)[0]
  final = json.loads(response.split("<|end|>".strip())[5].replace("<|start|>assistant<|channel|>final<|message|>", "").replace("<|return|>",""))
  print(response)
  print("<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>")
  print( final, final['score'] )
  print("<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>")
  print()
  return final


ai_bp = Blueprint('ai_score', __name__)



#have to feed it the current conversations
@ai_bp.route("/ai", methods=["POST"])
def chat_controller():
    response = None
    if not available:
        response = jsonify({"error":"service temporarily unavailable"}), 503
    else:
            
        data = request.get_json()
        if not data:
            response = jsonify({"error": "insuficient data"}), 400
            
        else:
            try:
                #score_request_counter += 1
                score = get_score(data)
                #score_request_counter -= 1
                response = jsonify(score), 200
            except Exception as e:
                #score_request_counter -= 1
                print(e)
                response =  jsonify({"error": "error with the score query"}), 500
    return response
'''