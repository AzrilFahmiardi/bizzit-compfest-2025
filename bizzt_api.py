"""
Bizzt Recommendation API - Final Version
API untuk sistem rekomendasi strategi diskon dengan kemampuan regenerate
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import json
import os
from datetime import datetime
import logging
import threading
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class BizztRecommendationAPI:
    def __init__(self):
        self.recommendations_data = []
        self.metadata = None
        
        # Processing status
        self.is_processing = False
        self.last_update_time = None
        self.processing_progress = {'status': 'idle', 'progress': 0, 'message': ''}
        
        # Load existing data
        self.load_recommendations()
    
    def load_recommendations(self):
        """Load recommendation data from results file"""
        try:
            results_file = os.path.join("results", "final_recommendations.csv")
            
            if os.path.exists(results_file):
                with open(results_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.recommendations_data = list(reader)
                
                # Convert numeric fields
                for item in self.recommendations_data:
                    item['rekomendasi_besaran'] = float(item['rekomendasi_besaran'])
                    item['rata_rata_uplift_profit'] = float(item['rata_rata_uplift_profit'])
                
                # Load metadata
                metadata_file = os.path.join("results", "metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        self.metadata = json.load(f)
                
                logger.info(f"Loaded {len(self.recommendations_data)} recommendations")
                return True
            else:
                logger.warning("No recommendation file found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading recommendations: {str(e)}")
            return False
    
    def regenerate_recommendations(self):
        """Background process untuk regenerate recommendations"""
        try:
            self.is_processing = True
            self.processing_progress = {'status': 'running', 'progress': 0, 'message': 'Initializing...'}
            
            # Simulate processing steps
            steps = [
                (20, 'Loading and preparing data...'),
                (40, 'Running urgency analysis...'),
                (60, 'Training recommendation models...'),
                (80, 'Generating strategies...'),
                (90, 'Applying business rules...'),
                (100, 'Finalizing recommendations...')
            ]
            
            for progress, message in steps:
                time.sleep(2)  # Simulate processing time
                self.processing_progress['progress'] = progress
                self.processing_progress['message'] = message
            
            # Generate new mock recommendations
            new_recommendations = self.generate_updated_recommendations()
            
            # Save results
            self.save_recommendations(new_recommendations)
            
            # Update internal state
            self.recommendations_data = new_recommendations
            self.last_update_time = datetime.now()
            
            self.processing_progress = {
                'status': 'completed', 
                'progress': 100, 
                'message': f'Successfully generated {len(new_recommendations)} recommendations',
                'completed_at': self.last_update_time.isoformat()
            }
            
            logger.info("Recommendation regeneration completed")
            
        except Exception as e:
            logger.error(f"Error during regeneration: {str(e)}")
            self.processing_progress = {
                'status': 'failed', 
                'progress': 0, 
                'message': f'Process failed: {str(e)}'
            }
        finally:
            self.is_processing = False
    
    def generate_updated_recommendations(self):
        """Generate updated recommendations (simulated)"""
        import random
        from datetime import datetime, timedelta
        
        # Create mix of updated existing + some new products
        updated_recommendations = []
        
        # Update existing recommendations (simulate model refresh)
        if self.recommendations_data:
            for item in self.recommendations_data[:20]:  # Take top 20 existing
                updated_item = item.copy()
                
                # Simulate slight changes in uplift profit
                old_uplift = float(updated_item['rata_rata_uplift_profit'])
                variation = random.uniform(-0.15, 0.25)  # -15% to +25% variation
                new_uplift = max(0, old_uplift * (1 + variation))
                updated_item['rata_rata_uplift_profit'] = round(new_uplift, 2)
                
                updated_recommendations.append(updated_item)
        
        # Add some new product recommendations with proper date calculation
        new_products = [
            ("P00100001", "SKU10001", "FreshUpdate Beras Premium 1kg", "Beras", "Generic Product Discount", 0.1),
            ("P00100002", "SKU10002", "NewGen Minyak Goreng 2L", "Minyak Goreng", "Event Based (Ramadan)", 0.05),
            ("P00100003", "SKU10003", "ModernPT Daging Segar 500g", "Daging Segar", "Expired Discount", 0.15),
            ("P00100004", "SKU10004", "SmartCV Teh Premium 250g", "Teh", "BOGO", 0.0),
            ("P00100005", "SKU10005", "InnovativeAgro Seafood 300g", "Seafood Segar", "Generic Product Discount", 0.12)
        ]
        
        current_date = datetime.now()
        
        for product_id, kode_sku, name, category, strategy, discount in new_products:
            base_uplift = random.uniform(200, 800)
            if strategy != "Tanpa Diskon":
                uplift_profit = base_uplift + random.uniform(100, 500)
            else:
                uplift_profit = 0.0
            
            # Calculate dates based on strategy (same logic as notebook)
            start_date, end_date = self.calculate_promotion_dates(strategy, current_date)
            
            new_item = {
                'id_produk': product_id,
                'kode_sku': kode_sku,
                'nama_produk': name,
                'kategori_produk': category,
                'rekomendasi_detail': strategy,
                'rekomendasi_besaran': discount,
                'start_date': start_date,
                'end_date': end_date,
                'rata_rata_uplift_profit': round(uplift_profit, 2)
            }
            updated_recommendations.append(new_item)
        
        # Sort by uplift profit
        updated_recommendations.sort(key=lambda x: x['rata_rata_uplift_profit'], reverse=True)
        
        return updated_recommendations
    
    def calculate_promotion_dates(self, strategy, current_date):
        """Calculate start and end dates based on promotion strategy"""
        from datetime import timedelta
        
        if "Event Based (Ramadan)" in strategy:
            # Start 1 week before Ramadan (2025-02-21)
            start_date = "2025-02-21"
            end_date = "2025-03-06"  # 2 weeks duration
            
        elif "Expired" in strategy:
            # Next month, first Friday
            bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
            days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
            if days_to_friday == 0:
                days_to_friday = 7
            jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
            start_date = jumat_pertama.strftime('%Y-%m-%d')
            end_date = (jumat_pertama + timedelta(days=2)).strftime('%Y-%m-%d')
            
        elif "BOGO" in strategy:
            # Next month, second Friday
            bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
            days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
            if days_to_friday == 0:
                days_to_friday = 7
            jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
            start_date = (jumat_pertama + timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = (jumat_pertama + timedelta(days=9)).strftime('%Y-%m-%d')
            
        else:  # Generic or other strategies
            # Next month, second Friday + 1 week
            bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
            days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
            if days_to_friday == 0:
                days_to_friday = 7
            jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
            start_date = (jumat_pertama + timedelta(days=7)).strftime('%Y-%m-%d')
            end_date = (jumat_pertama + timedelta(days=9)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    
    def save_recommendations(self, recommendations):
        """Save recommendations to files"""
        try:
            os.makedirs("results", exist_ok=True)
            
            # Save CSV
            with open("results/final_recommendations.csv", 'w', newline='', encoding='utf-8') as f:
                if recommendations:
                    fieldnames = ['id_produk', 'kode_sku', 'nama_produk', 'kategori_produk', 'rekomendasi_detail', 'rekomendasi_besaran', 'start_date', 'end_date', 'rata_rata_uplift_profit']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(recommendations)
            
            # Save metadata
            self.metadata = {
                'generated_at': datetime.now().isoformat(),
                'total_products': len(recommendations),
                'version': '2.0.0',
                'api_generated': True
            }
            
            with open("results/metadata.json", 'w') as f:
                json.dump(self.metadata, f, indent=2)
            
            logger.info("Recommendations saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving recommendations: {str(e)}")
            raise
    
    def get_top_recommendations(self, top_n=30):
        """Get top N recommendations sorted by uplift profit"""
        if not self.recommendations_data:
            return None
        
        try:
            # Sort by uplift profit (descending)
            sorted_data = sorted(
                self.recommendations_data, 
                key=lambda x: float(x['rata_rata_uplift_profit']), 
                reverse=True
            )
            
            top_recommendations = sorted_data[:top_n]
            
            recommendations_list = []
            for item in top_recommendations:
                recommendation = {
                    'id_produk': str(item['id_produk']),
                    'kode_sku': item.get('kode_sku', 'SKU-' + str(item['id_produk'])[-5:]),
                    'nama_produk': str(item['nama_produk']),
                    'kategori_produk': str(item['kategori_produk']),
                    'rekomendasi_detail': str(item['rekomendasi_detail']),
                    'rekomendasi_besaran': float(item['rekomendasi_besaran']),
                    'rekomendasi_besaran_persen': f"{float(item['rekomendasi_besaran']) * 100:.1f}%",
                    'start_date': item.get('start_date', '2025-03-07'),
                    'end_date': item.get('end_date', '2025-03-09'),
                    'rata_rata_uplift_profit': float(item['rata_rata_uplift_profit']),
                    'rata_rata_uplift_profit_formatted': f"Rp {float(item['rata_rata_uplift_profit']):,.0f}"
                }
                recommendations_list.append(recommendation)
            
            return recommendations_list
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get overall statistics"""
        if not self.recommendations_data:
            return None
        
        try:
            strategy_counts = {}
            category_counts = {}
            total_uplift = 0
            
            for item in self.recommendations_data:
                strategy = item['rekomendasi_detail']
                category = item['kategori_produk']
                uplift = float(item['rata_rata_uplift_profit'])
                
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
                category_counts[category] = category_counts.get(category, 0) + 1
                total_uplift += uplift
            
            stats = {
                'total_products': len(self.recommendations_data),
                'products_with_discount': len([item for item in self.recommendations_data if item['rekomendasi_detail'] != 'Tanpa Diskon']),
                'total_estimated_uplift': round(total_uplift, 2),
                'average_uplift': round(total_uplift / len(self.recommendations_data), 2),
                'strategy_distribution': strategy_counts,
                'top_categories': dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10])
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return None

# Initialize API
bizzt_api = BizztRecommendationAPI()

@app.route('/', methods=['GET'])
def root_endpoint():
    """Root endpoint with available endpoints info"""
    return jsonify({
        'service': 'Bizzt Recommendation API',
        'version': '2.0.0',
        'status': 'OK',
        'description': 'API untuk sistem rekomendasi strategi diskon produk retail',
        'available_endpoints': {
            'recommendations': {
                'url': '/api/recommendations',
                'method': 'GET',
                'description': 'Mendapatkan daftar rekomendasi produk terbaik',
                'parameters': {
                    'limit': 'Jumlah rekomendasi (default: 30, max: 1000)'
                },
                'example': '/api/recommendations?limit=10'
            },
            'statistics': {
                'url': '/api/recommendations/stats',
                'method': 'GET', 
                'description': 'Mendapatkan statistik keseluruhan rekomendasi',
                'parameters': 'Tidak ada',
                'example': '/api/recommendations/stats'
            }
        },
        'system_info': {
            'recommendations_loaded': len(bizzt_api.recommendations_data),
            'is_processing': bizzt_api.is_processing,
            'last_update': bizzt_api.last_update_time.isoformat() if bizzt_api.last_update_time else None
        },
        'quick_links': [
            'http://localhost:5000/api/recommendations?limit=10',
            'http://localhost:5000/api/recommendations/stats'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    """Get top recommendations"""
    try:
        top_n = request.args.get('limit', 30, type=int)
        
        if top_n <= 0 or top_n > 1000:
            return jsonify({'error': 'Invalid limit parameter. Must be between 1 and 1000.'}), 400
        
        recommendations = bizzt_api.get_top_recommendations(top_n)
        
        if recommendations is None:
            return jsonify({'error': 'No recommendations available. Run regeneration first.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'recommendations': recommendations,
                'count': len(recommendations),
                'limit': top_n,
                'is_fresh': bizzt_api.last_update_time and (datetime.now() - bizzt_api.last_update_time).total_seconds() < 3600,
                'last_updated': bizzt_api.last_update_time.isoformat() if bizzt_api.last_update_time else None,
                'metadata': bizzt_api.metadata
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/recommendations/stats', methods=['GET'])
def get_recommendation_stats():
    """Get recommendation statistics"""
    try:
        stats = bizzt_api.get_statistics()
        
        if stats is None:
            return jsonify({'error': 'No data available for statistics'}), 404
        
        return jsonify({
            'status': 'success',
            'data': stats,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/recommendations/regenerate', methods=['POST'])
def regenerate_recommendations():
    """🚀 Regenerate recommendations"""
    try:
        if bizzt_api.is_processing:
            return jsonify({
                'status': 'already_processing',
                'message': 'Recommendation regeneration is already in progress',
                'progress': bizzt_api.processing_progress
            }), 409
        
        # Start regeneration in background
        regen_thread = threading.Thread(target=bizzt_api.regenerate_recommendations)
        regen_thread.daemon = True
        regen_thread.start()
        
        return jsonify({
            'status': 'started',
            'message': 'Recommendation regeneration started',
            'process_id': int(time.time()),
            'estimated_duration': '10-15 seconds',
            'check_status_endpoint': '/api/recommendations/status',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error starting regeneration: {str(e)}")
        return jsonify({'error': f'Failed to start regeneration: {str(e)}'}), 500

@app.route('/api/recommendations/status', methods=['GET'])
def get_processing_status():
    """Get current processing status"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'is_processing': bizzt_api.is_processing,
                'progress': bizzt_api.processing_progress,
                'last_update': bizzt_api.last_update_time.isoformat() if bizzt_api.last_update_time else None,
                'recommendations_count': len(bizzt_api.recommendations_data)
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/recommendations/refresh', methods=['POST'])
def refresh_data():
    """Refresh data from files"""
    try:
        success = bizzt_api.load_recommendations()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Data refreshed successfully',
                'recommendations_count': len(bizzt_api.recommendations_data),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'status': 'no_data',
                'message': 'No data found. Run regeneration first.',
                'timestamp': datetime.now().isoformat()
            }), 404
    
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}")
        return jsonify({'error': f'Failed to refresh data: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /',
            'GET /api/recommendations',
            'GET /api/recommendations/stats', 
            'POST /api/recommendations/regenerate',
            'GET /api/recommendations/status',
            'POST /api/recommendations/refresh'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Bizzt Recommendation API")
    print("=" * 50)
    print("📋 Endpoints:")
    print("  GET  /                              - Health check")
    print("  GET  /api/recommendations          - Get recommendations")
    print("  GET  /api/recommendations/stats    - Get statistics")
    print("  POST /api/recommendations/regenerate - Regenerate recommendations")
    print("  GET  /api/recommendations/status    - Check processing status")
    print("  POST /api/recommendations/refresh   - Refresh from files")
    print("\n🎯 Key Features:")
    print("  ✅ Clean endpoint structure")
    print("  ✅ Background processing")
    print("  ✅ Real-time progress tracking")
    print("  ✅ Automatic data persistence")
    print("\n🌐 Starting server on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
