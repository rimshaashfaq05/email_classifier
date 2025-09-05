# # """Streamlit frontend for email classification pipeline."""

# # import streamlit as st
# # import os
# # import sys
# # import logging
# # import tempfile
# # import json
# # from pathlib import Path
# # import pandas as pd
# # import plotly.express as px
# # import plotly.graph_objects as go

# # # Add backend to path
# # backend_path = Path(__file__).parent.parent / "backend"
# # project_root = Path(__file__).parent.parent
# # sys.path.insert(0, str(project_root))
# # sys.path.insert(0, str(backend_path))

# # from backend.config import Config
# # from backend.pipeline.email_pipeline import EmailProcessingPipeline
# # from backend.utils.helpers import format_statistics, find_failure_cases, create_sample_emails
# # from backend.models.schemas import EmailCategory

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # Page config
# # st.set_page_config(
# #     page_title="Email Classification Pipeline",
# #     page_icon="📧",
# #     layout="wide"
# # )

# # def initialize_app():
# #     """Initialize the application and validate configuration."""
# #     try:
# #         Config.validate()
# #         return True
# #     except Exception as e:
# #         st.error(f"Configuration Error: {e}")
# #         st.info("Please check your .env file and ensure OPENAI_API_KEY is set.")
# #         return False

# # def create_sample_file():
# #     """Create a sample emails.txt file."""
# #     sample_emails = create_sample_emails()
    
# #     sample_content = "\n".join(sample_emails)
    
# #     return sample_content

# # def process_emails(uploaded_file):
# #     """Process uploaded emails through the pipeline."""
    
# #     # Create temporary files
# #     with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
# #         # Read uploaded file
# #         content = uploaded_file.getvalue().decode('utf-8')
# #         temp_input.write(content)
# #         temp_input_path = temp_input.name
    
# #     temp_output_path = tempfile.mktemp(suffix='.jsonl')
    
# #     try:
# #         # Initialize pipeline
# #         pipeline = EmailProcessingPipeline()
        
# #         # Process emails
# #         with st.spinner("Processing emails through AI pipeline..."):
# #             result_data = pipeline.process_and_save(temp_input_path, temp_output_path)
        
# #         return result_data, temp_output_path
    
# #     finally:
# #         # Clean up temporary input file
# #         if os.path.exists(temp_input_path):
# #             os.unlink(temp_input_path)

# # def display_results(result_data, output_path):
# #     """Display processing results in the UI."""
    
# #     results = result_data["results"]
# #     stats = result_data["statistics"]
    
# #     # Summary metrics
# #     st.subheader("📊 Processing Summary")
    
# #     col1, col2, col3, col4 = st.columns(4)
    
# #     with col1:
# #         st.metric("Total Emails", stats["total_emails"])
    
# #     with col2:
# #         st.metric("Schema Valid", f"{stats['schema_validation_rate']:.1%}")
    
# #     with col3:
# #         st.metric("Avg Confidence", f"{stats['average_confidence']:.2f}")
    
# #     with col4:
# #         st.metric("High Confidence", stats["high_confidence_count"])
    
# #     # Category distribution chart
# #     st.subheader("📈 Category Distribution")
    
# #     category_data = [(cat, count) for cat, count in stats["category_distribution"].items()]
# #     category_df = pd.DataFrame(category_data, columns=["Category", "Count"])
    
# #     fig = px.pie(category_df, values="Count", names="Category", 
# #                  title="Email Categories")
# #     st.plotly_chart(fig, use_container_width=True)
    
# #     # Confidence distribution
# #     st.subheader("🎯 Confidence Distribution")
    
# #     confidences = [r.confidence for r in results]
# #     confidence_df = pd.DataFrame({"Confidence": confidences})
    
# #     fig = px.histogram(confidence_df, x="Confidence", nbins=20, 
# #                       title="Distribution of Confidence Scores")
# #     st.plotly_chart(fig, use_container_width=True)
    
# #     # Results table
# #     st.subheader("📋 Detailed Results")
    
# #     # Convert results to DataFrame for display
# #     display_data = []
# #     for result in results:
# #         display_data.append({
# #             "Email ID": result.email_id,
# #             "Category": result.category.value,
# #             "Confidence": f"{result.confidence:.2f}",
# #             "Schema Valid": "✅" if result.schema_ok else "❌",
# #             "Fields Extracted": len([v for v in result.data.values() if v]),
# #             "Notes": result.processing_notes or "None"
# #         })
    
# #     results_df = pd.DataFrame(display_data)
# #     st.dataframe(results_df, use_container_width=True)
    
# #     # Download section
# #     st.subheader("💾 Download Results")
    
# #     # Read output file for download
# #     with open(output_path, 'rb') as f:
# #         result_data = f.read()
    
# #     st.download_button(
# #         label="📥 Download emails.jsonl",
# #         data=result_data,
# #         file_name="emails.jsonl",
# #         mime="application/json"
# #     )
    
# #     # Failure analysis
# #     if stats["failure_count"] > 0 or stats["low_confidence_count"] > 0:
# #         st.subheader("⚠️ Issues Analysis")
        
# #         failures = find_failure_cases([r.dict() for r in results])
        
# #         if failures:
# #             st.write("**Top failure cases for review:**")
# #             for i, failure in enumerate(failures, 1):
# #                 with st.expander(f"Issue #{i}: {failure['email_id']} (confidence: {failure['confidence']:.2f})"):
# #                     st.write(f"**Category:** {failure['category']}")
# #                     st.write(f"**Schema Valid:** {'Yes' if failure['schema_ok'] else 'No'}")
# #                     st.write(f"**Issues:** {failure['issues']}")
# #                     st.write(f"**Extracted Data:** {json.dumps(failure['data'], indent=2)}")

# # def generate_deliverables(result_data, output_path):
# #     """Generate report.md and prompts.md deliverables."""
    
# #     results = result_data["results"]
# #     stats = result_data["statistics"]
    
# #     # Generate report.md
# #     report_content = f"""# Email Classification Pipeline Report

# # ## Executive Summary

# # This report summarizes the results of processing {stats['total_emails']} emails through an automated classification and extraction pipeline using LangChain and OpenAI GPT-4o-mini.

# # ## Category Distribution

# # | Category | Count | Percentage |
# # |----------|-------|------------|
# # """
    
# #     for category, count in stats['category_distribution'].items():
# #         percentage = count / stats['total_emails'] * 100 if stats['total_emails'] > 0 else 0
# #         report_content += f"| {category} | {count} | {percentage:.1f}% |\n"
    
# #     report_content += f"""
# # ## Schema Validation Results

# # - **Total Emails Processed**: {stats['total_emails']}
# # - **Schema Validation Rate**: {stats['schema_validation_rate']:.1%}
# # - **Average Confidence Score**: {stats['average_confidence']:.2f}
# # - **High Confidence (≥0.8)**: {stats['high_confidence_count']} emails
# # - **Low Confidence (<0.5)**: {stats['low_confidence_count']} emails

# # ## Failure Case Analysis

# # """
    
# #     failures = find_failure_cases([r.dict() for r in results], limit=3)
    
# #     for i, failure in enumerate(failures, 1):
# #         report_content += f"""### Failure Case #{i}: {failure['email_id']}

# # - **Category**: {failure['category']}
# # - **Confidence**: {failure['confidence']:.2f}
# # - **Schema Valid**: {'Yes' if failure['schema_ok'] else 'No'}
# # - **Issues**: {failure['issues']}
# # - **Proposed Fix**: Review extraction prompts for this category, add more specific field validation

# # """
    
# #     report_content += """## Recommendations

# # 1. **Improve Low Confidence Cases**: Review and refine prompts for categories with low confidence scores
# # 2. **Enhance Schema Validation**: Add more robust data type checking in verification chain
# # 3. **Expand Training Examples**: Include more diverse email examples in prompts
# # 4. **Add Data Quality Checks**: Implement additional validation rules for specific field types

# # ## Technical Implementation

# # - **Framework**: LangChain with OpenAI GPT-4o-mini
# # - **Pipeline**: Classification → Extraction → Verification → Output
# # - **Output Format**: JSONL with structured schema per category
# # - **Validation**: Multi-stage confidence scoring with verification feedback
# # """
    
# #     # Generate prompts.md
# #     prompts_content = """# Email Classification Prompts Documentation

# # ## Version History

# # - **v1.0**: Initial prompts with basic classification and extraction
# # - **Current Version**: v1.0

# # ## Classification Prompt

# # ### Purpose
# # Classify emails into one of five predefined categories.

# # ### Prompt Template
# # ```
# # You are an expert email classifier. Your task is to classify emails into one of five categories:

# # CATEGORIES:
# # 1. "invoice/bill" - Bills, invoices, payment requests, financial statements
# # 2. "shipping/order" - Order confirmations, shipping notifications, delivery updates, tracking info
# # 3. "calendar_invite" - Meeting invitations, calendar events, appointment confirmations
# # 4. "newsletter" - Marketing emails, newsletters, promotional content, subscriptions
# # 5. "other" - Any email that doesn't fit the above categories

# # INSTRUCTIONS:
# # - Read the email content carefully
# # - Consider subject line, sender, and content patterns
# # - Assign confidence score (0.0-1.0) based on clarity of classification
# # - Provide brief reasoning for your classification
# # - Be decisive - choose the MOST appropriate category

# # EMAIL TO CLASSIFY:
# # {email_content}

# # {format_instructions}

# # Respond with valid JSON only.
# # ```

# # ## Extraction Prompts

# # ### Invoice/Bill Extraction
# # ```
# # Extract structured data from this invoice/bill email. Focus on financial and vendor information.

# # FIELDS TO EXTRACT:
# # - vendor: Company/person sending the bill
# # - amount: Total amount due (extract number only)
# # - currency: Currency symbol or code
# # - due_date: When payment is due (YYYY-MM-DD format if possible)
# # - invoice_number: Invoice/bill reference number
# # - description: Brief description of what the bill is for

# # EMAIL CONTENT:
# # {email_content}

# # Extract only the information that is clearly present. Use null for missing fields.
# # Return as JSON with the exact field names listed above.
# # ```

# # ### Shipping/Order Extraction
# # ```
# # Extract structured data from this shipping/order email. Focus on delivery and order information.

# # FIELDS TO EXTRACT:
# # - order_id: Order reference number
# # - tracking_number: Package tracking number
# # - carrier: Shipping company (UPS, FedEx, USPS, etc.)
# # - ship_date: Date item was shipped (YYYY-MM-DD format if possible)
# # - delivery_date: Expected delivery date (YYYY-MM-DD format if possible)
# # - status: Current shipping status
# # - items: Brief description of items being shipped

# # EMAIL CONTENT:
# # {email_content}

# # Extract only the information that is clearly present. Use null for missing fields.
# # Return as JSON with the exact field names listed above.
# # ```

# # ### Calendar Invite Extraction
# # ```
# # Extract structured data from this calendar invite email. Focus on event details.

# # FIELDS TO EXTRACT:
# # - event_title: Name/title of the event
# # - start_time: Event start time (include date and time if available)
# # - end_time: Event end time (include date and time if available)
# # - location: Where the event takes place
# # - organizer: Person organizing the event
# # - attendees: List of attendees (as comma-separated string)
# # - description: Event description or agenda

# # EMAIL CONTENT:
# # {email_content}

# # Extract only the information that is clearly present. Use null for missing fields.
# # Return as JSON with the exact field names listed above.
# # ```

# # ### Newsletter Extraction
# # ```
# # Extract structured data from this newsletter email. Focus on publication information.

# # FIELDS TO EXTRACT:
# # - sender: Newsletter sender/publication name
# # - subject: Email subject line
# # - newsletter_name: Name of the newsletter/publication
# # - main_topics: Key topics covered (as comma-separated string)
# # - unsubscribe_link: true if unsubscribe link is present, false otherwise

# # EMAIL CONTENT:
# # {email_content}

# # Extract only the information that is clearly present. Use null for missing fields.
# # Return as JSON with the exact field names listed above.
# # ```

# # ### Other Category Extraction
# # ```
# # Extract basic structured data from this email.

# # FIELDS TO EXTRACT:
# # - sender: Email sender name or address
# # - subject: Email subject line
# # - main_content: Brief summary of main content
# # - email_type: Your best guess at what type of email this is

# # EMAIL CONTENT:
# # {email_content}

# # Extract only the information that is clearly present. Use null for missing fields.
# # Return as JSON with the exact field names listed above.
# # ```

# # ## Verification Prompt

# # ### Purpose
# # Verify extracted data accuracy and suggest corrections.

# # ### Prompt Template
# # ```
# # You are a data quality validator. Your task is to verify extracted email data for accuracy and completeness.

# # ORIGINAL EMAIL:
# # {email_content}

# # EXTRACTED DATA:
# # {extracted_data}

# # EMAIL CATEGORY: {category}

# # VERIFICATION TASKS:
# # 1. Check if extracted data matches the email content
# # 2. Identify any missing important information
# # 3. Flag incorrect or inconsistent data
# # 4. Suggest corrections if needed

# # VALIDATION RULES BY CATEGORY:
# # - invoice/bill: Verify amounts, dates, vendor names are accurate
# # - shipping/order: Check order IDs, tracking numbers, dates are correct
# # - calendar_invite: Validate event times, dates, locations
# # - newsletter: Confirm sender, topics match content
# # - other: Basic accuracy check

# # RESPONSE FORMAT:
# # Return JSON with these fields:
# # - "schema_ok": true/false (whether data passes validation)
# # - "issues": array of strings describing problems found
# # - "corrected_data": object with corrections (only if corrections needed)
# # - "confidence_adjustment": number between -0.3 and 0.2 to adjust confidence

# # EXAMPLES:
# # Good data: {"schema_ok": true, "issues": [], "corrected_data": null, "confidence_adjustment": 0.1}
# # Bad data: {"schema_ok": false, "issues": ["Amount mismatch", "Invalid date format"], "corrected_data": {"amount": 99.99}, "confidence_adjustment": -0.2}
# # ```

# # ## Performance Notes

# # - Classification accuracy: Depends on email clarity and category distinctiveness
# # - Extraction completeness: Varies by email format and information availability
# # - Verification effectiveness: Catches obvious mismatches and formatting issues
# # - Recommended improvements: Add few-shot examples, implement field-specific validators
# # """
    
# #     return report_content, prompts_content

# # def main():
# #     """Main Streamlit application."""
    
# #     st.title("📧 Email Classification Pipeline")
# #     st.markdown("*Automated email processing using LangChain + OpenAI*")
    
# #     # Initialize app
# #     if not initialize_app():
# #         return
    
# #     # Sidebar
# #     st.sidebar.title("🔧 Configuration")
# #     st.sidebar.info(f"Model: {Config.OPENAI_MODEL}")
# #     st.sidebar.info(f"Temperature: {Config.TEMPERATURE}")
    
# #     # Main interface
# #     st.header("📁 Upload Emails")
    
# #     # File upload
# #     uploaded_file = st.file_uploader(
# #         "Upload emails.txt file (one email per line)",
# #         type=['txt'],
# #         help="Each line should contain one complete email"
# #     )
    
# #     # Sample file generation
# #     col1, col2 = st.columns(2)
    
# #     with col1:
# #         if st.button("📄 Generate Sample File"):
# #             sample_content = create_sample_file()
# #             st.download_button(
# #                 label="📥 Download Sample emails.txt",
# #                 data=sample_content,
# #                 file_name="sample_emails.txt",
# #                 mime="text/plain"
# #             )
    
# #     # Process emails
# #     if uploaded_file is not None:
# #         st.header("🚀 Processing")
        
# #         if st.button("▶️ Run Pipeline", type="primary"):
# #             try:
# #                 # Process emails
# #                 result_data, output_path = process_emails(uploaded_file)
                
# #                 # Display results
# #                 st.success("✅ Processing completed!")
# #                 display_results(result_data, output_path)
                
# #                 # Generate deliverables
# #                 st.header("📑 Generate Deliverables")
                
# #                 col1, col2 = st.columns(2)
                
# #                 with col1:
# #                     if st.button("📊 Generate Report"):
# #                         report_content, _ = generate_deliverables(result_data, output_path)
# #                         st.download_button(
# #                             label="📥 Download report.md",
# #                             data=report_content,
# #                             file_name="report.md",
# #                             mime="text/markdown"
# #                         )
                
# #                 with col2:
# #                     if st.button("📝 Generate Prompts Doc"):
# #                         _, prompts_content = generate_deliverables(result_data, output_path)
# #                         st.download_button(
# #                             label="📥 Download prompts.md",
# #                             data=prompts_content,
# #                             file_name="prompts.md",
# #                             mime="text/markdown"
# #                         )
                
# #                 # Clean up
# #                 if os.path.exists(output_path):
# #                     os.unlink(output_path)
                
# #             except Exception as e:
# #                 st.error(f"❌ Processing failed: {e}")
# #                 logger.error(f"Pipeline error: {e}")
    
# #     # Instructions
# #     st.sidebar.header("📖 Instructions")
# #     st.sidebar.markdown("""
# #     1. **Setup**: Ensure `.env` file contains your OpenAI API key
# #     2. **Upload**: Choose your `emails.txt` file (one email per line)
# #     3. **Process**: Click 'Run Pipeline' to classify and extract data
# #     4. **Download**: Get `emails.jsonl`, `report.md`, and `prompts.md`
# #     5. **Review**: Check failure cases and adjust prompts if needed
# #     """)

# # if __name__ == "__main__":
# #     main()


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

"""Streamlit frontend for email classification pipeline."""
from backend.pipeline.email_pipeline import EmailProcessingPipeline
import streamlit as st
import os
import sys
import logging
import tempfile
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

# Check Gmail availability
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

# Gmail client class (only if Gmail is available)
if GMAIL_AVAILABLE:
    class GmailClient:
        """Gmail client for fetching emails."""
        
        def __init__(self):
            self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            self.service = None
            self._authenticate()
        
        def _authenticate(self):
            """Authenticate with Gmail API."""
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('gmail', 'v1', credentials=creds)
        
        def fetch_emails(self, max_results=10, query=None):
            """Fetch emails from Gmail."""
            try:
                # Get message IDs
                results = self.service.users().messages().list(
                    userId='me', 
                    maxResults=max_results,
                    q=query
                ).execute()
                
                messages = results.get('messages', [])
                emails = []
                
                for message in messages:
                    # Get full message
                    msg = self.service.users().messages().get(
                        userId='me', 
                        id=message['id']
                    ).execute()
                    
                    # Extract email content
                    email_content = self._extract_email_content(msg)
                    emails.append(email_content)
                
                return emails
            
            except HttpError as error:
                raise Exception(f"Gmail API error: {error}")
        
        def _extract_email_content(self, message):
            """Extract readable content from Gmail message."""
            payload = message['payload']
            
            # Get headers
            headers = {h['name']: h['value'] for h in payload.get('headers', [])}
            subject = headers.get('Subject', 'No Subject')
            sender = headers.get('From', 'Unknown Sender')
            date = headers.get('Date', 'Unknown Date')
            
            # Get body
            body = self._get_message_body(payload)
            
            # Format as email
            email_text = f"From: {sender}\nSubject: {subject}\nDate: {date}\n\n{body}"
            return email_text
        
        def _get_message_body(self, payload):
            """Extract body text from message payload."""
            body = ""
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body']['data']
                        body = self._decode_base64(data)
                        break
                    elif part['mimeType'] == 'text/html':
                        data = part['body']['data']
                        body = self._decode_base64(data)
            else:
                if payload['mimeType'] == 'text/plain':
                    data = payload['body']['data']
                    body = self._decode_base64(data)
            
            return body
        
        def _decode_base64(self, data):
            """Decode base64 encoded email data."""
            import base64
            return base64.urlsafe_b64decode(data).decode('utf-8')

try:
    from backend.config import Config
    from backend.pipeline.email_pipeline import EmailProcessingPipeline
    from backend.utils.helpers import format_statistics, find_failure_cases, create_sample_emails
    from backend.models.schemas import EmailCategory
except ImportError as e:
    st.error(f"Backend import error: {e}")
    st.info("Please ensure the backend modules are properly installed and accessible.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# # Page config
# st.set_page_config(
#     page_title="Email Classification Pipeline",
#     page_icon="📧",
#     layout="wide"
# )

def initialize_app():
    """Initialize the application and validate configuration."""
    try:
        Config.validate()
        return True
    except Exception as e:
        st.error(f"Configuration Error: {e}")
        st.info("Please check your .env file and ensure OPENAI_API_KEY is set.")
        return False

def gmail_integration_section():
    """Gmail integration section for fetching real emails."""
    st.header("📬 Gmail Integration")
    
    # Check if Gmail packages are installed
    if not GMAIL_AVAILABLE:
        st.warning("⚠️ Gmail integration not available")
        st.markdown("""
        **To connect your Gmail account, install additional packages:**
        ```bash
        pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
        ```
        
        **Then restart the Streamlit app.**
        """)
        return None
    
    # Check if Gmail credentials exist
    has_credentials = os.path.exists("credentials.json")
    has_token = os.path.exists("token.json")
    
    if not has_credentials:
        st.warning("⚠️ Gmail credentials not found")
        st.markdown("""
        **To connect your Gmail account:**
        
        1. **Enable Gmail API**: Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. **Create Project**: Create new project or select existing
        3. **Enable Gmail API**: Search for Gmail API and enable it
        4. **Create Credentials**: Create OAuth 2.0 Client ID credentials
        5. **Download**: Download as `credentials.json` and place in project root
        
        **Security Note**: This gives read-only access to your Gmail. Credentials stay local.
        """)
        
        # File uploader for credentials
        cred_file = st.file_uploader(
            "Upload Gmail credentials.json", 
            type=['json'],
            help="Download from Google Cloud Console"
        )
        
        if cred_file:
            with open("credentials.json", "wb") as f:
                f.write(cred_file.getbuffer())
            st.success("✅ Credentials saved! Restart the app to use Gmail integration.")
            st.rerun()
        
        return None
    
    st.success("✅ Gmail credentials found!")
    if has_token:
        st.info("🔑 Authentication token exists - ready to fetch emails")
    
    # Gmail fetch options
    st.subheader("📥 Fetch Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_emails = st.number_input("Max emails to fetch", min_value=1, max_value=100, value=20)
    
    with col2:
        query_type = st.selectbox("Email filter", [
            "Recent emails (last 7 days)",
            "All emails",
            "Unread only", 
            "Bills/Invoices",
            "Shipping/Orders",
            "Calendar invites",
            "Custom query"
        ])
    
    # Query mapping
    query_map = {
        "Recent emails (last 7 days)": "newer_than:7d",
        "All emails": None,
        "Unread only": "is:unread",
        "Bills/Invoices": "subject:(invoice OR bill OR payment OR due)",
        "Shipping/Orders": "subject:(shipped OR tracking OR delivery OR order)",
        "Calendar invites": "subject:(meeting OR appointment OR invite OR calendar)",
        "Custom query": None
    }
    
    query = query_map[query_type]
    
    if query_type == "Custom query":
        query = st.text_input("Gmail search query", 
                             placeholder="e.g., from:billing@company.com OR subject:invoice",
                             help="Use Gmail search syntax")
    
    # Display current query
    if query:
        st.info(f"📝 Search query: `{query}`")
    
    # Preview and fetch buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👁️ Preview Emails"):
            try:
                with st.spinner("Connecting to Gmail..."):
                    gmail = GmailClient()
                    
                    # Fetch small sample for preview
                    emails = gmail.fetch_emails(max_results=5, query=query)
                
                if not emails:
                    st.warning("No emails found with the specified criteria.")
                    return
                
                st.subheader("📋 Email Preview")
                for i, email in enumerate(emails, 1):
                    with st.expander(f"Email {i} - {email.split(chr(10))[1][:50]}..."):
                        st.text(email[:500] + "..." if len(email) > 500 else email)
                
            except Exception as e:
                st.error(f"Gmail preview failed: {e}")
                if "credentials" in str(e).lower():
                    st.info("💡 Try setting up credentials again or check your Google Cloud Console setup")
    
    with col2:
        if st.button("📧 Fetch & Process", type="primary"):
            try:
                # Fetch emails from Gmail
                with st.spinner(f"Fetching {max_emails} emails from Gmail..."):
                    gmail = GmailClient()
                    emails = gmail.fetch_emails(max_results=max_emails, query=query)
                
                if not emails:
                    st.warning("No emails found with the specified criteria.")
                    return
                
                st.success(f"✅ Fetched {len(emails)} emails from Gmail!")
                
                # Create temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                    temp_file.write('\n\n'.join(emails))
                    temp_file_path = temp_file.name
                
                # Process through pipeline
                with st.spinner("Processing emails through AI pipeline..."):
                    pipeline = EmailProcessingPipeline()
                    result_data = pipeline.process_and_save(temp_file_path, "data/gmail_emails.jsonl")
                
                # Display results
                st.success("✅ Gmail emails processed successfully!")
                display_results(result_data, "data/gmail_emails.jsonl")
                
                # Generate deliverables section
                st.header("📑 Generate Deliverables")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Generate Report (Gmail)", key="gmail_report"):
                        report_content, _ = generate_deliverables(result_data, "data/gmail_emails.jsonl")
                        st.download_button(
                            label="📥 Download report.md",
                            data=report_content,
                            file_name="gmail_report.md",
                            mime="text/markdown",
                            key="download_gmail_report"
                        )
                
                with col2:
                    if st.button("📝 Generate Prompts Doc (Gmail)", key="gmail_prompts"):
                        _, prompts_content = generate_deliverables(result_data, "data/gmail_emails.jsonl")
                        st.download_button(
                            label="📥 Download prompts.md",
                            data=prompts_content,
                            file_name="gmail_prompts.md",
                            mime="text/markdown",
                            key="download_gmail_prompts"
                        )
                
                # Cleanup
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
            except Exception as e:
                st.error(f"Gmail processing failed: {e}")
                logger.error(f"Gmail processing error: {e}")
                
                # Helpful error messages
                if "credentials" in str(e).lower():
                    st.info("💡 Check your credentials.json file and Google Cloud Console setup")
                elif "quota" in str(e).lower():
                    st.info("💡 You might have hit Gmail API quota limits. Try again later or reduce max_emails")
                elif "authentication" in str(e).lower():
                    st.info("💡 Try deleting token.json and re-authenticating")

def create_sample_file():
    """Create a sample emails.txt file."""
    try:
        sample_emails = create_sample_emails()
        sample_content = "\n\n".join(sample_emails)
        return sample_content
    except Exception as e:
        # Fallback sample content if create_sample_emails is not available
        sample_content = """From: billing@acme.com
Subject: Invoice #12345 - Payment Due
Date: Mon, 1 Jan 2024 10:00:00 -0500

Dear Customer,

Your invoice #12345 for $150.00 USD is now due.
Please pay by January 15, 2024.

Best regards,
ACME Billing Team

From: shipping@store.com
Subject: Your order #54321 has shipped
Date: Tue, 2 Jan 2024 14:30:00 -0500

Hi there!

Great news! Your order #54321 has been shipped via UPS.
Tracking number: 1Z123456789
Expected delivery: January 5, 2024

Items shipped:
- Widget A x2
- Widget B x1

Track your package: https://ups.com/track

Thanks for shopping with us!

From: events@company.com
Subject: Meeting Invitation: Weekly Team Sync
Date: Wed, 3 Jan 2024 09:00:00 -0500

You're invited to:
Weekly Team Sync

When: Friday, January 5, 2024 at 2:00 PM EST
Where: Conference Room A / Zoom
Organizer: John Smith

Agenda:
- Project updates
- Q4 planning
- Open discussion

Please confirm your attendance.

From: newsletter@news.com
Subject: Weekly Newsletter - Tech Updates
Date: Thu, 4 Jan 2024 08:00:00 -0500

🚀 Weekly Tech Newsletter

This week's highlights:
- AI breakthrough in healthcare
- New programming languages
- Industry trends analysis

Read full articles: https://news.com/newsletter

Unsubscribe: https://news.com/unsubscribe"""
        return sample_content

def process_emails(uploaded_file):
    """Process uploaded emails through the pipeline."""
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_input:
        # Read uploaded file
        content = uploaded_file.getvalue().decode('utf-8')
        temp_input.write(content)
        temp_input_path = temp_input.name
    
    temp_output_path = tempfile.mktemp(suffix='.jsonl')
    
    try:
        # Initialize pipeline
        pipeline = EmailProcessingPipeline()
        
        # Process emails
        with st.spinner("Processing emails through AI pipeline..."):
            result_data = pipeline.process_and_save(temp_input_path, temp_output_path)
        
        return result_data, temp_output_path
    
    finally:
        # Clean up temporary input file
        if os.path.exists(temp_input_path):
            os.unlink(temp_input_path)

def display_results(result_data, output_path):
    """Display processing results in the UI."""
    
    results = result_data["results"]
    stats = result_data["statistics"]
    
    # Summary metrics
    st.subheader("📊 Processing Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Emails", stats["total_emails"])
    
    with col2:
        st.metric("Schema Valid", f"{stats['schema_validation_rate']:.1%}")
    
    with col3:
        st.metric("Avg Confidence", f"{stats['average_confidence']:.2f}")
    
    with col4:
        st.metric("High Confidence", stats["high_confidence_count"])
    
    # Category distribution chart
    st.subheader("📈 Category Distribution")
    
    category_data = [(cat, count) for cat, count in stats["category_distribution"].items()]
    category_df = pd.DataFrame(category_data, columns=["Category", "Count"])
    
    fig = px.pie(category_df, values="Count", names="Category", 
                 title="Email Categories")
    st.plotly_chart(fig, use_container_width=True)
    
    # Confidence distribution
    st.subheader("🎯 Confidence Distribution")
    
    confidences = [r.confidence for r in results]
    confidence_df = pd.DataFrame({"Confidence": confidences})
    
    fig = px.histogram(confidence_df, x="Confidence", nbins=20, 
                      title="Distribution of Confidence Scores")
    st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    st.subheader("📋 Detailed Results")
    
    # Convert results to DataFrame for display
    display_data = []
    for result in results:
        display_data.append({
            "Email ID": result.email_id,
            "Category": result.category.value,
            "Confidence": f"{result.confidence:.2f}",
            "Schema Valid": "✅" if result.schema_ok else "❌",
            "Fields Extracted": len([v for v in result.data.values() if v]),
            "Notes": result.processing_notes or "None"
        })
    
    results_df = pd.DataFrame(display_data)
    st.dataframe(results_df, use_container_width=True)
    
    # Download section
    st.subheader("💾 Download Results")
    
    # Read output file for download
    with open(output_path, 'rb') as f:
        result_data = f.read()
    
    st.download_button(
        label="📥 Download emails.jsonl",
        data=result_data,
        file_name="emails.jsonl",
        mime="application/json"
    )
    
    # Failure analysis
    if stats["failure_count"] > 0 or stats["low_confidence_count"] > 0:
        st.subheader("⚠️ Issues Analysis")
        
        failures = find_failure_cases([r.dict() for r in results])
        
        if failures:
            st.write("**Top failure cases for review:**")
            for i, failure in enumerate(failures, 1):
                with st.expander(f"Issue #{i}: {failure['email_id']} (confidence: {failure['confidence']:.2f})"):
                    st.write(f"**Category:** {failure['category']}")
                    st.write(f"**Schema Valid:** {'Yes' if failure['schema_ok'] else 'No'}")
                    st.write(f"**Issues:** {failure['issues']}")
                    st.write(f"**Extracted Data:** {json.dumps(failure['data'], indent=2)}")

def generate_deliverables(result_data, output_path):
    """Generate report.md and prompts.md deliverables."""
    
    results = result_data["results"]
    stats = result_data["statistics"]
    
    # Generate report.md
    report_content = f"""# Email Classification Pipeline Report

## Executive Summary

This report summarizes the results of processing {stats['total_emails']} emails through an automated classification and extraction pipeline using LangChain and OpenAI GPT-4o-mini.

## Category Distribution

| Category | Count | Percentage |
|----------|-------|------------|
"""
    
    for category, count in stats['category_distribution'].items():
        percentage = count / stats['total_emails'] * 100 if stats['total_emails'] > 0 else 0
        report_content += f"| {category} | {count} | {percentage:.1f}% |\n"
    
    report_content += f"""
## Schema Validation Results

- **Total Emails Processed**: {stats['total_emails']}
- **Schema Validation Rate**: {stats['schema_validation_rate']:.1%}
- **Average Confidence Score**: {stats['average_confidence']:.2f}
- **High Confidence (≥0.8)**: {stats['high_confidence_count']} emails
- **Low Confidence (<0.5)**: {stats['low_confidence_count']} emails

## Failure Case Analysis

"""
    
    failures = find_failure_cases([r.dict() for r in results], limit=3)
    
    for i, failure in enumerate(failures, 1):
        report_content += f"""### Failure Case #{i}: {failure['email_id']}

- **Category**: {failure['category']}
- **Confidence**: {failure['confidence']:.2f}
- **Schema Valid**: {'Yes' if failure['schema_ok'] else 'No'}
- **Issues**: {failure['issues']}
- **Proposed Fix**: Review extraction prompts for this category, add more specific field validation

"""
    
    report_content += """## Recommendations

1. **Improve Low Confidence Cases**: Review and refine prompts for categories with low confidence scores
2. **Enhance Schema Validation**: Add more robust data type checking in verification chain
3. **Expand Training Examples**: Include more diverse email examples in prompts
4. **Add Data Quality Checks**: Implement additional validation rules for specific field types

## Technical Implementation

- **Framework**: LangChain with OpenAI GPT-4o-mini
- **Pipeline**: Classification → Extraction → Verification → Output
- **Output Format**: JSONL with structured schema per category
- **Validation**: Multi-stage confidence scoring with verification feedback
"""
    
    # Generate prompts.md
    prompts_content = """# Email Classification Prompts Documentation

## Version History

- **v1.0**: Initial prompts with basic classification and extraction
- **Current Version**: v1.0

## Classification Prompt

### Purpose
Classify emails into one of five predefined categories.

### Prompt Template
```
You are an expert email classifier. Your task is to classify emails into one of five categories:

CATEGORIES:
1. "invoice/bill" - Bills, invoices, payment requests, financial statements
2. "shipping/order" - Order confirmations, shipping notifications, delivery updates, tracking info
3. "calendar_invite" - Meeting invitations, calendar events, appointment confirmations
4. "newsletter" - Marketing emails, newsletters, promotional content, subscriptions
5. "other" - Any email that doesn't fit the above categories

INSTRUCTIONS:
- Read the email content carefully
- Consider subject line, sender, and content patterns
- Assign confidence score (0.0-1.0) based on clarity of classification
- Provide brief reasoning for your classification
- Be decisive - choose the MOST appropriate category

EMAIL TO CLASSIFY:
{email_content}

{format_instructions}

Respond with valid JSON only.
```

## Extraction Prompts

### Invoice/Bill Extraction
```
Extract structured data from this invoice/bill email. Focus on financial and vendor information.

FIELDS TO EXTRACT:
- vendor: Company/person sending the bill
- amount: Total amount due (extract number only)
- currency: Currency symbol or code
- due_date: When payment is due (YYYY-MM-DD format if possible)
- invoice_number: Invoice/bill reference number
- description: Brief description of what the bill is for

EMAIL CONTENT:
{email_content}

Extract only the information that is clearly present. Use null for missing fields.
Return as JSON with the exact field names listed above.
```

### Shipping/Order Extraction
```
Extract structured data from this shipping/order email. Focus on delivery and order information.

FIELDS TO EXTRACT:
- order_id: Order reference number
- tracking_number: Package tracking number
- carrier: Shipping company (UPS, FedEx, USPS, etc.)
- ship_date: Date item was shipped (YYYY-MM-DD format if possible)
- delivery_date: Expected delivery date (YYYY-MM-DD format if possible)
- status: Current shipping status
- items: Brief description of items being shipped

EMAIL CONTENT:
{email_content}

Extract only the information that is clearly present. Use null for missing fields.
Return as JSON with the exact field names listed above.
```

### Calendar Invite Extraction
```
Extract structured data from this calendar invite email. Focus on event details.

FIELDS TO EXTRACT:
- event_title: Name/title of the event
- start_time: Event start time (include date and time if available)
- end_time: Event end time (include date and time if available)
- location: Where the event takes place
- organizer: Person organizing the event
- attendees: List of attendees (as comma-separated string)
- description: Event description or agenda

EMAIL CONTENT:
{email_content}

Extract only the information that is clearly present. Use null for missing fields.
Return as JSON with the exact field names listed above.
```

### Newsletter Extraction
```
Extract structured data from this newsletter email. Focus on publication information.

FIELDS TO EXTRACT:
- sender: Newsletter sender/publication name
- subject: Email subject line
- newsletter_name: Name of the newsletter/publication
- main_topics: Key topics covered (as comma-separated string)
- unsubscribe_link: true if unsubscribe link is present, false otherwise

EMAIL CONTENT:
{email_content}

Extract only the information that is clearly present. Use null for missing fields.
Return as JSON with the exact field names listed above.
```

### Other Category Extraction
```
Extract basic structured data from this email.

FIELDS TO EXTRACT:
- sender: Email sender name or address
- subject: Email subject line
- main_content: Brief summary of main content
- email_type: Your best guess at what type of email this is

EMAIL CONTENT:
{email_content}

Extract only the information that is clearly present. Use null for missing fields.
Return as JSON with the exact field names listed above.
```

## Verification Prompt

### Purpose
Verify extracted data accuracy and suggest corrections.

### Prompt Template
```
You are a data quality validator. Your task is to verify extracted email data for accuracy and completeness.

ORIGINAL EMAIL:
{email_content}

EXTRACTED DATA:
{extracted_data}

EMAIL CATEGORY: {category}

VERIFICATION TASKS:
1. Check if extracted data matches the email content
2. Identify any missing important information
3. Flag incorrect or inconsistent data
4. Suggest corrections if needed

VALIDATION RULES BY CATEGORY:
- invoice/bill: Verify amounts, dates, vendor names are accurate
- shipping/order: Check order IDs, tracking numbers, dates are correct
- calendar_invite: Validate event times, dates, locations
- newsletter: Confirm sender, topics match content
- other: Basic accuracy check

RESPONSE FORMAT:
Return JSON with these fields:
- "schema_ok": true/false (whether data passes validation)
- "issues": array of strings describing problems found
- "corrected_data": object with corrections (only if corrections needed)
- "confidence_adjustment": number between -0.3 and 0.2 to adjust confidence

EXAMPLES:
Good data: {"schema_ok": true, "issues": [], "corrected_data": null, "confidence_adjustment": 0.1}
Bad data: {"schema_ok": false, "issues": ["Amount mismatch", "Invalid date format"], "corrected_data": {"amount": 99.99}, "confidence_adjustment": -0.2}
```

## Performance Notes

- Classification accuracy: Depends on email clarity and category distinctiveness
- Extraction completeness: Varies by email format and information availability
- Verification effectiveness: Catches obvious mismatches and formatting issues
- Recommended improvements: Add few-shot examples, implement field-specific validators
"""
    
    return report_content, prompts_content

def main():
    """Main Streamlit application."""
    
    st.title("📧 Email Classification Pipeline")
    st.markdown("*Automated email processing using LangChain + OpenAI*")
    
    # Initialize app
    if not initialize_app():
        return
    
    # Sidebar
    st.sidebar.title("🔧 Configuration")
    try:
        st.sidebar.info(f"Model: {Config.OPENAI_MODEL}")
        st.sidebar.info(f"Temperature: {Config.TEMPERATURE}")
    except:
        st.sidebar.info("Model: Configuration not loaded")
    
    # Gmail integration section
    gmail_integration_section()
    
    # Original file upload section
    st.header("📁 Upload Emails (Alternative)")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload emails.txt file (one email per line)",
        type=['txt'],
        help="Each line should contain one complete email"
    )
    
    # Sample file generation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Generate Sample File"):
            sample_content = create_sample_file()
            st.download_button(
                label="📥 Download Sample emails.txt",
                data=sample_content,
                file_name="sample_emails.txt",
                mime="text/plain"
            )
    
    # Process emails
    if uploaded_file is not None:
        st.header("🚀 Processing")
        
        if st.button("▶️ Run Pipeline", type="primary"):
            try:
                # Process emails
                result_data, output_path = process_emails(uploaded_file)
                
                # Display results
                st.success("✅ Processing completed!")
                display_results(result_data, output_path)
                
                # Generate deliverables
                st.header("📑 Generate Deliverables")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("📊 Generate Report"):
                        report_content, _ = generate_deliverables(result_data, output_path)
                        st.download_button(
                            label="📥 Download report.md",
                            data=report_content,
                            file_name="report.md",
                            mime="text/markdown"
                        )
                
                with col2:
                    if st.button("📝 Generate Prompts Doc"):
                        _, prompts_content = generate_deliverables(result_data, output_path)
                        st.download_button(
                            label="📥 Download prompts.md",
                            data=prompts_content,
                            file_name="prompts.md",
                            mime="text/markdown"
                        )
                
                # Clean up
                if os.path.exists(output_path):
                    os.unlink(output_path)
                
            except Exception as e:
                st.error(f"❌ Processing failed: {e}")
                logger.error(f"Pipeline error: {e}")
    
    # Instructions
    st.sidebar.header("📖 Instructions")
    st.sidebar.markdown("""
    **Gmail Integration:**
    1. **Setup**: Upload credentials.json from Google Cloud Console
    2. **Authenticate**: First run opens browser for Gmail permission
    3. **Fetch**: Choose email filter and click 'Fetch & Process'
    
    **File Upload:**
    1. **Generate**: Click 'Generate Sample File' to test
    2. **Upload**: Choose your emails.txt file (one email per line)
    3. **Process**: Click 'Run Pipeline' to classify and extract data
    4. **Download**: Get emails.jsonl, report.md, and prompts.md
    5. **Review**: Check failure cases and adjust prompts if needed
    """)

if __name__ == "__main__":
    main()




























