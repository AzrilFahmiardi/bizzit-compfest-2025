"""
Simple API client untuk testing Bizzt Recommendation API
"""

import requests
import json
from typing import Optional, Dict, Any

class BizztAPIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """Check if API is running"""
        try:
            response = requests.get(f"{self.base_url}/")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_top_recommendations(self, top_n: int = 30) -> Dict[str, Any]:
        """Get top N recommendations"""
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/top", 
                                  params={"top_n": top_n})
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/stats")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_recommendations_by_category(self, category: str, top_n: int = 30) -> Dict[str, Any]:
        """Get recommendations filtered by category"""
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/category/{category}",
                                  params={"top_n": top_n})
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get system metadata"""
        try:
            response = requests.get(f"{self.base_url}/api/metadata")
            return response.json()
        except Exception as e:
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Initialize client
    client = BizztAPIClient()
    
    print("=== Testing Bizzt Recommendation API ===\n")
    
    # 1. Health check
    print("1. Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print("\n" + "="*50 + "\n")
    
    # 2. Get top 30 recommendations
    print("2. Top 30 Recommendations:")
    top_recs = client.get_top_recommendations(30)
    if "data" in top_recs:
        print(f"Total recommendations returned: {top_recs['data']['total_returned']}")
        print("\nTop 5 products:")
        for i, rec in enumerate(top_recs['data']['recommendations'][:5], 1):
            print(f"  {i}. {rec['nama_produk']}")
            print(f"     Strategy: {rec['rekomendasi_detail']}")
            print(f"     Discount: {rec['rekomendasi_besaran_persen']}")
            print(f"     Uplift: {rec['rata_rata_uplift_profit_formatted']}")
            print()
    else:
        print("Error:", top_recs.get('error', 'Unknown error'))
    
    print("="*50 + "\n")
    
    # 3. Get statistics
    print("3. Statistics:")
    stats = client.get_statistics()
    if "data" in stats:
        stat_data = stats['data']['statistics']
        print(f"Total products: {stat_data['total_products']}")
        print(f"Products with discount: {stat_data['products_with_discount']}")
        print(f"Total estimated uplift: Rp {stat_data['total_estimated_uplift']:,.0f}")
        print(f"Average uplift: Rp {stat_data['average_uplift']:,.0f}")
        print("\nTop strategies:")
        for strategy, count in list(stat_data['strategy_distribution'].items())[:5]:
            print(f"  - {strategy}: {count} products")
    else:
        print("Error:", stats.get('error', 'Unknown error'))
    
    print("\n" + "="*50 + "\n")
    
    # 4. Get recommendations by category (example: Beras)
    print("4. Recommendations for 'Beras' category:")
    category_recs = client.get_recommendations_by_category('Beras', 10)
    if "data" in category_recs:
        recs = category_recs['data']['recommendations']
        print(f"Found {len(recs)} recommendations for Beras:")
        for i, rec in enumerate(recs[:3], 1):
            print(f"  {i}. {rec['nama_produk']}")
            print(f"     Strategy: {rec['rekomendasi_detail']}")
            print(f"     Discount: {rec['rekomendasi_besaran_persen']}")
            print(f"     Uplift: {rec['rata_rata_uplift_profit_formatted']}")
            print()
    else:
        print("Error:", category_recs.get('error', 'Unknown error'))
