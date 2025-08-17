# Bizzt Recommendation API

API untuk sistem rekomendasi strategi diskon produk yang mengirimkan top 30 rekomendasi berdasarkan uplift profit.

## 🚀 Setup dan Installation

### Opsi 1: Menggunakan pandas (Rekomendasi)
```bash
pip install -r requirements_api.txt
python api.py
```

### Opsi 2: Tanpa pandas (jika ada masalah dependency)
```bash
pip install -r requirements_api_alternative.txt
python api_alternative.py
```

### 2. Pastikan File Results Tersedia
Pastikan folder `results/` berisi:
- `final_recommendations.csv`
- `metadata.json`
- `recommendation_summary.json`

### 3. Jalankan API
```bash
# Opsi 1: Versi dengan pandas
python api.py

# Opsi 2: Versi tanpa pandas (jika ada masalah dependency)
python api_alternative.py
```

API akan berjalan di: `http://localhost:5000`

## ⚠️ Troubleshooting

### Error: numpy.dtype size changed / binary incompatibility
Jika mendapat error seperti:
```
ValueError: numpy.dtype size changed, may indicate binary incompatibility
```

**Solusi 1**: Reinstall pandas dan numpy
```bash
pip uninstall pandas numpy -y
pip install numpy==1.24.3 pandas==1.5.3
```

**Solusi 2**: Gunakan API alternative
```bash
pip install -r requirements_api_alternative.txt
python api_alternative.py
```

## 📋 API Endpoints

### 1. Health Check
```http
GET /
```
Response:
```json
{
  "status": "OK",
  "message": "Bizzt Recommendation API is running",
  "timestamp": "2025-08-17T11:30:00",
  "version": "1.0.0"
}
```

### 2. Top Recommendations (Endpoint Utama)
```http
GET /api/recommendations/top?top_n=30
```
**Parameters:**
- `top_n` (optional): Jumlah rekomendasi (default: 30, max: 1000)

**Response:**
```json
{
  "status": "success",
  "data": {
    "recommendations": [
      {
        "id_produk": "P00084404",
        "nama_produk": "JayaPangan Beras Varian A 500g",
        "kategori_produk": "Beras",
        "rekomendasi_detail": "Generic Product Discount",
        "rekomendasi_besaran": 0.1,
        "rekomendasi_besaran_persen": "10.0%",
        "rata_rata_uplift_profit": 826.08,
        "rata_rata_uplift_profit_formatted": "Rp 826"
      }
    ],
    "total_returned": 30,
    "requested_count": 30,
    "timestamp": "2025-08-17T11:30:00"
  }
}
```

### 3. Statistics
```http
GET /api/recommendations/stats
```
**Response:**
```json
{
  "status": "success",
  "data": {
    "statistics": {
      "total_products": 1000,
      "products_with_discount": 337,
      "total_estimated_uplift": 23925.59,
      "average_uplift": 23.93,
      "strategy_distribution": {
        "Tanpa Diskon": 663,
        "Generic Product Discount": 137,
        "BOGO": 112
      }
    }
  }
}
```

### 4. Filter by Category
```http
GET /api/recommendations/category/{category}?top_n=30
```
**Parameters:**
- `category`: Nama kategori (case-insensitive, partial match)
- `top_n` (optional): Jumlah rekomendasi (default: 30)

**Example:**
```http
GET /api/recommendations/category/Beras
GET /api/recommendations/category/Daging
```

### 5. Metadata
```http
GET /api/metadata
```
**Response:** System metadata dan informasi model

## 🧪 Testing API

### Menggunakan Python Client
```python
python api_client.py
```

### Menggunakan cURL
```bash
# Health check
curl http://localhost:5000/

# Top 30 recommendations
curl http://localhost:5000/api/recommendations/top?top_n=30

# Statistics
curl http://localhost:5000/api/recommendations/stats

# Category filter
curl http://localhost:5000/api/recommendations/category/Beras
```

### Menggunakan Browser
Buka browser dan akses:
- `http://localhost:5000/api/recommendations/top?top_n=30`

## 🚀 Deployment

### Development
```bash
python api.py
```

### Production (menggunakan Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

### Docker (optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements_api.txt .
RUN pip install -r requirements_api.txt
COPY api.py .
COPY results/ ./results/
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```

## 📊 Response Format

Semua response mengikuti format standar:
```json
{
  "status": "success|error",
  "data": {
    // actual data
  },
  "error": "error message (jika error)"
}
```

## 🔄 Data Flow

1. **Load Data**: API membaca `final_recommendations.csv` saat startup
2. **Sort**: Data diurutkan berdasarkan `rata_rata_uplift_profit` (descending)
3. **Filter**: Mengambil top N (default 30) produk
4. **Format**: Menformat response dengan informasi tambahan (persentase, format Rupiah)
5. **Return**: Mengirim JSON response

## 🎯 Use Cases

1. **Dashboard Bisnis**: Menampilkan produk prioritas untuk diskon
2. **Mobile App**: Rekomendasi produk untuk customer
3. **Inventory Management**: Strategi diskon otomatis
4. **Analytics**: Monitoring performa rekomendasi

## ⚡ Performance Tips

- Data di-cache di memory saat startup
- Sorting dilakukan sekali saat load
- Response time < 100ms untuk endpoint utama
- Support hingga 1000 produk per request

## 🐛 Error Handling

API menangani error dengan response yang konsisten:
- **400**: Bad Request (parameter invalid)
- **404**: Endpoint tidak ditemukan  
- **500**: Internal Server Error
- **503**: Service Unavailable (data tidak tersedia)
