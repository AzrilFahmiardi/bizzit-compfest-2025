# Bizzt Analytics API Documentation

## Analytics Endpoints

API ini menyediakan endpoint untuk analisis grafik dan tren data transaksi yang dapat digunakan oleh frontend untuk membuat visualisasi chart.

## Business Metrics Endpoints

### 1. Dashboard Metrics
**Endpoint:** `GET /api/metrics/dashboard`

**Deskripsi:** Mendapatkan semua metrics dalam format yang siap pakai untuk dashboard (seperti yang terlihat di gambar dashboard)

**Parameters:**
- `start_date` (optional): Tanggal mulai (default: awal bulan ini)
- `end_date` (optional): Tanggal akhir (default: hari ini)  
- `store_id` (optional): Filter berdasarkan toko tertentu

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "kpi_cards": [
      {
        "title": "Total Revenue",
        "value": "Rp 22,000,000",
        "raw_value": 22000000,
        "growth": 15.2,
        "growth_formatted": "+15.2%",
        "trend": "up",
        "icon": "revenue"
      },
      {
        "title": "Total Transactions", 
        "value": "332",
        "raw_value": 332,
        "growth": -2.1,
        "growth_formatted": "-2.1%",
        "trend": "down",
        "icon": "transactions"
      },
      {
        "title": "Average Order Value",
        "value": "Rp 66,265",
        "raw_value": 66265,
        "growth": 8.5,
        "growth_formatted": "+8.5%",
        "trend": "up",
        "icon": "aov"
      },
      {
        "title": "Gross Profit*",
        "value": "Rp 0",
        "raw_value": 0,
        "growth": 0,
        "growth_formatted": "0.0%",
        "trend": "flat",
        "icon": "profit",
        "note": "*Requires cost data to calculate accurately"
      }
    ],
    "period_info": {
      "start_date": "2025-08-01",
      "end_date": "2025-08-17",
      "store_id": null,
      "period": "monthly"
    },
    "comparison": {
      "previous_period": {
        "total_revenue": 19130435,
        "total_transactions": 339,
        "average_order_value": 56432
      },
      "growth_summary": "Revenue increased by 15.2% compared to previous period"
    }
  },
  "timestamp": "2025-08-17T10:30:00"
}
```

### 2. Business Metrics Detail
**Endpoint:** `GET /api/metrics/business`

**Deskripsi:** Mendapatkan metrics bisnis utama dengan detail perbandingan periode

**Parameters:**
- `start_date` (optional): Tanggal mulai (YYYY-MM-DD)
- `end_date` (optional): Tanggal akhir (YYYY-MM-DD)
- `store_id` (optional): ID toko
- `period` (optional): daily/weekly/monthly (default: monthly)

**Response Format:**
```json
{
  "status": "success", 
  "data": {
    "current_period": {
      "total_revenue": 22000000,
      "total_transactions": 332,
      "average_order_value": 66265.06,
      "revenue_formatted": "Rp 22,000,000",
      "aov_formatted": "Rp 66,265"
    },
    "growth": {
      "revenue_growth": 15.2,
      "transactions_growth": -2.1,
      "aov_growth": 8.5,
      "previous_period": {
        "total_revenue": 19130435,
        "total_transactions": 339,
        "average_order_value": 56432,
        "start_date": "2025-07-01",
        "end_date": "2025-07-31"
      }
    },
    "period_info": {
      "start_date": "2025-08-01",
      "end_date": "2025-08-17",
      "store_id": null,
      "period": "monthly"
    }
  },
  "timestamp": "2025-08-17T10:30:00"
}
```

### 3. Revenue Breakdown
**Endpoint:** `GET /api/metrics/revenue?period=daily`

**Deskripsi:** Breakdown revenue berdasarkan periode waktu untuk chart trend

**Parameters:**
- `period`: daily/weekly/monthly (required)
- `start_date` (optional): Tanggal mulai
- `end_date` (optional): Tanggal akhir
- `store_id` (optional): ID toko

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "chart_data": [
      {
        "period": "2025-08-01",
        "revenue": 850000,
        "transactions": 15,
        "avg_transaction_value": 56666.67,
        "revenue_formatted": "Rp 850,000",
        "avg_formatted": "Rp 56,667"
      }
    ],
    "summary": {
      "total_periods": 17,
      "total_revenue": 22000000,
      "total_transactions": 332,
      "avg_period_revenue": 1294118,
      "period_type": "daily"
    },
    "chart_config": {
      "chart_type": "line",
      "x_axis": "period", 
      "y_axis": "revenue",
      "title": "Revenue per Hari",
      "x_label": "Hari",
      "y_label": "Revenue (Rp)"
    }
  },
  "parameters": {
    "period": "daily",
    "start_date": "2025-08-01",
    "end_date": "2025-08-17",
    "store_id": null
  },
  "timestamp": "2025-08-17T10:30:00"
}
```

### 1. Weekly Transaction Trends
**Endpoint:** `GET /api/analytics/trends/weekly`

**Deskripsi:** Mendapatkan data tren volume transaksi per minggu dari Januari 2023 sampai Februari 2025

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "chart_data": [
      {
        "week": 1,
        "week_label": "Week 1",
        "year": 2023,
        "week_in_year": 1,
        "transaction_count": 1250,
        "date_label": "2023-W01"
      }
    ],
    "statistics": {
      "total_weeks": 110,
      "total_transactions": 607563,
      "avg_weekly_transactions": 5523.3,
      "min_weekly_transactions": 3245,
      "max_weekly_transactions": 8976,
      "period": {
        "start_week": 1,
        "end_week": 110,
        "start_year": 2023,
        "end_year": 2025
      }
    },
    "chart_config": {
      "chart_type": "line",
      "x_axis": "week",
      "y_axis": "transaction_count",
      "title": "Volume Transaksi per Minggu (Jan 2023 - Feb 2025)",
      "x_label": "Minggu ke-",
      "y_label": "Jumlah Transaksi"
    }
  },
  "timestamp": "2025-08-17T10:30:00"
}
```

**Penggunaan Frontend:**
- Gunakan `chart_data` untuk membuat line chart
- X-axis: `week` atau `date_label`
- Y-axis: `transaction_count`
- Gunakan `chart_config` untuk setup chart

### 2. Event Analysis
**Endpoint:** `GET /api/analytics/events`

**Deskripsi:** Analisis volume dan performa transaksi berdasarkan event/promosi

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "chart_data": [
      {
        "event": "Promo Akhir Pekan",
        "transaction_count": 125430,
        "avg_price": 15750.5,
        "avg_discount": 0.1234,
        "avg_margin": 0.0456,
        "avg_discount_percent": "12.3%"
      }
    ],
    "chart_config": {
      "chart_type": "bar",
      "x_axis": "event",
      "y_axis": "transaction_count",
      "title": "Volume Transaksi per Event",
      "x_label": "Event",
      "y_label": "Jumlah Transaksi"
    }
  },
  "timestamp": "2025-08-17T10:30:00"
}
```

**Penggunaan Frontend:**
- Bar chart untuk `event` vs `transaction_count`
- Bisa juga buat chart tambahan untuk `avg_discount` atau `avg_price`

### 3. Category Performance
**Endpoint:** `GET /api/analytics/categories?limit=15`

**Deskripsi:** Top N kategori produk dengan volume transaksi tertinggi

**Parameters:**
- `limit` (optional): Jumlah kategori yang ditampilkan (default: 15, max: 50)

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "chart_data": [
      {
        "category": "Beras",
        "transaction_count": 45230,
        "avg_price": 12500.0,
        "avg_discount": 0.0856,
        "avg_discount_percent": "8.6%"
      }
    ],
    "chart_config": {
      "chart_type": "bar",
      "x_axis": "category",
      "y_axis": "transaction_count",
      "title": "Top 15 Kategori Produk dengan Volume Transaksi Tertinggi",
      "x_label": "Kategori Produk",
      "y_label": "Jumlah Transaksi"
    }
  },
  "limit": 15,
  "timestamp": "2025-08-17T10:30:00"
}
```

### 4. All Analytics Summary
**Endpoint:** `GET /api/analytics`

**Deskripsi:** Mendapatkan semua data analytics dalam satu request

**Response:** Kombinasi dari ketiga endpoint di atas dalam satu response.

## Frontend Implementation Example

### Dashboard KPI Cards Implementation:

```javascript
// Fetch dashboard metrics
const fetchDashboardMetrics = async (startDate = null, endDate = null, storeId = null) => {
  try {
    let url = '/api/metrics/dashboard';
    const params = new URLSearchParams();
    
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (storeId) params.append('store_id', storeId);
    
    if (params.toString()) {
      url += '?' + params.toString();
    }
    
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.status === 'success') {
      renderDashboardKPIs(data.data.kpi_cards);
      return data.data;
    }
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
  }
};

// Render KPI cards
const renderDashboardKPIs = (kpiCards) => {
  const kpiContainer = document.getElementById('kpi-container');
  kpiContainer.innerHTML = '';
  
  kpiCards.forEach(kpi => {
    const kpiCard = document.createElement('div');
    kpiCard.className = `kpi-card ${kpi.trend}`;
    
    kpiCard.innerHTML = `
      <div class="kpi-header">
        <h3>${kpi.title}</h3>
        <i class="icon-${kpi.icon}"></i>
      </div>
      <div class="kpi-value">${kpi.value}</div>
      <div class="kpi-growth ${kpi.trend}">
        <span class="growth-arrow">${kpi.trend === 'up' ? '↑' : kpi.trend === 'down' ? '↓' : '→'}</span>
        <span class="growth-text">${kpi.growth_formatted}</span>
      </div>
      ${kpi.note ? `<div class="kpi-note">${kpi.note}</div>` : ''}
    `;
    
    kpiContainer.appendChild(kpiCard);
  });
};

// Fetch revenue trend chart
const fetchRevenueTrend = async (period = 'daily') => {
  try {
    const response = await fetch(`/api/metrics/revenue?period=${period}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      const chartData = {
        labels: data.data.chart_data.map(item => item.period),
        datasets: [{
          label: 'Revenue',
          data: data.data.chart_data.map(item => item.revenue),
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.1
        }]
      };
      
      renderRevenueChart(chartData, data.data.chart_config);
    }
  } catch (error) {
    console.error('Error fetching revenue trend:', error);
  }
};
```

### React Component Example:

```jsx
import React, { useState, useEffect } from 'react';

const DashboardKPIs = ({ startDate, endDate, storeId }) => {
  const [kpiData, setKpiData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchDashboardMetrics();
  }, [startDate, endDate, storeId]);
  
  const fetchDashboardMetrics = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (storeId) params.append('store_id', storeId);
      
      const response = await fetch(`/api/metrics/dashboard?${params}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setKpiData(data.data.kpi_cards);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="kpi-grid">
      {kpiData.map((kpi, index) => (
        <div key={index} className={`kpi-card ${kpi.trend}`}>
          <div className="kpi-header">
            <h3>{kpi.title}</h3>
            <i className={`icon-${kpi.icon}`}></i>
          </div>
          <div className="kpi-value">{kpi.value}</div>
          <div className={`kpi-growth ${kpi.trend}`}>
            <span className="growth-arrow">
              {kpi.trend === 'up' ? '↑' : kpi.trend === 'down' ? '↓' : '→'}
            </span>
            <span className="growth-text">{kpi.growth_formatted}</span>
          </div>
          {kpi.note && <div className="kpi-note">{kpi.note}</div>}
        </div>
      ))}
    </div>
  );
};

export default DashboardKPIs;
```

### CSS for KPI Cards:

```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  border-left: 4px solid #ddd;
}

.kpi-card.up {
  border-left-color: #10B981;
}

.kpi-card.down {
  border-left-color: #EF4444;
}

.kpi-card.flat {
  border-left-color: #6B7280;
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.kpi-header h3 {
  margin: 0;
  color: #374151;
  font-size: 14px;
  font-weight: 500;
}

.kpi-value {
  font-size: 24px;
  font-weight: bold;
  color: #111827;
  margin-bottom: 8px;
}

.kpi-growth {
  display: flex;
  align-items: center;
  font-size: 12px;
}

.kpi-growth.up .growth-text {
  color: #10B981;
}

.kpi-growth.down .growth-text {
  color: #EF4444;
}

.kpi-growth.flat .growth-text {
  color: #6B7280;
}

.growth-arrow {
  margin-right: 4px;
  font-weight: bold;
}

.kpi-note {
  font-size: 11px;
  color: #6B7280;
  margin-top: 8px;
  font-style: italic;
}
```

### React/JavaScript Example:

```javascript
// Fetch weekly trends
const fetchWeeklyTrends = async () => {
  try {
    const response = await fetch('/api/analytics/trends/weekly');
    const data = await response.json();
    
    if (data.status === 'success') {
      // Setup Chart.js atau library chart lainnya
      const chartData = {
        labels: data.data.chart_data.map(item => item.date_label),
        datasets: [{
          label: 'Jumlah Transaksi',
          data: data.data.chart_data.map(item => item.transaction_count),
          borderColor: 'rgb(75, 192, 192)',
          tension: 0.1
        }]
      };
      
      // Render chart
      renderLineChart(chartData, data.data.chart_config);
    }
  } catch (error) {
    console.error('Error fetching weekly trends:', error);
  }
};

// Fetch category performance
const fetchCategoryPerformance = async (limit = 15) => {
  try {
    const response = await fetch(`/api/analytics/categories?limit=${limit}`);
    const data = await response.json();
    
    if (data.status === 'success') {
      const chartData = {
        labels: data.data.chart_data.map(item => item.category),
        datasets: [{
          label: 'Jumlah Transaksi',
          data: data.data.chart_data.map(item => item.transaction_count),
          backgroundColor: 'rgba(54, 162, 235, 0.6)'
        }]
      };
      
      renderBarChart(chartData, data.data.chart_config);
    }
  } catch (error) {
    console.error('Error fetching category performance:', error);
  }
};
```

### Chart.js Configuration Example:

```javascript
const renderLineChart = (chartData, config) => {
  const ctx = document.getElementById('weeklyTrendsChart').getContext('2d');
  
  new Chart(ctx, {
    type: 'line',
    data: chartData,
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: config.title
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: config.x_label
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: config.y_label
          }
        }
      }
    }
  });
};
```

## Key Features

1. **Ready-to-use chart data**: Data sudah dalam format yang siap digunakan untuk chart libraries
2. **Chart configuration included**: Setiap response menyertakan konfigurasi chart yang direkomendasikan
3. **Flexible parameters**: Endpoint mendukung parameter untuk customization
4. **Error handling**: Comprehensive error responses
5. **Statistics included**: Data statistik tambahan untuk insight

## Data Structure Benefits

- **chart_data**: Array of objects yang bisa langsung dimap ke chart
- **chart_config**: Metadata untuk setup chart (title, labels, type)
- **statistics**: Data agregat untuk menampilkan summary
- **timestamp**: Untuk tracking data freshness

Frontend developer dapat dengan mudah menggunakan data ini untuk membuat dashboard analytics yang informatif dan interaktif.
