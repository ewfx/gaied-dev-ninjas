def fetch_emails_from_db():
    from app.db.email_repo import EmailRepo  
    """Fetch existing emails and their attachment status from the database."""
    emailRepo = EmailRepo()
    emails = emailRepo.get_all_email()
    emailRepo.close()
    return emails