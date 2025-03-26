import sqlite3

class SQLiteDBConfig:
    def __init__(self):
        try:
            db_path = "hackathon.db"
            self.conn = sqlite3.connect(db_path)
            print(f"Connected to SQLite database at {db_path}")
            self.cursor = self.conn.cursor()
        except sqlite3.DatabaseError as e:
            print(f"Error connecting to SQLite database: {e}")
            self.conn = None
            self.cursor = None
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Closed connection to SQLite database")

# Example usage
# if __name__ == "__main__":
#     db_config = SQLiteDBConfig()
#     db_config.close()