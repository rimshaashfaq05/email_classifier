# """Pydantic schemas for email classification and extraction."""

# from pydantic import BaseModel, Field
# from typing import Optional, Dict, Any, Union
# from datetime import datetime
# from enum import Enum

# class EmailCategory(str, Enum):
#     """Email categories."""
#     INVOICE_BILL = "invoice/bill"
#     SHIPPING_ORDER = "shipping/order"
#     CALENDAR_INVITE = "calendar_invite"
#     NEWSLETTER = "newsletter"
#     OTHER = "other"

# class ClassificationResult(BaseModel):
#     """Classification result schema."""
#     category: EmailCategory
#     confidence: float = Field(..., ge=0.0, le=1.0)
#     reasoning: str

# class InvoiceBillData(BaseModel):
#     """Invoice/Bill extraction schema."""
#     vendor: Optional[str] = None
#     amount: Optional[float] = None
#     currency: Optional[str] = None
#     due_date: Optional[str] = None
#     invoice_number: Optional[str] = None
#     description: Optional[str] = None

# class ShippingOrderData(BaseModel):
#     """Shipping/Order extraction schema."""
#     order_id: Optional[str] = None
#     tracking_number: Optional[str] = None
#     carrier: Optional[str] = None
#     ship_date: Optional[str] = None
#     delivery_date: Optional[str] = None
#     status: Optional[str] = None
#     items: Optional[str] = None

# class CalendarInviteData(BaseModel):
#     """Calendar invite extraction schema."""
#     event_title: Optional[str] = None
#     start_time: Optional[str] = None
#     end_time: Optional[str] = None
#     location: Optional[str] = None
#     organizer: Optional[str] = None
#     attendees: Optional[str] = None
#     description: Optional[str] = None

# class NewsletterData(BaseModel):
#     """Newsletter extraction schema."""
#     sender: Optional[str] = None
#     subject: Optional[str] = None
#     newsletter_name: Optional[str] = None
#     main_topics: Optional[str] = None
#     unsubscribe_link: Optional[bool] = None

# class OtherData(BaseModel):
#     """Generic other email data."""
#     sender: Optional[str] = None
#     subject: Optional[str] = None
#     main_content: Optional[str] = None
#     email_type: Optional[str] = None

# class ExtractionResult(BaseModel):
#     """Extraction result schema."""
#     data: Union[InvoiceBillData, ShippingOrderData, CalendarInviteData, NewsletterData, OtherData]
#     confidence: float = Field(..., ge=0.0, le=1.0)
#     extracted_fields: int = 0

# class VerificationResult(BaseModel):
#     """Verification result schema."""
#     schema_ok: bool
#     issues: list[str] = []
#     corrected_data: Optional[Dict[str, Any]] = None
#     confidence_adjustment: float = 0.0

# class EmailProcessingResult(BaseModel):
#     """Final email processing result."""
#     email_id: str
#     category: EmailCategory
#     confidence: float = Field(..., ge=0.0, le=1.0)
#     schema_ok: bool
#     data: Dict[str, Any]
#     processing_notes: Optional[str] = None
    
#     class Config:
#         json_encoders = {
#             EmailCategory: lambda v: v.value
#         }







from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
from enum import Enum

# --- Categories Enum (new + fallback old) ---
class EmailCategory(str, Enum):
    """Email categories."""
    # New categories
    BANKING = "banking"
    ECOMMERCE = "ecommerce"
    EDUCATION = "education"
    JOB_ALERT = "job_alert"
    NOTIFICATIONS = "notifications"
    NEWSLETTER = "newsletter"
    OTHER = "other"

    # Legacy categories (kept for backward compatibility)
    INVOICE_BILL = "invoice/bill"
    SHIPPING_ORDER = "shipping/order"
    CALENDAR_INVITE = "calendar_invite"


# --- Classification Result ---
class ClassificationResult(BaseModel):
    category: EmailCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str


# --- Legacy Extraction Schemas ---
class InvoiceBillData(BaseModel):
    vendor: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    due_date: Optional[str] = None
    invoice_number: Optional[str] = None
    description: Optional[str] = None

class ShippingOrderData(BaseModel):
    order_id: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    ship_date: Optional[str] = None
    delivery_date: Optional[str] = None
    status: Optional[str] = None
    items: Optional[str] = None

class CalendarInviteData(BaseModel):
    event_title: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    organizer: Optional[str] = None
    attendees: Optional[str] = None
    description: Optional[str] = None


# --- New Extraction Schemas ---
class BankingData(BaseModel):
    transaction_id: Optional[str] = None
    amount: Optional[float] = None
    balance: Optional[float] = None
    currency: Optional[str] = None
    bank_name: Optional[str] = None

class EcommerceData(BaseModel):
    order_id: Optional[str] = None
    items: Optional[str] = None
    delivery_date: Optional[str] = None
    status: Optional[str] = None
    vendor: Optional[str] = None

class EducationData(BaseModel):
    university: Optional[str] = None
    subject: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None

class JobAlertData(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    link: Optional[str] = None

class NotificationData(BaseModel):
    source: Optional[str] = None
    subject: Optional[str] = None
    alert_type: Optional[str] = None
    date: Optional[str] = None

class NewsletterData(BaseModel):
    sender: Optional[str] = None
    subject: Optional[str] = None
    newsletter_name: Optional[str] = None
    main_topics: Optional[str] = None
    unsubscribe_link: Optional[str] = None

class OtherData(BaseModel):
    sender: Optional[str] = None
    subject: Optional[str] = None
    main_content: Optional[str] = None
    email_type: Optional[str] = None


# --- Extraction Result (union of both old + new) ---
class ExtractionResult(BaseModel):
    data: Union[
        BankingData, EcommerceData, EducationData,
        JobAlertData, NotificationData,
        NewsletterData, OtherData,
        InvoiceBillData, ShippingOrderData, CalendarInviteData
    ]
    confidence: float = Field(..., ge=0.0, le=1.0)
    extracted_fields: int = 0


# --- Verification + Final ---
class VerificationResult(BaseModel):
    schema_ok: bool
    issues: list[str] = []
    corrected_data: Optional[Dict[str, Any]] = None
    confidence_adjustment: float = 0.0

class EmailProcessingResult(BaseModel):
    email_id: str
    category: EmailCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    schema_ok: bool
    data: Dict[str, Any]
    processing_notes: Optional[str] = None

    class Config:
        json_encoders = {
            EmailCategory: lambda v: v.value
        }
