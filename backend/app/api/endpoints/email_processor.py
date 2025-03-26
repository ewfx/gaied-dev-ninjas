from fastapi import APIRouter, UploadFile, File
from app.services.email_service import process_email, classify

router = APIRouter(prefix="/email", tags=["Email Processing"])

@router.post("/process")
async def process_email_file(file: UploadFile = File(...)):
    result = await process_email(file)
    return {"message": "Email processed successfully", "data": result}

@router.post("/classify")
async def classify_email_file(selectedItems: dict):
    merged_text = ""
    if "body" in selectedItems and selectedItems["body"] is not None:
        merged_text += selectedItems["body"] + " "
    if "attachments" in selectedItems:
        for attachment in selectedItems["attachments"]:
            extracted_text = attachment.get("extracted_text", "")
            merged_text += extracted_text + " "
    merged_text = merged_text.strip()    
    result = await classify({"text": merged_text, "email_id": selectedItems.get("email_id"), "category_type": selectedItems.get("category_type")})
    return {"message": "Email classified successfully", "data": result}

