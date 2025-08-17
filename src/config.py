"""
Configuration file for the Bizzit Recommendation System
"""
from datetime import datetime, timedelta
import pandas as pd


class Config:
    """Main configuration class"""
    
    # Data paths
    DATA_DIR = "data"
    MODELS_DIR = "saved_models"
    
    # Data files
    PRODUK_FILE = "produk_v4.csv"
    TOKO_FILE = "toko.csv"
    TRANSAKSI_FILE = "transaksi_v4.csv"
    
    # Model parameters
    URGENCY_MODEL_PARAMS = {
        'objective': 'regression_l1',
        'metric': 'mae',
        'n_estimators': 1000,
        'learning_rate': 0.05,
        'random_state': 42,
        'n_jobs': -1,
        'num_leaves': 31
    }
    
    T_LEARNER_MODEL_PARAMS = {
        'random_state': 42,
        'n_estimators': 100,
        'verbose': -1
    }
    
    # Feature engineering parameters
    URGENCY_SCORE_WEIGHTS = {
        'kedaluwarsa': 0.6,  # Sesuai dengan notebook W_KEDALUWARSA = 0.6
        'kelambatan': 0.3,   # Sesuai dengan notebook W_KELAMBATAN = 0.3  
        'penjualan': 0.1     # Sesuai dengan notebook W_PENJUALAN = 0.1
    }
    
    # Model features - sesuai dengan fitur_model di notebook
    MODEL_FEATURES = [
        'margin',
        'hari_jual_minimal',
        'penjualan_harian_avg',
        'hari_sejak_penjualan_terakhir',
        'hari_menuju_kedaluwarsa',
        'margin_headroom'
    ]
    
    # Business rules
    TOTAL_SLOT_PROMOSI = 1000
    SKOR_THRESHOLD = 50
    
    # Event calendar
    EVENTS_CALENDAR = {
        "Ramadan_2023": (pd.Timestamp("2023-03-22"), pd.Timestamp("2023-04-21")),
        "Natal_2023": (pd.Timestamp("2023-12-15"), pd.Timestamp("2023-12-25")),
        "Tahun Baru_2023": (pd.Timestamp("2023-12-26"), pd.Timestamp("2024-01-02")),
        "Ramadan_2024": (pd.Timestamp("2024-03-10"), pd.Timestamp("2024-04-09")),
        "Natal_2024": (pd.Timestamp("2024-12-15"), pd.Timestamp("2024-12-25")),
        "Tahun Baru_2024": (pd.Timestamp("2024-12-26"), pd.Timestamp("2025-01-02")),
        "Ramadan_2025": (pd.Timestamp("2025-02-28"), pd.Timestamp("2025-03-29")),
        "Natal_2025": (pd.Timestamp("2025-12-15"), pd.Timestamp("2025-12-25")),
        "Tahun Baru_2025": (pd.Timestamp("2025-12-26"), pd.Timestamp("2026-01-02")),
    }
    
    # BOGO categories (expanded list from your analysis)
    BOGO_CATEGORIES = [
        'Biskuit', 'Soda', 'Cokelat', 'Sereal', 'Mie Instan', 'Jus Kemasan',
        'Teh', 'Pasta', 'Permen', 'Makaroni', 'Kuaci', 'Yogurt', 'Nugget',
        'Air Mineral', 'Minuman Isotonik', 'Keripik', 'Susu Kemasan',
        'Kopi Kemasan', 'Kacang', 'Ice Cream', 'Kentang Goreng', 'Sarden Kaleng', 'Kornet'
    ]
    
    # TFT parameters
    TFT_PARAMS = {
        'max_prediction_length': 90,
        'max_encoder_length': 180,
        'learning_rate': 0.03,
        'hidden_size': 8,
        'attention_head_size': 1,
        'dropout': 0.1,
        'hidden_continuous_size': 4
    }


class DataPaths:
    """Data path configurations"""
    
    @staticmethod
    def get_data_url(filename: str) -> str:
        """Get GitHub raw URL for data files"""
        base_url = "https://raw.githubusercontent.com/AzrilFahmiardi/bizzit-compfest-2025/refs/heads/master/data/"
        return f"{base_url}{filename}"


class ModelPaths:
    """Model path configurations"""
    
    URGENCY_MODEL = "saved_models/urgency_score_model.pkl"
    URGENCY_SCALER = "saved_models/urgency_scaler.pkl"
    T_LEARNER_MODELS = "saved_models/t_learner_models.pkl"
    TFT_MODEL = "saved_models/tft_model.pkl"
    METADATA = "saved_models/model_metadata.pkl"
