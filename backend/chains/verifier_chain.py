# """Email data verification chain using LangChain."""

# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema.runnable import RunnablePassthrough
# from backend.models.schemas import EmailCategory, VerificationResult
# from backend.config import Config
# import json
# import logging
# from typing import Dict, Any

# logger = logging.getLogger(__name__)

# class EmailVerifierChain:
#     """LangChain-based email data verifier."""
    
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model=Config.OPENAI_MODEL,
#             temperature=Config.TEMPERATURE,
#             max_tokens=Config.MAX_TOKENS,
#             api_key=Config.OPENAI_API_KEY
#         )
        
#         self.prompt = self._create_prompt()
#         self.chain = self._build_chain()
    
#     def _create_prompt(self) -> ChatPromptTemplate:
#         """Create verification prompt template."""
        
#         template = """
# You are a data quality validator. Your task is to verify extracted email data for accuracy and completeness.

# ORIGINAL EMAIL:
# {email_content}

# EXTRACTED DATA:
# {extracted_data}

# EMAIL CATEGORY: {category}

# VERIFICATION TASKS:
# 1. Check if extracted data matches the email content
# 2. Identify any missing important information
# 3. Flag incorrect or inconsistent data
# 4. Suggest corrections if needed

# VALIDATION RULES BY CATEGORY:
# - invoice/bill: Verify amounts, dates, vendor names are accurate
# - shipping/order: Check order IDs, tracking numbers, dates are correct
# - calendar_invite: Validate event times, dates, locations
# - newsletter: Confirm sender, topics match content
# - other: Basic accuracy check

# RESPONSE FORMAT:
# Return JSON with these fields:
# - "schema_ok": true/false (whether data passes validation)
# - "issues": array of strings describing problems found
# - "corrected_data": object with corrections (only if corrections needed)
# - "confidence_adjustment": number between -0.3 and 0.2 to adjust confidence

# EXAMPLES:
# Good data: {{"schema_ok": true, "issues": [], "corrected_data": null, "confidence_adjustment": 0.1}}
# Bad data: {{"schema_ok": false, "issues": ["Amount mismatch", "Invalid date format"], "corrected_data": {"amount": 99.99}, "confidence_adjustment": -0.2}}
# """
        
#         return ChatPromptTemplate.from_template(template)
    
#     def _build_chain(self):
#         """Build the verification chain."""
#         return (
#             {
#                 "email_content": lambda x: x["email_content"],
#                 "extracted_data": lambda x: x["extracted_data"],
#                 "category": lambda x: x["category"]
#             }
#             | self.prompt
#             | self.llm
#         )
    
#     def verify(self, email_content: str, extracted_data: Dict[str, Any], 
#               category: EmailCategory) -> VerificationResult:
#         """Verify extracted data against original email."""
#         try:
#             # Prepare input
#             input_data = {
#                 "email_content": email_content,
#                 "extracted_data": json.dumps(extracted_data, indent=2),
#                 "category": category.value
#             }
            
#             # Run verification
#             response = self.chain.invoke(input_data)
            
#             # Parse response
#             try:
#                 result_data = json.loads(response.content)
                
#                 verification_result = VerificationResult(
#                     schema_ok=result_data.get("schema_ok", False),
#                     issues=result_data.get("issues", []),
#                     corrected_data=result_data.get("corrected_data"),
#                     confidence_adjustment=result_data.get("confidence_adjustment", 0.0)
#                 )
                
#                 logger.info(f"Verification completed: {'PASS' if verification_result.schema_ok else 'FAIL'}")
#                 if verification_result.issues:
#                     logger.warning(f"Issues found: {verification_result.issues}")
                
#                 return verification_result
                
#             except json.JSONDecodeError as e:
#                 logger.error(f"Failed to parse verification response: {e}")
#                 return self._create_fallback_verification()
                
#         except Exception as e:
#             logger.error(f"Verification failed: {e}")
#             return self._create_fallback_verification()
    
#     def _create_fallback_verification(self) -> VerificationResult:
#         """Create fallback verification result."""
#         return VerificationResult(
#             schema_ok=False,
#             issues=["Verification system error"],
#             corrected_data=None,
#             confidence_adjustment=-0.1
#         )





"""Email data verification chain using rule-based validation."""

import json
import logging
import re
from typing import Dict, Any
from backend.models.schemas import EmailCategory, VerificationResult
from backend.config import Config

logger = logging.getLogger(__name__)

class EmailVerifierChain:
    """Rule-based email data verifier (no API required)."""
    
    def __init__(self):
        # No model initialization needed - using rule-based verification
        pass
    
    def _validate_invoice_data(self, email_content: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate invoice/bill data."""
        issues = []
        corrections = {}
        
        # Check if amount is reasonable
        if data.get('amount'):
            try:
                amount = float(data['amount'])
                if amount <= 0:
                    issues.append("Amount should be positive")
                elif amount > 100000:  # Unreasonably high
                    issues.append("Amount seems unusually high")
            except (ValueError, TypeError):
                issues.append("Invalid amount format")
        
        # Validate date format
        if data.get('due_date'):
            date_str = str(data['due_date'])
            # Check for common date patterns
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or MM-DD-YYYY
                r'\w+\s+\d{1,2},\s+\d{4}'  # Month DD, YYYY
            ]
            
            if not any(re.match(pattern, date_str) for pattern in date_patterns):
                issues.append("Date format may be invalid")
        
        # Check if vendor exists and is reasonable
        if data.get('vendor'):
            vendor = str(data['vendor']).strip()
            if len(vendor) < 2:
                issues.append("Vendor name too short")
            elif len(vendor) > 100:
                corrections['vendor'] = vendor[:100]
        
        # Verify currency if amount exists
        if data.get('amount') and not data.get('currency'):
            # Default to USD if amount found but no currency
            corrections['currency'] = 'USD'
        
        return {
            'issues': issues,
            'corrections': corrections,
            'score': max(0.0, 1.0 - len(issues) * 0.2)
        }
    
    def _validate_shipping_data(self, email_content: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shipping/order data."""
        issues = []
        corrections = {}
        
        # Validate tracking number format
        if data.get('tracking_number'):
            tracking = str(data['tracking_number']).strip()
            
            # Common tracking number patterns
            valid_patterns = [
                r'1Z[A-Z0-9]{16}',  # UPS
                r'\d{12}',  # USPS
                r'\d{4}\s?\d{4}\s?\d{4}',  # FedEx
                r'[A-Z0-9]{10,}'  # Generic
            ]
            
            if not any(re.match(pattern, tracking) for pattern in valid_patterns):
                issues.append("Tracking number format may be invalid")
        
        # Validate carrier
        if data.get('carrier'):
            carrier = str(data['carrier']).strip()
            valid_carriers = ['UPS', 'FEDEX', 'USPS', 'DHL', 'AMAZON']
            if carrier.upper() not in valid_carriers:
                # Try to correct common variations
                carrier_corrections = {
                    'FEDEX': ['FEDERAL EXPRESS', 'FED EX'],
                    'USPS': ['US POSTAL', 'POST OFFICE'],
                    'UPS': ['UNITED PARCEL']
                }
                
                corrected = False
                for correct_carrier, variations in carrier_corrections.items():
                    if any(var in carrier.upper() for var in variations):
                        corrections['carrier'] = correct_carrier
                        corrected = True
                        break
                
                if not corrected:
                    issues.append(f"Unknown carrier: {carrier}")
        
        # Check order ID format
        if data.get('order_id'):
            order_id = str(data['order_id']).strip()
            if len(order_id) < 3:
                issues.append("Order ID seems too short")
            elif len(order_id) > 50:
                corrections['order_id'] = order_id[:50]
        
        return {
            'issues': issues,
            'corrections': corrections,
            'score': max(0.0, 1.0 - len(issues) * 0.2)
        }
    
    def _validate_calendar_data(self, email_content: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate calendar invite data."""
        issues = []
        corrections = {}
        
        # Check time format
        if data.get('start_time'):
            time_str = str(data['start_time'])
            time_patterns = [
                r'\d{1,2}:\d{2}\s*[AP]M',
                r'\d{1,2}[AP]M',
                r'\d{1,2}:\d{2}'
            ]
            
            if not any(re.search(pattern, time_str, re.IGNORECASE) for pattern in time_patterns):
                issues.append("Start time format may be invalid")
        
        # Validate event title
        if data.get('event_title'):
            title = str(data['event_title']).strip()
            if len(title) < 2:
                issues.append("Event title too short")
            elif len(title) > 200:
                corrections['event_title'] = title[:200]
        
        # Check if organizer email format is valid (basic check)
        if data.get('organizer'):
            organizer = str(data['organizer'])
            if '@' in organizer:
                # Basic email validation
                email_pattern = r'^[^@]+@[^@]+\.[^@]+$'
                if not re.match(email_pattern, organizer.strip()):
                    issues.append("Organizer email format may be invalid")
        
        return {
            'issues': issues,
            'corrections': corrections,
            'score': max(0.0, 1.0 - len(issues) * 0.15)
        }
    
    def _validate_newsletter_data(self, email_content: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate newsletter data."""
        issues = []
        corrections = {}
        
        # Check if unsubscribe_link is boolean
        if data.get('unsubscribe_link') is not None:
            unsubscribe = data['unsubscribe_link']
            if not isinstance(unsubscribe, bool):
                # Convert to boolean
                if str(unsubscribe).lower() in ['true', '1', 'yes']:
                    corrections['unsubscribe_link'] = True
                else:
                    corrections['unsubscribe_link'] = False
        
        # Validate sender
        if data.get('sender'):
            sender = str(data['sender']).strip()
            if len(sender) < 2:
                issues.append("Sender name too short")
            elif len(sender) > 100:
                corrections['sender'] = sender[:100]
        
        # Check main topics format
        if data.get('main_topics'):
            topics = str(data['main_topics'])
            if len(topics) > 500:
                corrections['main_topics'] = topics[:500]
        
        return {
            'issues': issues,
            'corrections': corrections,
            'score': max(0.0, 1.0 - len(issues) * 0.2)
        }
    
    def _validate_other_data(self, email_content: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate other email data."""
        issues = []
        corrections = {}
        
        # Basic validation for other category
        if data.get('main_content'):
            content = str(data['main_content'])
            if len(content) > 1000:
                corrections['main_content'] = content[:1000]
        
        if data.get('sender'):
            sender = str(data['sender']).strip()
            if len(sender) > 100:
                corrections['sender'] = sender[:100]
        
        return {
            'issues': issues,
            'corrections': corrections,
            'score': 0.7  # Default score for other category
        }
    
    def verify(self, email_content: str, extracted_data: Dict[str, Any], 
              category: EmailCategory) -> VerificationResult:
        """Verify extracted data against original email."""
        try:
            # Route to appropriate validation method
            if category == EmailCategory.INVOICE_BILL:
                validation = self._validate_invoice_data(email_content, extracted_data)
            elif category == EmailCategory.SHIPPING_ORDER:
                validation = self._validate_shipping_data(email_content, extracted_data)
            elif category == EmailCategory.CALENDAR_INVITE:
                validation = self._validate_calendar_data(email_content, extracted_data)
            elif category == EmailCategory.NEWSLETTER:
                validation = self._validate_newsletter_data(email_content, extracted_data)
            else:
                validation = self._validate_other_data(email_content, extracted_data)
            
            # Determine if schema is OK
            schema_ok = len(validation['issues']) == 0
            
            # Calculate confidence adjustment based on validation score
            confidence_adjustment = (validation['score'] - 0.7) * 0.3  # Scale to ±0.3
            confidence_adjustment = max(-0.3, min(0.2, confidence_adjustment))
            
            verification_result = VerificationResult(
                schema_ok=schema_ok,
                issues=validation['issues'],
                corrected_data=validation['corrections'] if validation['corrections'] else None,
                confidence_adjustment=confidence_adjustment
            )
            
            logger.info(f"Verification completed: {'PASS' if verification_result.schema_ok else 'FAIL'}")
            if verification_result.issues:
                logger.warning(f"Issues found: {verification_result.issues}")
            
            return verification_result
                
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return self._create_fallback_verification()
    
    def _create_fallback_verification(self) -> VerificationResult:
        """Create fallback verification result."""
        return VerificationResult(
            schema_ok=False,
            issues=["Verification system error"],
            corrected_data=None,
            confidence_adjustment=-0.1
        )