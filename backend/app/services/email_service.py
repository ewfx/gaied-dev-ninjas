import email
import os
from io import BytesIO
from app.utils.email_parser import parse_email
from app.utils.email_classifier import classify_email

async def process_email(file):
    contents = await file.read()
    parsed_data = parse_email(contents)
    return parsed_data


async def classify(selected_items: dict):
    results = classify_email(selected_items)
    return results