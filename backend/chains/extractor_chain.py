# """Email data extraction chain using LangChain."""

# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.output_parsers import PydanticOutputParser
# from backend.models.schemas import (
#     EmailCategory, ExtractionResult,
#     InvoiceBillData, ShippingOrderData, CalendarInviteData,
#     NewsletterData, OtherData
# )
# from backend.config import Config
# import json
# import logging
# from typing import Dict, Any, Type, Union

# logger = logging.getLogger(__name__)

# class EmailExtractorChain:
#     """LangChain-based email data extractor."""
    
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model=Config.OPENAI_MODEL,
#             temperature=Config.TEMPERATURE,
#             max_tokens=Config.MAX_TOKENS,
#             api_key=Config.OPENAI_API_KEY
#         )
        
#         self.schema_map = {
#             EmailCategory.INVOICE_BILL: InvoiceBillData,
#             EmailCategory.SHIPPING_ORDER: ShippingOrderData,
#             EmailCategory.CALENDAR_INVITE: CalendarInviteData,
#             EmailCategory.NEWSLETTER: NewsletterData,
#             EmailCategory.OTHER: OtherData
#         }
        
#         self.prompt_map = {
#             EmailCategory.INVOICE_BILL: self._create_invoice_prompt(),
#             EmailCategory.SHIPPING_ORDER: self._create_shipping_prompt(),
#             EmailCategory.CALENDAR_INVITE: self._create_calendar_prompt(),
#             EmailCategory.NEWSLETTER: self._create_newsletter_prompt(),
#             EmailCategory.OTHER: self._create_other_prompt()
#         }
    
#     def _create_invoice_prompt(self) -> ChatPromptTemplate:
#         """Create invoice/bill extraction prompt."""
#         template = """
# Extract structured data from this invoice/bill email. Focus on financial and vendor information.

# FIELDS TO EXTRACT:
# - vendor: Company/person sending the bill
# - amount: Total amount due (extract number only)
# - currency: Currency symbol or code
# - due_date: When payment is due (YYYY-MM-DD format if possible)
# - invoice_number: Invoice/bill reference number
# - description: Brief description of what the bill is for

# EMAIL CONTENT:
# {email_content}

# Extract only the information that is clearly present. Use null for missing fields.
# Return as JSON with the exact field names listed above.
# """
#         return ChatPromptTemplate.from_template(template)
    
#     def _create_shipping_prompt(self) -> ChatPromptTemplate:
#         """Create shipping/order extraction prompt."""
#         template = """
# Extract structured data from this shipping/order email. Focus on delivery and order information.

# FIELDS TO EXTRACT:
# - order_id: Order reference number
# - tracking_number: Package tracking number
# - carrier: Shipping company (UPS, FedEx, USPS, etc.)
# - ship_date: Date item was shipped (YYYY-MM-DD format if possible)
# - delivery_date: Expected delivery date (YYYY-MM-DD format if possible)
# - status: Current shipping status
# - items: Brief description of items being shipped

# EMAIL CONTENT:
# {email_content}

# Extract only the information that is clearly present. Use null for missing fields.
# Return as JSON with the exact field names listed above.
# """
#         return ChatPromptTemplate.from_template(template)
    
#     def _create_calendar_prompt(self) -> ChatPromptTemplate:
#         """Create calendar invite extraction prompt."""
#         template = """
# Extract structured data from this calendar invite email. Focus on event details.

# FIELDS TO EXTRACT:
# - event_title: Name/title of the event
# - start_time: Event start time (include date and time if available)
# - end_time: Event end time (include date and time if available)
# - location: Where the event takes place
# - organizer: Person organizing the event
# - attendees: List of attendees (as comma-separated string)
# - description: Event description or agenda

# EMAIL CONTENT:
# {email_content}

# Extract only the information that is clearly present. Use null for missing fields.
# Return as JSON with the exact field names listed above.
# """
#         return ChatPromptTemplate.from_template(template)
    
#     def _create_newsletter_prompt(self) -> ChatPromptTemplate:
#         """Create newsletter extraction prompt."""
#         template = """
# Extract structured data from this newsletter email. Focus on publication information.

# FIELDS TO EXTRACT:
# - sender: Newsletter sender/publication name
# - subject: Email subject line
# - newsletter_name: Name of the newsletter/publication
# - main_topics: Key topics covered (as comma-separated string)
# - unsubscribe_link: true if unsubscribe link is present, false otherwise

# EMAIL CONTENT:
# {email_content}

# Extract only the information that is clearly present. Use null for missing fields.
# Return as JSON with the exact field names listed above.
# """
#         return ChatPromptTemplate.from_template(template)
    
#     def _create_other_prompt(self) -> ChatPromptTemplate:
#         """Create generic extraction prompt."""
#         template = """
# Extract basic structured data from this email.

# FIELDS TO EXTRACT:
# - sender: Email sender name or address
# - subject: Email subject line
# - main_content: Brief summary of main content
# - email_type: Your best guess at what type of email this is

# EMAIL CONTENT:
# {email_content}

# Extract only the information that is clearly present. Use null for missing fields.
# Return as JSON with the exact field names listed above.
# """
#         return ChatPromptTemplate.from_template(template)
    
#     def extract(self, email_content: str, category: EmailCategory) -> ExtractionResult:
#         """Extract structured data from email based on category."""
#         try:
#             prompt = self.prompt_map[category]
#             schema_class = self.schema_map[category]
            
#             # Build chain for this category
#             chain = (
#                 {"email_content": RunnablePassthrough()}
#                 | prompt
#                 | self.llm
#             )
            
#             # Get response and parse
#             response = chain.invoke(email_content)
            
#             # Parse JSON response
#             try:
#                 parsed_data = json.loads(response.content)
                
#                 # Validate against schema
#                 validated_data = schema_class(**parsed_data)
                
#                 # Count non-null fields
#                 extracted_fields = len([v for v in parsed_data.values() if v is not None])
                
#                 # Calculate confidence based on field extraction
#                 max_fields = len(schema_class.__fields__)
#                 confidence = min(0.9, extracted_fields / max_fields) if max_fields > 0 else 0.5
                
#                 logger.info(f"Extracted {extracted_fields} fields for {category} email")
                
#                 return ExtractionResult(
#                     data=validated_data,
#                     confidence=confidence,
#                     extracted_fields=extracted_fields
#                 )
                
#             except json.JSONDecodeError as e:
#                 logger.error(f"Failed to parse JSON response: {e}")
#                 return self._create_fallback_extraction(category)
                
#             except Exception as e:
#                 logger.error(f"Schema validation failed: {e}")
#                 return self._create_fallback_extraction(category)
        
#         except Exception as e:
#             logger.error(f"Extraction failed: {e}")
#             return self._create_fallback_extraction(category)
    
#     def _create_fallback_extraction(self, category: EmailCategory) -> ExtractionResult:
#         """Create fallback extraction result."""
#         schema_class = self.schema_map[category]
#         empty_data = schema_class()
        
#         return ExtractionResult(
#             data=empty_data,
#             confidence=0.1,
#             extracted_fields=0
#         )




"""Email data extraction chain using LangChain."""

import json
import logging

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

from backend.models.schemas import (
    # new schemas
    BankingData,
    EcommerceData,
    EducationData,
    JobAlertData,
    NotificationData,
    NewsletterData,
    OtherData,

    # legacy schemas
    InvoiceBillData,
    ShippingOrderData,
    CalendarInviteData,

    # shared
    EmailCategory,
    ExtractionResult,
)

from backend.config import Config

logger = logging.getLogger(__name__)


class EmailExtractorChain:
    """LangChain-based email data extractor."""

    def __init__(self):
        self.llm = ChatOpenAI(max_tokens=Config.MAX_TOKENS)

        # --- Map categories → schemas ---
        self.schema_map = {
            # new
            EmailCategory.BANKING: BankingData,
            EmailCategory.ECOMMERCE: EcommerceData,
            EmailCategory.EDUCATION: EducationData,
            EmailCategory.JOB_ALERT: JobAlertData,
            EmailCategory.NOTIFICATIONS: NotificationData,
            EmailCategory.NEWSLETTER: NewsletterData,
            EmailCategory.OTHER: OtherData,

            # legacy
            EmailCategory.INVOICE_BILL: InvoiceBillData,
            EmailCategory.SHIPPING_ORDER: ShippingOrderData,
            EmailCategory.CALENDAR_INVITE: CalendarInviteData,
        }

        # --- Map categories → prompts ---
        self.prompt_map = {
            # new
            EmailCategory.BANKING: self._create_banking_prompt(),
            EmailCategory.ECOMMERCE: self._create_ecommerce_prompt(),
            EmailCategory.EDUCATION: self._create_education_prompt(),
            EmailCategory.JOB_ALERT: self._create_job_alert_prompt(),
            EmailCategory.NOTIFICATIONS: self._create_notification_prompt(),
            EmailCategory.NEWSLETTER: self._create_newsletter_prompt(),
            EmailCategory.OTHER: self._create_other_prompt(),

            # legacy
            EmailCategory.INVOICE_BILL: self._create_invoice_prompt(),
            EmailCategory.SHIPPING_ORDER: self._create_shipping_prompt(),
            EmailCategory.CALENDAR_INVITE: self._create_calendar_prompt(),
        }

    # ---------------- NEW PROMPTS ----------------
    def _create_banking_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this banking/payment email. Focus on transactions.

FIELDS TO EXTRACT:
- transaction_id
- amount
- balance
- currency
- bank_name

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_ecommerce_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this e-commerce/shopping email. Focus on order and delivery info.

FIELDS TO EXTRACT:
- order_id
- items
- delivery_date
- status
- vendor

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_education_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this education/university email.

FIELDS TO EXTRACT:
- university
- subject
- deadline
- notes

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_job_alert_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this job alert email.

FIELDS TO EXTRACT:
- job_title
- company
- location
- link

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_notification_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this notification/security alert email.

FIELDS TO EXTRACT:
- source
- subject
- alert_type
- date

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    # ---------------- LEGACY PROMPTS ----------------
    def _create_invoice_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this invoice/bill email. Focus on financial and vendor info.

FIELDS TO EXTRACT:
- vendor
- amount
- currency
- due_date
- invoice_number
- description

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_shipping_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this shipping/order email.

FIELDS TO EXTRACT:
- order_id
- tracking_number
- carrier
- ship_date
- delivery_date
- status
- items

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_calendar_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this calendar invite email.

FIELDS TO EXTRACT:
- event_title
- start_time
- end_time
- location
- organizer
- attendees
- description

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_newsletter_prompt(self) -> ChatPromptTemplate:
        template = """
Extract structured data from this newsletter email.

FIELDS TO EXTRACT:
- sender
- subject
- newsletter_name
- main_topics
- unsubscribe_link

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    def _create_other_prompt(self) -> ChatPromptTemplate:
        template = """
Extract basic structured data from this generic email.

FIELDS TO EXTRACT:
- sender
- subject
- main_content
- email_type

EMAIL CONTENT:
{email_content}

Return JSON with these fields only. Use null if missing.
"""
        return ChatPromptTemplate.from_template(template)

    # ---------------- EXTRACTION LOGIC ----------------
    def extract(self, email_content: str, category: EmailCategory) -> ExtractionResult:
        """Extract structured data from email based on category."""
        try:
            prompt = self.prompt_map[category]
            schema_class = self.schema_map[category]

            # Build chain
            chain = (
                {"email_content": RunnablePassthrough()}
                | prompt
                | self.llm
            )

            response = chain.invoke(email_content)

            try:
                parsed_data = json.loads(response.content)
                validated_data = schema_class(**parsed_data)

                extracted_fields = len([v for v in parsed_data.values() if v is not None])
                max_fields = len(schema_class.__fields__)
                confidence = min(0.9, extracted_fields / max_fields) if max_fields > 0 else 0.5

                logger.info(f"Extracted {extracted_fields} fields for {category} email")

                return ExtractionResult(
                    data=validated_data,
                    confidence=confidence,
                    extracted_fields=extracted_fields
                )

            except Exception as e:
                logger.error(f"Parsing/validation failed: {e}")
                return self._create_fallback_extraction(category)

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return self._create_fallback_extraction(category)

    def _create_fallback_extraction(self, category: EmailCategory) -> ExtractionResult:
        schema_class = self.schema_map.get(category, OtherData)
        empty_data = schema_class()

        return ExtractionResult(
            data=empty_data,
            confidence=0.1,
            extracted_fields=0
        )
