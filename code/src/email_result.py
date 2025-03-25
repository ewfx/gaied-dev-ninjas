import os
import logging
import re
import google.generativeai as genai
from typing import List, Optional, Dict
from dataclasses import dataclass
# from google.colab import userdata
import json
import time

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load API Key Securely
def get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    #api_key = userdata.get("GOOGLE_API_KEY")
    if not api_key:
        logger.critical("API key is missing. Set GEMINI_API_KEY as an environment variable.")
        raise ValueError("API key is required")
    return api_key

API_KEY = get_api_key()

# Configure Gemini API with Exception Handling
try:
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel('gemini-2.0-flash-lite-001')
except Exception as e:
    logger.critical("Failed to configure Gemini API", exc_info=True)
    raise RuntimeError("Gemini API configuration failed") from e

@dataclass(frozen=True)
class ExtractedEntity:
    """Immutable Data Class for Extracted Financial Entities"""
    entity: str
    label: str
    confidence: float

def validate_input(text: Optional[str]) -> str:
    """Validate and sanitize input text."""
    if not text or not isinstance(text, str) or not text.strip():
        logger.error("Invalid input: Text must be a non-empty string.")
        raise ValueError("Invalid input: Text must be a non-empty string.")
    return text.strip()

def parse_entities(response_text: str) -> List[ExtractedEntity]:
    """Parse response text and extract structured financial entities."""
    entities = []
    if not response_text:
        logger.warning("Received empty response from Gemini API")
        return entities
        
    entity_pattern = re.compile(
        r"Entity:\s*([^,]+(?:,[^,]+)*)\s*,\s*Type:\s*([^,]+?)\s*,\s*Confidence Score:\s*([\d.]+)",
        re.IGNORECASE,
    )

    for line in response_text.splitlines():
        line = re.sub(r"\*\*", "", line).strip()
        if not line or "extraction of financial entities" in line.lower() or "note" in line.lower():
            continue

        match = entity_pattern.search(line)
        if match:
            entity, label, confidence_str = match.groups()
            try:
                confidence = float(confidence_str)
                if confidence >= 0.8:
                    entities.append(ExtractedEntity(entity.strip(), label.strip(), confidence))
            except ValueError:
                logger.warning("Skipping invalid confidence score in line: %s", line)
        else:
            logger.warning("Skipping unrecognized response format: %s", line)
    return entities

def extract_named_entities(text: str, temperature: float = 0.2, retries: int = 3) -> List[ExtractedEntity]:
    """Extract named entities using Gemini API with retries."""
    text = validate_input(text)
    prompt = f"""
    Extract financial entities from the following text and label them.
    Return the entities in the format:
    Entity: <value>, Type: <label>, Confidence Score: <0-1 range>.
    Do not include explanations or notes, only structured data.

    Text:
    {text}
    """
    for attempt in range(retries):
        try:
            response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
            response_text = response.text.strip() if hasattr(response, 'text') and response.text else ""
            if response_text:
                logger.info("Gemini Response:\n%s", response_text)
                return parse_entities(response_text)
            logger.warning("Received empty response from Gemini API")
        except genai.GoogleGenerativeAIError as api_error:
            logger.error("Gemini API error: %s", str(api_error), exc_info=True)
        except Exception as e:
            logger.critical("Unexpected error in entity extraction: %s", str(e), exc_info=True)

        time.sleep(2 ** attempt) 

    return []

def extract_key_phrases(text: str, temperature: float = 0.2, retries: int = 3) -> List[str]:
    """Extract key phrases using Gemini API with retries."""
    text = validate_input(text)
    
    # Step 1: Split the text into words and merge terms like "NA", "INC", etc.
    words = re.findall(r'\b\w+\b', text.upper())  # Split text into words
    merged_key_phrases = merge_terms(words)
    
    # Step 2: Join the merged key phrases back into a single string
    merged_text = ' '.join(merged_key_phrases)

    # Construct the prompt with the merged text
    prompt = f"""
    Extract key phrases from the following text and return them as a comma-separated list.
    Do not include explanations or notes.

    Text:
    {merged_text}
    """
    
    # Retry logic for calling the Gemini API
    for attempt in range(retries):
        try:
            response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
            response_text = response.text.strip() if hasattr(response, 'text') and response.text else ""
            if response_text:
                logger.info("Gemini Key Phrases Response:\n%s", response_text)
                
                # Split the response into key phrases
                key_phrases = response_text.split(',')
                
                # Filter out key phrases that contain numbers
                filtered_key_phrases = [phrase.strip() for phrase in key_phrases if not re.search(r'\d', phrase)]
                return filtered_key_phrases
            
            logger.warning("Received empty response from Gemini API for key phrases")
        
        except genai.GoogleGenerativeAIError as api_error:
            logger.error("Gemini API error: %s", str(api_error), exc_info=True)
        except Exception as e:
            logger.critical("Unexpected error in key phrase extraction: %s", str(e), exc_info=True)

        time.sleep(2 ** attempt)

    return []

# List of terms to merge
MERGE_TERMS = [
    "NA", "N.A.", "INC", "LTD", "LLC", "PLC", "GMBH", "Ltd.", "Corp.", "S.A.", "S.p.A.", "B.V.",
    "AG", "Co.", "U.S.", "USA", "U.K.", "UK", "E.U.", "EUR", "GBP", "USD", "INR", "JPY", "CNY",
    "AUD", "CHF", "CAD", "INR", "AUS$", "€", "FBI", "CIA", "IRS", "FDA", "SEC", "S&P", "NASDAQ", 
    "Bank", "Group", "Investments", "Partners", "Associates", "Pty", "BHD", "ATF", "Synd.", 
    "Investments", "Agency", "Firm"
]

def merge_terms(words: List[str]) -> List[str]:
    merged_key_phrases = []
    temp_phrase = ""
    
    for word in words:
        if word in MERGE_TERMS:
            if temp_phrase:
                temp_phrase = f"{temp_phrase} {word}"
            else:
                temp_phrase = word
        else:
            if temp_phrase:
                merged_key_phrases.append(temp_phrase)
                temp_phrase = ""
            merged_key_phrases.append(word)
    
    if temp_phrase:
        merged_key_phrases.append(temp_phrase)
    
    return merged_key_phrases

def generate_summary(text: str, temperature: float = 0.2, retries: int = 3) -> str:
    """Generate summary using Gemini API with retries."""
    text = validate_input(text)
    prompt = f"""
    Summarize the following financial document in 4-5 concise, professional sentences. 
    Focus on the key financial actions and requests made.

    Text:
    {text}
    """
    for attempt in range(retries):
        try:
            response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
            response_text = response.text.strip() if hasattr(response, 'text') and response.text else ""
            if response_text:
                logger.info("Gemini Summary Response:\n%s", response_text)
                return response_text
            logger.warning("Received empty response from Gemini API for summary")
        except genai.GoogleGenerativeAIError as api_error:
            logger.error("Gemini API error: %s", str(api_error), exc_info=True)
        except Exception as e:
            logger.critical("Unexpected error in summary generation: %s", str(e), exc_info=True)

        time.sleep(2 ** attempt)

    return "Summary generation failed."
	
def generate_final_response(text: str, temperature: float = 0.2, retries: int = 3) -> str:
    """Generate summary using Gemini API with retries."""
    text = validate_input(text)
    prompt = f"""
    Categorize following financial result based on named entities, key phrases and summary 
    into request type, request sub type, deal name and confidence score. 
    Focus on the key financial actions and requests made.

    result:
    {text}
    """
    for attempt in range(retries):
        try:
            response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
            response_text = response.text.strip() if hasattr(response, 'text') and response.text else ""
            if response_text:
                logger.info("Gemini Final Response:\n%s", response_text)
                return response_text
            logger.warning("Received empty response from Gemini API for summary")
        except genai.GoogleGenerativeAIError as api_error:
            logger.error("Gemini API error: %s", str(api_error), exc_info=True)
        except Exception as e:
            logger.critical("Unexpected error in FInal Response generation: %s", str(e), exc_info=True)

        time.sleep(2 ** attempt)

    return "Final response generation failed."
	

def extract_output(email_text: str, temperature: float = 0.2) -> str:
    """Extract financial entities, key phrases, and summary and return them as JSON."""
    try:
        extracted_entities = extract_named_entities(email_text, temperature)
        key_phrases = extract_key_phrases(email_text, temperature)
        summary = generate_summary(email_text, temperature)
        
        result = {
            "named_entities": [{"Entity": entity.entity, "Type": entity.label} for entity in extracted_entities],
            "key_phrases": key_phrases,
            "summary": summary
        }
        return json.dumps(result, indent=2)

    except ValueError as ve:
        logger.error("Input validation error", exc_info=True)
        return json.dumps({"error": str(ve)}, indent=2)
    except Exception as e:
        logger.critical("Unexpected error", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)

if __name__ == "__main__":
    provided_text = """
    XYZ Bank, N.A.
    Loan Agency Services
    Date: 05-Feb-2025
    TO: ABC BANK, NATIONAL ASSOCIATION
    ATTN: RAMAKRISHNA KUNCHALA
    Fax: 123-456-9345
    Re: ABTB MID-ATLANTIC LLC $171.3MM 11-4-2022, TERM LOAN A-2
    Description: Facility Lender Share Adjustment
    BORROWER: ABTB MID-ATLANTIC LLC
    DEAL NAME: ABTB MID-ATLANTIC LLC $171.3MM 11-4-2022
    Effective 04-Feb-2025, the Lender Shares of facility TERM LOAN A-2 have been adjusted. Your
    share of the commitment was USD 5,518,249.19. It has been Increased to USD 5,542,963.55.
    For: WELLS FARGO BANK, NA
    Reference: ABTB MID-ATLANTIC LLC $171.3MM 11-4-2022,
    If you have any questions, please call the undersigned.
    ****************************** COMMENT *********************************
    PLEASE FUND YOUR SHARE OF $24,714.36
    Bank Name: XYZ Bank NA
    ABA f 0111324560
    Account : 001234011 Account Name: LIQ CLO Operating Account
    Ref: ABTB Mid-Atlantic LLC
    ************************************************************************* Regards,
    SCOTT WALLACE
    Citizens Commercial Banking is a brand name of XYZ Bank, N.A. Member FDIC
    """
    result = extract_output(provided_text, temperature=0.2)
    final_output = generate_final_response(result, temperature=0.2)
    print(final_output)