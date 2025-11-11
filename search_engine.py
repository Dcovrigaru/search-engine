"""
Search Engine: Core search functionality with combined ranking.
"""

import os
import json
import math
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import config


class SearchEngine:
    """Search engine with vector space model and PageRank ranking."""

    def __init__(self):
        self.index = {}
        self.idf = {}
        self.doc_lengths = {}
        self.doc_info = {}
        self.pagerank = {}
        self.stop_words = set(stopwords.words(config.STOP_WORDS_LANGUAGE))
        self.loaded = False

    def load_index(self):
        """Load inverted index and related data."""
        index_dir = config.INDEX_DIR

        if not os.path.exists(index_dir):
            raise FileNotFoundError(f"Index directory not found: {index_dir}")

        # Load inverted index
        index_file = os.path.join(index_dir, 'inverted_index.json')
        with open(index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)

        # Load IDF scores
        idf_file = os.path.join(index_dir, 'idf.json')
        with open(idf_file, 'r', encoding='utf-8') as f:
            self.idf = json.load(f)

        # Load document lengths
        lengths_file = os.path.join(index_dir, 'doc_lengths.json')
        with open(lengths_file, 'r', encoding='utf-8') as f:
            self.doc_lengths = json.load(f)

        # Load document info
        info_file = os.path.join(index_dir, 'doc_info.json')
        with open(info_file, 'r', encoding='utf-8') as f:
            self.doc_info = json.load(f)

        # Load PageRank scores
        pagerank_file = os.path.join(index_dir, 'pagerank.json')
        with open(pagerank_file, 'r', encoding='utf-8') as f:
            self.pagerank = json.load(f)

        self.loaded = True
        print(f"Loaded index: {len(self.index)} terms, {len(self.doc_info)} documents")

    def tokenize_query(self, query):
        """Tokenize and normalize query."""
        # Convert to lowercase
        query = query.lower()

        # Tokenize
        tokens = word_tokenize(query)

        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            # Keep only alphabetic tokens
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

    def calculate_cosine_similarity(self, query_tokens):
        """Calculate cosine similarity scores for all documents."""
        # Calculate query term frequencies
        query_tf = defaultdict(int)
        for token in query_tokens:
            query_tf[token] += 1

        # Calculate query vector with TF-IDF weights
        query_vector = {}
        query_length = 0.0

        for term, tf in query_tf.items():
            if term in self.idf:
                weight = tf * self.idf[term]
                query_vector[term] = weight
                query_length += weight ** 2

        if query_length == 0:
            return {}

        query_length = math.sqrt(query_length)

        # Normalize query vector
        for term in query_vector:
            query_vector[term] /= query_length

        # Calculate similarity for each document
        scores = {}

        for term, q_weight in query_vector.items():
            if term not in self.index:
                continue

            postings = self.index[term]
            idf = self.idf[term]

            for doc_id, tf in postings.items():
                # Calculate TF-IDF weight for document
                d_weight = tf * idf

                # Normalize by document length
                if doc_id in self.doc_lengths and self.doc_lengths[doc_id] > 0:
                    d_weight /= self.doc_lengths[doc_id]

                # Add to similarity score
                if doc_id not in scores:
                    scores[doc_id] = 0.0
                scores[doc_id] += q_weight * d_weight

        return scores

    def normalize_scores(self, scores):
        """Normalize scores to [0, 1] range."""
        if not scores:
            return {}

        min_score = min(scores.values())
        max_score = max(scores.values())

        if max_score - min_score > 0:
            normalized = {}
            for doc_id, score in scores.items():
                normalized[doc_id] = (score - min_score) / (max_score - min_score)
            return normalized
        else:
            # All scores are the same
            return {doc_id: 0.5 for doc_id in scores}

    def combine_scores(self, cosine_scores, pagerank_scores):
        """Combine cosine similarity and PageRank scores."""
        # Normalize cosine scores
        normalized_cosine = self.normalize_scores(cosine_scores)

        # ONLY use documents that match the query (have cosine similarity > 0)
        # This prevents irrelevant pages from appearing just because of high PageRank
        combined = {}
        for doc_id in normalized_cosine.keys():
            cos_score = normalized_cosine[doc_id]
            pr_score = pagerank_scores.get(doc_id, 0.0)

            # Combined score: w1 * cosine + w2 * pagerank
            combined[doc_id] = (
                config.WEIGHT_COSINE * cos_score +
                config.WEIGHT_PAGERANK * pr_score
            )

        return combined

    def search(self, query, top_k=10, min_cosine_threshold=0.01):
        """Search for documents matching the query."""
        if not self.loaded:
            raise RuntimeError("Index not loaded. Call load_index() first.")

        # Tokenize query
        query_tokens = self.tokenize_query(query)

        if not query_tokens:
            return []

        # Calculate cosine similarity scores
        cosine_scores = self.calculate_cosine_similarity(query_tokens)

        if not cosine_scores:
            return []

        # Filter out documents with very low relevance (before normalization)
        # This prevents irrelevant pages from appearing just due to high PageRank
        filtered_cosine_scores = {
            doc_id: score
            for doc_id, score in cosine_scores.items()
            if score >= min_cosine_threshold
        }

        if not filtered_cosine_scores:
            return []

        # Combine with PageRank scores (only for relevant documents)
        final_scores = self.combine_scores(filtered_cosine_scores, self.pagerank)

        # Sort by score
        ranked_docs = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        # Get top-k results
        results = []
        for doc_id, score in ranked_docs[:top_k]:
            if doc_id in self.doc_info:
                result = {
                    'doc_id': doc_id,
                    'url': self.doc_info[doc_id]['url'],
                    'title': self.doc_info[doc_id]['title'],
                    'score': score,
                    'cosine_score': cosine_scores.get(doc_id, 0.0),
                    'pagerank_score': self.pagerank.get(doc_id, 0.0)
                }
                results.append(result)

        return results


def main():
    """Test the search engine."""
    print("Loading search engine...")
    engine = SearchEngine()
    engine.load_index()

    print("\nSearch Engine Ready!")
    print("Enter queries (or 'quit' to exit):\n")

    while True:
        query = input("Query: ").strip()

        if query.lower() in ['quit', 'exit', 'q']:
            break

        if not query:
            continue

        results = engine.search(query, top_k=10)

        print(f"\nFound {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Score: {result['score']:.4f} "
                  f"(Cosine: {result['cosine_score']:.4f}, "
                  f"PageRank: {result['pagerank_score']:.4f})")
            print()


if __name__ == '__main__':
    main()
