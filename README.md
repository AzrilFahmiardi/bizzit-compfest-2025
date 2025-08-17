# Bizzt Recommendation API

🚀 **Production-ready API** untuk sistem rekomendasi strategi diskon produk retail

## 📋 Features

- ✅ **Recommendation Engine** - ML-powered product recommendations
- ✅ **Analytics Dashboard** - Transaction trends and insights
- ✅ **Business Metrics** - Revenue, Transactions, AOV with growth tracking
- ✅ **Real-time Processing** - Background model regeneration
- ✅ **REST API** - Clean, documented endpoints

## 🌐 API Endpoints

### Core Recommendations
- `GET /api/recommendations` - Top product recommendations
- `GET /api/recommendations/stats` - Recommendation statistics
- `POST /api/recommendations/regenerate` - Regenerate recommendations

### Analytics
- `GET /api/analytics/trends/weekly` - Weekly transaction trends
- `GET /api/analytics/events` - Event-based analysis
- `GET /api/analytics/categories` - Category performance

### Business Metrics
- `GET /api/metrics/dashboard` - Dashboard KPIs
- `GET /api/metrics/business` - Business metrics with growth
- `GET /api/metrics/revenue` - Revenue breakdown

### Health Check
- `GET /health` - Service health check

## 🚀 Deployment

Deployed on **Render.com** with auto-scaling and monitoring.

### Environment Variables
- `FLASK_ENV=production`
- `PORT` (automatically set by Render)

## 📊 Data Sources

- Product catalog (87K+ products)
- Transaction history (600K+ transactions)
- Store demographics and customer profiles

## 🛠 Tech Stack

- **Framework**: Flask + Gunicorn
- **ML**: scikit-learn, LightGBM
- **Data**: Pandas, NumPy
- **Deployment**: Render.com
- **Monitoring**: Health checks + logging

## 📈 Performance

- **Response time**: <200ms average
- **Uptime**: 99.9% target
- **Auto-scaling**: Based on traffic
- **Data refresh**: Real-time capable

---

**API Documentation**: Available at root endpoint `/`  
**Health Check**: `/health`  
**Version**: 2.0.0
