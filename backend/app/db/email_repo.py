import sqlite3 # type: ignore
from app.db.email_dto import Email

class EmailRepo:
    def __init__(self):
        from app.db.sqlite_db_config import SQLiteDBConfig as DBConfig
        self.db_config = DBConfig()
    
    def insert_email(self, email: Email):
        try:
            row = self.db_config.cursor.execute("INSERT INTO EMAIL (SENDER, RECIEPIENT, SUBJECT, BODY, "
            "S3_MESSAGE_PATH, REQUEST_TYPE, SUB_REQUEST_TYPE, PROCESSING_STATUS, HAS_ATTACHMENTS, "
            "ATTACHMENT_METADATA, CATEGORY_TYPE, CATEGORY, CREATED_AT )"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, strftime('%s','now')) RETURNING EMAIL_ID",
            (email.sender, email.recipient, email.subject, email.body, email.s3_message_path, email.request_type, 
             email.sub_request_type, email.processing_status, email.has_attachment, email.attachment_metadata, 
             email.category_type, email.category))
            if row:
                email_id = int(row.fetchone()[0])
                print("Email INSERTED with email_id:", email_id)
                self.db_config.conn.commit()
                return email_id
        except sqlite3.DatabaseError as e:
            print(f"Error inserting email: {e}")
        return None
    
    def update_email(self, email: Email):
        try:
            self.db_config.cursor.execute("UPDATE EMAIL SET SENDER = ?, RECIEPIENT = ?, SUBJECT = ?, BODY = ?, "
            "S3_MESSAGE_PATH = ?, REQUEST_TYPE = ?, SUB_REQUEST_TYPE = ?, PROCESSING_STATUS = ?, HAS_ATTACHMENTS = ?, ATTACHMENT_METADATA = ?, "
            "UPDATED_AT = strftime('%s','now'), CATEGORY_TYPE = ?, CATEGORY = ? WHERE EMAIL_ID = ?",
            (email.sender, email.recipient, email.subject, email.body, email.s3_message_path, email.request_type, 
             email.sub_request_type, email.processing_status, email.has_attachment, email.attachment_metadata, 
             email.category_type, email.category, email.email_id))
            self.db_config.conn.commit()
            print("Email updated successfully")
        except sqlite3.DatabaseError as e:
            print(f"Error updating email: {e}")
    
    def get_email(self, email_id: int):
        try:
            self.db_config.cursor.execute("SELECT EMAIL_ID, SENDER, RECIEPIENT, SUBJECT, BODY, S3_MESSAGE_PATH, "
            "datetime(CREATED_AT, 'unixepoch'), datetime(UPDATED_AT, 'YYYY-MM-DD HH24:MI:SS'), "
            "REQUEST_TYPE, SUB_REQUEST_TYPE, PROCESSING_STATUS, HAS_ATTACHMENTS, ATTACHMENT_METADATA, "
            "CATEGORY_TYPE, CATEGORY FROM EMAIL WHERE EMAIL_ID = ?", (email_id,))
            row = self.db_config.cursor.fetchone()
            if row:
                print("Email found for id: ", email_id)
                return EmailRepo.build_email_dto(row)
        except sqlite3.DatabaseError as e:
            print(f"Error fetching email: {e}")
        return None
    
    def get_all_email(self):
        try:
            self.db_config.cursor.execute("SELECT EMAIL_ID, SENDER, RECIEPIENT, SUBJECT, BODY, S3_MESSAGE_PATH, "
            "datetime(CREATED_AT, 'unixepoch'), datetime(UPDATED_AT, 'unixepoch'), "
            "REQUEST_TYPE, SUB_REQUEST_TYPE, PROCESSING_STATUS, HAS_ATTACHMENTS, ATTACHMENT_METADATA, CATEGORY_TYPE, CATEGORY FROM EMAIL")
            rows = self.db_config.cursor.fetchall()
            return [EmailRepo.build_email_dto(row) for row in rows]
        except sqlite3.DatabaseError as e:
            print(f"Error fetching all emails: {e}")
            return []
    
    def build_email_dto(row):
        return Email({
            "email_id": row[0],
            "sender": row[1],
            "recipient": row[2],
            "subject": row[3],
            "body": row[4],
            "s3_message_path": row[5],
            "created_at": row[6],
            "updated_at": row[7],
            "request_type": row[8],
            "sub_request_type": row[9],
            "processing_status": row[10],
            "has_attachment": bool(row[11]),
            "attachment_metadata": row[12],
            "category_type": row[13],
            "category": row[14]
        })
    
    def close(self):
        self.db_config.close()

