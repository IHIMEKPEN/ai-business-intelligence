#!/usr/bin/env python3
"""
Test script for AI Business Intelligence API

This script tests the new specialized analysis endpoints to ensure they work correctly.
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_health():
    """Test health endpoint"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            print(f"Health check: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"  Status: {data.get('status')}")
                return True
            return False

async def test_system_status():
    """Test system status endpoint"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/status") as response:
            print(f"System status: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"  Total agents: {data.get('total_agents')}")
                print(f"  Active agents: {data.get('active_agents')}")
                print(f"  System health: {data.get('system_health')}")
                return True
            return False

async def test_stock_analysis():
    """Test stock analysis endpoint"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "symbols": ["TSLA", "GOOGL"],
            "period": "1mo",
            "interval": "1d"
        }
        
        async with session.post(f"{BASE_URL}/analysis/stocks", json=payload) as response:
            print(f"Stock analysis: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"  Task ID: {data.get('task_id')}")
                print(f"  Symbols: {data.get('symbols')}")
                print(f"  Data collected: {data.get('data_collected')}")
                
                # Wait for task completion
                task_id = data.get('task_id')
                if task_id:
                    await asyncio.sleep(5)  # Wait for processing
                    async with session.get(f"{BASE_URL}/tasks/{task_id}") as task_response:
                        if task_response.status == 200:
                            task_data = await task_response.json()
                            print(f"  Task status: {task_data.get('status')}")
                            if task_data.get('result'):
                                result = task_data.get('result')
                                if 'error' not in result:
                                    print(f"  Analysis completed successfully!")
                                    print(f"  Stocks analyzed: {result.get('stocks_analyzed', [])}")
                                    return True
                                else:
                                    print(f"  Analysis failed: {result.get('error')}")
                            else:
                                print(f"  Task still processing...")
                        else:
                            print(f"  Failed to get task status: {task_response.status}")
                return True
            else:
                error_text = await response.text()
                print(f"  Error: {error_text}")
                return False

async def test_forex_analysis():
    """Test forex analysis endpoint"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "pairs": ["EUR/USD", "GBP/USD"]
        }
        
        async with session.post(f"{BASE_URL}/analysis/forex", json=payload) as response:
            print(f"Forex analysis: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"  Task ID: {data.get('task_id')}")
                print(f"  Pairs: {data.get('pairs')}")
                print(f"  Data collected: {data.get('data_collected')}")
                return True
            else:
                error_text = await response.text()
                print(f"  Error: {error_text}")
                return False

async def test_crypto_analysis():
    """Test crypto analysis endpoint"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "symbols": ["BTC-USD", "ETH-USD"]
        }
        
        async with session.post(f"{BASE_URL}/analysis/crypto", json=payload) as response:
            print(f"Crypto analysis: {response.status}")
            if response.status == 200:
                data = await response.json()
                print(f"  Task ID: {data.get('task_id')}")
                print(f"  Symbols: {data.get('symbols')}")
                print(f"  Data collected: {data.get('data_collected')}")
                return True
            else:
                error_text = await response.text()
                print(f"  Error: {error_text}")
                return False

async def main():
    """Run all tests"""
    print("🧪 Testing AI Business Intelligence API")
    print("=" * 50)
    
    # Test health
    print("\n1. Testing health endpoint...")
    health_ok = await test_health()
    
    if not health_ok:
        print("❌ Health check failed. Make sure the API server is running.")
        return
    
    # Test system status
    print("\n2. Testing system status...")
    await test_system_status()
    
    # Test stock analysis
    print("\n3. Testing stock analysis...")
    await test_stock_analysis()
    
    # Test forex analysis
    print("\n4. Testing forex analysis...")
    await test_forex_analysis()
    
    # Test crypto analysis
    print("\n5. Testing crypto analysis...")
    await test_crypto_analysis()
    
    print("\n✅ API testing completed!")

if __name__ == "__main__":
    asyncio.run(main()) 