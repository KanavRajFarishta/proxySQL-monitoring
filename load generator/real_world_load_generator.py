# real_world_load_generator.py

import time
import random
import pymysql

DB_CONFIG = {
    'host': '127.0.0.1',   # ProxySQL MySQL traffic port
    'port': 16033,
    'user': 'testuser',
    'password': 'testpassword',
    'database': 'testdb',
    'cursorclass': pymysql.cursors.DictCursor
}

def random_sleep():
    """Sleep a random time between 0.5 and 1.5 seconds to simulate real users."""
    time.sleep(random.uniform(0.5, 1.5))

def simulate_real_world_traffic():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        with connection.cursor() as cursor:
            # Create a simple table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    activity VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            connection.commit()

            activities = ['login', 'logout', 'view', 'purchase', 'click']

            while True:
                action = random.choice(['select', 'insert', 'update', 'delete'])

                if action == 'select':
                    cursor.execute("SELECT * FROM user_activity ORDER BY created_at DESC LIMIT 5;")
                    result = cursor.fetchall()
                    print(f"SELECT {len(result)} rows")
                
                elif action == 'insert':
                    username = f"user{random.randint(1, 100)}"
                    activity = random.choice(activities)
                    cursor.execute("INSERT INTO user_activity (username, activity) VALUES (%s, %s);", (username, activity))
                    connection.commit()
                    print(f"INSERT {username} - {activity}")
                
                elif action == 'update':
                    cursor.execute("UPDATE user_activity SET activity=%s WHERE id IN (SELECT id FROM (SELECT id FROM user_activity ORDER BY RAND() LIMIT 1) as t);", (random.choice(activities),))
                    connection.commit()
                    print("UPDATE 1 row")
                
                elif action == 'delete':
                    cursor.execute("DELETE FROM user_activity WHERE id IN (SELECT id FROM (SELECT id FROM user_activity ORDER BY RAND() LIMIT 1) as t);")
                    connection.commit()
                    print("DELETE 1 row")

                random_sleep()

    except KeyboardInterrupt:
        print("\nStopping real-world load generator...")
    finally:
        connection.close()

if __name__ == "__main__":
    simulate_real_world_traffic()
