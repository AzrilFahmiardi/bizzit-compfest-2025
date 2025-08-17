"""
API untuk Sistem Rekomendasi Strategi Diskon Bizzt
Mengirimkan top 30 rekomendasi produk berdasarkan uplift profit
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime
import logging

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
        self.recommendations_df = None
        self.metadata = None
        self.summary = None
        self.load_data()
    
    def load_data(self):
        """Load recommendation data from files"""
        try:
            # Load main recommendations
            if os.path.exists(FINAL_RECOMMENDATIONS_FILE):
                self.recommendations_df = pd.read_csv(FINAL_RECOMMENDATIONS_FILE)
                logger.info(f"Loaded {len(self.recommendations_df)} recommendations")
            else:
                logger.error(f"Recommendations file not found: {FINAL_RECOMMENDATIONS_FILE}")
                return False
            
            # Load metadata
            if os.path.exists(METADATA_FILE):
                with open(METADATA_FILE, 'r') as f:
                    self.metadata = json.load(f)
                logger.info("Loaded metadata")
            
            # Load summary
            if os.path.exists(SUMMARY_FILE):
                with open(SUMMARY_FILE, 'r') as f:
                    self.summary = json.load(f)
                logger.info("Loaded summary")
            
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def get_top_recommendations(self, top_n=30):
        """Get top N recommendations sorted by uplift profit"""
        if self.recommendations_df is None:
            return None
        
        try:
            # Sort by rata_rata_uplift_profit in descending order
            top_recommendations = (
                self.recommendations_df
                .sort_values('rata_rata_uplift_profit', ascending=False)
                .head(top_n)
                .copy()
            )
            
            # Convert to list of dictionaries for JSON response
            recommendations_list = []
            for _, row in top_recommendations.iterrows():
                recommendation = {
                    'id_produk': row['id_produk'],
                    'nama_produk': row['nama_produk'],
                    'kategori_produk': row['kategori_produk'],
                    'rekomendasi_detail': row['rekomendasi_detail'],
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
        if self.recommendations_df is None:
            return None
        
        try:
            stats = {
                'total_products': len(self.recommendations_df),
                'products_with_discount': len(self.recommendations_df[
                    self.recommendations_df['rekomendasi_detail'] != 'Tanpa Diskon'
                ]),
                'total_estimated_uplift': float(self.recommendations_df['rata_rata_uplift_profit'].sum()),
                'average_uplift': float(self.recommendations_df['rata_rata_uplift_profit'].mean()),
                'strategy_distribution': self.recommendations_df['rekomendasi_detail'].value_counts().to_dict(),
                'category_distribution': self.recommendations_df['kategori_produk'].value_counts().head(10).to_dict()
            }
            return stats
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return None

# Initialize API
recommendation_api = RecommendationAPI()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'OK',
        'message': 'Bizzt Recommendation API is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
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
        
        if recommendation_api.recommendations_df is None:
            return jsonify({
                'error': 'Failed to load recommendations'
            }), 500
        
        # Filter by category
        category_df = recommendation_api.recommendations_df[
            recommendation_api.recommendations_df['kategori_produk'].str.contains(category, case=False, na=False)
        ].sort_values('rata_rata_uplift_profit', ascending=False).head(top_n)
        
        if category_df.empty:
            return jsonify({
                'status': 'success',
                'data': {
                    'recommendations': [],
                    'total_returned': 0,
                    'message': f'No recommendations found for category: {category}'
                }
            })
        
        # Convert to list
        recommendations = []
        for _, row in category_df.iterrows():
            recommendation = {
                'id_produk': row['id_produk'],
                'nama_produk': row['nama_produk'],
                'kategori_produk': row['kategori_produk'],
                'rekomendasi_detail': row['rekomendasi_detail'],
                'rekomendasi_besaran': float(row['rekomendasi_besaran']),
                'rekomendasi_besaran_persen': f"{float(row['rekomendasi_besaran']) * 100:.1f}%",
                'rata_rata_uplift_profit': float(row['rata_rata_uplift_profit']),
                'rata_rata_uplift_profit_formatted': f"Rp {float(row['rata_rata_uplift_profit']):,.0f}"
            }
            recommendations.append(recommendation)
        
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
                    'version': '1.0.0',
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
    
    print("Starting Bizzt Recommendation API...")
    print("Available endpoints:")
    print("  - GET / (health check)")
    print("  - GET /api/recommendations/top?top_n=30 (top recommendations)")
    print("  - GET /api/recommendations/stats (statistics)")
    print("  - GET /api/recommendations/category/<category> (by category)")
    print("  - GET /api/metadata (system metadata)")
    print("\nRunning on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
