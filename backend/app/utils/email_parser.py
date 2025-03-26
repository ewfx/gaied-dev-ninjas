import email
import os
from email import policy
from email.parser import BytesParser
from typing import Dict, List
from io import BytesIO
from .extract_text_from_attachment import extract_text_from_attachment
from .store_email_to_db import store_email

def parse_email(eml_content: bytes) -> Dict:
    """
    Parses an EML file content and extracts key email components.
    
    :param eml_content: The raw bytes content of an EML file
    :return: Dictionary containing email body, subject, sender, recipient(s), and attachment names.
    """
    # Parse the email content
    msg = BytesParser(policy=policy.default).parse(BytesIO(eml_content))

    # Extract subject, sender, and recipients
    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    recipients = msg.get("To", "")

    # Extract the email body (handling plain text and HTML)
    body = None
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":  # Prefer plain text over HTML
                body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                break
    else:
        body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")

    # Extract attachment names
    email_data = {       
        "attachments": []
    }
    for part in msg.walk():
        if part.get_content_disposition() == "attachment":
            filename = part.get_filename()
            if filename:
               email_data["attachments"].append({
                    "filename": filename,
                    "content": part.get_payload(decode=True)
                })
    
    attachments = []
    for attachment in email_data["attachments"]:
        text = extract_text_from_attachment(attachment["filename"], attachment["content"])
        attachments.append({"filename": attachment["filename"], "extracted_text": text})
    
    # check if duplicate
    # store else
    email_db_attribute = store_email({
        "subject": subject,
        "from": sender,
        "to": recipients,
        "body": body or "",
        "attachments": attachments,
    })

    return {
        "subject": subject,
        "from": sender,
        "to": recipients,
        "body": body or "",
        "attachments": attachments,
        "email_id": email_db_attribute.get("email_id"),
        "is_duplicate": email_db_attribute.get("is_duplicate")
    }
