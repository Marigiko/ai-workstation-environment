---
name: compose-scraper
description: Compose workflow for building async web scrapers with rate limiting, error handling, and data export
---

# Compose Workflow: Web Scraper

You are orchestrating the creation of a production-ready async web scraper.

## Phase 1: Specification
Gather requirements:
- Target website(s) and URLs
- Data to extract (fields, structure)
- Rate limiting requirements
- Output format (JSON, CSV, database)
- Error handling strategy

## Phase 2: Planning
Break down into tasks:
1. Project structure setup
2. HTTP client configuration (aiohttp/httpx)
3. HTML parsing (BeautifulSoup/lxml)
4. Data models and validation
5. Rate limiting and retry logic
6. Error handling and logging
7. Data export pipeline
8. Testing with mocks

## Phase 3: Execution
Execute tasks in order:
- Implement core scraping logic
- Add rate limiting and retries
- Implement data validation
- Build export pipeline
- Write tests with mocked responses

## Phase 4: Verification
- Test against sample pages
- Verify rate limiting works
- Check error handling
- Validate output format

## Phase 5: Documentation
- Usage examples
- Configuration guide
- Rate limiting explanation
- Troubleshooting common issues

## Deliverables
- Async scraper with rate limiting
- Data validation and cleaning
- Multiple export formats
- Comprehensive error handling
- Test suite with mocks
- Usage documentation

Use `@tdd-driver` for test writing, `@perf-analyzer` for performance review.
