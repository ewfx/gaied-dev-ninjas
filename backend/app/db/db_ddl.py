
from app.db.sqlite_db_config import SQLiteDBConfig as DBConfig

class DB_DDL:
    def __init__(self):
        self.db_config = DBConfig()
    
    def create_email_table(self):
        self.db_config.cursor.execute("CREATE TABLE IF NOT EXISTS EMAIL "
        "("
        "EMAIL_ID INTEGER PRIMARY KEY AUTOINCREMENT, "
        "SENDER TEXT, "
        "RECIEPIENT TEXT, "
        "SUBJECT TEXT, "
        "BODY TEXT, "
        "S3_MESSAGE_PATH TEXT, "
        "CREATED_AT int, "
        "UPDATED_AT int, "
        "REQUEST_TYPE TEXT, "
        "SUB_REQUEST_TYPE TEXT, "
        "PROCESSING_STATUS TEXT, "
        "HAS_ATTACHMENTS BOOLEAN, "
        "ATTACHMENT_METADATA TEXT, "
        "CATEGORY_TYPE TEXT, "
        "CATEGORY TEXT "
        ")")
        self.db_config.conn.commit()
        print("Created EMAIL table")
    
    def delete_email_table(self):
        self.db_config.cursor.execute("DROP TABLE IF EXISTS EMAIL")
        self.db_config.conn.commit()
        print("Deleted EMAIL table")
    
    def close(self):
        self.db_config.close()
    
# if __name__ == "__main__":
#     db_ddl = DB_DDL()
#     db_ddl.delete_email_table()
#     db_ddl.create_email_table()
#     db_ddl.close()