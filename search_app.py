"""
Flask web application for the search engine.
"""

from flask import Flask, render_template, request, jsonify
from search_engine import SearchEngine
import config

app = Flask(__name__, template_folder=config.TEMPLATES_DIR)

# Initialize search engine
search_engine = SearchEngine()

try:
    search_engine.load_index()
    print("Search engine loaded successfully!")
except Exception as e:
    print(f"Error loading search engine: {e}")
    print("Please run indexer.py and pagerank.py first.")


@app.route('/')
def index():
    """Render the search page."""
    return render_template('search.html')


@app.route('/search', methods=['GET'])
def search():
    """Handle search queries."""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'No query provided'}), 400

    try:
        results = search_engine.search(query, top_k=config.RESULTS_PER_PAGE)

        return jsonify({
            'query': query,
            'num_results': len(results),
            'results': results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'index_loaded': search_engine.loaded,
        'num_documents': len(search_engine.doc_info) if search_engine.loaded else 0,
        'num_terms': len(search_engine.index) if search_engine.loaded else 0
    })


def main():
    """Run the Flask application."""
    print(f"Starting search engine web interface...")
    print(f"Open your browser to http://localhost:{config.FLASK_PORT}")

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=True
    )


if __name__ == '__main__':
    main()
