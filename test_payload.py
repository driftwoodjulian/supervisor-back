from backend.ai_client import AIClient
import json

def test():
    client = AIClient()
    mock_history = [
        {"role": "user", "content": "hola, estoy teniendo inconvenientes con la cuenta de correo, no me entran los mails", "timestamp": "2026-03-04T12:00:00"},
        {"role": "agent", "content": "por favor revise su configuracion", "timestamp": "2026-03-04T12:05:00", "author": {"name": "TestAgent"}}
    ]
    
    print("Building Payload...")
    payload = client.build_payload(mock_history)
    print("--------------------------------------------------")
    print("SYSTEM ROLE CONTENT INJECTED:")
    print("--------------------------------------------------")
    print(payload["messages"][0]["content"])
    print("--------------------------------------------------")

if __name__ == "__main__":
    test()
