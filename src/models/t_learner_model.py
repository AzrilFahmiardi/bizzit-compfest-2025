"""
Model 2: T-Learner for Discount Strategy Selection
Determines optimal discount strategy for each product using causal inference
"""
import pandas as pd
import numpy as np
import lightgbm as lgb
from typing import Dict, List, Tuple, Any
import joblib
import os

from src.config import Config, ModelPaths
from src.utils.feature_engineering import FeatureEngineer
from src.utils.data_loader import get_current_event


class TLearnerModel:
    """
    T-Learner implementation for discount strategy optimization
    Migrated from notebook Model 2 logic
    """
    
    def __init__(self):
        self.config = Config()
        self.trained_models = {}  # Dictionary to store models for each treatment
        self.feature_columns = []
        self.feature_engineer = FeatureEngineer()
    
    def prepare_master_training_data(self, df_produk: pd.DataFrame, 
                                   df_toko: pd.DataFrame, 
                                   df_transaksi: pd.DataFrame) -> pd.DataFrame:
        """
        Create master training dataset by combining all data sources
        """
        print("Creating master training dataset...")
        
        # Merge transactions with products (avoiding duplicate id_toko if present)
        if 'id_toko' in df_produk.columns:
            df_produk_cleaned = df_produk.drop(columns=['id_toko'])
        else:
            df_produk_cleaned = df_produk
        
        df_master = pd.merge(df_transaksi, df_produk_cleaned, on='id_produk', how='left')
        df_master = pd.merge(df_master, df_toko, on='id_toko', how='left')
        
        # Create profit_transaksi column - sesuai dengan notebook
        df_master['profit_transaksi'] = df_master['harga_promosi'] - df_master['harga_beli']
        
        # Add event context
        df_master['current_event'] = df_master['tanggal_transaksi'].apply(get_current_event)
        
        print(f"Master training data created: {df_master.shape}")
        
        return df_master
    
    def prepare_features(self, df_master: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply feature engineering for T-Learner
        """
        print("Applying feature engineering...")
        
        df_featured, feature_columns = self.feature_engineer.create_t_learner_features(df_master)
        self.feature_columns = feature_columns
        
        print(f"Feature engineering completed: {len(feature_columns)} features")
        
        return df_featured, feature_columns
    
    def split_by_treatment(self, df_featured: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Split data by treatment (discount type) for T-Learner training
        """
        print("Splitting data by treatment...")
        
        if 'tipe_diskon' not in df_featured.columns:
            raise ValueError("Column 'tipe_diskon' not found in data")
        
        treatments = {}
        for treatment_name in df_featured['tipe_diskon'].unique():
            treatment_df = df_featured[df_featured['tipe_diskon'] == treatment_name].copy()
            treatments[treatment_name] = treatment_df
            print(f"- {treatment_name}: {len(treatment_df)} samples")
        
        return treatments
    
    def train_individual_models(self, treatments: Dict[str, pd.DataFrame], 
                              target_column: str = 'profit_transaksi',
                              min_samples: int = 100) -> Dict[str, Any]:
        """
        Train individual models for each treatment
        """
        print("Training individual treatment models...")
        
        self.trained_models = {}
        training_metrics = {}
        
        for treatment_name, df_treatment in treatments.items():
            print(f"Training model for: '{treatment_name}'")
            
            if len(df_treatment) < min_samples:
                print(f"  Warning: Insufficient data ({len(df_treatment)} samples), skipping...")
                continue
            
            # Prepare features and target
            X_train = df_treatment[self.feature_columns]
            y_train = df_treatment[target_column]
            
            # Train model
            model = lgb.LGBMRegressor(**self.config.T_LEARNER_MODEL_PARAMS)
            model.fit(X_train, y_train)
            
            # Store model
            self.trained_models[treatment_name] = model
            
            # Calculate basic metrics
            y_pred = model.predict(X_train)
            from sklearn.metrics import mean_absolute_error, r2_score
            
            training_metrics[treatment_name] = {
                'samples': len(df_treatment),
                'mae': mean_absolute_error(y_train, y_pred),
                'r2': r2_score(y_train, y_pred)
            }
            
            print(f"  Model trained successfully (MAE: {training_metrics[treatment_name]['mae']:.2f})")
        
        print(f"Training completed for {len(self.trained_models)} treatments")
        
        return training_metrics
    
    def train(self, df_produk: pd.DataFrame, df_toko: pd.DataFrame, 
              df_transaksi: pd.DataFrame) -> Dict[str, Any]:
        """
        Complete training pipeline for T-Learner
        """
        print("Starting T-Learner training pipeline...")
        
        # Prepare master dataset
        df_master = self.prepare_master_training_data(df_produk, df_toko, df_transaksi)
        
        # Apply feature engineering
        df_featured, _ = self.prepare_features(df_master)
        
        # Split by treatment
        treatments = self.split_by_treatment(df_featured)
        
        # Train individual models
        metrics = self.train_individual_models(treatments)
        
        print("T-Learner training completed!")
        
        return metrics
    
    def predict_all_treatments(self, X_features: pd.DataFrame) -> pd.DataFrame:
        """
        Predict outcomes for all treatments
        """
        if not self.trained_models:
            raise ValueError("No trained models found. Train the model first.")
        
        print("Predicting outcomes for all treatments...")
        
        predictions = {}
        for treatment_name, model in self.trained_models.items():
            predictions[treatment_name] = model.predict(X_features)
        
        df_predictions = pd.DataFrame(predictions, index=X_features.index)
        
        return df_predictions
    
    def calculate_uplift_and_recommend(self, df_predictions: pd.DataFrame, 
                                     baseline_treatment: str = 'Tanpa Diskon') -> pd.DataFrame:
        """
        Calculate uplift and recommend best strategy for each product
        """
        print("Calculating uplift and generating recommendations...")
        
        # Calculate uplift relative to baseline
        if baseline_treatment in df_predictions.columns:
            baseline_profit = df_predictions[baseline_treatment]
            df_uplift = df_predictions.drop(columns=[baseline_treatment], errors='ignore').subtract(baseline_profit, axis=0)
        else:
            print(f"Warning: Baseline treatment '{baseline_treatment}' not found")
            df_uplift = df_predictions
            baseline_profit = 0
        
        # Create recommendations
        df_recommendations = pd.DataFrame(index=df_uplift.index)
        
        # Find best strategy for each product
        df_recommendations['rekomendasi_strategi'] = df_uplift.idxmax(axis=1)
        df_recommendations['estimasi_uplift_profit'] = df_uplift.max(axis=1)
        
        # Handle negative uplifts (recommend no discount)
        negative_mask = df_recommendations['estimasi_uplift_profit'] < 0
        df_recommendations.loc[negative_mask, 'rekomendasi_strategi'] = baseline_treatment
        df_recommendations.loc[negative_mask, 'estimasi_uplift_profit'] = 0
        
        print(f"Generated recommendations for {len(df_recommendations)} products")
        
        return df_recommendations
    
    def generate_recommendations(self, df_produk_candidates: pd.DataFrame, 
                               df_toko: pd.DataFrame,
                               current_event: str = "Promo Akhir Pekan") -> pd.DataFrame:
        """
        Generate discount strategy recommendations for candidate products
        """
        print("Generating discount strategy recommendations...")
        
        # Prepare features for inference
        X_features, df_context = self.feature_engineer.prepare_recommendation_features(
            df_produk_candidates, df_toko, self.feature_columns, current_event
        )
        
        # Predict all treatments
        df_predictions = self.predict_all_treatments(X_features)
        
        # Calculate uplift and recommendations
        df_recommendations = self.calculate_uplift_and_recommend(df_predictions)
        
        # Combine with product context
        df_final = pd.concat([
            df_context[['id_produk', 'nama_produk', 'kategori_produk', 'id_toko']].reset_index(drop=True),
            df_recommendations.reset_index(drop=True)
        ], axis=1)
        
        # Aggregate by product (average across stores)
        df_aggregated = df_final.groupby(['id_produk', 'nama_produk', 'kategori_produk']).agg({
            'rekomendasi_strategi': lambda x: x.mode()[0] if not x.empty else "N/A",
            'estimasi_uplift_profit': 'mean'
        }).reset_index().sort_values('estimasi_uplift_profit', ascending=False)
        
        df_aggregated.rename(columns={
            'rekomendasi_strategi': 'rekomendasi_utama',
            'estimasi_uplift_profit': 'rata_rata_uplift_profit'
        }, inplace=True)
        
        print(f"Final recommendations generated for {len(df_aggregated)} products")
        
        return df_aggregated
    
    def save_models(self, save_path: str = None):
        """Save all trained models"""
        if not self.trained_models:
            raise ValueError("No models to save. Train the models first.")
        
        if save_path is None:
            save_path = ModelPaths.T_LEARNER_MODELS
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        model_data = {
            'trained_models': self.trained_models,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, save_path)
        print(f"T-Learner models saved to {save_path}")
    
    def load_models(self, load_path: str = None):
        """Load trained models"""
        if load_path is None:
            load_path = ModelPaths.T_LEARNER_MODELS
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        model_data = joblib.load(load_path)
        self.trained_models = model_data['trained_models']
        self.feature_columns = model_data['feature_columns']
        
        print(f"T-Learner models loaded from {load_path}")
        print(f"Available treatments: {list(self.trained_models.keys())}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about trained models"""
        if not self.trained_models:
            return {"status": "No models trained"}
        
        info = {
            "num_treatments": len(self.trained_models),
            "treatments": list(self.trained_models.keys()),
            "num_features": len(self.feature_columns),
            "feature_columns": self.feature_columns
        }
        
        return info
