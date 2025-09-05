# """Gmail API integration for fetching real emails."""

# import os
# import base64
# import email
# from typing import List, Dict, Any
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# import logging

# logger = logging.getLogger(__name__)

# class GmailClient:
#     """Gmail API client for fetching emails."""
    
#     # Gmail API scope for reading emails
#     SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
#     def __init__(self, credentials_file='credentials.json'):
#         """Initialize Gmail client with credentials."""
#         self.credentials_file = credentials_file
#         self.service = None
#         self._authenticate()
    
#     def _authenticate(self):
#         """Authenticate with Gmail API."""
#         creds = None
        
#         # Check if token.json exists (saved credentials)
#         if os.path.exists('token.json'):
#             creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
#         # If no valid credentials, get new ones
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())
#             else:
#                 if not os.path.exists(self.credentials_file):
#                     raise FileNotFoundError(f"Gmail credentials file {self.credentials_file} not found")
                
#                 flow = InstalledAppFlow.from_client_secrets_file(
#                     self.credentials_file, self.SCOPES
#                 )
#                 creds = flow.run_local_server(port=0)
            
#             # Save credentials for next run
#             with open('token.json', 'w') as token:
#                 token.write(creds.to_json())
        
#         self.service = build('gmail', 'v1', credentials=creds)
#         logger.info("Successfully authenticated with Gmail API")
    
#     def fetch_emails(self, max_results: int = 50, query: str = None) -> List[str]:
#         """
#         Fetch emails from Gmail.
        
#         Args:
#             max_results: Maximum number of emails to fetch
#             query: Gmail search query (e.g., 'is:unread', 'from:billing', 'subject:invoice')
        
#         Returns:
#             List of email contents as strings
#         """
#         try:
#             # Get list of message IDs
#             results = self.service.users().messages().list(
#                 userId='me',
#                 maxResults=max_results,
#                 q=query
#             ).execute()
            
#             messages = results.get('messages', [])
            
#             if not messages:
#                 logger.warning("No messages found")
#                 return []
            
#             logger.info(f"Found {len(messages)} emails to process")
            
#             # Fetch full email content
#             email_contents = []
#             for i, msg in enumerate(messages):
#                 try:
#                     email_content = self._get_email_content(msg['id'])
#                     if email_content:
#                         email_contents.append(email_content)
                    
#                     if (i + 1) % 10 == 0:
#                         logger.info(f"Processed {i + 1}/{len(messages)} emails")
                        
#                 except Exception as e:
#                     logger.error(f"Error processing email {msg['id']}: {e}")
#                     continue
            
#             logger.info(f"Successfully fetched {len(email_contents)} emails")
#             return email_contents
            
#         except Exception as e:
#             logger.error(f"Error fetching emails: {e}")
#             raise
    
#     def _get_email_content(self, msg_id: str) -> str:
#         """Get full email content by message ID."""
#         try:
#             message = self.service.users().messages().get(
#                 userId='me', id=msg_id, format='full'
#             ).execute()
            
#             # Extract headers
#             headers = message['payload'].get('headers', [])
#             subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
#             sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
#             date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
#             # Extract body
#             body = self._extract_body(message['payload'])
            
#             # Format as email text
#             email_text = f"""From: {sender}
# Subject: {subject}
# Date: {date}

# {body}"""
            
#             return email_text
            
#         except Exception as e:
#             logger.error(f"Error getting email content for {msg_id}: {e}")
#             return None
    
#     def _extract_body(self, payload: Dict[str, Any]) -> str:
#         """Extract email body from payload."""
#         body = ""
        
#         if 'parts' in payload:
#             # Multi-part message
#             for part in payload['parts']:
#                 if part['mimeType'] == 'text/plain':
#                     data = part['body']['data']
#                     body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
#                 elif part['mimeType'] == 'text/html' and not body:
#                     # Fallback to HTML if no plain text
#                     data = part['body']['data']
#                     html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
#                     # Simple HTML to text conversion (you might want to use html2text library)
#                     body += html_body.replace('<br>', '\n').replace('<p>', '\n')
#         else:
#             # Single part message
#             if payload['body'].get('data'):
#                 data = payload['body']['data']
#                 body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
#         return body.strip()
    
#     def get_email_categories_preview(self, max_results: int = 20) -> Dict[str, List[str]]:
#         """Get a preview of different email types for analysis."""
        
#         category_queries = {
#             'invoices': 'subject:(invoice OR bill OR payment OR due)',
#             'shipping': 'subject:(shipped OR tracking OR delivery OR order)',
#             'calendar': 'subject:(meeting OR appointment OR invite OR calendar)',
#             'newsletters': 'from:(newsletter OR marketing OR no-reply)',
#             'recent': 'newer_than:7d'
#         }
        
#         preview = {}
#         for category, query in category_queries.items():
#             try:
#                 emails = self.fetch_emails(max_results=5, query=query)
#                 preview[category] = [email[:200] + "..." for email in emails[:3]]
#             except Exception as e:
#                 logger.error(f"Error fetching {category}: {e}")
#                 preview[category] = []
        
#         return preview

# # Usage instructions for the frontend
# GMAIL_SETUP_INSTRUCTIONS = """
# ## Gmail API Setup Instructions

# ### Step 1: Enable Gmail API
# 1. Go to https://console.cloud.google.com/
# 2. Create a new project or select existing one
# 3. Enable Gmail API for your project
# 4. Create credentials (OAuth 2.0 Client ID)
# 5. Download credentials as `credentials.json`

# ### Step 2: Install Additional Dependencies
# ```bash
# pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
# ```

# ### Step 3: Place Credentials
# 1. Put `credentials.json` in your project root
# 2. First run will open browser for authentication
# 3. Subsequent runs use saved `token.json`

# ### Step 4: Use Gmail Integration
# - Fetch recent emails: `query=None`
# - Fetch unread: `query='is:unread'`
# - Fetch invoices: `query='subject:invoice'`
# - Fetch from specific sender: `query='from:billing@company.com'`
# """




"""Gmail API integration for fetching real emails."""

import os
import base64
import email
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

class GmailClient:
    """Gmail API client for fetching emails."""
    
    # Gmail API scope for reading emails
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file='credentials.json'):
        """Initialize Gmail client with credentials."""
        self.credentials_file = credentials_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        
        # Check if token.json exists (saved credentials)
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"Gmail credentials file {self.credentials_file} not found")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Successfully authenticated with Gmail API")
    
    def fetch_emails(self, max_results: int = 50, query: str = None) -> List[str]:
        """
        Fetch emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            query: Gmail search query (e.g., 'is:unread', 'from:billing', 'subject:invoice')
        
        Returns:
            List of email contents as strings
        """
        try:
            # Get list of message IDs
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                logger.warning("No messages found")
                return []
            
            logger.info(f"Found {len(messages)} emails to process")
            
            # Fetch full email content
            email_contents = []
            for i, msg in enumerate(messages):
                try:
                    email_content = self._get_email_content(msg['id'])
                    if email_content:
                        email_contents.append(email_content)
                    
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i + 1}/{len(messages)} emails")
                        
                except Exception as e:
                    logger.error(f"Error processing email {msg['id']}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(email_contents)} emails")
            return email_contents
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
    
    def _get_email_content(self, msg_id: str) -> str:
        """Get full email content by message ID."""
        try:
            message = self.service.users().messages().get(
                userId='me', id=msg_id, format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            # Extract body
            body = self._extract_body(message['payload'])
            
            # Format as email text
            email_text = f"""From: {sender}
Subject: {subject}
Date: {date}

{body}"""
            
            return email_text
            
        except Exception as e:
            logger.error(f"Error getting email content for {msg_id}: {e}")
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from payload."""
        body = ""
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    data = part['body']['data']
                    html_body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    # Simple HTML to text conversion
                    body += html_body.replace('<br>', '\n').replace('<p>', '\n')
        else:
            # Single part message
            if payload['body'].get('data'):
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def get_email_categories_preview(self, max_results: int = 20) -> Dict[str, List[str]]:
        """Get a preview of different email types for analysis."""
        
        category_queries = {
            'invoices': 'subject:(invoice OR bill OR payment OR due)',
            'shipping': 'subject:(shipped OR tracking OR delivery OR order)',
            'calendar': 'subject:(meeting OR appointment OR invite OR calendar)',
            'newsletters': 'from:(newsletter OR marketing OR no-reply)',
            'recent': 'newer_than:7d'
        }
        
        preview = {}
        for category, query in category_queries.items():
            try:
                emails = self.fetch_emails(max_results=5, query=query)
                preview[category] = [email[:200] + "..." for email in emails[:3]]
            except Exception as e:
                logger.error(f"Error fetching {category}: {e}")
                preview[category] = []
        
        return preview