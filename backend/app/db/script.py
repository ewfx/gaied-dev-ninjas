from app.db import Email
from app.db.email_repo import EmailRepo
from sentence_transformers import SentenceTransformer, util
from google.generativeai import configure, GenerativeModel
import os

#pip install sentence_transformers
#pip install transformers==4.41.0
#pip install google.generativeai
#numpy <"2.0.0"

# Configure Gemini API
configure(api_key=os.getenv("GEMINI_API_KEY"))
model_gemini = GenerativeModel("gemini-1.5-pro")

# Load sentence embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def fetch_emails_from_db():
    """Fetch existing emails and their attachment status from the database."""
    emailRepo = EmailRepo()
    emails = emailRepo.get_all_email()
    emailRepo.close()
    return emails


def get_email_embeddings(email_bodies):
    """Generate embeddings for email bodies."""
    return embedding_model.encode(email_bodies, convert_to_tensor=True)


def check_duplicate_email(email_body, has_attachment, threshold=0.85, llm_threshold=90):
    """Checks if an email is a duplicate by comparing both body text and attachment status."""
    
    stored_emails = fetch_emails_from_db()
    if not stored_emails:
        return False  # No stored emails to compare

    stored_bodies = [email.body for email in stored_emails]
    stored_embeddings = get_email_embeddings(stored_bodies)
    
    # Compute embedding for the new email
    email_embedding = embedding_model.encode(email_body, convert_to_tensor=True)

    # Compute cosine similarity with stored emails
    similarities = util.pytorch_cos_sim(email_embedding, stored_embeddings)[0]

    # Find potential duplicates (above similarity threshold)
    potential_duplicates = [
        (stored_emails[i], score.item()) for i, score in enumerate(similarities) if score.item() >= threshold
    ]

    if not potential_duplicates:
        return False  # No potential matches found

    # Check LLM similarity for highly similar emails
    for stored_email, similarity_score in potential_duplicates:
        prompt = f"""
        Compare the following two emails and determine if they are duplicates.
        - Consider minor wording differences.
        - Check if one email has an attachment while the other does not.
        - If they are duplicates, return a similarity percentage (0-100).

        Email 1: {stored_email.body}
        Email 2: {email_body}

        Return only a numeric value.
        """
        response = model_gemini.generate_content(prompt)

        try:
            llm_similarity_score = float(response.text.strip())

            if llm_similarity_score >= llm_threshold:
                # Case 1: Exact duplicate (same attachment status)
                if stored_email.has_attachment == has_attachment:
                    return True

                # Case 2: Same email, only attachment differs
                if stored_email.has_attachment and not has_attachment:
                    print("Duplicate found: The same email was sent earlier with an attachment.")
                    return True

                if not stored_email.has_attachment and has_attachment:
                    print("Duplicate found: The same email was sent earlier, now with an attachment.")
                    return True

        except ValueError:
            continue  # Skip invalid responses

    return False  # Not a duplicate


def store_email_in_db(email_body, has_attachment):
    email = Email({
        "sender": "abc@test.com",
        "recipient": "xyz@test.com",
        "subject": "My Subject Line",
        "body": email_body,
        "s3_message_path": None,
        "request_type": None,
        "sub_request_type": None,
        "processing_status": None,
        "has_attachment": has_attachment,
        "attachment_metadata": None
    }, allows_missing_keys=True)
    """Stores new email in the database."""
    emailRepo = EmailRepo()
    emailRepo.insert_email(email)
    emailRepo.close()


if __name__ == "__main__":
    # Example emails
    email1_body = "Hello team, please find the report."
    email2_body = "Hello team, please find the report.This is a different mail"  # Same as email1, no attachment
    email3_body = "Hello team, please find the report."  # Same, but with an attachment

    # Store first email
    store_email_in_db(email1_body, has_attachment=False)

    # Check duplicates
    print("Is email 2 a duplicate?", check_duplicate_email(email2_body, has_attachment=False))  # Should return True
    print("Is email 3 a duplicate?", check_duplicate_email(email3_body, has_attachment=True))  # Should return True

    # Store new emails only if they are unique
    if not check_duplicate_email(email2_body, has_attachment=False):
        store_email_in_db(email2_body, has_attachment=False)

    if not check_duplicate_email(email3_body, has_attachment=True):
        store_email_in_db(email3_body, has_attachment=True)