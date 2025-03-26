
import json
from app.db import Email, EmailRepo, DB_DDL

def main():
    email = Email({
        "sender": "b",
        "recipient": "b",
        "subject": "my-subject",
        "body": "my-body",
        "s3_message_path": None,
        "request_type": "test",
        "sub_request_type": "tes-sub",
        "processing_status": "SUCCESS",
        "has_attachment": True,
        "attachment_metadata": ""
    }, allows_missing_keys=True)
    emailRepo = EmailRepo()
    emailRepo.insert_email(email)
    emailId = emailRepo.get_all_email()[0].email_id
    print("Email ID:", emailId)
    tempEmail = emailRepo.get_email(emailId)
    if tempEmail is not None:
        print(json.dumps(tempEmail.__dict__))
        tempEmail.request_type = "new request"
        emailRepo.update_email(tempEmail)
        temp2 = emailRepo.get_email(emailId)
        print(json.dumps(temp2.__dict__))
        print("REQUEST_TYPE: ", temp2.request_type)

def get_all_emails():
    print("************* All emails *************")
    emailRepo = EmailRepo()
    allEmails = emailRepo.get_all_email()
    for e in allEmails:
        print(json.dumps(e.__dict__))
    emailRepo.close()

def create_email_table():
    db_ddl = DB_DDL()
    db_ddl.create_email_table()
    db_ddl.close()

def delete_email_table():
    db_ddl = DB_DDL()
    db_ddl.delete_email_table()
    db_ddl.close()

if __name__ == "__main__":
    # delete_email_table()
     create_email_table()
    # main()
    #get_all_emails()
    