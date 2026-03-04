import pymysql

def find_victor():
    try:
        connection = pymysql.connect(
            host='mysql.towebs.com',
            user='julian',
            password='jul23789ian',
            database='twchat',
            cursorclass=pymysql.cursors.DictCursor
        )
        with connection.cursor() as cursor:
            # Get list of unique operator aliases to find "Victor"
            cursor.execute("SELECT DISTINCT user_alias, user_role FROM chat_message WHERE user_role = 'operator';")
            operators = cursor.fetchall()
            print("Found Operator Aliases:")
            for op in operators:
                if 'victor' in (op['user_alias'] or '').lower():
                    print(f"*** EXACT MATCH ***: {op}")
                else:
                    print(op['user_alias'])
                    
            # Let's also check if there's another DB with users
            cursor.execute("SHOW DATABASES;")
            print("\nDatabases available:", [db['Database'] for db in cursor.fetchall()])
            
            # Let's check operator_id in chat_chat
            cursor.execute('''
                SELECT operator_id, COUNT(*) as chat_count 
                FROM chat_chat 
                WHERE operator_id IS NOT NULL 
                GROUP BY operator_id 
                ORDER BY chat_count DESC LIMIT 10;
            ''')
            top_ops = cursor.fetchall()
            print("\nTop Operator IDs by Chat Count:")
            for op in top_ops:
                print(op)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    find_victor()
