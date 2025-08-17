# Bizzit Recommendation System

A comprehensive machine learning system for product discount recommendation and promotional strategy optimization.

## 🎯 Overview

This system consists of three main components:
1. **Product Urgency Model**: Identifies products that need promotional intervention
2. **T-Learner Strategy Model**: Determines optimal discount strategy for each product
3. **Recommendation Engine**: Applies business rules and generates final actionable recommendations

## 📁 Project Structure

```
compfest_bizzit/
├── data/                       # Data files
│   ├── produk_v4.csv
│   ├── toko.csv
│   └── transaksi_v4.csv
├── src/                        # Source code
│   ├── config.py              # Configuration settings
│   ├── main.py                # Main pipeline
│   ├── core/                  # Core business logic
│   │   └── recommendation_engine.py
│   ├── models/                # ML models
│   │   ├── urgency_model.py
│   │   └── t_learner_model.py
│   └── utils/                 # Utilities
│       ├── data_loader.py
│       └── feature_engineering.py
├── saved_models/              # Trained model artifacts
├── results/                   # Output results
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run Complete Pipeline

```python
from src.main import BizzitRecommendationPipeline

# Initialize pipeline
pipeline = BizzitRecommendationPipeline(use_local_data=True)

# Run complete training and recommendation pipeline
results = pipeline.run_complete_pipeline(save_models=True, total_slots=1000)
```

### 3. Run Inference Only (with pre-trained models)

```python
# Load trained models and generate recommendations
pipeline = BizzitRecommendationPipeline(use_local_data=True)
recommendations = pipeline.predict_only(total_slots=1000)
```

## 📊 Models Description

### Model 1: Product Urgency Scorer
- **Purpose**: Identify products needing promotional intervention
- **Algorithm**: LightGBM Regressor
- **Features**: Sales history, expiry dates, inventory levels
- **Output**: Urgency scores (0-100) for product ranking

### Model 2: T-Learner Strategy Optimizer
- **Purpose**: Determine optimal discount strategy per product
- **Algorithm**: Multiple LightGBM Regressors (one per treatment)
- **Strategies**: BOGO, Generic Discount, Event-based, Expired Discount
- **Output**: Expected profit uplift per strategy

### Model 3: Recommendation Engine
- **Purpose**: Apply business rules and generate final recommendations
- **Logic**: Event calendar, competitor pricing, category analysis
- **Output**: Final promotional calendar with discount magnitudes

## 🛠️ Configuration

Key parameters can be adjusted in `src/config.py`:

- `TOTAL_SLOT_PROMOSI`: Total promotional slots available
- `SKOR_THRESHOLD`: Minimum urgency score for candidates
- `BOGO_CATEGORIES`: Product categories suitable for BOGO offers
- Model hyperparameters for both urgency and T-learner models

## 📈 Usage Examples

### Training Models

```python
from src.models.urgency_model import ProductUrgencyModel
from src.models.t_learner_model import TLearnerModel
from src.utils.data_loader import DataLoader

# Load data
loader = DataLoader()
df_produk, df_toko, df_transaksi = loader.load_all_data()

# Train urgency model
urgency_model = ProductUrgencyModel()
metrics = urgency_model.train(df_produk, df_transaksi)
urgency_model.save_model()

# Train T-Learner
t_learner = TLearnerModel()
metrics = t_learner.train(df_produk, df_toko, df_transaksi)
t_learner.save_models()
```

### Generating Recommendations

```python
from src.core.recommendation_engine import RecommendationEngine

# Get candidates from urgency model
candidates = urgency_model.get_top_candidates(urgency_scores, total_slots=1000)

# Get strategy recommendations from T-Learner
strategy_recs = t_learner.generate_recommendations(candidates, df_toko)

# Apply business rules for final recommendations
rec_engine = RecommendationEngine()
final_recs = rec_engine.generate_final_recommendations(
    strategy_recs, df_produk, df_transaksi
)
```

## 📋 Output Format

The final recommendations include:

- `id_produk`: Product identifier
- `nama_produk`: Product name
- `kategori_produk`: Product category
- `rekomendasi_detail`: Specific discount strategy (e.g., "Event Based (Ramadan)")
- `rekomendasi_besaran`: Discount percentage (0.05 = 5%)
- `rata_rata_uplift_profit`: Expected profit uplift in IDR

## 🧪 Model Performance

The system includes comprehensive evaluation metrics:

- **Urgency Model**: MAE, R², Feature importance
- **T-Learner**: Individual treatment model performance
- **Business Impact**: Total estimated uplift, strategy distribution

## 🔧 Customization

### Adding New Discount Strategies
1. Add strategy to training data with `tipe_diskon` column
2. T-Learner will automatically train a model for the new strategy
3. Update business rules in `RecommendationEngine` if needed

### Modifying Business Rules
- Edit `get_recommendation_magnitude()` in `RecommendationEngine`
- Update event calendars in `config.py`
- Adjust category mappings for different strategies

### Feature Engineering
- Add new features in `FeatureEngineer` class
- Update feature lists in model configurations
- Ensure feature consistency across training and inference

## 📊 Monitoring & Evaluation

The system provides comprehensive logging and metrics:

- Data quality validation
- Model performance metrics
- Business impact estimates
- Recommendation distribution analysis

## 🤝 Contributing

1. Follow the existing code structure
2. Add unit tests for new features
3. Update documentation for any changes
4. Ensure backward compatibility

## 📝 License

This project is developed for the Compfest Bizzit 2025 competition.

---

**Generated from Jupyter Notebook migration - August 2025**
