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
    "You are a concise AI assistant. user's that can view a user's messages and rate the support agent's customer attention to the client which can be one of 5 (horrible, bad, neutral, good, great), and thus your answer must be limited to a json with a score key that must contain one of those 5 words"
    "Read the conversation and output ONLY a json containing a 'score' key indicating the client's satisfaction with the support agent's attention. "
    "Do NOT explain or justify the rating. DO NOT output anything else, only the json score."
    'the final answer must be inside a json such as this example: {"score": "neutral" }'
)

available= True


def get_score(prompt):
  conversation_text = "\n".join(
      [f"{m['role'].capitalize()}: {m['content']}" for m in prompt["messages"]]
/  )

  messages =[
              {"role": "developer", "content": system_prompt},
              {"role": "user" , "content": conversation_text},
              {"role": "assistant", "thinking": "null", "content":"json score of: 'horrible', 'bad', 'neutral', 'good', 'great'..."},
          ] 

  input_ids = tokenizer.apply_chat_template(
      messages,
      add_generation_prompt=True,
      return_tensors="pt",
  ).to(model.device)

  output_ids = model.generate(input_ids, max_new_tokens=512)
  response = tokenizer.batch_decode(output_ids)[0]
  final = json.loads(response.split("<|end|>".strip())[5].replace("<|start|>assistant<|channel|>final<|message|>", "").replace("<|return|>",""))

  #print( final, final['score'] )
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
                response =  jsonify({"error": "error with the ai query"}), 500
    return response
