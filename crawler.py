"""
Web Crawler using Scrapy.

This module implements a web crawler using the Scrapy framework to crawl
educational CS content from specified domains. Crawled pages are saved as
JSON files for later indexing.

Usage:
    python3 crawler.py
"""

import os
import json
import hashlib
from urllib.parse import urlparse
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import config


class WebSpider(CrawlSpider):
    """
    Scrapy spider for crawling web pages.
    """
    name = 'web_spider'

    def __init__(self, *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)
        self.start_urls = config.SEED_URLS
        self.allowed_domains = config.ALLOWED_DOMAINS if config.ALLOWED_DOMAINS else []
        self.pages_crawled = 0
        self.max_pages = config.MAX_PAGES
        self.output_dir = config.CRAWLED_PAGES_DIR
        self.graph_data = {}

        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)

        # Setup link extraction rules
        self.rules = (
            Rule(
                LinkExtractor(),
                callback='parse_page',
                follow=True
            ),
        )
        super(WebSpider, self)._compile_rules()

    def get_url_id(self, url):
        """Generate a unique ID for a URL."""
        return hashlib.md5(url.encode()).hexdigest()

    def parse_start_url(self, response):
        """Parse seed URLs."""
        return self.parse_page(response)

    def parse_page(self, response):
        """Parse and save a page."""
        if self.pages_crawled >= self.max_pages:
            raise scrapy.exceptions.CloseSpider('max_pages_reached')

        # Only process HTML
        if 'text/html' not in response.headers.get('Content-Type', b'').decode('utf-8'):
            return

        url = response.url
        url_id = self.get_url_id(url)

        # Extract all links
        links = []
        for link in response.css('a::attr(href)').getall():
            absolute_url = response.urljoin(link)
            # Remove fragments
            absolute_url = absolute_url.split('#')[0]
            links.append(absolute_url)

        # Save page data
        page_data = {
            'url': url,
            'url_id': url_id,
            'html': response.text,
            'links': links,
            'timestamp': response.headers.get('Date', b'').decode('utf-8', errors='ignore')
        }

        file_path = os.path.join(self.output_dir, f"{url_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, ensure_ascii=False, indent=2)

        # Store graph data
        self.graph_data[url] = links

        self.pages_crawled += 1
        self.logger.info(f'Crawled [{self.pages_crawled}/{self.max_pages}]: {url}')

    def closed(self, reason):
        """Save graph data when spider closes."""
        graph_file = os.path.join(self.output_dir, 'link_graph.json')
        with open(graph_file, 'w', encoding='utf-8') as f:
            json.dump(self.graph_data, f, ensure_ascii=False, indent=2)
        self.logger.info(f'Crawling complete! Pages crawled: {self.pages_crawled}')


def main():
    """Run the Scrapy crawler."""
    print("Starting web crawl with Scrapy...")
    print(f"Target: {config.MAX_PAGES} pages")
    print(f"Seed URLs: {len(config.SEED_URLS)}")
    print("-" * 60)

    # Configure Scrapy
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': False,  # For educational purposes
        'CONCURRENT_REQUESTS': 1,  # Politeness
        'DOWNLOAD_DELAY': config.CRAWL_DELAY,
        'DEPTH_LIMIT': config.MAX_DEPTH,
        'LOG_LEVEL': 'INFO',
        'CLOSESPIDER_PAGECOUNT': config.MAX_PAGES,
    })

    process.crawl(WebSpider)
    process.start()

    print("-" * 60)
    print(f"Output directory: {config.CRAWLED_PAGES_DIR}")


if __name__ == '__main__':
    main()
