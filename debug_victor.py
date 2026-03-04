import pymysql

def debug_victor_chat():
    connection = pymysql.connect(
        host='mysql.towebs.com',
        user='julian',
        password='jul23789ian',
        database='twchat',
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM chat_chat WHERE operator_id = 146 ORDER BY id DESC LIMIT 1;")
        chat = cursor.fetchone()
        print("Chat ID:", chat['id'])
        
        cursor.execute(f"SELECT user_alias, user_role, message_type, message_text FROM chat_message WHERE chat_id_id = {chat['id']};")
        messages = cursor.fetchall()
        for i, m in enumerate(messages):
            print(f"[{i}] Alias: '{m['user_alias']}', Role: '{m['user_role']}', Type: '{m['message_type']}'")
            print(f"    Text: {m['message_text'][:100]}")
            
if __name__ == "__main__":
    debug_victor_chat()
