"""
Email Analysis Script - Detect patterns in your email data
Run this to understand what types of emails you have before setting categories.

Usage: python email_analyzer.py
"""

import re
from collections import Counter, defaultdict
import json
import os

class EmailAnalyzer:
    def __init__(self):
        self.senders = Counter()
        self.subjects = []
        self.keywords = Counter()
        self.domains = Counter()
        self.patterns = defaultdict(list)
        
    def analyze_emails(self, email_file_path):
        """Analyze emails from a text file."""
        if not os.path.exists(email_file_path):
            print(f"❌ File {email_file_path} not found!")
            print("📝 Please create emails.txt file first with your email data.")
            return None
            
        with open(email_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split emails (assuming they're separated by double newlines)
        emails = content.split('\n\n')
        emails = [email.strip() for email in emails if email.strip()]
        
        print(f"📧 Found {len(emails)} emails to analyze...")
        
        if len(emails) == 0:
            print("⚠️ No emails found in the file!")
            return None
        
        for i, email in enumerate(emails):
            self._analyze_single_email(email, i+1)
        
        return self._generate_report()
    
    def _analyze_single_email(self, email_content, email_num):
        """Analyze a single email."""
        lines = email_content.strip().split('\n')
        
        sender = None
        subject = None
        
        # Extract sender and subject
        for line in lines:
            if line.startswith('From:'):
                sender = line.replace('From:', '').strip()
                self.senders[sender] += 1
                
                # Extract domain
                domain_match = re.search(r'@([^>\s]+)', sender)
                if domain_match:
                    domain = domain_match.group(1).lower()
                    self.domains[domain] += 1
                    
            elif line.startswith('Subject:'):
                subject = line.replace('Subject:', '').strip()
                self.subjects.append(subject)
        
        # Extract keywords from entire email
        words = re.findall(r'\b[a-zA-Z]{3,}\b', email_content.lower())
        for word in words:
            # Skip common words
            if word not in ['the', 'and', 'you', 'for', 'are', 'with', 'this', 'that', 'have', 'your', 'from', 'will', 'can', 'our', 'email', 'please', 'dear', 'best', 'regards', 'thanks']:
                self.keywords[word] += 1
        
        # Detect patterns
        self._detect_patterns(email_content, sender, subject)
    
    def _detect_patterns(self, content, sender, subject):
        """Detect common email patterns."""
        content_lower = content.lower()
        
        # Financial patterns
        if any(word in content_lower for word in ['invoice', 'bill', 'payment', 'amount', 'due', 'bank', 'account', 'balance', 'transaction']):
            self.patterns['financial'].append({'sender': sender, 'subject': subject})
        
        # Shopping/Order patterns
        if any(word in content_lower for word in ['order', 'shipping', 'delivery', 'tracking', 'purchase', 'shipped', 'cart']):
            self.patterns['shopping'].append({'sender': sender, 'subject': subject})
        
        # Work/Business patterns
        if any(word in content_lower for word in ['meeting', 'project', 'deadline', 'team', 'office', 'work', 'conference', 'schedule']):
            self.patterns['work'].append({'sender': sender, 'subject': subject})
        
        # Social/Personal patterns
        if any(word in content_lower for word in ['birthday', 'family', 'friend', 'personal', 'wedding', 'party', 'congratulations']):
            self.patterns['personal'].append({'sender': sender, 'subject': subject})
        
        # Marketing/Promotional patterns
        if any(word in content_lower for word in ['offer', 'sale', 'discount', 'deal', 'promo', 'unsubscribe', 'limited', 'free']):
            self.patterns['promotional'].append({'sender': sender, 'subject': subject})
        
        # Notifications/Alerts patterns
        if any(word in content_lower for word in ['notification', 'alert', 'reminder', 'update', 'verify', 'confirm', 'security']):
            self.patterns['notifications'].append({'sender': sender, 'subject': subject})
        
        # Educational patterns
        if any(word in content_lower for word in ['university', 'course', 'assignment', 'exam', 'grade', 'professor', 'student', 'college']):
            self.patterns['educational'].append({'sender': sender, 'subject': subject})
        
        # Government/Official patterns
        if any(word in content_lower for word in ['government', 'tax', 'official', 'legal', 'court', 'ministry', 'department']):
            self.patterns['official'].append({'sender': sender, 'subject': subject})
        
        # News/Newsletter patterns
        if any(word in content_lower for word in ['newsletter', 'news', 'weekly', 'monthly', 'digest', 'update', 'subscribe']):
            self.patterns['newsletter'].append({'sender': sender, 'subject': subject})
    
    def _generate_report(self):
        """Generate analysis report."""
        total_emails = sum(self.senders.values())
        
        report = {
            'summary': {
                'total_emails': total_emails,
                'unique_senders': len(self.senders),
                'unique_domains': len(self.domains)
            },
            'top_senders': dict(self.senders.most_common(10)),
            'top_domains': dict(self.domains.most_common(10)),
            'top_keywords': dict(self.keywords.most_common(20)),
            'detected_patterns': {k: len(v) for k, v in self.patterns.items()},
            'pattern_examples': {}
        }
        
        # Add examples for each pattern
        for pattern_type, emails in self.patterns.items():
            if emails:
                report['pattern_examples'][pattern_type] = emails[:3]  # First 3 examples
        
        return report

def print_analysis_report(report):
    """Print a formatted analysis report."""
    print("\n" + "="*60)
    print("📧 EMAIL ANALYSIS REPORT")
    print("="*60)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"   Total Emails: {report['summary']['total_emails']}")
    print(f"   Unique Senders: {report['summary']['unique_senders']}")
    print(f"   Unique Domains: {report['summary']['unique_domains']}")
    
    # Top domains
    print(f"\n🌐 TOP EMAIL DOMAINS:")
    for domain, count in report['top_domains'].items():
        percentage = (count / report['summary']['total_emails']) * 100
        print(f"   {domain}: {count} emails ({percentage:.1f}%)")
    
    # Detected patterns
    print(f"\n🔍 DETECTED EMAIL PATTERNS:")
    total_emails = report['summary']['total_emails']
    for pattern, count in sorted(report['detected_patterns'].items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            percentage = (count / total_emails) * 100
            print(f"   {pattern.upper()}: {count} emails ({percentage:.1f}%)")
    
    # Top keywords
    print(f"\n🔑 MOST COMMON KEYWORDS:")
    for keyword, count in list(report['top_keywords'].items())[:10]:
        print(f"   {keyword}: {count} times")
    
    # Pattern examples
    print(f"\n💡 PATTERN EXAMPLES:")
    for pattern_type, examples in report['pattern_examples'].items():
        if examples:
            print(f"\n   {pattern_type.upper()} examples:")
            for i, example in enumerate(examples, 1):
                sender = example['sender'][:40] + "..." if example['sender'] and len(example['sender']) > 40 else example['sender']
                subject = example['subject'][:50] + "..." if example['subject'] and len(example['subject']) > 50 else example['subject']
                print(f"      {i}. From: {sender}")
                print(f"         Subject: {subject}")

def suggest_categories(report):
    """Suggest email categories based on analysis."""
    patterns = report['detected_patterns']
    total_emails = report['summary']['total_emails']
    
    print(f"\n🎯 SUGGESTED EMAIL CATEGORIES FOR CONFIG.PY:")
    print("   Copy this to your backend/config.py file:")
    print("\n   EMAIL_CATEGORIES = [")
    
    suggestions = []
    
    # Only suggest categories that have significant email volume (>5% of total)
    threshold = max(1, total_emails * 0.05)  # At least 5% or 1 email
    
    for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True):
        if count >= threshold:
            suggestions.append(pattern)
            percentage = (count / total_emails) * 100
            print(f'       "{pattern}",  # {count} emails ({percentage:.1f}%)')
    
    # Always include 'other' as fallback
    if 'other' not in suggestions:
        print(f'       "other"   # Fallback category')
        suggestions.append('other')
    
    print("   ]")
    return suggestions

def create_sample_emails_file():
    """Create a sample emails.txt file for testing."""
    sample_content = """From: billing@easypaisa.com.pk
Subject: EasyPaisa Transaction Alert
Date: Mon, 1 Jan 2024 10:00:00 +0500

Dear Customer,
Your EasyPaisa account has been debited Rs. 500.
Transaction ID: EP123456789
Balance: Rs. 2,500
Thank you for using EasyPaisa.

From: orders@daraz.pk
Subject: Your order #D123456 has been shipped
Date: Tue, 2 Jan 2024 14:30:00 +0500

Assalam-o-Alaikum!
Great news! Your Daraz order #D123456 has been shipped.
Tracking: TCS123456789
Expected delivery: January 5, 2024
Items: Mobile Phone Case, Earphones
Track: https://daraz.pk/track

From: noreply@vu.edu.pk
Subject: Assignment Submission Reminder
Date: Wed, 3 Jan 2024 09:00:00 +0500

Dear Student,
This is a reminder that your CS101 assignment is due on January 10, 2024.
Please submit through VULMS portal.
Course: Introduction to Computing
Instructor: Dr. Ahmed Khan

From: newsletter@dawn.com
Subject: Dawn News Update - Daily Headlines
Date: Thu, 4 Jan 2024 08:00:00 +0500

Today's top stories:
- Political developments
- Economic updates  
- Sports highlights
- Weather forecast
Read full news at dawn.com
Unsubscribe: dawn.com/unsubscribe

From: alerts@hbl.com.pk
Subject: HBL Account Statement Available
Date: Fri, 5 Jan 2024 11:00:00 +0500

Dear Valued Customer,
Your monthly account statement is now available.
Account: ****1234
Statement Period: December 2023
Login to HBL portal to download.

From: hr@company.com
Subject: Team Meeting Tomorrow
Date: Mon, 8 Jan 2024 16:00:00 +0500

Dear Team,
Please join tomorrow's team meeting at 10 AM.
Agenda: Project updates, Q1 planning
Location: Conference Room A
Zoom link: https://zoom.us/meeting

From: support@olx.com.pk
Subject: Your Ad has been approved
Date: Tue, 9 Jan 2024 12:00:00 +0500

Congratulations! Your OLX ad has been approved.
Ad Title: Samsung Galaxy Phone
Category: Mobiles
Views: 45
Manage your ads: olx.com.pk/account

From: family@gmail.com
Subject: Birthday party invitation
Date: Wed, 10 Jan 2024 18:00:00 +0500

Assalam-o-Alaikum cousin!
You're invited to my birthday party this Saturday.
Time: 7 PM
Location: Our house in Defence
Please confirm if you can come.
Looking forward to seeing you!"""

    with open('emails.txt', 'w', encoding='utf-8') as f:
        f.write(sample_content)
    
    print("✅ Sample emails.txt file created!")
    print("📧 Contains 8 sample Pakistani emails for testing")

# Main execution
if __name__ == "__main__":
    print("📧 EMAIL ANALYZER - Discover Your Email Patterns")
    print("=" * 50)
    
    # Check if emails.txt exists
    if not os.path.exists('emails.txt'):
        print("❌ emails.txt file not found!")
        print("\n💡 Options:")
        print("1. Create sample file for testing")
        print("2. Add your own emails to emails.txt")
        
        choice = input("\nCreate sample file? (y/n): ").lower().strip()
        if choice == 'y' or choice == 'yes':
            create_sample_emails_file()
        else:
            print("\n📝 Please create emails.txt file with your email data.")
            print("Format: Each email separated by double newline (\\n\\n)")
            print("Include From:, Subject:, and email content.")
            exit()
    
    # Run analysis
    analyzer = EmailAnalyzer()
    report = analyzer.analyze_emails('emails.txt')
    
    if report:
        # Print detailed report
        print_analysis_report(report)
        
        # Get category suggestions
        suggested_categories = suggest_categories(report)
        
        # Save report as JSON
        with open('email_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed report saved as 'email_analysis_report.json'")
        print(f"✅ Analysis complete!")
        print(f"\n📋 Next steps:")
        print(f"1. Copy the suggested categories to backend/config.py")
        print(f"2. Update your classifier and extractor chains")
        print(f"3. Test with your categories!")