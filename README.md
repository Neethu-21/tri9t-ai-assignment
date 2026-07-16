# Tri9T AI Assignment

## Overview

This project implements a document parsing and QA generation system for engineering manuals.

The application parses PDF documents, reconstructs their hierarchical structure, stores multiple document versions, compares document versions, allows users to create reusable document selections, generates QA test cases using Google's Gemini API, and detects whether previously generated outputs are stale after document updates.

---

# Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyMuPDF
- Google Gemini API

---

# Project Structure

```
tri9t-ai-assignment/

│── app/
│   ├── main.py
│   ├── parser.py
│   ├── database.py
│   ├── models.py
│   ├── gemini_api.py
│
│── data/
│   ├── ct200_manual.pdf
│   ├── ct200_manual_v2.pdf
│   └── document.db
│
│── tests/
│   └── test_parser.py
│
│── README.md
│── APPROACH.md
│── requirements.txt
```

---

# Installation

Create a virtual environment.

```bash
python -m venv venv
```

Activate the environment.

### Windows

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

# Environment Variable

Create a `.env` file in the project root.

```
GEMINI_API_KEY=YOUR_API_KEY
```

Update `gemini_api.py` to read the key from the environment.

---

# Running the Project

## Step 1

Import Version 1.

```bash
python -m app.parser
```

This parses the PDF and stores Version 1 and Version 2 in SQLite.

---

## Step 2

Start the API.

```bash
uvicorn app.main:app --reload
```

---

## Step 3

Open Swagger UI.

```
http://127.0.0.1:8000/docs
```

---

# Re-ingesting Version 2

The parser imports both document versions into the SQLite database.

Version comparison can be viewed using:

```
GET /compare
```

The endpoint returns:

- Added Sections
- Removed Sections
- Modified Sections

---

# Available APIs

## Home

```
GET /
```

---

## View Headings

```
GET /headings
```

---

## View Section

```
GET /section/{node_id}
```

Returns:

- Heading
- Body
- Version

---

## Search

```
GET /search?keyword=Device
```

Searches document headings.

---

## Compare Versions

```
GET /compare
```

Shows:

- Added headings
- Removed headings
- Changed headings

---

## Create Selection

```
POST /selection
```

Example

```json
{
    "name":"Safety Tests",
    "version":2,
    "nodes":[1,2,3]
}
```

---

## Generate QA Test Cases

```
GET /generate/{selection_id}
```

Selected document text is sent to Gemini.

Generated QA test cases are stored in the database.

---

## Retrieve Generation

```
GET /generation/{generation_id}
```

Returns:

- Generation ID
- Selection ID
- Document Version
- Generated QA Test Cases
- Staleness Status

---

# Running Unit Tests

```bash
python -m unittest tests.test_parser
```

---

# Version Matching Strategy

The project compares document versions using:

- Heading Name
- SHA256 Content Hash

Sections are classified as:

- Added
- Removed
- Changed

---

# Staleness Detection

Generated QA test cases are linked to the document version used during generation.

During retrieval the stored version is compared with the latest version.

If versions differ:

```
stale = true
```

Otherwise:

```
stale = false
```

---

# Known Limitations

- Heading matching is based on heading names and content hashes.
- Unnumbered documents are not fully supported.
- Complex tables are extracted as plain text.
- Gemini API responses depend on API availability and quota limits.

---

# Future Improvements

- MongoDB for generated outputs
- Semantic version matching
- Better parser support for complex formatting
- Structured JSON validation for LLM responses

---

# Author

Neethu Shree V