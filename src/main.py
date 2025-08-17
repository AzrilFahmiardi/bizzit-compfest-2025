"""
Main pipeline for the Bizzit Recommendation System
Orchestrates the complete workflow from data loading to final recommendations
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
from typing import Dict, Any, Optional

from src.config import Config, ModelPaths
from src.utils.data_loader import DataLoader, DataValidator
from src.models.urgency_model import ProductUrgencyModel
from src.models.t_learner_model import TLearnerModel
from src.core.recommendation_engine import RecommendationEngine


class BizzitRecommendationPipeline:
    """
    Main pipeline class that orchestrates the complete recommendation workflow
    """
    
    def __init__(self, use_local_data: bool = True):
        self.config = Config()
        self.use_local_data = use_local_data
        
        # Initialize components
        self.data_loader = DataLoader(use_local=use_local_data)
        self.urgency_model = ProductUrgencyModel()
        self.t_learner_model = TLearnerModel()
        self.recommendation_engine = RecommendationEngine()
        
        # Data containers
        self.df_produk = None
        self.df_toko = None
        self.df_transaksi = None
        
        # Results containers
        self.urgency_results = None
        self.strategy_results = None
        self.final_recommendations = None
    
    def load_and_validate_data(self) -> Dict[str, Any]:
        """
        Load all datasets and perform validation
        """
        print("="*60)
        print("STEP 1: DATA LOADING AND VALIDATION")
        print("="*60)
        
        # Load data
        self.df_produk, self.df_toko, self.df_transaksi = self.data_loader.load_all_data()
        
        # Validate data quality
        quality_report = DataValidator.validate_data_quality(
            self.df_produk, self.df_toko, self.df_transaksi
        )
        
        # Check consistency
        consistency_report = DataValidator.check_data_consistency(
            self.df_produk, self.df_toko, self.df_transaksi
        )
        
        print("Data validation completed!")
        print(f"Quality checks: {len(quality_report)} metrics")
        print(f"Consistency checks: {consistency_report}")
        
        return {
            'quality_report': quality_report,
            'consistency_report': consistency_report
        }
    
    def train_urgency_model(self, save_model: bool = True) -> Dict[str, float]:
        """
        Train the product urgency scoring model (Model 1)
        """
        print("="*60)
        print("STEP 2: TRAINING PRODUCT URGENCY MODEL")
        print("="*60)
        
        if self.df_produk is None or self.df_transaksi is None:
            raise ValueError("Data not loaded. Call load_and_validate_data() first.")
        
        # Train the model
        metrics = self.urgency_model.train(self.df_produk, self.df_transaksi)
        
        # Save model if requested
        if save_model:
            self.urgency_model.save_model()
        
        print("Urgency model training completed!")
        return metrics
    
    def generate_product_candidates(self, total_slots: int = None) -> pd.DataFrame:
        """
        Generate product candidates using the urgency model
        """
        print("="*60)
        print("STEP 3: GENERATING PRODUCT CANDIDATES")
        print("="*60)
        
        if self.urgency_model.model is None:
            raise ValueError("Urgency model not trained. Call train_urgency_model() first.")
        
        if total_slots is None:
            total_slots = self.config.TOTAL_SLOT_PROMOSI
        
        # Predict urgency scores
        urgency_scores = self.urgency_model.predict_urgency_scores(
            self.df_produk, self.df_transaksi
        )
        
        # Get top candidates
        candidates = self.urgency_model.get_top_candidates(urgency_scores, total_slots)
        
        self.urgency_results = candidates
        
        print(f"Generated {len(candidates)} product candidates")
        return candidates
    
    def train_strategy_model(self, save_model: bool = True) -> Dict[str, Any]:
        """
        Train the T-Learner model for strategy selection (Model 2)
        """
        print("="*60)
        print("STEP 4: TRAINING STRATEGY SELECTION MODEL")
        print("="*60)
        
        if any(df is None for df in [self.df_produk, self.df_toko, self.df_transaksi]):
            raise ValueError("Data not loaded. Call load_and_validate_data() first.")
        
        # Train T-Learner
        metrics = self.t_learner_model.train(self.df_produk, self.df_toko, self.df_transaksi)
        
        # Save model if requested
        if save_model:
            self.t_learner_model.save_models()
        
        print("Strategy selection model training completed!")
        return metrics
    
    def generate_strategy_recommendations(self, product_candidates: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate discount strategy recommendations for candidate products
        """
        print("="*60)
        print("STEP 5: GENERATING STRATEGY RECOMMENDATIONS")
        print("="*60)
        
        if self.t_learner_model.trained_models == {}:
            raise ValueError("T-Learner model not trained. Call train_strategy_model() first.")
        
        if product_candidates is None:
            if self.urgency_results is None:
                raise ValueError("No product candidates available. Call generate_product_candidates() first.")
            product_candidates = self.urgency_results
        
        # Generate recommendations
        recommendations = self.t_learner_model.generate_recommendations(
            product_candidates, self.df_toko
        )
        
        self.strategy_results = recommendations
        
        print(f"Generated strategy recommendations for {len(recommendations)} products")
        return recommendations
    
    def generate_final_recommendations(self, strategy_results: pd.DataFrame = None) -> pd.DataFrame:
        """
        Generate final enhanced recommendations with business rules
        """
        print("="*60)
        print("STEP 6: GENERATING FINAL RECOMMENDATIONS")
        print("="*60)
        
        if strategy_results is None:
            if self.strategy_results is None:
                raise ValueError("No strategy results available. Call generate_strategy_recommendations() first.")
            strategy_results = self.strategy_results
        
        # Generate final recommendations
        final_recs = self.recommendation_engine.generate_final_recommendations(
            strategy_results, self.df_produk, self.df_transaksi
        )
        
        self.final_recommendations = final_recs
        
        # Get summary
        summary = self.recommendation_engine.get_recommendation_summary(final_recs)
        
        print("Final recommendations generated!")
        print(f"Total products: {summary['total_products']}")
        print(f"Strategy distribution: {summary['strategy_distribution']}")
        
        return final_recs
    
    def run_complete_pipeline(self, save_models: bool = True, 
                            total_slots: int = None) -> Dict[str, Any]:
        """
        Run the complete recommendation pipeline
        """
        print("🚀 STARTING BIZZIT RECOMMENDATION PIPELINE")
        print("="*60)
        
        start_time = datetime.now()
        results = {}
        
        try:
            # Step 1: Load and validate data
            validation_results = self.load_and_validate_data()
            results['data_validation'] = validation_results
            
            # Step 2: Train urgency model
            urgency_metrics = self.train_urgency_model(save_model=save_models)
            results['urgency_model_metrics'] = urgency_metrics
            
            # Step 3: Generate product candidates
            candidates = self.generate_product_candidates(total_slots=total_slots)
            results['num_candidates'] = len(candidates)
            
            # Step 4: Train strategy model
            strategy_metrics = self.train_strategy_model(save_model=save_models)
            results['strategy_model_metrics'] = strategy_metrics
            
            # Step 5: Generate strategy recommendations
            strategy_recs = self.generate_strategy_recommendations(candidates)
            results['num_strategy_recommendations'] = len(strategy_recs)
            
            # Step 6: Generate final recommendations
            final_recs = self.generate_final_recommendations(strategy_recs)
            results['num_final_recommendations'] = len(final_recs)
            
            # Final summary
            summary = self.recommendation_engine.get_recommendation_summary(final_recs)
            results['recommendation_summary'] = summary
            
            # Save final results
            if save_models:
                self.save_results(final_recs, summary)
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("="*60)
            print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"⏱️  Total execution time: {duration}")
            print(f"📊 Final recommendations: {len(final_recs)} products")
            print("="*60)
            
            results['execution_time'] = str(duration)
            results['status'] = 'success'
            
        except Exception as e:
            end_time = datetime.now()
            duration = end_time - start_time
            
            print("="*60)
            print("❌ PIPELINE FAILED!")
            print(f"⚠️  Error: {str(e)}")
            print(f"⏱️  Execution time: {duration}")
            print("="*60)
            
            results['error'] = str(e)
            results['execution_time'] = str(duration)
            results['status'] = 'failed'
        
        return results
    
    def save_results(self, final_recommendations: pd.DataFrame, summary: Dict[str, Any]):
        """
        Save final results and metadata
        """
        print("Saving results...")
        
        # Create results directory
        os.makedirs("results", exist_ok=True)
        
        # Ensure we have the correct column order for CSV export
        csv_columns = [
            'id_produk', 'nama_produk', 'kategori_produk', 
            'rekomendasi_detail', 'rekomendasi_besaran', 
            'start_date', 'end_date', 'rata_rata_uplift_profit'
        ]
        
        # Make sure all required columns exist
        for col in csv_columns:
            if col not in final_recommendations.columns:
                if col in ['start_date', 'end_date']:
                    # Add default dates if missing
                    final_recommendations[col] = '2025-03-07' if col == 'start_date' else '2025-03-09'
                else:
                    print(f"Warning: Column '{col}' missing from recommendations")
        
        # Save final recommendations with specified column order
        final_recommendations[csv_columns].to_csv("results/final_recommendations.csv", index=False)
        
        # Save summary
        with open("results/recommendation_summary.json", 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            summary_serializable = {}
            for key, value in summary.items():
                if isinstance(value, (pd.Series, pd.DataFrame)):
                    summary_serializable[key] = value.to_dict()
                elif isinstance(value, np.number):
                    summary_serializable[key] = float(value)
                else:
                    summary_serializable[key] = value
            
            json.dump(summary_serializable, f, indent=2, default=str)
        
        # Save metadata
        metadata = {
            'generation_date': datetime.now().isoformat(),
            'total_products': len(final_recommendations),
            'model_versions': {
                'urgency_model': 'v1.0',
                't_learner': 'v1.0',
                'recommendation_engine': 'v1.0'
            }
        }
        
        with open("results/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Results saved to 'results/' directory")
    
    def load_trained_models(self):
        """
        Load previously trained models
        """
        print("Loading trained models...")
        
        try:
            self.urgency_model.load_model()
            print("✅ Urgency model loaded")
        except FileNotFoundError:
            print("⚠️  Urgency model not found")
        
        try:
            self.t_learner_model.load_models()
            print("✅ T-Learner models loaded")
        except FileNotFoundError:
            print("⚠️  T-Learner models not found")
    
    def predict_only(self, total_slots: int = None) -> pd.DataFrame:
        """
        Run prediction only (assumes models are already trained)
        """
        print("🔮 RUNNING PREDICTION PIPELINE")
        print("="*60)
        
        # Load data
        self.load_and_validate_data()
        
        # Load trained models
        self.load_trained_models()
        
        # Generate candidates
        candidates = self.generate_product_candidates(total_slots=total_slots)
        
        # Generate strategy recommendations
        strategy_recs = self.generate_strategy_recommendations(candidates)
        
        # Generate final recommendations
        final_recs = self.generate_final_recommendations(strategy_recs)
        
        print("✅ Prediction completed!")
        
        return final_recs


def main():
    """
    Main execution function
    """
    # Initialize pipeline
    pipeline = BizzitRecommendationPipeline(use_local_data=True)
    
    # Run complete pipeline
    results = pipeline.run_complete_pipeline(
        save_models=True,
        total_slots=1000  # Can be adjusted
    )
    
    # Print results summary
    if results['status'] == 'success':
        print("\n📋 EXECUTION SUMMARY:")
        print(f"• Data validation: ✅")
        print(f"• Urgency model: ✅ (R²: {results['urgency_model_metrics'].get('test_r2', 'N/A'):.4f})")
        print(f"• Strategy models: ✅ ({len(results['strategy_model_metrics'])} treatments)")
        print(f"• Product candidates: {results['num_candidates']}")
        print(f"• Final recommendations: {results['num_final_recommendations']}")
        print(f"• Total estimated uplift: Rp {results['recommendation_summary']['total_estimated_uplift']:,.0f}")
    
    return results


if __name__ == "__main__":
    main()
