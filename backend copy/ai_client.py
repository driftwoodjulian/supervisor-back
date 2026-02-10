import json
import random
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AIClient:
    def __init__(self):
        self.host_b_ip = os.getenv("HOST_B_IP", "127.0.0.1")
        self.base_url = f"http://{self.host_b_ip}:8000/v1"
        self.simulate = os.getenv("SIMULATE_AI", "False").lower() == "true"
        self.model_name = "supervisor-ai"

        # Load Quality Manual
        try:
            # Assumes backend/ai_client.py -> parent is backend -> parent is root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            manual_path = os.path.join(base_dir, 'manual.txt')
            with open(manual_path, 'r', encoding='utf-8') as f:
                manual_content = f.read()
        except Exception as e:
            print(f"Warning: Could not load manual.txt: {e}")
            manual_content = ""

        self.system_prompt = (
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
            "}\n\n"
            "### QUALITY MANUAL / GUIDELINES\n"
            f"{manual_content}\n"
        )

    def _resolve_connection(self):
        """
        Query AI Manager to find out which model is active and where it is running.
        Returns (base_url, model_name)
        """
        manager_url = f"http://{self.host_b_ip}:5002/status"
        try:
            resp = requests.get(manager_url, timeout=2).json()
            status = resp.get("status")
            model = resp.get("model")
            
            if status != "active":
                print(f"Warning: AI Manager reports status '{status}'")
            
            if model == "gemma":
                # Ollama Configuration
                return f"http://{self.host_b_ip}:11434/v1", "gemma2:27b"
            else:
                # Default / GPT-OSS Configuration (vLLM)
                return f"http://{self.host_b_ip}:8000/v1", "supervisor-ai"
                
        except Exception as e:
            print(f"Error querying AI Manager: {e}. Defaulting to GPT-OSS.")
            return f"http://{self.host_b_ip}:8000/v1", "supervisor-ai"

    def evaluate_chat(self, history):
        """
        Sends chat history to AI Host and returns parsed JSON evaluation.
        History should be a list of dicts: [{'role': 'user'|'agent', 'content': '...', 'timestamp': '...', 'author_name': '...'}]
        """
        if self.simulate:
            print("AI Client: SIMULATION MODE")
            return self._test_response()

        # Resolve active model connection
        base_url, model_name = self._resolve_connection()

        # Filter history to only include the conversation after the last agent transfer
        history = self._filter_transfer_history(history)

        formatted_conversation = self._format_conversation_with_time(history)
        
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": formatted_conversation}
            ],
            "temperature": 0.0,
            "max_tokens": 4096
        }
        
        # Safety Truncation Logic (Targeting 8192 context)
        # 1024 (output) + System (~400) + Manual (~2300) = ~3724 reserved.
        # Leaving ~4400 for chat.
        # We'll use a conservative estimate: 8192 - 1024 - 500 (buffer) = 6668 max input tokens.
        
        TOTAL_CTX_LIMIT = 8192
        MAX_INPUT_TOKENS = TOTAL_CTX_LIMIT - payload["max_tokens"] - 200 # Buffer
        
        # Estimate current input
        current_input_text = self.system_prompt + formatted_conversation
        estimated_tokens = self._estimate_tokens(current_input_text)
        
        # Truncate if necessary
        if estimated_tokens > MAX_INPUT_TOKENS:
            print(f"DEBUG: Input too long ({estimated_tokens} > {MAX_INPUT_TOKENS}). Truncating history...")
            # Iteratively remove oldest messages
            while estimated_tokens > MAX_INPUT_TOKENS and len(history) > 1:
                history.pop(0) # Remove oldest
                formatted_conversation = self._format_conversation_with_time(history)
                current_input_text = self.system_prompt + formatted_conversation
                estimated_tokens = self._estimate_tokens(current_input_text)
            
            # Update payload content
            payload["messages"][1]["content"] = formatted_conversation
        
        # Safety Truncation Logic (Targeting 8192 context)
        # 1024 (output) + System (~400) + Manual (~2300) = ~3724 reserved.
        # Leaving ~4400 for chat.
        # We'll use a conservative estimate: 8192 - 1024 - 500 (buffer) = 6668 max input tokens.
        
        TOTAL_CTX_LIMIT = 8192
        MAX_INPUT_TOKENS = TOTAL_CTX_LIMIT - payload["max_tokens"] - 200 # Buffer
        
        # Estimate current input
        current_input_text = self.system_prompt + formatted_conversation
        estimated_tokens = self._estimate_tokens(current_input_text)
        
        # Truncate if necessary
        if estimated_tokens > MAX_INPUT_TOKENS:
            print(f"DEBUG: Input too long ({estimated_tokens} > {MAX_INPUT_TOKENS}). Truncating history...")
            # Iteratively remove oldest messages
            while estimated_tokens > MAX_INPUT_TOKENS and len(history) > 1:
                history.pop(0) # Remove oldest
                formatted_conversation = self._format_conversation_with_time(history)
                current_input_text = self.system_prompt + formatted_conversation
                estimated_tokens = self._estimate_tokens(current_input_text)
            
            # Update payload content
            payload["messages"][1]["content"] = formatted_conversation


        try:
            print(f"Sending request to AI Host: {base_url}")
            response = requests.post(f"{base_url}/chat/completions", json=payload)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"AI CONNECTION ERROR: {e}")
                print(f"RESPONSE BODY: {response.text}")
                print(f"FAILED PAYLOAD: {json.dumps(payload, indent=2)}")
                raise e
            
            result = response.json()
            print(f"DEBUG RAW AI RESPONSE: {json.dumps(result, indent=2)}")
            if not result or 'choices' not in result or not result['choices']:
                 raise Exception(f"Invalid API response: {result}")

            # Handling for reasoning models (e.g. DeepSeek R1, or similar distilled models)
            # The model seems to output reasoning in 'content' or 'reasoning_content' and hits token limit.
            
            msg = result["choices"][0]["message"]
            content = msg.get("content")
            
            # If content is null, check reasoning_content (common in some vLLM setups for reasoning models)
            if content is None:
                print(f"DEBUG: Content is None. Checking reasoning_content...")
                content = msg.get("reasoning_content") or msg.get("reasoning")
            
            if content is None:
                 print(f"DEBUG: AI returned None content. Raw result: {json.dumps(result)}")
                 raise Exception("AI returned empty/null content")

            # Clean up content to ensure it's just JSON
            # Sometimes reasoning models output: <think>...</think> JSON
            # or ```json ... ```
            content = self._extract_json(content)
            parsed_result = json.loads(content)
            
            # Ensure required fields exist
            return {
                "score": parsed_result.get("score") or "unknown",
                "reason": parsed_result.get("reason") or "No reason provided",
                "improvement": parsed_result.get("improvement") or "No improvement provided",
                "key_messages": parsed_result.get("key_messages") or []
            }

        except Exception as e:
            print(f"AI Client Error: {e}")
            # Fallback must return a valid structure for the DB
            return {
                "score": "unknown", 
                "reason": f"AI Connection Failure: {str(e)}",
                "improvement": "Check Host B connection.",
                "key_messages": []
            }

    def _estimate_tokens(self, text):
        """
        Rough token estimation. Safe replacement for len(text)/4.
        Llama/GPT tokenizers are roughly 3-4 chars per token.
        We'll use 3.0 to be safe (over-estimate token count).
        """
        if not text:
            return 0
        return int(len(text) / 3.5) # Standard estimate: 3.5 chars per token

    def _extract_json(self, text):
        if text is None:
             return "{}"
        
        # Remove <think> blocks if present (DeepSeek Style)
        if "<think>" in text and "</think>" in text:
            text = text.split("</think>")[-1]
            
        # Try to find JSON code block
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end != -1:
                return text[start:end]
                
        # Fallback to find the first '{' and last '}'
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
            
        return text # Try parsing raw as last resort

    def _format_time_diff(self, prev_time, curr_time):
        if not prev_time or not curr_time:
            return ""
        try:
            if isinstance(prev_time, str):
                dt1 = datetime.fromisoformat(prev_time)
            else:
                dt1 = prev_time

            if isinstance(curr_time, str):
                dt2 = datetime.fromisoformat(curr_time)
            else:
                dt2 = curr_time

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

    def _format_conversation_with_time(self, messages_list):
        formatted_lines = []
        last_time = None
        last_operator_name = None
        
        for i, m in enumerate(messages_list):
            # Safe get for models.Message which might not be a dict
            if isinstance(m, dict):
                current_time = m.get("timestamp")
                author = m.get("author", {}) or {}
                author_name = author.get("name") if isinstance(author, dict) else None
                role = m.get("role", "user")
                content = m.get("content")
                if content is None:
                    content = ""
            else:
                # If it's a SQLAlchemy object, attributes accessed differently
                # But Orchestrator seems to pass a cleaned dict or we need to adjust Orchestrator
                # Let's assume Orchestrator passes logical objects.
                # Actually, Orchestrator line 48: history = [{"role": ..., "content": ...}] without timestamps.
                # We need to update Orchestrator to pass full context.
                return "Error: Message format update required."

            # Calculate time diff
            time_str = ""
            if last_time and current_time:
                time_str = self._format_time_diff(last_time, current_time)
                
            role_label = role.capitalize()
            
            if role == "agent" and author_name:
                role_label = f"Support agent ({author_name})"
                if last_operator_name and last_operator_name != author_name:
                     formatted_lines.append(f"[System: Conversation transferred from {last_operator_name} to {author_name}]")
                last_operator_name = author_name
                
            line = f"{i+1} - {role_label}{time_str}: {content}"
            formatted_lines.append(line)
            
            if current_time:
                last_time = current_time
                
        return "\n".join(formatted_lines)

    def _test_response(self):
        return {
            "score": random.choice(["horrible", "bad", "neutral", "good", "great"]),
            "reason": "Evaluación simulada: El agente respondió correctamente pero podría haber sido más rápido.",
            "improvement": "Se sugiere utilizar plantillas de respuesta para agilizar la atención.",
            "key_messages": [1, 3]
        }

    def _filter_transfer_history(self, history):
        """
        Scans history for agent transfers (change in agent name).
        Returns the slice of history starting from the last confirmed transfer.
        If no transfer, returns full history.
        """
        last_agent_name = None
        transfer_index = 0
        
        for i, m in enumerate(history):
            if isinstance(m, dict):
                role = m.get("role", "user")
                if role == "agent":
                    author = m.get("author", {}) or {}
                    name = author.get("name") if isinstance(author, dict) else None
                    
                    if name:
                        # If we have a previous agent and the name changed, it's a transfer
                        if last_agent_name and name != last_agent_name:
                            # We set the start point to this message (start of new agent's session)
                            transfer_index = i
                            print(f"DEBUG: Agent transfer detected at index {i} ({last_agent_name} -> {name})")
                        
                        last_agent_name = name
        
        if transfer_index > 0:
            print(f"DEBUG: Truncating history to last transfer (keeping {len(history)-transfer_index} messages)")
            return history[transfer_index:]
            
        return history
