"""
Feature engineering utilities for the recommendation system
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from src.config import Config


class FeatureEngineer:
    """Class for feature engineering operations"""
    
    def __init__(self):
        self.config = Config()
        self.scaler = MinMaxScaler(feature_range=(0, 100))
    
    def create_urgency_features(self, df_produk: pd.DataFrame, 
                              df_transaksi: pd.DataFrame) -> pd.DataFrame:
        """
        Create urgency-related features for Model 1 (Product Selector)
        Migrated from notebook urgency score calculation
        """
        print("Creating urgency features...")
        
        # Calculate sales statistics per product - sesuai dengan kode notebook  
        sales_stats = df_transaksi.groupby('id_produk').agg(
            total_penjualan=('id_produk', 'count'),
            penjualan_terakhir=('tanggal_transaksi', 'max'),
            jumlah_hari_jual=('tanggal_transaksi', 'nunique')
        ).reset_index()
        
        # Calculate daily average sales - sesuai dengan notebook
        # Tambah 1 untuk menghindari pembagian dengan nol
        sales_stats['penjualan_harian_avg'] = sales_stats['total_penjualan'] / (sales_stats['jumlah_hari_jual'] + 1)
        
        # Calculate days since last sale
        current_date = df_transaksi['tanggal_transaksi'].max()
        sales_stats['hari_sejak_penjualan_terakhir'] = (current_date - sales_stats['penjualan_terakhir']).dt.days
        
        # Merge with product data
        df_model = pd.merge(df_produk, sales_stats, on='id_produk', how='left')
        
        # Fill missing values
        df_model['total_penjualan'] = df_model['total_penjualan'].fillna(0)
        df_model['penjualan_harian_avg'] = df_model['penjualan_harian_avg'].fillna(0)
        df_model['hari_sejak_penjualan_terakhir'] = df_model['hari_sejak_penjualan_terakhir'].fillna(999)
        
        # Create expiry features - sesuai dengan notebook
        today = datetime.now().date()
        if 'expire_date' in df_model.columns:
            df_model['expire_date'] = pd.to_datetime(df_model['expire_date'])
            df_model['hari_menuju_kedaluwarsa'] = (df_model['expire_date'] - pd.Timestamp(today)).dt.days
        else:
            # Use hari_jual_minimal as proxy
            df_model['hari_menuju_kedaluwarsa'] = df_model.get('hari_jual_minimal', 365)
        
        # Create margin headroom - sesuai dengan notebook
        df_model['minimal_margin'] = df_model['margin'] * 0.4
        df_model['margin_headroom'] = df_model['margin'] - df_model['minimal_margin']
        
        return df_model
    
    def calculate_urgency_score(self, df_model: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate urgency score using the weights from config
        Migrated from notebook urgency score logic
        """
        print("Calculating urgency scores...")
        
        weights = self.config.URGENCY_SCORE_WEIGHTS
        
        # Avoid division by zero - sesuai dengan notebook
        df_model['hari_menuju_kedaluwarsa_safe'] = df_model['hari_menuju_kedaluwarsa'].clip(lower=1)
        
        # Calculate component scores
        df_model['skor_kedaluwarsa'] = 1 / df_model['hari_menuju_kedaluwarsa_safe']
        df_model['skor_kelambatan'] = df_model['hari_sejak_penjualan_terakhir']
        df_model['skor_penalti_penjualan'] = df_model['penjualan_harian_avg']
        
        # Combine into raw urgency score
        df_model['urgency_score_raw'] = (
            weights['kedaluwarsa'] * df_model['skor_kedaluwarsa'] +
            weights['kelambatan'] * df_model['skor_kelambatan'] -
            weights['penjualan'] * df_model['skor_penalti_penjualan']
        )
        
        # Normalize to 0-100 scale
        df_model['urgency_score'] = self.scaler.fit_transform(df_model[['urgency_score_raw']])
        
        print(f"Urgency score distribution:\n{df_model['urgency_score'].describe()}")
        
        return df_model
    
    def create_t_learner_features(self, df_master: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Create features for T-Learner models
        Migrated from notebook feature engineering logic
        """
        print("Creating T-Learner features...")
        
        df_featured = df_master.copy()
        
        # Parse store context features
        try:
            df_featured['rasio_pekerja_kantoran'] = df_featured['pekerjaan_konsumen'].str.extract(r'pekerja_kantoran: (\\d+\\.\\d+)').astype(float).fillna(0)
            df_featured['rasio_impulsif'] = df_featured['kebiasaan_konsumen'].str.extract(r'impulsif: (\\d+\\.\\d+)').astype(float).fillna(0)
        except Exception as e:
            print(f"Warning: Failed to extract store features. Error: {e}")
            df_featured['rasio_pekerja_kantoran'] = 0
            df_featured['rasio_impulsif'] = 0
        
        # Create product detail features
        df_featured['gramasi'] = df_featured['nama_produk'].str.extract(r'(\\d+)\\s?(g|ml)')[0].astype(float).fillna(0)
        df_featured['harga_per_gram'] = (df_featured['harga_jual'] / df_featured['gramasi']).replace([np.inf, -np.inf], 0).fillna(0)
        df_featured['hari_jual'] = df_featured.get('hari_jual_minimal', df_featured.get('hari_jual', 30))
        df_featured['kedaluwarsa'] = 365 - df_featured['hari_jual']
        
        # One-hot encoding for categorical features
        categorical_columns = []
        if 'brand' in df_featured.columns:
            categorical_columns.append('brand')
        if 'kategori_produk' in df_featured.columns:
            categorical_columns.append('kategori_produk')
        if 'current_event' in df_featured.columns:
            categorical_columns.append('current_event')
        
        df_featured = pd.get_dummies(df_featured, columns=categorical_columns, prefix=['brand', 'kat', 'event'][:len(categorical_columns)])
        
        # Define feature columns
        fitur_numerik = [
            'harga_jual', 'margin', 'hari_jual', 'kedaluwarsa',
            'rasio_pekerja_kantoran', 'rasio_impulsif', 'gramasi', 'harga_per_gram'
        ]
        fitur_ohe = [col for col in df_featured.columns if col.startswith(('brand_', 'kat_', 'event_'))]
        feature_columns = fitur_numerik + fitur_ohe
        
        # Ensure all numeric features exist
        for col in fitur_numerik:
            if col not in df_featured.columns:
                df_featured[col] = 0
        
        print(f"Created {len(feature_columns)} features for T-Learner")
        
        return df_featured, feature_columns
    
    def prepare_recommendation_features(self, df_products: pd.DataFrame, 
                                      df_toko: pd.DataFrame, 
                                      feature_columns: List[str],
                                      current_event: str = "Promo Akhir Pekan") -> pd.DataFrame:
        """
        Prepare features for recommendation inference
        """
        print("Preparing recommendation features...")
        
        # Merge with store data
        df_rekomendasi = pd.merge(df_products, df_toko, on='id_toko', how='left')
        
        # Add current event context
        df_rekomendasi['current_event'] = current_event
        
        # Apply same feature engineering as training
        df_rekomendasi_featured, _ = self.create_t_learner_features(df_rekomendasi)
        
        # Ensure all feature columns exist
        for col in feature_columns:
            if col not in df_rekomendasi_featured.columns:
                df_rekomendasi_featured[col] = 0
        
        # Return only the required features in correct order
        X_rekomendasi = df_rekomendasi_featured[feature_columns]
        
        return X_rekomendasi, df_rekomendasi
    
    def create_time_series_features(self, df_transaksi: pd.DataFrame, 
                                  product_ids: List[str]) -> pd.DataFrame:
        """
        Create time series features for TFT model
        """
        print("Creating time series features...")
        
        # Filter for target products
        df_filtered = df_transaksi[df_transaksi['id_produk'].isin(product_ids)].copy()
        
        # Create daily sales aggregation
        df_daily_sales = df_filtered.groupby(['tanggal_transaksi', 'id_produk']).size().reset_index(name='penjualan_harian')
        
        # Create complete date range
        start_date = df_filtered['tanggal_transaksi'].min()
        end_date = df_filtered['tanggal_transaksi'].max()
        all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create multi-index for all combinations
        multi_index = pd.MultiIndex.from_product([all_dates, product_ids], names=['tanggal_transaksi', 'id_produk'])
        df_timeseries = pd.DataFrame(index=multi_index).reset_index()
        
        # Merge with sales data and fill missing values
        df_timeseries = pd.merge(df_timeseries, df_daily_sales, on=['tanggal_transaksi', 'id_produk'], how='left').fillna(0)
        
        # Add time-based features
        df_timeseries['time_idx'] = (df_timeseries['tanggal_transaksi'] - df_timeseries['tanggal_transaksi'].min()).dt.days
        df_timeseries['bulan'] = df_timeseries['tanggal_transaksi'].dt.month
        df_timeseries['hari_dalam_minggu'] = df_timeseries['tanggal_transaksi'].dt.dayofweek
        
        print(f"Created time series data with {len(df_timeseries)} records")
        
        return df_timeseries
