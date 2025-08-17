"""
Data loading and preprocessing utilities
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import os
from src.config import Config, DataPaths


class DataLoader:
    """Class for loading and initial preprocessing of data"""
    
    def __init__(self, use_local: bool = True):
        self.use_local = use_local
        self.config = Config()
    
    def load_produk(self) -> pd.DataFrame:
        """Load produk data"""
        if self.use_local and os.path.exists(f"{self.config.DATA_DIR}/{self.config.PRODUK_FILE}"):
            df = pd.read_csv(f"{self.config.DATA_DIR}/{self.config.PRODUK_FILE}")
        else:
            df = pd.read_csv(DataPaths.get_data_url(self.config.PRODUK_FILE))
        
        # Clean and convert data types
        if 'margin' in df.columns:
            # Handle margin column if it's in percentage string format
            if df['margin'].dtype == 'object':
                df['margin'] = pd.to_numeric(df['margin'].astype(str).str.replace('%', ''), errors='coerce') / 100
        
        return df
    
    def load_toko(self) -> pd.DataFrame:
        """Load toko data"""
        if self.use_local and os.path.exists(f"{self.config.DATA_DIR}/{self.config.TOKO_FILE}"):
            df = pd.read_csv(f"{self.config.DATA_DIR}/{self.config.TOKO_FILE}")
        else:
            df = pd.read_csv(DataPaths.get_data_url(self.config.TOKO_FILE))
        
        return df
    
    def load_transaksi(self) -> pd.DataFrame:
        """Load transaksi data"""
        if self.use_local and os.path.exists(f"{self.config.DATA_DIR}/{self.config.TRANSAKSI_FILE}"):
            df = pd.read_csv(f"{self.config.DATA_DIR}/{self.config.TRANSAKSI_FILE}")
        else:
            df = pd.read_csv(DataPaths.get_data_url(self.config.TRANSAKSI_FILE))
        
        # Convert date column
        df['tanggal_transaksi'] = pd.to_datetime(df['tanggal_transaksi'])
        
        return df
    
    def load_all_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load all datasets"""
        print("Loading datasets...")
        
        df_produk = self.load_produk()
        df_toko = self.load_toko()
        df_transaksi = self.load_transaksi()
        
        print(f"Loaded: {len(df_produk)} products, {len(df_toko)} stores, {len(df_transaksi)} transactions")
        
        return df_produk, df_toko, df_transaksi


class DataValidator:
    """Class for data validation and quality checks"""
    
    @staticmethod
    def validate_data_quality(df_produk: pd.DataFrame, 
                            df_toko: pd.DataFrame, 
                            df_transaksi: pd.DataFrame) -> Dict[str, Any]:
        """Perform basic data quality checks"""
        
        quality_report = {}
        
        # Check for missing values
        quality_report['produk_missing'] = df_produk.isnull().sum().to_dict()
        quality_report['toko_missing'] = df_toko.isnull().sum().to_dict()
        quality_report['transaksi_missing'] = df_transaksi.isnull().sum().to_dict()
        
        # Check data types
        quality_report['produk_dtypes'] = df_produk.dtypes.to_dict()
        quality_report['toko_dtypes'] = df_toko.dtypes.to_dict()
        quality_report['transaksi_dtypes'] = df_transaksi.dtypes.to_dict()
        
        # Check for unique identifiers
        quality_report['unique_products'] = df_produk['id_produk'].nunique()
        quality_report['unique_stores'] = df_toko['id_toko'].nunique()
        quality_report['unique_skus'] = df_produk['kode_sku'].nunique() if 'kode_sku' in df_produk.columns else 0
        
        # Date range check
        if 'tanggal_transaksi' in df_transaksi.columns:
            quality_report['date_range'] = {
                'min_date': df_transaksi['tanggal_transaksi'].min(),
                'max_date': df_transaksi['tanggal_transaksi'].max()
            }
        
        return quality_report
    
    @staticmethod
    def check_data_consistency(df_produk: pd.DataFrame, 
                             df_toko: pd.DataFrame, 
                             df_transaksi: pd.DataFrame) -> Dict[str, bool]:
        """Check data consistency across datasets"""
        
        consistency_checks = {}
        
        # Check if all products in transactions exist in produk table
        produk_in_trans = set(df_transaksi['id_produk'].unique())
        produk_in_master = set(df_produk['id_produk'].unique())
        consistency_checks['all_products_exist'] = produk_in_trans.issubset(produk_in_master)
        
        # Check if all stores in transactions exist in toko table
        if 'id_toko' in df_transaksi.columns:
            toko_in_trans = set(df_transaksi['id_toko'].unique())
            toko_in_master = set(df_toko['id_toko'].unique())
            consistency_checks['all_stores_exist'] = toko_in_trans.issubset(toko_in_master)
        
        return consistency_checks


def get_current_event(date, events_calendar=None):
    """
    Get current event for a given date
    Migrated from notebook logic
    """
    if events_calendar is None:
        events_calendar = Config.EVENTS_CALENDAR
    
    for event, (start, end) in events_calendar.items():
        if start <= date <= end:
            return event.split('_')[0]  # Return main event name
    
    if date.weekday() >= 4:  # Friday (4), Saturday (5), Sunday (6)
        return "Promo Akhir Pekan"
    
    return "Hari Biasa"
