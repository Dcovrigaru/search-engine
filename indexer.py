"""
Indexer: Builds inverted index from crawled HTML pages.
"""

import os
import json
import re
import math
from collections import defaultdict
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import config


class HTMLParser:
    """Parse HTML content and extract text."""

    def __init__(self):
        # Download NLTK data if needed
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        self.stop_words = set(stopwords.words(config.STOP_WORDS_LANGUAGE))

    def extract_text(self, html_content):
        """Extract clean text from HTML."""
        soup = BeautifulSoup(html_content, 'lxml')

        # Remove script and style elements
        for element in soup(['script', 'style', 'meta', 'link']):
            element.decompose()

        # Get text
        text = soup.get_text(separator=' ')

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def extract_title(self, html_content):
        """Extract page title from HTML."""
        soup = BeautifulSoup(html_content, 'lxml')
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return "Untitled"

    def tokenize(self, text):
        """Tokenize and normalize text."""
        # Convert to lowercase
        text = text.lower()

        # Tokenize
        tokens = word_tokenize(text)

        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            # Remove non-alphabetic tokens
            if not token.isalpha():
                continue

            # Check length
            if len(token) < config.MIN_TERM_LENGTH or len(token) > config.MAX_TERM_LENGTH:
                continue

            # Remove stopwords
            if token in self.stop_words:
                continue

            filtered_tokens.append(token)

        return filtered_tokens


class InvertedIndex:
    """Build and manage inverted index."""

    def __init__(self):
        self.index = defaultdict(dict)  # term -> {doc_id: term_freq}
        self.doc_lengths = {}  # doc_id -> document length (for normalization)
        self.doc_info = {}  # doc_id -> {url, title, token_count}
        self.total_docs = 0
        self.parser = HTMLParser()

    def add_document(self, doc_id, url, html_content):
        """Add a document to the index."""
        # Extract text and title
        text = self.parser.extract_text(html_content)
        title = self.parser.extract_title(html_content)

        # Tokenize
        tokens = self.parser.tokenize(text)

        if not tokens:
            return

        # Count term frequencies
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1

        # Add to inverted index
        for term, freq in term_freq.items():
            self.index[term][doc_id] = freq

        # Calculate document length (Euclidean norm for cosine similarity)
        doc_length = math.sqrt(sum(freq ** 2 for freq in term_freq.values()))
        self.doc_lengths[doc_id] = doc_length

        # Store document info
        self.doc_info[doc_id] = {
            'url': url,
            'title': title,
            'token_count': len(tokens)
        }

        self.total_docs += 1

    def calculate_idf(self):
        """Calculate IDF (Inverse Document Frequency) for all terms."""
        self.idf = {}
        for term, postings in self.index.items():
            df = len(postings)  # Document frequency
            self.idf[term] = math.log(self.total_docs / df)

    def save(self, output_dir):
        """Save index to disk."""
        os.makedirs(output_dir, exist_ok=True)

        # Calculate IDF before saving
        self.calculate_idf()

        # Save inverted index
        index_file = os.path.join(output_dir, 'inverted_index.json')
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(dict(self.index), f, ensure_ascii=False, indent=2)

        # Save IDF scores
        idf_file = os.path.join(output_dir, 'idf.json')
        with open(idf_file, 'w', encoding='utf-8') as f:
            json.dump(self.idf, f, ensure_ascii=False, indent=2)

        # Save document lengths
        lengths_file = os.path.join(output_dir, 'doc_lengths.json')
        with open(lengths_file, 'w', encoding='utf-8') as f:
            json.dump(self.doc_lengths, f, ensure_ascii=False, indent=2)

        # Save document info
        info_file = os.path.join(output_dir, 'doc_info.json')
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(self.doc_info, f, ensure_ascii=False, indent=2)

        print(f"Index saved to {output_dir}")
        print(f"Total terms: {len(self.index)}")
        print(f"Total documents: {self.total_docs}")


def build_index():
    """Build inverted index from crawled pages."""
    print("Building inverted index...")

    index = InvertedIndex()
    crawled_dir = config.CRAWLED_PAGES_DIR

    if not os.path.exists(crawled_dir):
        print(f"Error: Crawled pages directory not found: {crawled_dir}")
        print("Please run crawler.py first.")
        return

    # Get all JSON files
    files = [f for f in os.listdir(crawled_dir) if f.endswith('.json') and f != 'link_graph.json']

    if not files:
        print(f"Error: No crawled pages found in {crawled_dir}")
        return

    print(f"Found {len(files)} crawled pages")

    # Process each page
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(crawled_dir, filename)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)

            doc_id = page_data['url_id']
            url = page_data['url']
            html = page_data['html']

            index.add_document(doc_id, url, html)

            if i % 50 == 0:
                print(f"Processed {i}/{len(files)} pages...")

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Save index
    index.save(config.INDEX_DIR)
    print("Indexing complete!")


def main():
    """Run the indexer."""
    build_index()


if __name__ == '__main__':
    main()
