"""
PageRank algorithm implementation.
"""

import os
import json
import hashlib
from collections import defaultdict
import config


class PageRank:
    """Compute PageRank scores for web pages."""

    def __init__(self, damping=0.85, iterations=20):
        self.damping = damping
        self.iterations = iterations
        self.graph = defaultdict(list)  # url -> [outgoing_urls]
        self.pagerank = {}
        self.url_to_id = {}
        self.id_to_url = {}

    def get_url_id(self, url):
        """Generate a unique ID for a URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def load_graph(self, graph_file):
        """Load link graph from crawled data."""
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)

        # Build graph and URL mappings
        all_urls = set()
        for source_url, target_urls in graph_data.items():
            all_urls.add(source_url)
            all_urls.update(target_urls)

        # Create URL to ID mappings
        for url in all_urls:
            url_id = self.get_url_id(url)
            self.url_to_id[url] = url_id
            self.id_to_url[url_id] = url

        # Build adjacency list
        for source_url, target_urls in graph_data.items():
            source_id = self.url_to_id[source_url]
            target_ids = [self.url_to_id[url] for url in target_urls if url in self.url_to_id]
            self.graph[source_id] = target_ids

        return len(all_urls)

    def compute(self):
        """Compute PageRank scores using power iteration."""
        n = len(self.url_to_id)

        if n == 0:
            print("Error: No URLs found in graph")
            return

        # Initialize PageRank scores
        initial_pr = 1.0 / n
        for url_id in self.id_to_url.keys():
            self.pagerank[url_id] = initial_pr

        # Build reverse graph (incoming links)
        incoming = defaultdict(list)
        for source_id, target_ids in self.graph.items():
            for target_id in target_ids:
                incoming[target_id].append(source_id)

        # Count outgoing links
        outgoing_count = {}
        for url_id in self.id_to_url.keys():
            count = len(self.graph.get(url_id, []))
            outgoing_count[url_id] = count if count > 0 else 1  # Avoid division by zero

        # Power iteration
        print(f"Computing PageRank ({self.iterations} iterations)...")
        for iteration in range(self.iterations):
            new_pagerank = {}

            for url_id in self.id_to_url.keys():
                # Random surfer component
                rank = (1 - self.damping) / n

                # Link-based component
                link_sum = 0.0
                for source_id in incoming.get(url_id, []):
                    link_sum += self.pagerank[source_id] / outgoing_count[source_id]

                rank += self.damping * link_sum
                new_pagerank[url_id] = rank

            self.pagerank = new_pagerank

            if (iteration + 1) % 5 == 0:
                print(f"  Iteration {iteration + 1}/{self.iterations}")

        print("PageRank computation complete!")

    def normalize_scores(self):
        """Normalize PageRank scores to [0, 1] range."""
        if not self.pagerank:
            return

        min_score = min(self.pagerank.values())
        max_score = max(self.pagerank.values())

        if max_score - min_score > 0:
            for url_id in self.pagerank:
                self.pagerank[url_id] = (self.pagerank[url_id] - min_score) / (max_score - min_score)
        else:
            # All scores are the same, set to 0.5
            for url_id in self.pagerank:
                self.pagerank[url_id] = 0.5

    def save(self, output_dir):
        """Save PageRank scores to disk."""
        os.makedirs(output_dir, exist_ok=True)

        # Normalize before saving
        self.normalize_scores()

        pagerank_file = os.path.join(output_dir, 'pagerank.json')
        with open(pagerank_file, 'w', encoding='utf-8') as f:
            json.dump(self.pagerank, f, ensure_ascii=False, indent=2)

        print(f"PageRank scores saved to {pagerank_file}")

        # Print statistics
        scores = list(self.pagerank.values())
        print(f"Total pages: {len(scores)}")
        print(f"Min score: {min(scores):.6f}")
        print(f"Max score: {max(scores):.6f}")
        print(f"Avg score: {sum(scores) / len(scores):.6f}")


def compute_pagerank():
    """Compute PageRank from crawled link graph."""
    graph_file = os.path.join(config.CRAWLED_PAGES_DIR, 'link_graph.json')

    if not os.path.exists(graph_file):
        print(f"Error: Link graph not found: {graph_file}")
        print("Please run crawler.py first.")
        return

    print("Loading link graph...")
    pr = PageRank(damping=config.PAGERANK_DAMPING, iterations=config.PAGERANK_ITERATIONS)
    num_urls = pr.load_graph(graph_file)
    print(f"Loaded {num_urls} URLs")

    pr.compute()
    pr.save(config.INDEX_DIR)


def main():
    """Run PageRank computation."""
    compute_pagerank()


if __name__ == '__main__':
    main()
