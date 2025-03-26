from app.db import check_duplicate_email


def store_email(email: dict):
  from app.db import Email
  from app.db.email_repo import EmailRepo 
  subject = email.get("subject")
  sender = email.get("from")
  recipients = email.get("to")
  body = email.get("body", "")
  attachments = email.get("attachments")
  has_attachment = len(attachments) > 0 if attachments else False
  is_duplicate = check_duplicate_email(body, has_attachment)
  print("is_duplicate", is_duplicate)
  if not is_duplicate: 
    # Store email in database
    email = Email({
          "sender": sender,
          "recipient": recipients,
          "subject": subject,
          "body": body,
          "s3_message_path": None,
          "request_type": None,
          "sub_request_type": None,
          "processing_status": None,
          "has_attachment": has_attachment,
          "attachment_metadata": None,
          "category_type": None,
          "category": None
      }, allows_missing_keys=True)    
    emailRepo = EmailRepo()
    email_id = emailRepo.insert_email(email)
    emailRepo.close()
    return {"email_id": email_id, "is_duplicate": is_duplicate}
  return {"email_id": None, "is_duplicate": is_duplicate}