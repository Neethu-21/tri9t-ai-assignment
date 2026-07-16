# Tri9T AI Assignment – Approach Document

## Overview

This project implements a document parsing and QA generation system for engineering manuals. The system parses PDF documents, reconstructs their hierarchical structure, stores multiple document versions, compares document versions, allows users to create reusable document selections, generates QA test cases using a Large Language Model (Gemini), and detects when generated outputs become stale after document updates.

---

# Architecture

The project consists of the following components:

- FastAPI
- SQLAlchemy ORM
- SQLite Database
- PyMuPDF (fitz)
- Google Gemini API

SQLite is used for storing parsed document structures, versions, selections, and generated outputs. Since this assignment is a prototype, SQLite was chosen for simplicity and portability.

---

# Data Model

The project contains three primary entities.

## Node

Each parsed heading becomes a Node.

Each node stores:

- Document Version
- Heading
- Heading Level
- Body Text
- Parent Node
- Content Hash

The content hash is generated using SHA256 and is later used for change detection.

---

## Selection

A selection represents a user-selected group of document nodes.

Each selection stores:

- Selection Name
- Document Version
- Selected Node IDs

Selections remain associated with the version they were created from.

---

## Generation

Each LLM response is stored as a Generation.

Each generation stores:

- Selection ID
- Generated QA Test Cases
- Document Version

This allows generated outputs to be checked against future document versions.

---

# Parsing Strategy

The parser processes the PDF using PyMuPDF.

For each page:

1. Extract text.
2. Split text into lines.
3. Detect headings using numbering patterns.

Example:

1.
1.1
1.1.1

The heading level is determined from the number of dots.

Example:

1 → Level 1

2.3 → Level 2

4.5.6 → Level 3

Body text is attached to the nearest previous heading.

Parent-child relationships are maintained using a stack that tracks the most recent heading at each level.

---

# Handling Parser Irregularities

The parser currently handles:

- Nested headings
- Multi-level numbering
- Empty lines
- Multiple pages

Known limitations:

- Duplicate headings with identical numbering are treated as separate nodes.
- Documents without numeric heading formats are not fully supported.
- Complex tables are extracted as plain text.

These limitations are acceptable for the provided engineering manual.

---

# Version Matching Strategy

The project imports Version 1 and Version 2 independently.

Each node stores a SHA256 content hash.

Version comparison works as follows:

- If a heading exists only in Version 2 → Added
- If a heading exists only in Version 1 → Removed
- If heading exists in both but hashes differ → Changed

This is a heading + content hash matching strategy.

## Known Limitations

If a heading is renamed while its content remains identical, it is treated as a new section rather than the same logical node.

A more robust production system could use fuzzy matching or semantic embeddings.

---

# Browse API

The system provides endpoints for:

- Listing document headings
- Viewing individual sections
- Searching headings
- Comparing document versions

---

# Selection API

Users can create named selections containing multiple document nodes.

Selections are associated with the document version used during creation.

These selections are later reused for QA generation.

---

# LLM Prompt Design

Selected document text is reconstructed into a single prompt.

The prompt requests:

- Exactly 5 QA Test Cases
- Test Case ID
- Title
- Steps
- Expected Result

This produces structured QA ideas while remaining concise.

---

# Structured Output Validation

The project validates that Gemini returns non-empty output.

If the API returns an error or malformed response, the system stores an informative error message instead of crashing.

Examples include:

- API quota exceeded
- Authentication failure
- Empty response

This allows the API to remain operational even when the external LLM service fails.

---

# Duplicate Generation Policy

If the same selection is submitted multiple times, a new Generation record is created.

This preserves historical generations and allows users to compare outputs generated at different times.

---

# Staleness Detection

Each generation stores the document version used during generation.

During retrieval:

Current Document Version is compared with Stored Generation Version.

If versions differ:

stale = true

Otherwise:

stale = false

This provides a lightweight mechanism for determining whether generated QA test cases may no longer reflect the latest document.

## Limitation

This version-based approach cannot distinguish between:

- Minor wording changes
- Significant technical specification changes

Both are treated equally.

A production system could compare hashes of the selected nodes instead of only document versions.

---

# Technologies

- Python
- FastAPI
- SQLAlchemy
- SQLite
- PyMuPDF
- Google Gemini API

---

# Future Improvements

Given additional development time, the following improvements would be implemented:

- MongoDB for LLM outputs
- Fuzzy heading matching
- Semantic version matching using embeddings
- Rich table parsing
- Structured JSON validation for LLM responses
- Automatic regeneration of stale test cases

---

# Decision Log

## 1. What part of the system is most likely to silently produce incorrect results?

The version-matching strategy based on heading names and content hashes.

If a heading is renamed without significant content changes, it may be treated as a new section instead of the same logical node.

This could be improved using semantic similarity or embedding-based matching.

---

## 2. Where did you choose simplicity over correctness?

SQLite was used for storing generated outputs instead of introducing a separate NoSQL database.

This reduced project complexity and allowed all project data to remain in a single portable database.

For a production system, generated outputs would likely be stored separately with richer metadata and indexing.

---

## 3. Name one input that is not fully handled.

The parser assumes numbered headings.

Documents containing completely unnumbered heading structures or highly irregular formatting may not reconstruct the hierarchy correctly.

Such content is currently imported as regular body text rather than structured headings.

---

# Conclusion

The project demonstrates an end-to-end workflow for parsing engineering documents, maintaining document versions, generating QA test cases using an LLM, and identifying stale outputs after document updates. The design prioritizes simplicity, readability, and maintainability while leaving room for future enhancements such as semantic version matching, improved parser robustness, and richer LLM output validation.