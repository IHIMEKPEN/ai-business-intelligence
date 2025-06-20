#!/usr/bin/env python3
"""
Quick test script for the new API endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_stock_analysis():
    """Test the new stock analysis endpoint"""
    print("Testing stock analysis endpoint...")
    
    payload = {
        "symbols": ["TSLA", "GOOGL"],
        "period": "1mo",
        "interval": "1d"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analysis/stocks", json=payload)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Task ID: {data.get('task_id')}")
            print(f"Symbols: {data.get('symbols')}")
            print(f"Data collected: {data.get('data_collected')}")
            
            # Wait for completion
            task_id = data.get('task_id')
            if task_id:
                print("Waiting for task completion...")
                time.sleep(5)
                
                task_response = requests.get(f"{BASE_URL}/tasks/{task_id}")
                if task_response.status_code == 200:
                    task_data = task_response.json()
                    print(f"Task status: {task_data.get('status')}")
                    
                    if task_data.get('result'):
                        result = task_data.get('result')
                        if 'error' not in result:
                            print("✅ Stock analysis completed successfully!")
                            print(f"Stocks analyzed: {result.get('stocks_analyzed', [])}")
                            return True
                        else:
                            print(f"❌ Analysis failed: {result.get('error')}")
                    else:
                        print("⏳ Task still processing...")
                else:
                    print(f"❌ Failed to get task status: {task_response.status_code}")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    return False

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Health: {data.get('status')}")
            return True
        else:
            print(f"❌ Health check failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    return False

def main():
    print("🧪 Quick API Test")
    print("=" * 30)
    
    # Test health first
    if not test_health():
        print("❌ API server not running. Please start it with: python -m api.main")
        return
    
    print("\n" + "=" * 30)
    
    # Test stock analysis
    test_stock_analysis()

if __name__ == "__main__":
    main() 