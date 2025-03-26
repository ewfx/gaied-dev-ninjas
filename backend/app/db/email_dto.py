from py_dto import DTO  # type: ignore
from typing import Optional, get_type_hints

# EMAIL DTO
class Email(DTO):
    email_id: int
    sender: Optional[str]
    recipient: Optional[str]
    subject: Optional[str]
    body: Optional[str]
    s3_message_path: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    request_type: Optional[str]
    sub_request_type: Optional[str]
    processing_status: Optional[str]
    has_attachment: Optional[bool]
    attachment_metadata: Optional[str]    
    category_type: Optional[str]
    category: Optional[str]