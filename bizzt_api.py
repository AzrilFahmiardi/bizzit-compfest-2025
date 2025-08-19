"""
Bizzt Recommendation API - Final Version
API untuk sistem rekomendasi strategi diskon dengan kemampuan regenerate
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import csv
import json
import os
import pandas as pd
from datetime import datetime
import logging
import threading
import time

# Production environment setup
ENV = os.environ.get('FLASK_ENV', 'development')
DEBUG = ENV != 'production'

# Setup logging untuk production
if ENV == 'production':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class BizztRecommendationAPI:
    def __init__(self):
        self.recommendations_data = []
        self.metadata = None
        self.df_produk = None
        
        # Processing status
        self.is_processing = False
        self.last_update_time = None
        self.processing_progress = {'status': 'idle', 'progress': 0, 'message': ''}
        
        # Load existing data
        self.load_recommendations()
        self.load_product_data()
    
    def load_product_data(self):
        """Load product data for baseline price lookup"""
        try:
            produk_path = os.path.join("data", "produk_v4.csv")
            if os.path.exists(produk_path):
                self.df_produk = pd.read_csv(produk_path)
                logger.info(f"Loaded {len(self.df_produk)} product records for recommendations")
            else:
                logger.warning("Product data file not found")
        except Exception as e:
            logger.error(f"Error loading product data: {str(e)}")
    
    def load_recommendations(self):
        """Load recommendation data from results file"""
        try:
            results_file = os.path.join("results", "final_recommendations.csv")
            
            print(f"DEBUG: Checking file: {results_file}")
            print(f"DEBUG: File exists: {os.path.exists(results_file)}")
            
            if os.path.exists(results_file):
                with open(results_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    self.recommendations_data = list(reader)
                
                print(f"DEBUG: Loaded {len(self.recommendations_data)} recommendations")
                
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
            print(f"DEBUG: Exception loading recommendations: {str(e)}")
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
        print(f"DEBUG: Recommendations data type: {type(self.recommendations_data)}")
        print(f"DEBUG: Recommendations data length: {len(self.recommendations_data) if self.recommendations_data else 'None'}")
        
        if not self.recommendations_data:
            print("DEBUG: No recommendations data available")
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
                # Get baseline price from product data
                harga_baseline = self.get_harga_baseline(item['id_produk'])
                
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
                    'harga_baseline': harga_baseline,
                    'harga_baseline_formatted': f"Rp {harga_baseline:,.0f}" if harga_baseline else "N/A",
                    'rata_rata_uplift_profit': float(item['rata_rata_uplift_profit']),
                    'rata_rata_uplift_profit_formatted': f"Rp {float(item['rata_rata_uplift_profit']):,.0f}"
                }
                recommendations_list.append(recommendation)
            
            return recommendations_list
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return None
    
    def get_harga_baseline(self, id_produk):
        """Get baseline price (harga_jual) for a product by ID"""
        if self.df_produk is None:
            return None
        
        try:
            # Find product by ID
            product_row = self.df_produk[self.df_produk['id_produk'] == id_produk]
            
            if not product_row.empty:
                harga_baseline = product_row['harga_jual'].iloc[0]
                return float(harga_baseline) if pd.notna(harga_baseline) else None
            else:
                logger.warning(f"Product {id_produk} not found in product data")
                return None
                
        except Exception as e:
            logger.error(f"Error getting baseline price for product {id_produk}: {str(e)}")
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

class BizztAnalyticsAPI:
    """
    Analytics API untuk grafik dan tren data transaksi
    """
    def __init__(self):
        self.df_transaksi = None
        self.df_produk = None
        self.df_toko = None
        self.load_data()
    
    def load_data(self):
        """Load transaction and product data"""
        try:
            # Load transaction data
            transaksi_path = os.path.join("data", "transaksi_v4.csv")
            if os.path.exists(transaksi_path):
                self.df_transaksi = pd.read_csv(transaksi_path)
                self.df_transaksi['tanggal_transaksi'] = pd.to_datetime(self.df_transaksi['tanggal_transaksi'])
                logger.info(f"Loaded {len(self.df_transaksi)} transaction records")
            
            # Load product data  
            produk_path = os.path.join("data", "produk_v4.csv")
            if os.path.exists(produk_path):
                self.df_produk = pd.read_csv(produk_path)
                logger.info(f"Loaded {len(self.df_produk)} product records")
            
            # Load store data
            toko_path = os.path.join("data", "toko.csv")
            if os.path.exists(toko_path):
                self.df_toko = pd.read_csv(toko_path)
                logger.info(f"Loaded {len(self.df_toko)} store records")
                
        except Exception as e:
            logger.error(f"Error loading analytics data: {str(e)}")
    
    def get_products_data(self, limit=None, offset=0, kategori=None, brand=None, search=None, id_toko=None):
        """Get raw product data with filtering and pagination"""
        if self.df_produk is None:
            return None
        
        try:
            df = self.df_produk.copy()
            
            # Apply filters
            if kategori:
                df = df[df['kategori_produk'].str.contains(kategori, case=False, na=False)]
            
            if brand:
                df = df[df['brand'].str.contains(brand, case=False, na=False)]
            
            if search:
                df = df[df['nama_produk'].str.contains(search, case=False, na=False)]
            
            if id_toko:
                df = df[df['id_toko'] == int(id_toko)]
            
            # Apply pagination
            total_records = len(df)
            df = df.iloc[offset:]
            
            if limit:
                df = df.head(limit)
            
            # Convert to records
            records = df.to_dict('records')
            
            return {
                'data': records,
                'meta': {
                    'total_records': total_records,
                    'returned_records': len(records),
                    'offset': offset,
                    'limit': limit,
                    'filters': {
                        'kategori': kategori,
                        'brand': brand,
                        'search': search,
                        'id_toko': id_toko
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting products data: {str(e)}")
            return None
    
    def get_stores_data(self, limit=None, offset=0, tipe=None):
        """Get raw store data with filtering and pagination"""
        if self.df_toko is None:
            return None
        
        try:
            df = self.df_toko.copy()
            
            # Apply filters
            if tipe:
                df = df[df['tipe'].str.contains(tipe, case=False, na=False)]
            
            # Apply pagination
            total_records = len(df)
            df = df.iloc[offset:]
            
            if limit:
                df = df.head(limit)
            
            # Convert to records
            records = df.to_dict('records')
            
            return {
                'data': records,
                'meta': {
                    'total_records': total_records,
                    'returned_records': len(records),
                    'offset': offset,
                    'limit': limit,
                    'filters': {
                        'tipe': tipe
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting stores data: {str(e)}")
            return None
    
    def get_weekly_transaction_trend(self):
        """Generate weekly transaction volume trend data"""
        if self.df_transaksi is None:
            return None
        
        try:
            # Group by week and count transactions
            weekly_data = self.df_transaksi.groupby('minggu').size().reset_index(name='jumlah_transaksi')
            
            # Add date range for each week (approximate)
            weekly_data['tahun'] = weekly_data['minggu'].apply(lambda x: 2023 if x <= 52 else 2024 if x <= 104 else 2025)
            weekly_data['minggu_dalam_tahun'] = weekly_data['minggu'].apply(lambda x: x if x <= 52 else (x-52) if x <= 104 else (x-104))
            
            # Convert to chart-ready format
            chart_data = []
            for _, row in weekly_data.iterrows():
                chart_data.append({
                    'week': int(row['minggu']),
                    'week_label': f"Week {int(row['minggu'])}",
                    'year': int(row['tahun']),
                    'week_in_year': int(row['minggu_dalam_tahun']),
                    'transaction_count': int(row['jumlah_transaksi']),
                    'date_label': f"{int(row['tahun'])}-W{int(row['minggu_dalam_tahun']):02d}"
                })
            
            # Calculate trend statistics
            stats = {
                'total_weeks': len(chart_data),
                'total_transactions': int(weekly_data['jumlah_transaksi'].sum()),
                'avg_weekly_transactions': float(weekly_data['jumlah_transaksi'].mean()),
                'min_weekly_transactions': int(weekly_data['jumlah_transaksi'].min()),
                'max_weekly_transactions': int(weekly_data['jumlah_transaksi'].max()),
                'period': {
                    'start_week': int(weekly_data['minggu'].min()),
                    'end_week': int(weekly_data['minggu'].max()),
                    'start_year': 2023,
                    'end_year': 2025
                }
            }
            
            return {
                'chart_data': chart_data,
                'statistics': stats,
                'chart_config': {
                    'chart_type': 'line',
                    'x_axis': 'week',
                    'y_axis': 'transaction_count',
                    'title': 'Volume Transaksi per Minggu (Jan 2023 - Feb 2025)',
                    'x_label': 'Minggu ke-',
                    'y_label': 'Jumlah Transaksi'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating weekly trend: {str(e)}")
            return None
    
    def get_event_analysis(self):
        """Analyze transaction patterns during events"""
        if self.df_transaksi is None:
            return None
        
        try:
            # Group by event and calculate metrics
            event_analysis = self.df_transaksi.groupby('current_event').agg({
                'id_produk': 'count',
                'harga_promosi': 'mean',
                'diskon': 'mean',
                'margin_promosi': 'mean'
            }).reset_index()
            
            event_analysis.columns = ['event', 'transaction_count', 'avg_price', 'avg_discount', 'avg_margin']
            
            # Sort by transaction count
            event_analysis = event_analysis.sort_values('transaction_count', ascending=False)
            
            chart_data = []
            for _, row in event_analysis.iterrows():
                chart_data.append({
                    'event': row['event'],
                    'transaction_count': int(row['transaction_count']),
                    'avg_price': float(row['avg_price']),
                    'avg_discount': float(row['avg_discount']),
                    'avg_margin': float(row['avg_margin']),
                    'avg_discount_percent': f"{float(row['avg_discount']) * 100:.1f}%"
                })
            
            return {
                'chart_data': chart_data,
                'chart_config': {
                    'chart_type': 'bar',
                    'x_axis': 'event',
                    'y_axis': 'transaction_count',
                    'title': 'Volume Transaksi per Event',
                    'x_label': 'Event',
                    'y_label': 'Jumlah Transaksi'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating event analysis: {str(e)}")
            return None
    
    def get_category_performance(self, top_n=15):
        """Get top performing categories by transaction volume"""
        if self.df_transaksi is None or self.df_produk is None:
            return None
        
        try:
            # Merge with product data to get categories
            merged_data = pd.merge(
                self.df_transaksi, 
                self.df_produk[['id_produk', 'kategori_produk']], 
                on='id_produk', 
                how='left'
            )
            
            # Group by category
            category_performance = merged_data.groupby('kategori_produk').agg({
                'id_produk': 'count',
                'harga_promosi': 'mean',
                'diskon': 'mean'
            }).reset_index()
            
            category_performance.columns = ['category', 'transaction_count', 'avg_price', 'avg_discount']
            category_performance = category_performance.sort_values('transaction_count', ascending=False).head(top_n)
            
            chart_data = []
            for _, row in category_performance.iterrows():
                chart_data.append({
                    'category': row['category'],
                    'transaction_count': int(row['transaction_count']),
                    'avg_price': float(row['avg_price']),
                    'avg_discount': float(row['avg_discount']),
                    'avg_discount_percent': f"{float(row['avg_discount']) * 100:.1f}%"
                })
            
            return {
                'chart_data': chart_data,
                'chart_config': {
                    'chart_type': 'bar',
                    'x_axis': 'category',
                    'y_axis': 'transaction_count',
                    'title': f'Top {top_n} Kategori Produk dengan Volume Transaksi Tertinggi',
                    'x_label': 'Kategori Produk',
                    'y_label': 'Jumlah Transaksi'
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating category performance: {str(e)}")
            return None
    
    def get_business_metrics(self, start_date=None, end_date=None, store_id=None, period='monthly'):
        """Get key business metrics: Revenue, Transactions, AOV"""
        if self.df_transaksi is None:
            return None
        
        try:
            df_filtered = self.df_transaksi.copy()
            
            # Filter by date range if provided
            if start_date:
                df_filtered = df_filtered[df_filtered['tanggal_transaksi'] >= pd.to_datetime(start_date)]
            if end_date:
                df_filtered = df_filtered[df_filtered['tanggal_transaksi'] <= pd.to_datetime(end_date)]
            
            # Filter by store if provided
            if store_id:
                df_filtered = df_filtered[df_filtered['id_toko'] == store_id]
            
            # Calculate metrics
            total_revenue = float(df_filtered['harga_promosi'].sum())
            total_transactions = int(len(df_filtered))
            average_order_value = float(total_revenue / total_transactions) if total_transactions > 0 else 0
            
            # Calculate growth (compare with previous period)
            growth_data = self._calculate_growth_metrics(df_filtered, period, start_date, end_date, store_id)
            
            return {
                'current_period': {
                    'total_revenue': total_revenue,
                    'total_transactions': total_transactions,
                    'average_order_value': average_order_value,
                    'revenue_formatted': f"Rp {total_revenue:,.0f}",
                    'aov_formatted': f"Rp {average_order_value:,.0f}"
                },
                'growth': growth_data,
                'period_info': {
                    'start_date': start_date or df_filtered['tanggal_transaksi'].min().strftime('%Y-%m-%d'),
                    'end_date': end_date or df_filtered['tanggal_transaksi'].max().strftime('%Y-%m-%d'),
                    'store_id': store_id,
                    'period': period
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating business metrics: {str(e)}")
            return None
    
    def _calculate_growth_metrics(self, df_current, period, start_date, end_date, store_id):
        """Calculate growth compared to previous period"""
        try:
            if not start_date or not end_date:
                return {'revenue_growth': 0, 'transactions_growth': 0, 'aov_growth': 0}
            
            # Calculate previous period dates
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            period_length = (end_dt - start_dt).days
            
            prev_end = start_dt - pd.Timedelta(days=1)
            prev_start = prev_end - pd.Timedelta(days=period_length)
            
            # Filter previous period data
            df_previous = self.df_transaksi.copy()
            df_previous = df_previous[
                (df_previous['tanggal_transaksi'] >= prev_start) & 
                (df_previous['tanggal_transaksi'] <= prev_end)
            ]
            
            if store_id:
                df_previous = df_previous[df_previous['id_toko'] == store_id]
            
            # Calculate previous metrics
            prev_revenue = float(df_previous['harga_promosi'].sum()) if len(df_previous) > 0 else 0
            prev_transactions = int(len(df_previous))
            prev_aov = float(prev_revenue / prev_transactions) if prev_transactions > 0 else 0
            
            # Calculate current metrics
            curr_revenue = float(df_current['harga_promosi'].sum())
            curr_transactions = int(len(df_current))
            curr_aov = float(curr_revenue / curr_transactions) if curr_transactions > 0 else 0
            
            # Calculate growth percentages
            revenue_growth = ((curr_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0
            transactions_growth = ((curr_transactions - prev_transactions) / prev_transactions * 100) if prev_transactions > 0 else 0
            aov_growth = ((curr_aov - prev_aov) / prev_aov * 100) if prev_aov > 0 else 0
            
            return {
                'revenue_growth': round(revenue_growth, 2),
                'transactions_growth': round(transactions_growth, 2),
                'aov_growth': round(aov_growth, 2),
                'previous_period': {
                    'total_revenue': prev_revenue,
                    'total_transactions': prev_transactions,
                    'average_order_value': prev_aov,
                    'start_date': prev_start.strftime('%Y-%m-%d'),
                    'end_date': prev_end.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth metrics: {str(e)}")
            return {'revenue_growth': 0, 'transactions_growth': 0, 'aov_growth': 0}
    
    def get_revenue_by_period(self, period='daily', start_date=None, end_date=None, store_id=None):
        """Get revenue breakdown by time period"""
        if self.df_transaksi is None:
            return None
        
        try:
            df_filtered = self.df_transaksi.copy()
            
            # Apply filters
            if start_date:
                df_filtered = df_filtered[df_filtered['tanggal_transaksi'] >= pd.to_datetime(start_date)]
            if end_date:
                df_filtered = df_filtered[df_filtered['tanggal_transaksi'] <= pd.to_datetime(end_date)]
            if store_id:
                df_filtered = df_filtered[df_filtered['id_toko'] == store_id]
            
            # Group by period
            if period == 'daily':
                df_filtered['period'] = df_filtered['tanggal_transaksi'].dt.strftime('%Y-%m-%d')
                period_label = 'Hari'
            elif period == 'weekly':
                df_filtered['period'] = df_filtered['tanggal_transaksi'].dt.strftime('%Y-W%U')
                period_label = 'Minggu'
            elif period == 'monthly':
                df_filtered['period'] = df_filtered['tanggal_transaksi'].dt.strftime('%Y-%m')
                period_label = 'Bulan'
            else:
                df_filtered['period'] = df_filtered['tanggal_transaksi'].dt.strftime('%Y-%m-%d')
                period_label = 'Hari'
            
            # Calculate metrics by period
            period_metrics = df_filtered.groupby('period').agg({
                'harga_promosi': ['sum', 'count', 'mean']
            }).round(2)
            
            period_metrics.columns = ['revenue', 'transactions', 'avg_transaction_value']
            period_metrics = period_metrics.reset_index()
            
            # Convert to chart-ready format
            chart_data = []
            for _, row in period_metrics.iterrows():
                chart_data.append({
                    'period': row['period'],
                    'revenue': float(row['revenue']),
                    'transactions': int(row['transactions']),
                    'avg_transaction_value': float(row['avg_transaction_value']),
                    'revenue_formatted': f"Rp {float(row['revenue']):,.0f}",
                    'avg_formatted': f"Rp {float(row['avg_transaction_value']):,.0f}"
                })
            
            return {
                'chart_data': chart_data,
                'summary': {
                    'total_periods': len(chart_data),
                    'total_revenue': float(period_metrics['revenue'].sum()),
                    'total_transactions': int(period_metrics['transactions'].sum()),
                    'avg_period_revenue': float(period_metrics['revenue'].mean()),
                    'period_type': period
                },
                'chart_config': {
                    'chart_type': 'line' if period == 'daily' else 'bar',
                    'x_axis': 'period',
                    'y_axis': 'revenue',
                    'title': f'Revenue per {period_label}',
                    'x_label': period_label,
                    'y_label': 'Revenue (Rp)'
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue by period: {str(e)}")
            return None

# Initialize APIs
bizzt_api = BizztRecommendationAPI()
analytics_api = BizztAnalyticsAPI()

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
            },
            'analytics_weekly': {
                'url': '/api/analytics/trends/weekly',
                'method': 'GET',
                'description': 'Mendapatkan tren volume transaksi per minggu',
                'parameters': 'Tidak ada',
                'example': '/api/analytics/trends/weekly'
            },
            'analytics_events': {
                'url': '/api/analytics/events',
                'method': 'GET',
                'description': 'Mendapatkan analisis transaksi per event',
                'parameters': 'Tidak ada',
                'example': '/api/analytics/events'
            },
            'analytics_categories': {
                'url': '/api/analytics/categories',
                'method': 'GET',
                'description': 'Mendapatkan performa kategori produk',
                'parameters': {
                    'limit': 'Jumlah kategori (default: 15, max: 50)'
                },
                'example': '/api/analytics/categories?limit=10'
            },
            'business_metrics': {
                'url': '/api/metrics/business',
                'method': 'GET',
                'description': 'Mendapatkan metrics bisnis utama (Revenue, Transactions, AOV)',
                'parameters': {
                    'start_date': 'Tanggal mulai (YYYY-MM-DD)',
                    'end_date': 'Tanggal akhir (YYYY-MM-DD)',
                    'store_id': 'ID toko (optional)',
                    'period': 'Period untuk perbandingan (daily/weekly/monthly)'
                },
                'example': '/api/metrics/business?start_date=2025-01-01&end_date=2025-01-31'
            },
            'revenue_breakdown': {
                'url': '/api/metrics/revenue',
                'method': 'GET',
                'description': 'Mendapatkan breakdown revenue per periode waktu',
                'parameters': {
                    'period': 'Periode waktu (daily/weekly/monthly)',
                    'start_date': 'Tanggal mulai (YYYY-MM-DD)',
                    'end_date': 'Tanggal akhir (YYYY-MM-DD)',
                    'store_id': 'ID toko (optional)'
                },
                'example': '/api/metrics/revenue?period=daily&start_date=2025-01-01'
            },
            'dashboard_metrics': {
                'url': '/api/metrics/dashboard',
                'method': 'GET',
                'description': 'Mendapatkan semua metrics dalam format dashboard',
                'parameters': {
                    'start_date': 'Tanggal mulai (default: awal bulan ini)',
                    'end_date': 'Tanggal akhir (default: hari ini)',
                    'store_id': 'ID toko (optional)'
                },
                'example': '/api/metrics/dashboard'
            },
            'raw_products': {
                'url': '/api/data/products',
                'method': 'GET',
                'description': 'Mendapatkan data mentah produk dengan filtering (termasuk kolom stock)',
                'parameters': {
                    'limit': 'Jumlah record (max: 5000)',
                    'offset': 'Skip record untuk pagination',
                    'kategori': 'Filter berdasarkan kategori',
                    'brand': 'Filter berdasarkan brand',
                    'search': 'Pencarian dalam nama produk',
                    'id_toko': 'Filter berdasarkan ID toko'
                },
                'example': '/api/data/products?limit=10&kategori=Daging&id_toko=1'
            },
            'raw_stores': {
                'url': '/api/data/stores',
                'method': 'GET',
                'description': 'Mendapatkan data mentah toko dengan filtering',
                'parameters': {
                    'limit': 'Jumlah record (max: 1000)',
                    'offset': 'Skip record untuk pagination',
                    'tipe': 'Filter berdasarkan tipe toko'
                },
                'example': '/api/data/stores?tipe=perkantoran'
            },
            'data_summary': {
                'url': '/api/data',
                'method': 'GET',
                'description': 'Mendapatkan ringkasan semua data mentah yang tersedia',
                'parameters': 'Tidak ada',
                'example': '/api/data'
            },
            'data_refresh': {
                'url': '/api/data/refresh',
                'method': 'POST',
                'description': 'Memuat ulang semua data mentah dari file CSV (termasuk kolom stock baru)',
                'parameters': 'Tidak ada',
                'example': 'POST /api/data/refresh'
            }
        },
        'system_info': {
            'recommendations_loaded': len(bizzt_api.recommendations_data),
            'is_processing': bizzt_api.is_processing,
            'last_update': bizzt_api.last_update_time.isoformat() if bizzt_api.last_update_time else None
        },
        'quick_links': [
            'http://localhost:5000/api/recommendations?limit=10',
            'http://localhost:5000/api/recommendations/stats',
            'http://localhost:5000/api/analytics/trends/weekly',
            'http://localhost:5000/api/analytics/events',
            'http://localhost:5000/api/analytics/categories?limit=10',
            'http://localhost:5000/api/metrics/dashboard',
            'http://localhost:5000/api/metrics/business',
            'http://localhost:5000/api/metrics/revenue?period=daily',
            'http://localhost:5000/api/data',
            'http://localhost:5000/api/data/products?limit=10',
            'http://localhost:5000/api/data/products?id_toko=1&limit=10',
            'http://localhost:5000/api/data/stores'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render monitoring"""
    try:
        # Test data access
        recommendations_available = len(bizzt_api.recommendations_data) > 0 if bizzt_api.recommendations_data else False
        analytics_available = analytics_api.df_transaksi is not None and len(analytics_api.df_transaksi) > 0
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '2.0.0',
            'environment': ENV,
            'services': {
                'recommendations': recommendations_available,
                'analytics': analytics_available
            },
            'uptime': 'OK'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

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

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/trends/weekly', methods=['GET'])
def get_weekly_trends():
    """Get weekly transaction volume trends"""
    try:
        trend_data = analytics_api.get_weekly_transaction_trend()
        
        if trend_data is None:
            return jsonify({'error': 'Unable to generate weekly trends. Check data availability.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': trend_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting weekly trends: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/analytics/events', methods=['GET'])
def get_event_analysis():
    """Get event-based transaction analysis"""
    try:
        event_data = analytics_api.get_event_analysis()
        
        if event_data is None:
            return jsonify({'error': 'Unable to generate event analysis. Check data availability.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': event_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting event analysis: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/analytics/categories', methods=['GET'])
def get_category_performance():
    """Get category performance analysis"""
    try:
        top_n = request.args.get('limit', 15, type=int)
        
        if top_n <= 0 or top_n > 50:
            return jsonify({'error': 'Invalid limit parameter. Must be between 1 and 50.'}), 400
        
        category_data = analytics_api.get_category_performance(top_n)
        
        if category_data is None:
            return jsonify({'error': 'Unable to generate category analysis. Check data availability.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': category_data,
            'limit': top_n,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting category performance: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics_summary():
    """Get all analytics data in one endpoint"""
    try:
        weekly_trends = analytics_api.get_weekly_transaction_trend()
        event_analysis = analytics_api.get_event_analysis()
        category_performance = analytics_api.get_category_performance(10)  # Top 10
        
        analytics_data = {
            'weekly_trends': weekly_trends,
            'event_analysis': event_analysis,
            'category_performance': category_performance
        }
        
        # Check if any data is available
        available_data = [k for k, v in analytics_data.items() if v is not None]
        
        if not available_data:
            return jsonify({'error': 'No analytics data available. Check data files.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': analytics_data,
            'available_datasets': available_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# ============================================================================
# RAW DATA ENDPOINTS
# ============================================================================

@app.route('/api/data/products', methods=['GET'])
def get_products_data():
    """Get raw product data with filtering and pagination"""
    try:
        # Get parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        kategori = request.args.get('kategori')
        brand = request.args.get('brand')
        search = request.args.get('search')
        id_toko = request.args.get('id_toko', type=int)
        
        # Validate parameters
        if limit and (limit <= 0 or limit > 5000):
            return jsonify({'error': 'Invalid limit parameter. Must be between 1 and 5000.'}), 400
        
        if offset < 0:
            return jsonify({'error': 'Invalid offset parameter. Must be >= 0.'}), 400
        
        if id_toko and id_toko <= 0:
            return jsonify({'error': 'Invalid id_toko parameter. Must be > 0.'}), 400
        
        # Get data
        result = analytics_api.get_products_data(
            limit=limit, 
            offset=offset, 
            kategori=kategori, 
            brand=brand, 
            search=search,
            id_toko=id_toko
        )
        
        if result is None:
            return jsonify({'error': 'No product data available.'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Product data retrieved successfully',
            'data': result['data'],
            'meta': result['meta'],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in get_products_data endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/stores', methods=['GET'])
def get_stores_data():
    """Get raw store data with filtering and pagination"""
    try:
        # Get parameters
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        tipe = request.args.get('tipe')
        
        # Validate parameters
        if limit and (limit <= 0 or limit > 1000):
            return jsonify({'error': 'Invalid limit parameter. Must be between 1 and 1000.'}), 400
        
        if offset < 0:
            return jsonify({'error': 'Invalid offset parameter. Must be >= 0.'}), 400
        
        # Get data
        result = analytics_api.get_stores_data(
            limit=limit, 
            offset=offset, 
            tipe=tipe
        )
        
        if result is None:
            return jsonify({'error': 'No store data available.'}), 404
        
        return jsonify({
            'status': 'success',
            'message': 'Store data retrieved successfully',
            'data': result['data'],
            'meta': result['meta'],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in get_stores_data endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data', methods=['GET'])
def get_data_summary():
    """Get summary of all available raw data"""
    try:
        summary = {
            'products': {
                'total_records': len(analytics_api.df_produk) if analytics_api.df_produk is not None else 0,
                'columns': list(analytics_api.df_produk.columns) if analytics_api.df_produk is not None else [],
                'available_categories': list(analytics_api.df_produk['kategori_produk'].unique()) if analytics_api.df_produk is not None else [],
                'available_brands': list(analytics_api.df_produk['brand'].unique()[:20]) if analytics_api.df_produk is not None else [],  # Limit to first 20 brands
                'endpoint': '/api/data/products',
                'parameters': {
                    'limit': 'Number of records to return (max 5000)',
                    'offset': 'Number of records to skip (for pagination)',
                    'kategori': 'Filter by product category',
                    'brand': 'Filter by brand',
                    'search': 'Search in product names'
                }
            },
            'stores': {
                'total_records': len(analytics_api.df_toko) if analytics_api.df_toko is not None else 0,
                'columns': list(analytics_api.df_toko.columns) if analytics_api.df_toko is not None else [],
                'available_types': list(analytics_api.df_toko['tipe'].unique()) if analytics_api.df_toko is not None else [],
                'endpoint': '/api/data/stores',
                'parameters': {
                    'limit': 'Number of records to return (max 1000)',
                    'offset': 'Number of records to skip (for pagination)',
                    'tipe': 'Filter by store type'
                }
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Data summary retrieved successfully',
            'data': summary,
            'examples': {
                'products': [
                    '/api/data/products?limit=10',
                    '/api/data/products?kategori=Daging&limit=20',
                    '/api/data/products?brand=IndoAgro&offset=0&limit=50',
                    '/api/data/products?search=sarden&limit=5',
                    '/api/data/products?id_toko=1&limit=100',
                    '/api/data/products?kategori=Daging&id_toko=1&limit=20'
                ],
                'stores': [
                    '/api/data/stores',
                    '/api/data/stores?tipe=perkantoran',
                    '/api/data/stores?limit=5&offset=2'
                ]
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in get_data_summary endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/data/refresh', methods=['POST'])
def refresh_raw_data():
    """Refresh/reload all raw data from CSV files"""
    try:
        # Reload data for both APIs
        analytics_api.load_data()
        bizzt_api.load_product_data()
        
        # Get updated summary
        summary = {
            'products': {
                'total_records': len(analytics_api.df_produk) if analytics_api.df_produk is not None else 0,
                'columns': list(analytics_api.df_produk.columns) if analytics_api.df_produk is not None else [],
                'sample_data': analytics_api.df_produk.head(2).to_dict('records') if analytics_api.df_produk is not None else []
            },
            'stores': {
                'total_records': len(analytics_api.df_toko) if analytics_api.df_toko is not None else 0,
                'columns': list(analytics_api.df_toko.columns) if analytics_api.df_toko is not None else []
            },
            'transactions': {
                'total_records': len(analytics_api.df_transaksi) if analytics_api.df_transaksi is not None else 0
            }
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Raw data refreshed successfully',
            'data': summary,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error in refresh_raw_data endpoint: {str(e)}")
        return jsonify({'error': f'Failed to refresh data: {str(e)}'}), 500

# ============================================================================
# BUSINESS METRICS ENDPOINTS
# ============================================================================

@app.route('/api/metrics/business', methods=['GET'])
def get_business_metrics():
    """Get key business metrics: Revenue, Transactions, AOV with growth comparison"""
    try:
        # Get parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        store_id = request.args.get('store_id', type=int)
        period = request.args.get('period', 'monthly')
        
        # Validate period
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period. Must be daily, weekly, or monthly.'}), 400
        
        metrics_data = analytics_api.get_business_metrics(start_date, end_date, store_id, period)
        
        if metrics_data is None:
            return jsonify({'error': 'Unable to calculate business metrics. Check data availability.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': metrics_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting business metrics: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/metrics/revenue', methods=['GET'])
def get_revenue_metrics():
    """Get detailed revenue breakdown by period"""
    try:
        # Get parameters
        period = request.args.get('period', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        store_id = request.args.get('store_id', type=int)
        
        # Validate period
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period. Must be daily, weekly, or monthly.'}), 400
        
        revenue_data = analytics_api.get_revenue_by_period(period, start_date, end_date, store_id)
        
        if revenue_data is None:
            return jsonify({'error': 'Unable to generate revenue breakdown. Check data availability.'}), 404
        
        return jsonify({
            'status': 'success',
            'data': revenue_data,
            'parameters': {
                'period': period,
                'start_date': start_date,
                'end_date': end_date,
                'store_id': store_id
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting revenue metrics: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/metrics/dashboard', methods=['GET'])
def get_dashboard_metrics():
    """Get all dashboard metrics in dashboard-ready format"""
    try:
        # Get parameters (default to current month)
        end_date = request.args.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        # Default start_date to beginning of current month
        start_date = request.args.get('start_date', datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        store_id = request.args.get('store_id', type=int)
        
        # Get business metrics
        business_metrics = analytics_api.get_business_metrics(start_date, end_date, store_id, 'monthly')
        
        if business_metrics is None:
            return jsonify({'error': 'Unable to generate dashboard metrics. Check data availability.'}), 404
        
        # Format for dashboard
        current = business_metrics['current_period']
        growth = business_metrics.get('growth', {})
        
        dashboard_data = {
            'kpi_cards': [
                {
                    'title': 'Total Revenue',
                    'value': current['revenue_formatted'],
                    'raw_value': current['total_revenue'],
                    'growth': growth.get('revenue_growth', 0),
                    'growth_formatted': f"{growth.get('revenue_growth', 0):+.1f}%",
                    'trend': 'up' if growth.get('revenue_growth', 0) > 0 else 'down' if growth.get('revenue_growth', 0) < 0 else 'flat',
                    'icon': 'revenue'
                },
                {
                    'title': 'Total Transactions',
                    'value': f"{current['total_transactions']:,}",
                    'raw_value': current['total_transactions'],
                    'growth': growth.get('transactions_growth', 0),
                    'growth_formatted': f"{growth.get('transactions_growth', 0):+.1f}%",
                    'trend': 'up' if growth.get('transactions_growth', 0) > 0 else 'down' if growth.get('transactions_growth', 0) < 0 else 'flat',
                    'icon': 'transactions'
                },
                {
                    'title': 'Average Order Value',
                    'value': current['aov_formatted'],
                    'raw_value': current['average_order_value'],
                    'growth': growth.get('aov_growth', 0),
                    'growth_formatted': f"{growth.get('aov_growth', 0):+.1f}%",
                    'trend': 'up' if growth.get('aov_growth', 0) > 0 else 'down' if growth.get('aov_growth', 0) < 0 else 'flat',
                    'icon': 'aov'
                },
                {
                    'title': 'Gross Profit*',
                    'value': 'Rp 0',
                    'raw_value': 0,
                    'growth': 0,
                    'growth_formatted': '0.0%',
                    'trend': 'flat',
                    'icon': 'profit',
                    'note': '*Requires cost data to calculate accurately'
                }
            ],
            'period_info': business_metrics['period_info'],
            'comparison': {
                'previous_period': growth.get('previous_period', {}),
                'growth_summary': f"Revenue {'increased' if growth.get('revenue_growth', 0) > 0 else 'decreased'} by {abs(growth.get('revenue_growth', 0)):.1f}% compared to previous period"
            }
        }
        
        return jsonify({
            'status': 'success',
            'data': dashboard_data,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

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
            'POST /api/recommendations/refresh',
            'GET /api/analytics/trends/weekly',
            'GET /api/analytics/events',
            'GET /api/analytics/categories',
            'GET /api/analytics',
            'GET /api/metrics/business',
            'GET /api/metrics/revenue',
            'GET /api/metrics/dashboard'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    if ENV == 'production':
        # Production mode - simple start
        logger.info(f"🚀 Bizzt Recommendation API starting in production on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode with detailed info
        print("🚀 Bizzt Recommendation API")
        print("=" * 50)
        print("📋 Endpoints:")
        print("  GET  /                              - Health check")
        print("  GET  /api/recommendations          - Get recommendations")
        print("  GET  /api/recommendations/stats    - Get statistics")
        print("  POST /api/recommendations/regenerate - Regenerate recommendations")
        print("  GET  /api/recommendations/status    - Check processing status")
        print("  POST /api/recommendations/refresh   - Refresh from files")
        print("  GET  /api/analytics/trends/weekly   - Weekly transaction trends")
        print("  GET  /api/analytics/events          - Event analysis")
        print("  GET  /api/analytics/categories      - Category performance")
        print("  GET  /api/analytics                 - All analytics data")
        print("  GET  /api/data                      - Raw data summary")
        print("  GET  /api/data/products             - Raw product data (includes stock, filter by store)")
        print("  GET  /api/data/stores               - Raw store data")
        print("  POST /api/data/refresh              - Refresh raw data from files")
        print("  GET  /api/metrics/business          - Business KPIs (Revenue, Transactions, AOV)")
        print("  GET  /api/metrics/revenue           - Revenue breakdown by period")
        print("  GET  /api/metrics/dashboard         - Dashboard-ready metrics")
        print("\n🎯 Key Features:")
        print("  ✅ Clean endpoint structure")
        print("  ✅ Background processing")
        print("  ✅ Real-time progress tracking")
        print("  ✅ Automatic data persistence")
        print("\n🌐 Starting server on http://localhost:5000")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
