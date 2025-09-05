"""Utility functions for email processing."""

import uuid
import hashlib
from datetime import datetime
from typing import List, Dict, Any

def generate_email_id() -> str:
    """Generate unique email ID."""
    return str(uuid.uuid4())[:8]

def calculate_final_confidence(classification_conf: float, 
                             extraction_conf: float, 
                             verification_adjustment: float) -> float:
    """Calculate final confidence score combining all pipeline stages."""
    
    # Weighted average of classification and extraction confidence
    base_confidence = (classification_conf * 0.6) + (extraction_conf * 0.4)
    
    # Apply verification adjustment
    final_confidence = base_confidence + verification_adjustment
    
    # Clamp between 0 and 1
    return max(0.0, min(1.0, final_confidence))

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text for display purposes."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def hash_email_content(content: str) -> str:
    """Create hash of email content for deduplication."""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def format_statistics(stats: Dict[str, Any]) -> str:
    """Format statistics for display."""
    lines = []
    lines.append(f"Total Emails: {stats['total_emails']}")
    lines.append(f"Schema Validation Rate: {stats['schema_validation_rate']:.1%}")
    lines.append(f"Average Confidence: {stats['average_confidence']:.2f}")
    lines.append("")
    lines.append("Category Distribution:")
    
    for category, count in stats['category_distribution'].items():
        percentage = count / stats['total_emails'] * 100 if stats['total_emails'] > 0 else 0
        lines.append(f"  {category}: {count} ({percentage:.1f}%)")
    
    return "\n".join(lines)

def find_failure_cases(results: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
    """Find failure cases for analysis."""
    failures = []
    
    for result in results:
        if (not result.get('schema_ok', True) or 
            result.get('confidence', 1.0) < 0.3):
            failures.append({
                'email_id': result.get('email_id'),
                'category': result.get('category'),
                'confidence': result.get('confidence'),
                'schema_ok': result.get('schema_ok'),
                'issues': result.get('processing_notes', ''),
                'data': result.get('data', {})
            })
    
    # Sort by confidence (lowest first) and return top N
    failures.sort(key=lambda x: x['confidence'])
    return failures[:limit]

def create_sample_emails() -> List[str]:
    """Create sample emails for testing (if no emails.txt provided)."""
    
    samples = [
        # Invoice/Bill
        """From: billing@acmeservices.com
Subject: Invoice #INV-2024-001 Due

Dear Customer,

Your invoice #INV-2024-001 for $150.00 is now due.
Amount: $150.00
Due Date: 2024-02-15
Description: Monthly consulting services

Please remit payment by the due date.

Best regards,
Acme Services""",

        # Shipping/Order
        """From: orders@shoponline.com
Subject: Your order has shipped!

Hi there!

Great news! Your order #ORD-789123 has shipped.

Order Details:
- Order ID: ORD-789123
- Tracking: 1Z999AA1234567890
- Carrier: UPS
- Expected delivery: 2024-02-10

Track your package at ups.com

Thanks for shopping with us!""",

        # Calendar Invite
        """From: alice@company.com
Subject: Team Meeting - February 8th

Hi team,

You're invited to our weekly team meeting.

Event: Team Meeting
Date: February 8, 2024
Time: 10:00 AM - 11:00 AM PST
Location: Conference Room A
Organizer: Alice Smith

Please let me know if you can attend.

Best,
Alice""",

        # Newsletter
        """From: newsletter@techblog.com
Subject: Weekly Tech Update #47

Tech Weekly Newsletter

This week in technology:
- AI developments continue to accelerate
- New framework releases
- Industry merger news

Read full articles at techblog.com
Unsubscribe: Click here to unsubscribe

© 2024 Tech Blog""",

        # Other
        """From: friend@email.com
Subject: Catch up soon?

Hey!

Hope you're doing well. Want to grab coffee sometime this week?
Let me know what works for you.

Talk soon,
Sarah"""
    ]
    
    return samples