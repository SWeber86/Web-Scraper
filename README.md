# Web-Scraper
Scrape HTML heading tags, meta descriptions, and paragraph tags from a list of URLs
# HTML Scraper and Indexer

## Overview

This Python script automates the process of scraping and indexing important HTML elements from a list of URLs. It extracts heading tags, meta descriptions, paragraph tags, and images, providing structured data for analysis and SEO optimization.

## Features

- **Extracts**: 
  - Heading tags (`<h1>`, `<h2>`, `<h3>`, `<h4>`, `<h5>`)
  - Meta descriptions
  - Paragraph tags
  - Image sources and alt text
- **Fetches Links**: Gathers all anchor tags and their corresponding links.
- **Measures Page Load Time**: Provides insights into the performance of each URL.
- **Output**: Returns data in three structured pandas DataFrames.

## Requirements

- Python 3.x
- Libraries:
  - `requests`
  - `beautifulsoup4`
  - `pandas`
  - `tqdm`

You can install the required libraries using pip:

```bash
pip install requests beautifulsoup4 pandas tqdm
