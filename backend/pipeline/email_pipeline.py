"""Main email processing pipeline orchestrating all chains."""

import logging
import json
import jsonlines
from typing import List, Dict, Any
from backend.chains.classifier_chain import EmailClassifierChain
from backend.chains.extractor_chain import EmailExtractorChain
from backend.chains.verifier_chain import EmailVerifierChain
from backend.models.schemas import EmailProcessingResult, EmailCategory
from backend.config import Config
from backend.utils.helpers import generate_email_id, calculate_final_confidence

logger = logging.getLogger(__name__)

class EmailProcessingPipeline:
    """Complete email processing pipeline."""
    
    def __init__(self):
        self.classifier = EmailClassifierChain()
        self.extractor = EmailExtractorChain()
        self.verifier = EmailVerifierChain()
        
        # Statistics tracking
        self.stats = {
            "total_processed": 0,
            "categories": {cat.value: 0 for cat in EmailCategory},
            "schema_valid": 0,
            "failures": []
        }
    
    def process_email(self, email_content: str, email_id: str = None) -> EmailProcessingResult:
        """Process a single email through the complete pipeline."""
        
        if not email_id:
            email_id = generate_email_id()
        
        logger.info(f"Processing email {email_id}")
        
        try:
            # Step 1: Classification
            logger.debug("Step 1: Classifying email")
            classification = self.classifier.classify(email_content)
            
            # Step 2: Extraction
            logger.debug("Step 2: Extracting structured data")
            extraction = self.extractor.extract(email_content, classification.category)
            
            # Step 3: Verification
            logger.debug("Step 3: Verifying extracted data")
            verification = self.verifier.verify(
                email_content, 
                extraction.data.dict(), 
                classification.category
            )
            
            # Step 4: Combine results
            final_confidence = calculate_final_confidence(
                classification.confidence,
                extraction.confidence,
                verification.confidence_adjustment
            )
            
            # Apply corrections if available
            final_data = extraction.data.dict()
            if verification.corrected_data:
                final_data.update(verification.corrected_data)
            
            # Create final result
            result = EmailProcessingResult(
                email_id=email_id,
                category=classification.category,
                confidence=final_confidence,
                schema_ok=verification.schema_ok,
                data=final_data,
                processing_notes=self._generate_processing_notes(
                    classification, extraction, verification
                )
            )
            
            # Update statistics
            self._update_stats(result)
            
            logger.info(f"Successfully processed email {email_id} as {result.category}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process email {email_id}: {e}")
            
            # Create error result
            error_result = EmailProcessingResult(
                email_id=email_id,
                category=EmailCategory.OTHER,
                confidence=0.0,
                schema_ok=False,
                data={},
                processing_notes=f"Processing failed: {str(e)}"
            )
            
            self.stats["failures"].append({
                "email_id": email_id,
                "error": str(e),
                "content_preview": email_content[:100] + "..." if len(email_content) > 100 else email_content
            })
            
            return error_result
    
    def process_emails_from_file(self, file_path: str) -> List[EmailProcessingResult]:
        """Process emails from a text file (one email per line)."""
        
        logger.info(f"Processing emails from {file_path}")
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                emails = [line.strip() for line in f if line.strip()]
            
            logger.info(f"Found {len(emails)} emails to process")
            
            for i, email_content in enumerate(emails, 1):
                email_id = f"email_{i:03d}"
                logger.info(f"Processing email {i}/{len(emails)}")
                
                result = self.process_email(email_content, email_id)
                results.append(result)
            
            logger.info(f"Completed processing {len(results)} emails")
            return results
            
        except FileNotFoundError:
            logger.error(f"Email file not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading email file: {e}")
            raise
    
    def save_results_to_jsonl(self, results: List[EmailProcessingResult], output_path: str):
        """Save processing results to JSONL file."""
        
        logger.info(f"Saving results to {output_path}")
        
        try:
            with jsonlines.open(output_path, mode='w') as writer:
                for result in results:
                    # Convert to dict and ensure proper serialization
                    result_dict = result.dict()
                    writer.write(result_dict)
            
            logger.info(f"Successfully saved {len(results)} results to {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def process_and_save(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """Complete pipeline: process emails and save results."""
        
        # Reset statistics
        self.stats = {
            "total_processed": 0,
            "categories": {cat.value: 0 for cat in EmailCategory},
            "schema_valid": 0,
            "failures": []
        }
        
        # Process emails
        results = self.process_emails_from_file(input_file)
        
        # Save results
        self.save_results_to_jsonl(results, output_file)
        
        # Generate final statistics
        final_stats = self._generate_final_stats(results)
        
        return {
            "results": results,
            "statistics": final_stats,
            "output_file": output_file
        }
    
    def _update_stats(self, result: EmailProcessingResult):
        """Update processing statistics."""
        self.stats["total_processed"] += 1
        self.stats["categories"][result.category.value] += 1
        
        if result.schema_ok:
            self.stats["schema_valid"] += 1
    
    def _generate_processing_notes(self, classification, extraction, verification) -> str:
        """Generate processing notes for debugging."""
        notes = []
        
        notes.append(f"Classification: {classification.category.value} ({classification.confidence:.2f})")
        notes.append(f"Extraction: {extraction.extracted_fields} fields ({extraction.confidence:.2f})")
        
        if verification.issues:
            notes.append(f"Issues: {', '.join(verification.issues)}")
        
        if verification.corrected_data:
            notes.append("Data corrections applied")
        
        return " | ".join(notes)
    
    def _generate_final_stats(self, results: List[EmailProcessingResult]) -> Dict[str, Any]:
        """Generate final processing statistics."""
        
        total = len(results)
        schema_valid_count = sum(1 for r in results if r.schema_ok)
        avg_confidence = sum(r.confidence for r in results) / total if total > 0 else 0
        
        return {
            "total_emails": total,
            "schema_validation_rate": schema_valid_count / total if total > 0 else 0,
            "average_confidence": avg_confidence,
            "category_distribution": {
                cat.value: sum(1 for r in results if r.category == cat) 
                for cat in EmailCategory
            },
            "failure_count": len([r for r in results if r.confidence == 0.0]),
            "high_confidence_count": sum(1 for r in results if r.confidence >= 0.8),
            "low_confidence_count": sum(1 for r in results if r.confidence < 0.5)
        }






