# Email Classification Agentic AI Pipeline

A complete email processing pipeline using LangChain and OpenAI GPT models for automated email classification and structured data extraction.

## 🎯 Project Overview

This project implements a three-stage agentic AI pipeline:

1. **Classification**: Categorize emails into 5 types (invoice/bill, shipping/order, calendar_invite, newsletter, other)
2. **Extraction**: Extract structured data fields specific to each category
3. **Verification**: Self-check and correct extracted data for accuracy

## 🏗️ Architecture

```
Email Input → Classifier → Extractor → Verifier → Structured Output
     ↓            ↓           ↓          ↓           ↓
   Raw Text   Category   Field Data  Validation  JSONL File
```

- **LangChain**: Orchestrates AI chains and prompt management
- **OpenAI GPT-4o-mini**: Powers classification, extraction, and verification
- **Pydantic**: Ensures type-safe data schemas
- **Streamlit**: Provides user-friendly web interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd email_classifier
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash

   ```
