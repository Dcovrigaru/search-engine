"""
Configuration settings for the search engine.
"""

# Crawler settings
SEED_URLS = [
    # GeeksforGeeks - Programming and CS tutorials
    'https://www.geeksforgeeks.org/python-programming-language/',
    'https://www.geeksforgeeks.org/data-structures/',
    'https://www.geeksforgeeks.org/algorithms/',
    'https://www.geeksforgeeks.org/machine-learning/',

    # W3Schools - Web development
    'https://www.w3schools.com/python/',
    'https://www.w3schools.com/js/',
    'https://www.w3schools.com/sql/',

    # TutorialsPoint - Various CS topics
    'https://www.tutorialspoint.com/python/index.htm',
    'https://www.tutorialspoint.com/data_structures_algorithms/index.htm',

    # Wikipedia CS articles (English only)
    'https://en.wikipedia.org/wiki/Python_(programming_language)',
    'https://en.wikipedia.org/wiki/Computer_science',
    'https://en.wikipedia.org/wiki/Data_structure',
    'https://en.wikipedia.org/wiki/Algorithm',
]

MAX_PAGES = 500  # Minimum number of pages to crawl
CRAWL_DELAY = 1.0  # Delay in seconds between requests (politeness policy)
REQUEST_TIMEOUT = 10  # Timeout for HTTP requests in seconds
MAX_DEPTH = 2  # Maximum crawl depth from seed URLs (reduced to stay focused)

# Domain restrictions (set to None to crawl any domain, or list allowed domains)
ALLOWED_DOMAINS = ['geeksforgeeks.org', 'w3schools.com', 'tutorialspoint.com', 'en.wikipedia.org']

# Indexer settings
STOP_WORDS_LANGUAGE = 'english'
MIN_TERM_LENGTH = 2
MAX_TERM_LENGTH = 50

# PageRank settings
PAGERANK_ITERATIONS = 20
PAGERANK_DAMPING = 0.85

# Ranking weights (must sum to 1.0)
WEIGHT_COSINE = 0.6  # w1: weight for cosine similarity score
WEIGHT_PAGERANK = 0.4  # w2: weight for PageRank score

# Storage paths
CRAWLED_PAGES_DIR = 'crawled_pages'
INDEX_DIR = 'index_data'
TEMPLATES_DIR = 'templates'

# Web interface settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5001
RESULTS_PER_PAGE = 10
