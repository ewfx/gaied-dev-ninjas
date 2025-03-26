from app.db import Email
from sentence_transformers import SentenceTransformer, util
from google.generativeai import configure, GenerativeModel
from app.utils.get_api_key import api_key
API_KEY = api_key()

# Configure Gemini API
configure(api_key=API_KEY)


model_gemini = GenerativeModel("gemini-1.5-pro")

# Load sentence embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')


def fetch_emails_from_db():
    """Fetch existing emails and their attachment status from the database."""
    from app.db.email_repo import EmailRepo
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

    print("===================")
    print(potential_duplicates)
    print("===================")

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
            print("llm_similarity_score")
            print(llm_similarity_score)
            print("llm_threadhold")
            print(llm_threshold)
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



    # # Store new emails only if they are unique
    # if not check_duplicate_email(email2_body, has_attachment=False):
    #     store_email_in_db(email2_body, has_attachment=False)

    # if not check_duplicate_email(email3_body, has_attachment=True):
    #     store_email_in_db(email3_body, has_attachment=True)