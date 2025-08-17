"""
Model 1: Product Urgency Scorer
Determines which products need discounting based on urgency score
"""
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, Dict, List
import joblib
import os

from src.config import Config, ModelPaths
from src.utils.feature_engineering import FeatureEngineer


class ProductUrgencyModel:
    """
    Model to predict urgency scores for products
    Migrated from notebook Model 1 logic
    """
    
    def __init__(self):
        self.config = Config()
        self.model = None
        self.scaler = MinMaxScaler(feature_range=(0, 100))
        self.feature_columns = self.config.MODEL_FEATURES
        self.feature_engineer = FeatureEngineer()
    
    def prepare_training_data(self, df_produk: pd.DataFrame, 
                            df_transaksi: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        """
        Prepare training data with features and targets
        """
        print("Preparing training data for urgency model...")
        
        # Create features using feature engineer
        df_model = self.feature_engineer.create_urgency_features(df_produk, df_transaksi)
        df_model = self.feature_engineer.calculate_urgency_score(df_model)
        
        # Prepare features and target
        X = df_model[self.feature_columns].fillna(0)
        y = df_model['urgency_score'].values
        
        print(f"Training data prepared: {X.shape[0]} samples, {X.shape[1]} features")
        
        return df_model, X, y
    
    def train(self, df_produk: pd.DataFrame, df_transaksi: pd.DataFrame, 
              test_size: float = 0.2) -> Dict[str, float]:
        """
        Train the urgency prediction model
        """
        print("Training Product Urgency Model...")
        
        # Prepare data
        df_model, X, y = self.prepare_training_data(df_produk, df_transaksi)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.config.URGENCY_MODEL_PARAMS['random_state']
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Initialize and train model
        self.model = lgb.LGBMRegressor(**self.config.URGENCY_MODEL_PARAMS)
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='mae',
            callbacks=[lgb.early_stopping(20, verbose=False)]
        )
        
        # Evaluate model
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        from sklearn.metrics import mean_absolute_error, r2_score
        
        metrics = {
            'train_mae': mean_absolute_error(y_train, train_pred),
            'test_mae': mean_absolute_error(y_test, test_pred),
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred)
        }
        
        print("Training completed!")
        print(f"Test MAE: {metrics['test_mae']:.4f}")
        print(f"Test R²: {metrics['test_r2']:.4f}")
        
        return metrics
    
    def predict_urgency_scores(self, df_produk: pd.DataFrame, 
                             df_transaksi: pd.DataFrame) -> pd.DataFrame:
        """
        Predict urgency scores for all products
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        print("Predicting urgency scores...")
        
        # Prepare features
        df_model = self.feature_engineer.create_urgency_features(df_produk, df_transaksi)
        X = df_model[self.feature_columns].fillna(0)
        
        # Predict scores
        predicted_scores = self.model.predict(X)
        
        # Create results dataframe - include all necessary columns for T-Learner
        df_results = df_model.copy()  # Keep all original columns including id_toko
        
        df_results['skor_prediksi'] = predicted_scores
        
        # Sort by prediction score (highest first)
        df_results = df_results.sort_values('skor_prediksi', ascending=False)
        
        print(f"Predicted urgency scores for {len(df_results)} products")
        
        return df_results
    
    def get_top_candidates(self, df_results: pd.DataFrame, 
                          total_slots: int = None) -> pd.DataFrame:
        """
        Get top product candidates using dynamic quota allocation
        Migrated from notebook quota allocation logic
        """
        if total_slots is None:
            total_slots = self.config.TOTAL_SLOT_PROMOSI
        
        print(f"Selecting top {total_slots} product candidates...")
        
        # Mark candidates above threshold
        df_results['is_candidate'] = df_results['skor_prediksi'] > self.config.SKOR_THRESHOLD
        
        # Count candidates per category
        candidate_counts = df_results[df_results['is_candidate']].groupby('kategori_produk').size()
        total_candidates = candidate_counts.sum()
        
        print(f"Found {total_candidates} candidates above threshold")
        
        if total_candidates <= total_slots:
            # If we have fewer candidates than slots, take all candidates
            return df_results[df_results['is_candidate']].copy()
        
        # Dynamic quota allocation
        df_top_candidates = []
        
        for kategori in candidate_counts.index:
            kategori_candidates = df_results[
                (df_results['kategori_produk'] == kategori) & 
                (df_results['is_candidate'])
            ].copy()
            
            # Calculate quota for this category
            kategori_quota = int((candidate_counts[kategori] / total_candidates) * total_slots)
            kategori_quota = max(1, kategori_quota)  # Ensure at least 1 slot per category
            
            # Take top products from this category
            top_from_kategori = kategori_candidates.head(kategori_quota)
            df_top_candidates.append(top_from_kategori)
        
        # Combine all categories
        df_final_candidates = pd.concat(df_top_candidates, ignore_index=True)
        
        # If we still have remaining slots, fill with highest scoring products
        remaining_slots = total_slots - len(df_final_candidates)
        if remaining_slots > 0:
            used_ids = set(df_final_candidates['id_produk'])
            remaining_candidates = df_results[
                (~df_results['id_produk'].isin(used_ids)) & 
                (df_results['is_candidate'])
            ].head(remaining_slots)
            
            if not remaining_candidates.empty:
                df_final_candidates = pd.concat([df_final_candidates, remaining_candidates], ignore_index=True)
        
        # Sort by score
        df_final_candidates = df_final_candidates.sort_values('skor_prediksi', ascending=False)
        
        print(f"Selected {len(df_final_candidates)} final candidates")
        
        return df_final_candidates
    
    def save_model(self, save_path: str = None):
        """Save trained model and scaler"""
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        if save_path is None:
            os.makedirs("saved_models", exist_ok=True)
            model_path = ModelPaths.URGENCY_MODEL
            scaler_path = ModelPaths.URGENCY_SCALER
        else:
            model_path = f"{save_path}_model.pkl"
            scaler_path = f"{save_path}_scaler.pkl"
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        
        print(f"Model saved to {model_path}")
        print(f"Scaler saved to {scaler_path}")
    
    def load_model(self, model_path: str = None):
        """Load trained model and scaler"""
        if model_path is None:
            model_path = ModelPaths.URGENCY_MODEL
            scaler_path = ModelPaths.URGENCY_SCALER
        else:
            scaler_path = f"{model_path}_scaler.pkl"
            model_path = f"{model_path}_model.pkl"
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        print(f"Model loaded from {model_path}")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance from trained model"""
        if self.model is None:
            raise ValueError("Model not trained yet.")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df
