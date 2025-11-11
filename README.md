# Web Search Engine

A complete search engine implementation featuring web crawling, indexing, and ranking using Vector Space Model with TF-IDF and PageRank algorithms.

## Features

- **Scrapy-based Crawler**: Professional web crawling with politeness policies
- **Inverted Index**: TF-IDF based indexing for efficient retrieval
- **PageRank**: Link-based ranking algorithm
- **Combined Ranking**: Weighted combination (60% relevance + 40% PageRank)
- **Web Interface**: Clean Flask-based search UI
- **CS-focused**: Crawls educational content from GeeksforGeeks, W3Schools, TutorialsPoint, and Wikipedia

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
python3 -m nltk.downloader stopwords punkt
```

### 2. Run the Pipeline

```bash
# Step 1: Crawl web pages (~8-10 minutes for 500 pages)
python3 crawler.py

# Step 2: Build index and compute PageRank (~30 seconds)
python3 indexer.py
python3 pagerank.py

# Step 3: Start web interface
python3 search_app.py
```

Then open http://localhost:5001 in your browser.

## Configuration

Edit `config.py` to customize:

- **SEED_URLS**: Starting URLs for crawling
- **ALLOWED_DOMAINS**: Restrict crawling to specific domains
- **MAX_PAGES**: Number of pages to crawl (default: 500)
- **CRAWL_DELAY**: Politeness delay in seconds (default: 1.0)
- **MAX_DEPTH**: Maximum crawl depth (default: 2)
- **WEIGHT_COSINE**: Relevance weight (default: 0.6)
- **WEIGHT_PAGERANK**: PageRank weight (default: 0.4)

## Project Structure

```
search_engine/
├── config.py           # Configuration settings
├── crawler.py          # Scrapy-based web crawler
├── indexer.py          # TF-IDF index builder
├── pagerank.py         # PageRank algorithm
├── search_engine.py    # Core search with combined ranking
├── search_app.py       # Flask web interface
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
│   ├── search.html     # Main search page
│   └── about.html      # About page
├── crawled_pages/      # Generated: crawled HTML pages
└── index_data/         # Generated: inverted index & PageRank
```

## Algorithm Details

### Ranking Formula
```
score(d, q) = 0.6 × cosine_similarity(d, q) + 0.4 × pagerank(d)
```

- **Cosine Similarity**: TF-IDF weighted Vector Space Model
- **PageRank**: Iterative link-based ranking (20 iterations, damping=0.85)
- **Relevance Threshold**: Filters results with cosine < 0.01

### Example Queries

Try these queries for best results:
- `python programming`
- `data structures`
- `dijkstra algorithm`
- `machine learning`

## Technical Specifications

- **Language**: Python 3.9+
- **Crawler**: Scrapy 2.13+
- **Text Processing**: NLTK
- **Web Framework**: Flask
- **Crawl Rate**: ~1 page/second (respects politeness policy)
- **Index Size**: ~500 pages, ~10,000 terms
- **Query Time**: < 100ms
# search-engine
# search-engine
