"""
Test script to verify the migrated codebase works correctly
"""
import sys
import os
import traceback
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import BizzitRecommendationPipeline


def test_data_loading():
    """Test data loading functionality"""
    print("🧪 Testing data loading...")
    
    try:
        pipeline = BizzitRecommendationPipeline(use_local_data=True)
        validation_results = pipeline.load_and_validate_data()
        
        print("✅ Data loading successful")
        print(f"   - Products: {len(pipeline.df_produk)}")
        print(f"   - Stores: {len(pipeline.df_toko)}")
        print(f"   - Transactions: {len(pipeline.df_transaksi)}")
        
        return True, pipeline
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        traceback.print_exc()
        return False, None


def test_urgency_model(pipeline):
    """Test urgency model training"""
    print("\n🧪 Testing urgency model...")
    
    try:
        metrics = pipeline.train_urgency_model(save_model=False)
        candidates = pipeline.generate_product_candidates(total_slots=100)
        
        print("✅ Urgency model successful")
        print(f"   - Test R²: {metrics.get('test_r2', 'N/A'):.4f}")
        print(f"   - Test MAE: {metrics.get('test_mae', 'N/A'):.4f}")
        print(f"   - Candidates: {len(candidates)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Urgency model failed: {e}")
        traceback.print_exc()
        return False


def test_t_learner_model(pipeline):
    """Test T-Learner model training"""
    print("\n🧪 Testing T-Learner model...")
    
    try:
        metrics = pipeline.train_strategy_model(save_model=False)
        strategy_recs = pipeline.generate_strategy_recommendations()
        
        print("✅ T-Learner model successful")
        print(f"   - Treatments trained: {len(metrics)}")
        print(f"   - Strategy recommendations: {len(strategy_recs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ T-Learner model failed: {e}")
        traceback.print_exc()
        return False


def test_final_recommendations(pipeline):
    """Test final recommendation generation"""
    print("\n🧪 Testing final recommendations...")
    
    try:
        final_recs = pipeline.generate_final_recommendations()
        
        print("✅ Final recommendations successful")
        print(f"   - Final recommendations: {len(final_recs)}")
        print(f"   - Strategy distribution:")
        
        strategy_dist = final_recs['rekomendasi_detail'].value_counts().head()
        for strategy, count in strategy_dist.items():
            print(f"     • {strategy}: {count}")
        
        return True, final_recs
        
    except Exception as e:
        print(f"❌ Final recommendations failed: {e}")
        traceback.print_exc()
        return False, None


def test_complete_pipeline():
    """Test complete pipeline end-to-end"""
    print("\n🧪 Testing complete pipeline...")
    
    try:
        pipeline = BizzitRecommendationPipeline(use_local_data=True)
        results = pipeline.run_complete_pipeline(
            save_models=False, 
            total_slots=100  # Small number for testing
        )
        
        if results['status'] == 'success':
            print("✅ Complete pipeline successful")
            print(f"   - Execution time: {results['execution_time']}")
            print(f"   - Final recommendations: {results['num_final_recommendations']}")
            return True
        else:
            print(f"❌ Complete pipeline failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Complete pipeline failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 STARTING CODEBASE MIGRATION TESTS")
    print("="*60)
    
    start_time = datetime.now()
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Data Loading
    success, pipeline = test_data_loading()
    if success:
        tests_passed += 1
    else:
        print("⚠️  Skipping subsequent tests due to data loading failure")
        return
    
    # Test 2: Urgency Model
    success = test_urgency_model(pipeline)
    if success:
        tests_passed += 1
    
    # Test 3: T-Learner Model
    success = test_t_learner_model(pipeline)
    if success:
        tests_passed += 1
    
    # Test 4: Final Recommendations
    success, final_recs = test_final_recommendations(pipeline)
    if success:
        tests_passed += 1
        
        # Save test results
        if final_recs is not None:
            os.makedirs("test_results", exist_ok=True)
            final_recs.to_csv("test_results/test_recommendations.csv", index=False)
            print("   - Test results saved to test_results/")
    
    # Test 5: Complete Pipeline
    success = test_complete_pipeline()
    if success:
        tests_passed += 1
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"✅ Tests passed: {tests_passed}/{total_tests}")
    print(f"⏱️  Total test time: {duration}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Migration successful!")
        print("\n🚀 You can now run the main pipeline:")
        print("   python -m src.main")
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed. Please check the errors above.")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
