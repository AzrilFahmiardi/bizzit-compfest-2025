"""
Bizzt Recommendation API Test Client
Clean testing interface untuk final API
"""

import requests
import json
import time
from datetime import datetime

class BizztAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def health_check(self):
        """Test API health"""
        print("🔍 Checking API health...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Service: {data['service']}")
                print(f"📊 Recommendations: {data['recommendations_count']}")
                print(f"🔄 Processing: {data['is_processing']}")
                return True
            else:
                print(f"❌ API not healthy")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API: {str(e)}")
            return False
    
    def get_recommendations(self, limit=10):
        """Get current recommendations"""
        print(f"\n📊 Getting top {limit} recommendations...")
        try:
            response = requests.get(f"{self.base_url}/api/recommendations?limit={limit}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ Retrieved {data['count']} recommendations")
                print(f"🔥 Fresh: {data['is_fresh']}")
                print(f"📅 Last updated: {data.get('last_updated', 'Never')}")
                
                print(f"\nTop {min(5, len(data['recommendations']))} products:")
                for i, rec in enumerate(data['recommendations'][:5], 1):
                    print(f"{i:2d}. {rec['nama_produk'][:45]:<45} | {rec['rekomendasi_detail']:<20} | {rec['rata_rata_uplift_profit_formatted']}")
                
                return data
            else:
                print(f"❌ Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def get_statistics(self):
        """Get recommendation statistics"""
        print(f"\n📈 Getting statistics...")
        try:
            response = requests.get(f"{self.base_url}/api/recommendations/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()['data']
                print(f"✅ Statistics retrieved")
                print(f"📦 Total products: {data['total_products']}")
                print(f"🎯 With discounts: {data['products_with_discount']}")
                print(f"💰 Total uplift: Rp {data['total_estimated_uplift']:,.0f}")
                print(f"📊 Average uplift: Rp {data['average_uplift']:,.0f}")
                
                print(f"\nTop strategies:")
                for strategy, count in list(data['strategy_distribution'].items())[:3]:
                    print(f"  - {strategy}: {count} products")
                
                return data
            else:
                print(f"❌ Error: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def regenerate_recommendations(self):
        """Trigger recommendation regeneration"""
        print(f"\n🚀 Triggering recommendation regeneration...")
        try:
            response = requests.post(f"{self.base_url}/api/recommendations/regenerate", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Regeneration started!")
                print(f"⏱️ Estimated duration: {data['estimated_duration']}")
                return True
            elif response.status_code == 409:
                print(f"⚠️ Already processing")
                return False
            else:
                print(f"❌ Error: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def monitor_processing(self, max_wait=30):
        """Monitor processing progress"""
        print(f"\n👀 Monitoring progress (max {max_wait}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/api/recommendations/status", timeout=5)
                
                if response.status_code == 200:
                    data = response.json()['data']
                    is_processing = data['is_processing']
                    progress = data['progress']
                    
                    if is_processing:
                        print(f"🔄 {progress['progress']:3d}% - {progress['message']}")
                        time.sleep(2)
                    else:
                        if progress['status'] == 'completed':
                            print(f"✅ Completed! {progress['message']}")
                            return True
                        elif progress['status'] == 'failed':
                            print(f"❌ Failed: {progress['message']}")
                            return False
                        else:
                            print(f"⏸️ Not processing")
                            return False
                else:
                    print(f"❌ Error checking status")
                    time.sleep(3)
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Error: {str(e)}")
                time.sleep(3)
        
        print(f"⏰ Timeout after {max_wait}s")
        return False
    
    def full_workflow_test(self):
        """Complete workflow test"""
        print("🧪 FULL WORKFLOW TEST")
        print("=" * 60)
        
        # Step 1: Current state
        print("\n1️⃣ Current recommendations:")
        before = self.get_recommendations(5)
        
        # Step 2: Get statistics
        print("\n2️⃣ Current statistics:")
        stats_before = self.get_statistics()
        
        # Step 3: Trigger regeneration
        print("\n3️⃣ Triggering regeneration...")
        if self.regenerate_recommendations():
            
            # Step 4: Monitor progress
            print("\n4️⃣ Monitoring progress...")
            if self.monitor_processing(max_wait=20):
                
                # Step 5: Check new results
                print("\n5️⃣ New recommendations:")
                after = self.get_recommendations(5)
                
                # Step 6: Compare
                if before and after:
                    print(f"\n6️⃣ Comparison:")
                    before_ids = [r['id_produk'] for r in before['recommendations']]
                    after_ids = [r['id_produk'] for r in after['recommendations']]
                    
                    same = len(set(before_ids) & set(after_ids))
                    new = len(set(after_ids) - set(before_ids))
                    
                    print(f"  📊 Same products: {same}/5")
                    print(f"  🆕 New products: {new}/5")
                
                print(f"\n✅ Workflow completed successfully!")
            else:
                print(f"\n❌ Processing failed or timeout")
        else:
            print(f"\n❌ Failed to start regeneration")

def interactive_menu():
    """Interactive testing menu"""
    tester = BizztAPITester()
    
    print("🧪 Bizzt Recommendation API Tester")
    print("=" * 50)
    
    # Health check
    if not tester.health_check():
        print("❌ API not available. Make sure to run: python bizzt_api.py")
        return
    
    while True:
        print(f"\n🎯 Select test:")
        print("1. Get recommendations")
        print("2. Get statistics")
        print("3. Regenerate recommendations")
        print("4. Check processing status")
        print("5. Full workflow test")
        print("6. Exit")
        
        try:
            choice = input("\nChoice (1-6): ").strip()
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        
        if choice == '1':
            tester.get_recommendations(10)
        elif choice == '2':
            tester.get_statistics()
        elif choice == '3':
            if tester.regenerate_recommendations():
                tester.monitor_processing()
        elif choice == '4':
            tester.monitor_processing(max_wait=5)
        elif choice == '5':
            tester.full_workflow_test()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    interactive_menu()
