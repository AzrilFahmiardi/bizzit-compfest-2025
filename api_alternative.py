"""
Alternative API untuk Sistem Rekomendasi Strategi Diskon Bizzt
Version tanpa pandas untuk menghindari dependency conflicts
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import csv
import os
from datetime import datetime
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
RESULTS_DIR = "results"
FINAL_RECOMMENDATIONS_FILE = os.path.join(RESULTS_DIR, "final_recommendations.csv")
METADATA_FILE = os.path.join(RESULTS_DIR, "metadata.json")
SUMMARY_FILE = os.path.join(RESULTS_DIR, "recommendation_summary.json")

class RecommendationAPI:
    def __init__(self):
        self.recommendations_data = []
        self.metadata = None
        self.summary = None
        self.load_data()
    
    def load_data(self):
        """Load recommendation data from CSV file without pandas"""
        try:
            # Load main recommendations from CSV
            if os.path.exists(FINAL_RECOMMENDATIONS_FILE):
                with open(FINAL_RECOMMENDATIONS_FILE, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    self.recommendations_data = []
                    
                    for row in csv_reader:
                        # Convert numeric fields
                        try:
                            row['rekomendasi_besaran'] = float(row['rekomendasi_besaran'])
                            row['rata_rata_uplift_profit'] = float(row['rata_rata_uplift_profit'])
                        except (ValueError, KeyError):
                            # Skip rows with invalid data
                            continue
                        
                        self.recommendations_data.append(row)
                
                # Sort by rata_rata_uplift_profit (descending)
                self.recommendations_data.sort(
                    key=lambda x: x['rata_rata_uplift_profit'], 
                    reverse=True
                )
                
                logger.info(f"Loaded {len(self.recommendations_data)} recommendations")
            else:
                logger.error(f"Recommendations file not found: {FINAL_RECOMMENDATIONS_FILE}")
                return False
            
            # Load metadata
            if os.path.exists(METADATA_FILE):
                with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info("Loaded metadata")
            
            # Load summary
            if os.path.exists(SUMMARY_FILE):
                with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
                    self.summary = json.load(f)
                logger.info("Loaded summary")
            
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def get_top_recommendations(self, top_n=30):
        """Get top N recommendations sorted by uplift profit"""
        if not self.recommendations_data:
            return None
        
        try:
            # Take top N (data already sorted)
            top_recommendations = self.recommendations_data[:top_n]
            
            # Format for API response
            recommendations_list = []
            for row in top_recommendations:
                recommendation = {
                    'id_produk': str(row['id_produk']),
                    'nama_produk': str(row['nama_produk']),
                    'kategori_produk': str(row['kategori_produk']),
                    'rekomendasi_detail': str(row['rekomendasi_detail']),
                    'rekomendasi_besaran': float(row['rekomendasi_besaran']),
                    'rekomendasi_besaran_persen': f"{float(row['rekomendasi_besaran']) * 100:.1f}%",
                    'rata_rata_uplift_profit': float(row['rata_rata_uplift_profit']),
                    'rata_rata_uplift_profit_formatted': f"Rp {float(row['rata_rata_uplift_profit']):,.0f}"
                }
                recommendations_list.append(recommendation)
            
            return recommendations_list
        except Exception as e:
            logger.error(f"Error getting top recommendations: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get overall statistics"""
        if not self.recommendations_data:
            return None
        
        try:
            total_products = len(self.recommendations_data)
            
            # Count products with discount (not "Tanpa Diskon")
            products_with_discount = sum(
                1 for item in self.recommendations_data 
                if item['rekomendasi_detail'] != 'Tanpa Diskon'
            )
            
            # Calculate total and average uplift
            total_uplift = sum(
                float(item['rata_rata_uplift_profit']) 
                for item in self.recommendations_data
            )
            average_uplift = total_uplift / total_products if total_products > 0 else 0
            
            # Strategy distribution
            strategy_dist = {}
            category_dist = {}
            
            for item in self.recommendations_data:
                strategy = item['rekomendasi_detail']
                category = item['kategori_produk']
                
                strategy_dist[strategy] = strategy_dist.get(strategy, 0) + 1
                category_dist[category] = category_dist.get(category, 0) + 1
            
            # Get top 10 categories
            top_categories = dict(
                sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:10]
            )
            
            stats = {
                'total_products': total_products,
                'products_with_discount': products_with_discount,
                'total_estimated_uplift': total_uplift,
                'average_uplift': average_uplift,
                'strategy_distribution': strategy_dist,
                'category_distribution': top_categories
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return None
    
    def get_recommendations_by_category(self, category_filter: str, top_n: int = 30):
        """Get recommendations filtered by category"""
        if not self.recommendations_data:
            return None
        
        try:
            # Filter by category (case-insensitive partial match)
            filtered_data = [
                item for item in self.recommendations_data 
                if category_filter.lower() in item['kategori_produk'].lower()
            ]
            
            # Take top N from filtered data
            top_filtered = filtered_data[:top_n]
            
            # Format for API response
            recommendations_list = []
            for row in top_filtered:
                recommendation = {
                    'id_produk': str(row['id_produk']),
                    'nama_produk': str(row['nama_produk']),
                    'kategori_produk': str(row['kategori_produk']),
                    'rekomendasi_detail': str(row['rekomendasi_detail']),
                    'rekomendasi_besaran': float(row['rekomendasi_besaran']),
                    'rekomendasi_besaran_persen': f"{float(row['rekomendasi_besaran']) * 100:.1f}%",
                    'rata_rata_uplift_profit': float(row['rata_rata_uplift_profit']),
                    'rata_rata_uplift_profit_formatted': f"Rp {float(row['rata_rata_uplift_profit']):,.0f}"
                }
                recommendations_list.append(recommendation)
            
            return recommendations_list
        except Exception as e:
            logger.error(f"Error filtering by category: {str(e)}")
            return None

# Initialize API
recommendation_api = RecommendationAPI()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Bizzt Recommendation API is running (pandas-free version)',
        'timestamp': datetime.now().isoformat(),
        'version': '1.1.0',
        'total_products': len(recommendation_api.recommendations_data)
    })

@app.route('/api/recommendations/top', methods=['GET'])
def get_top_recommendations():
    """Get top N recommendations (default 30)"""
    try:
        # Get query parameters
        top_n = request.args.get('top_n', 30, type=int)
        
        # Validate top_n
        if top_n <= 0 or top_n > 1000:
            return jsonify({
                'error': 'Invalid top_n parameter. Must be between 1 and 1000.'
            }), 400
        
        # Get recommendations
        recommendations = recommendation_api.get_top_recommendations(top_n)
        
        if recommendations is None:
            return jsonify({
                'error': 'Failed to load recommendations'
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'total_returned': len(recommendations),
                'requested_count': top_n,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_top_recommendations: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/recommendations/stats', methods=['GET'])
def get_statistics():
    """Get overall recommendation statistics"""
    try:
        stats = recommendation_api.get_statistics()
        
        if stats is None:
            return jsonify({
                'error': 'Failed to load statistics'
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': {
                'statistics': stats,
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_statistics: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/recommendations/category/<category>', methods=['GET'])
def get_recommendations_by_category(category):
    """Get recommendations filtered by category"""
    try:
        top_n = request.args.get('top_n', 30, type=int)
        
        if top_n <= 0 or top_n > 1000:
            return jsonify({
                'error': 'Invalid top_n parameter. Must be between 1 and 1000.'
            }), 400
        
        recommendations = recommendation_api.get_recommendations_by_category(category, top_n)
        
        if recommendations is None:
            return jsonify({
                'error': 'Failed to load recommendations'
            }), 500
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'category_filter': category,
                'total_returned': len(recommendations),
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_recommendations_by_category: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    """Get system metadata"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'metadata': recommendation_api.metadata,
                'summary': recommendation_api.summary,
                'api_info': {
                    'version': '1.1.0',
                    'type': 'pandas-free',
                    'total_products_loaded': len(recommendation_api.recommendations_data),
                    'endpoints': [
                        '/api/recommendations/top',
                        '/api/recommendations/stats',
                        '/api/recommendations/category/<category>',
                        '/api/metadata'
                    ]
                },
                'timestamp': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_metadata: {str(e)}")
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/',
            '/api/recommendations/top',
            '/api/recommendations/stats',
            '/api/recommendations/category/<category>',
            '/api/metadata'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    # Check if data files exist
    if not os.path.exists(FINAL_RECOMMENDATIONS_FILE):
        print(f"ERROR: Recommendations file not found: {FINAL_RECOMMENDATIONS_FILE}")
        print("Please ensure the recommendation system has been run and results are available.")
        exit(1)
    
    print("Starting Bizzt Recommendation API (Pandas-Free Version)...")
    print(f"Loaded {len(recommendation_api.recommendations_data)} products")
    print("Available endpoints:")
    print("  - GET / (health check)")
    print("  - GET /api/recommendations/top?top_n=30 (top recommendations)")
    print("  - GET /api/recommendations/stats (statistics)")
    print("  - GET /api/recommendations/category/<category> (by category)")
    print("  - GET /api/metadata (system metadata)")
    print("\nRunning on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
