# """Email classification chain using LangChain."""

# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema.runnable import RunnablePassthrough
# from langchain.output_parsers import PydanticOutputParser
# from backend.models.schemas import ClassificationResult, EmailCategory
# from backend.config import Config
# import json
# import logging

# logger = logging.getLogger(__name__)

# class EmailClassifierChain:
#     """LangChain-based email classifier."""
    
#     def __init__(self):
#         self.llm = ChatOpenAI(
#             model=Config.OPENAI_MODEL,
#             temperature=Config.TEMPERATURE,
#             max_tokens=Config.MAX_TOKENS,
#             # api_key=Config.OPENAI_API_KEY  # Not needed for HF
#         )
        
#         self.parser = PydanticOutputParser(pydantic_object=ClassificationResult)
#         self.prompt = self._create_prompt()
#         self.chain = self._build_chain()
    
#     def _create_prompt(self) -> ChatPromptTemplate:
#         """Create classification prompt template."""
        
#         prompt_template = """
# You are an expert email classifier. Your task is to classify emails into one of five categories:

# CATEGORIES:
# 1. "invoice/bill" - Bills, invoices, payment requests, financial statements
# 2. "shipping/order" - Order confirmations, shipping notifications, delivery updates, tracking info
# 3. "calendar_invite" - Meeting invitations, calendar events, appointment confirmations
# 4. "newsletter" - Marketing emails, newsletters, promotional content, subscriptions
# 5. "other" - Any email that doesn't fit the above categories

# INSTRUCTIONS:
# - Read the email content carefully
# - Consider subject line, sender, and content patterns
# - Assign confidence score (0.0-1.0) based on clarity of classification
# - Provide brief reasoning for your classification
# - Be decisive - choose the MOST appropriate category

# EMAIL TO CLASSIFY:
# {email_content}

# {format_instructions}

# Respond with valid JSON only.
# """
        
#         return ChatPromptTemplate.from_template(prompt_template)
    
#     def _build_chain(self):
#         """Build the classification chain."""
#         return (
#             {
#                 "email_content": RunnablePassthrough(),
#                 "format_instructions": lambda _: self.parser.get_format_instructions()
#             }
#             | self.prompt
#             | self.llm
#             | self.parser
#         )
    
#     def classify(self, email_content: str) -> ClassificationResult:
#         """Classify a single email."""
#         try:
#             result = self.chain.invoke(email_content)
#             logger.info(f"Classified email as '{result.category}' with confidence {result.confidence}")
#             return result
        
#         except Exception as e:
#             logger.error(f"Classification failed: {e}")
#             # Return fallback classification
#             return ClassificationResult(
#                 category=EmailCategory.OTHER,
#                 confidence=0.1,
#                 reasoning=f"Classification failed: {str(e)}"
#             )
    
#     def classify_batch(self, email_contents: list[str]) -> list[ClassificationResult]:
#         """Classify multiple emails."""
#         results = []
#         for i, content in enumerate(email_contents):
#             logger.info(f"Classifying email {i+1}/{len(email_contents)}")
#             result = self.classify(content)
#             results.append(result)
#         return results


"""Email classification chain using LangChain."""

import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.output_parsers import PydanticOutputParser
from backend.models.schemas import ClassificationResult, EmailCategory
from backend.config import Config
import json
import logging

logger = logging.getLogger(__name__)

class EmailClassifierChain:
    """LangChain-based email classifier."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            # model=Config.OPENAI_MODEL,
            # temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
            # api_key=Config.OPENAI_API_KEY  # Not needed for HF
        )
        
        self.parser = PydanticOutputParser(pydantic_object=ClassificationResult)
        self.prompt = self._create_prompt()
        self.chain = self._build_chain()
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create classification prompt template."""
        
        prompt_template = """
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
"""
        
        return ChatPromptTemplate.from_template(prompt_template)
    
    def _build_chain(self):
        """Build the classification chain."""
        return (
            {
                "email_content": RunnablePassthrough(),
                "format_instructions": lambda _: self.parser.get_format_instructions()
            }
            | self.prompt
            | self.llm
            | self.parser
        )
    
    def classify(self, email_content: str) -> ClassificationResult:
        """Classify a single email."""
        try:
            result = self.chain.invoke(email_content)
            logger.info(f"Classified email as '{result.category}' with confidence {result.confidence}")
            return result
        
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            # Return fallback classification
            return ClassificationResult(
                category=EmailCategory.OTHER,
                confidence=0.1,
                reasoning=f"Classification failed: {str(e)}"
            )
    
    def classify_batch(self, email_contents: list[str]) -> list[ClassificationResult]:
        """Classify multiple emails."""
        results = []
        for i, content in enumerate(email_contents):
            logger.info(f"Classifying email {i+1}/{len(email_contents)}")
            result = self.classify(content)
            results.append(result)
        return results