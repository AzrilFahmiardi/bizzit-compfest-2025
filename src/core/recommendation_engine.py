"""
Recommendation Engine
Combines business rules with ML predictions to generate final recommendations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

from src.config import Config
from src.utils.data_loader import get_current_event


class RecommendationEngine:
    """
    Main recommendation engine that applies business rules and generates final recommendations
    Migrated from notebook business logic
    """
    
    def __init__(self):
        self.config = Config()
    
    def round_discount(self, discount: float) -> float:
        """
        Round discount to nearest 5%
        """
        if discount is None or discount < 0.05:
            return 0.05
        return round((discount * 100) / 5) * 5 / 100
    
    def get_recommendation_magnitude(self, row: pd.Series, upcoming_events: Dict[str, Tuple]) -> float:
        """
        Calculate discount magnitude based on business rules
        Migrated from notebook recommendation logic
        """
        strategi = row['rekomendasi_utama']
        kategori = row['kategori_produk']
        hari_menuju_kedaluwarsa = row.get('hari_menuju_kedaluwarsa', 365)
        harga_kita = row.get('harga_jual', 0)
        harga_kompetitor = row.get('harga_kompetitor', np.nan)
        hari_jual_min = row.get('hari_jual_minimal', row.get('hari_jual', 30))
        
        # BOGO strategy
        if strategi == 'BOGO':
            return 0.50
        
        # No discount
        if strategi == 'Tanpa Diskon':
            return 0.0
        
        # Expired product discount
        if 'Expired' in strategi:
            if harga_kita > 0 and pd.notna(harga_kompetitor) and harga_kompetitor > 0:
                target_price = harga_kompetitor * 0.95
                calculated_discount = 1 - (target_price / harga_kita)
                return self.round_discount(max(0.05, calculated_discount))
            else:
                return 0.25  # Default expired discount
        
        # Event-based discount
        if 'Event' in strategi:
            if harga_kita > 0 and pd.notna(harga_kompetitor) and harga_kompetitor > 0:
                target_price = harga_kompetitor * 0.98
                calculated_discount = 1 - (target_price / harga_kita)
                return self.round_discount(max(0.05, calculated_discount))
            else:
                return 0.15  # Default event discount
        
        # Generic product discount based on shelf life
        if hari_jual_min <= 7:
            return 0.15
        elif hari_jual_min <= 30:
            return 0.10
        else:
            return 0.05
    
    def analyze_event_categories(self, df_transaksi: pd.DataFrame, 
                               df_produk: pd.DataFrame, 
                               lift_threshold: float = 1.2) -> Dict[str, List[str]]:
        """
        Dynamically analyze which categories perform well during events
        """
        print("Analyzing event-category performance...")
        
        # Merge transaction data with product categories
        df_analysis = pd.merge(
            df_transaksi, 
            df_produk[['id_produk', 'kategori_produk']], 
            on='id_produk', 
            how='left'
        )
        
        # Add event information
        df_analysis['tanggal_transaksi'] = pd.to_datetime(df_analysis['tanggal_transaksi'])
        df_analysis['event'] = df_analysis['tanggal_transaksi'].apply(get_current_event)
        
        # Calculate daily sales per category
        daily_sales = df_analysis.groupby(['tanggal_transaksi', 'kategori_produk']).size().reset_index(name='penjualan')
        daily_sales['event'] = daily_sales['tanggal_transaksi'].apply(get_current_event)
        
        # Calculate average sales during normal periods
        normal_events = ['Hari Biasa', 'Promo Akhir Pekan']
        normal_sales = daily_sales[daily_sales['event'].isin(normal_events)]
        avg_normal_sales = normal_sales.groupby('kategori_produk')['penjualan'].mean().to_dict()
        
        # Analyze performance during major events
        event_categories_map = {}
        major_events = ['Ramadan', 'Natal', 'Tahun Baru']
        
        for event in major_events:
            event_sales = daily_sales[daily_sales['event'] == event]
            if not event_sales.empty:
                avg_event_sales = event_sales.groupby('kategori_produk')['penjualan'].mean()
                
                # Find categories with significant lift
                event_categories = []
                for category, event_avg in avg_event_sales.items():
                    normal_avg = avg_normal_sales.get(category, 0)
                    if normal_avg > 0 and event_avg > normal_avg * lift_threshold:
                        event_categories.append(category)
                
                event_categories_map[event] = event_categories
        
        print(f"Event categories mapping: {event_categories_map}")
        return event_categories_map
    
    def enhance_recommendations_with_events(self, df_recommendations: pd.DataFrame,
                                          event_categories_map: Dict[str, List[str]],
                                          upcoming_events: Dict[str, Tuple]) -> pd.DataFrame:
        """
        Enhance recommendations with event-specific details
        """
        print("Enhancing recommendations with event details...")
        
        df_enhanced = df_recommendations.copy()
        df_enhanced['rekomendasi_detail'] = df_enhanced['rekomendasi_utama']
        
        # Apply event-specific recommendations
        for event_name in upcoming_events:
            relevant_categories = event_categories_map.get(event_name, [])
            
            # Find products with Event Based Discount in relevant categories
            mask = (
                (df_enhanced['rekomendasi_utama'] == 'Event Based Discount') & 
                (df_enhanced['kategori_produk'].isin(relevant_categories))
            )
            
            df_enhanced.loc[mask, 'rekomendasi_detail'] = f'Event Based ({event_name})'
        
        return df_enhanced
    
    def apply_fallback_logic(self, df_enhanced: pd.DataFrame) -> pd.DataFrame:
        """
        Apply fallback logic for generic event-based recommendations
        """
        print("Applying fallback logic...")
        
        # Find products that still have generic 'Event Based Discount'
        mask_generic = df_enhanced['rekomendasi_detail'] == 'Event Based Discount'
        
        if mask_generic.sum() > 0:
            print(f"Applying fallback logic to {mask_generic.sum()} products")
            
            def get_fallback_recommendation(row):
                # Priority 1: Expiry-based
                if row.get('hari_menuju_kedaluwarsa', 365) <= 45:
                    return {
                        'tipe': "Expired Discount",
                        'besaran': self.get_recommendation_magnitude(
                            pd.Series({**row, 'rekomendasi_utama': 'Expired Discount'}), {}
                        )
                    }
                
                # Priority 2: BOGO for suitable categories
                if row['kategori_produk'] in self.config.BOGO_CATEGORIES:
                    return {'tipe': "BOGO", 'besaran': 0.50}
                
                # Priority 3: Generic discount
                return {
                    'tipe': "Generic Product Discount",
                    'besaran': 0.15 if row.get('hari_jual_minimal', 30) <= 7 else 0.10
                }
            
            # Apply fallback logic
            fallback_results = df_enhanced[mask_generic].apply(get_fallback_recommendation, axis=1)
            
            df_enhanced.loc[mask_generic, 'rekomendasi_detail'] = [r['tipe'] for r in fallback_results]
            df_enhanced.loc[mask_generic, 'rekomendasi_besaran'] = [r['besaran'] for r in fallback_results]
        
        return df_enhanced
    
    def generate_final_recommendations(self, df_t_learner_results: pd.DataFrame,
                                     df_produk: pd.DataFrame,
                                     df_transaksi: pd.DataFrame,
                                     current_date: datetime = None) -> pd.DataFrame:
        """
        Generate final enhanced recommendations with business rules
        """
        print("Generating final enhanced recommendations...")
        
        if current_date is None:
            current_date = datetime.now()
        
        # Merge with additional product information
        df_final = df_t_learner_results.copy()
        df_final['id_produk'] = df_final['id_produk'].astype(str)
        df_produk['id_produk'] = df_produk['id_produk'].astype(str)
        
        additional_features = ['id_produk', 'kode_sku', 'harga_jual', 'harga_kompetitor', 
                             'produk_musiman', 'hari_jual_minimal', 'expire_date']
        available_features = [f for f in additional_features if f in df_produk.columns]
        
        df_final = pd.merge(df_final, df_produk[available_features], on='id_produk', how='left')
        
        # Calculate days until expiry
        if 'expire_date' in df_final.columns:
            df_final['expire_date'] = pd.to_datetime(df_final['expire_date'])
            df_final['hari_menuju_kedaluwarsa'] = (df_final['expire_date'] - pd.Timestamp(current_date)).dt.days
        else:
            df_final['hari_menuju_kedaluwarsa'] = df_final.get('hari_jual_minimal', 365)
        
        # Determine upcoming events
        upcoming_events = {}
        for event_name, (start_date, end_date) in {
            "Ramadan": (pd.Timestamp("2025-02-28"), pd.Timestamp("2025-03-29")),
            "Natal": (pd.Timestamp("2025-12-15"), pd.Timestamp("2025-12-25"))
        }.items():
            if start_date < pd.Timestamp(current_date) + pd.Timedelta(days=90):
                upcoming_events[event_name] = (start_date, end_date)
        
        print(f"Upcoming events: {list(upcoming_events.keys())}")
        
        # Analyze event categories
        event_categories_map = self.analyze_event_categories(df_transaksi, df_produk)
        
        # Calculate discount magnitudes
        df_final['rekomendasi_besaran'] = df_final.apply(
            lambda row: self.get_recommendation_magnitude(row, upcoming_events), axis=1
        )
        
        # Enhance with event details
        df_final = self.enhance_recommendations_with_events(
            df_final, event_categories_map, upcoming_events
        )
        
        # Apply fallback logic
        df_final = self.apply_fallback_logic(df_final)
        
        # Calculate promotion dates
        df_final = self.calculate_promotion_dates(df_final, current_date)
        
        # Select final columns
        final_columns = [
            'id_produk', 'kode_sku', 'nama_produk', 'kategori_produk', 
            'rekomendasi_detail', 'rekomendasi_besaran', 'start_date', 'end_date',
            'rata_rata_uplift_profit'
        ]
        
        df_final_output = df_final[final_columns].sort_values('rata_rata_uplift_profit', ascending=False)
        
        print(f"Final recommendations generated for {len(df_final_output)} products")
        
        return df_final_output
    
    def calculate_promotion_dates(self, df_recommendations: pd.DataFrame, current_date: datetime = None) -> pd.DataFrame:
        """
        Calculate start_date and end_date for each promotion based on recommendation strategy
        Migrated from notebook business logic
        """
        if current_date is None:
            current_date = datetime.now()
        
        df_with_dates = df_recommendations.copy()
        
        # Initialize date columns
        df_with_dates['start_date'] = None
        df_with_dates['end_date'] = None
        
        for idx, row in df_with_dates.iterrows():
            rekomendasi = row['rekomendasi_detail']
            start_date, end_date_promo = None, None
            
            if "Event Based (Ramadan)" in rekomendasi:
                # Start 1 week before Ramadan (2025-02-21)
                start_date = datetime.strptime("2025-02-21", "%Y-%m-%d").date()
                end_date_promo = start_date + timedelta(days=13)  # 2 weeks duration
                
            elif "Expired" in rekomendasi:
                # Next month, first Friday
                bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
                # Find first Friday of next month
                days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
                if days_to_friday == 0:
                    days_to_friday = 7
                jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
                start_date = jumat_pertama.date()
                end_date_promo = start_date + timedelta(days=2)  # Friday-Sunday
                
            elif "BOGO" in rekomendasi:
                # Next month, second Friday
                bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
                days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
                if days_to_friday == 0:
                    days_to_friday = 7
                jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
                start_date = (jumat_pertama + timedelta(days=7)).date()
                end_date_promo = start_date + timedelta(days=2)  # Friday-Sunday
                
            else:  # Generic Product Discount or others
                # Next month, second Friday + 1 week
                bulan_depan = (current_date + timedelta(days=30)).replace(day=1)
                days_to_friday = (4 - bulan_depan.weekday() + 7) % 7
                if days_to_friday == 0:
                    days_to_friday = 7
                jumat_pertama = bulan_depan + timedelta(days=days_to_friday)
                start_date = (jumat_pertama + timedelta(days=7)).date()
                end_date_promo = start_date + timedelta(days=2)  # Friday-Sunday
            
            df_with_dates.at[idx, 'start_date'] = start_date
            df_with_dates.at[idx, 'end_date'] = end_date_promo
        
        return df_with_dates
    
    def get_recommendation_summary(self, df_recommendations: pd.DataFrame) -> Dict[str, any]:
        """
        Get summary statistics of recommendations
        """
        summary = {
            'total_products': len(df_recommendations),
            'strategy_distribution': df_recommendations['rekomendasi_detail'].value_counts().to_dict(),
            'average_discount': df_recommendations['rekomendasi_besaran'].mean(),
            'total_estimated_uplift': df_recommendations['rata_rata_uplift_profit'].sum(),
            'category_distribution': df_recommendations['kategori_produk'].value_counts().to_dict()
        }
        
        return summary
