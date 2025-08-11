#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Crypto Investment Website
Tests all backend endpoints including CoinMarketCap integration and OpenAI recommendations
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Backend URL from frontend environment
BACKEND_URL = "https://54e27f01-4392-494a-abdb-cac4a1e5d780.preview.emergentagent.com/api"

# Expected cryptocurrencies
EXPECTED_CRYPTOS = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'TRX', 'ADA', 'HYPE', 'LINK', 'XLM', 'BCH', 'HBAR', 'AVAX', 'LTC']

class CryptoAPITester:
    def __init__(self):
        self.session = None
        self.test_results = {
            'basic_health': {'status': 'pending', 'details': ''},
            'crypto_prices': {'status': 'pending', 'details': ''},
            'ai_analysis': {'status': 'pending', 'details': ''},
            'individual_recommendation': {'status': 'pending', 'details': ''},
            'recommendation_history': {'status': 'pending', 'details': ''}
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(ssl=False)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def test_basic_health(self):
        """Test basic API health endpoint"""
        print("🔍 Testing Basic API Health...")
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data:
                        self.test_results['basic_health'] = {
                            'status': 'pass',
                            'details': f"API health check successful. Response: {data}"
                        }
                        print("✅ Basic API health check passed")
                        return True
                    else:
                        self.test_results['basic_health'] = {
                            'status': 'fail',
                            'details': f"Unexpected response format: {data}"
                        }
                        print("❌ Basic API health check failed - unexpected response format")
                        return False
                else:
                    self.test_results['basic_health'] = {
                        'status': 'fail',
                        'details': f"HTTP {response.status}: {await response.text()}"
                    }
                    print(f"❌ Basic API health check failed - HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.test_results['basic_health'] = {
                'status': 'fail',
                'details': f"Exception: {str(e)}"
            }
            print(f"❌ Basic API health check failed - Exception: {str(e)}")
            return False

    async def test_crypto_prices(self):
        """Test CoinMarketCap API integration"""
        print("🔍 Testing CoinMarketCap API Integration...")
        try:
            async with self.session.get(f"{BACKEND_URL}/crypto/prices") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not isinstance(data, list):
                        self.test_results['crypto_prices'] = {
                            'status': 'fail',
                            'details': f"Expected list, got {type(data)}"
                        }
                        print("❌ CoinMarketCap API test failed - response is not a list")
                        return False
                    
                    if len(data) == 0:
                        self.test_results['crypto_prices'] = {
                            'status': 'fail',
                            'details': "No cryptocurrency data returned"
                        }
                        print("❌ CoinMarketCap API test failed - no data returned")
                        return False
                    
                    # Validate data structure
                    required_fields = ['id', 'symbol', 'name', 'price', 'percent_change_24h', 'market_cap', 'volume_24h', 'last_updated']
                    symbols_found = []
                    
                    for crypto in data:
                        symbols_found.append(crypto.get('symbol'))
                        for field in required_fields:
                            if field not in crypto:
                                self.test_results['crypto_prices'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in crypto data"
                                }
                                print(f"❌ CoinMarketCap API test failed - missing field '{field}'")
                                return False
                    
                    # Check if we got expected cryptocurrencies
                    missing_cryptos = [crypto for crypto in EXPECTED_CRYPTOS if crypto not in symbols_found]
                    
                    self.test_results['crypto_prices'] = {
                        'status': 'pass',
                        'details': f"Successfully fetched {len(data)} cryptocurrencies. Symbols: {symbols_found}. Missing: {missing_cryptos if missing_cryptos else 'None'}"
                    }
                    print(f"✅ CoinMarketCap API test passed - {len(data)} cryptocurrencies fetched")
                    if missing_cryptos:
                        print(f"⚠️  Note: Missing some expected cryptocurrencies: {missing_cryptos}")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.test_results['crypto_prices'] = {
                        'status': 'fail',
                        'details': f"HTTP {response.status}: {error_text}"
                    }
                    print(f"❌ CoinMarketCap API test failed - HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.test_results['crypto_prices'] = {
                'status': 'fail',
                'details': f"Exception: {str(e)}"
            }
            print(f"❌ CoinMarketCap API test failed - Exception: {str(e)}")
            return False

    async def test_ai_analysis(self):
        """Test OpenAI AI analysis integration"""
        print("🔍 Testing OpenAI AI Analysis Integration...")
        try:
            async with self.session.get(f"{BACKEND_URL}/crypto/analysis") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not isinstance(data, list):
                        self.test_results['ai_analysis'] = {
                            'status': 'fail',
                            'details': f"Expected list, got {type(data)}"
                        }
                        print("❌ AI Analysis test failed - response is not a list")
                        return False
                    
                    if len(data) == 0:
                        self.test_results['ai_analysis'] = {
                            'status': 'fail',
                            'details': "No AI analysis data returned"
                        }
                        print("❌ AI Analysis test failed - no data returned")
                        return False
                    
                    # Validate AI analysis structure
                    symbols_analyzed = []
                    for analysis in data:
                        required_fields = ['symbol', 'current_price', 'price_change_24h', 'recommendation']
                        for field in required_fields:
                            if field not in analysis:
                                self.test_results['ai_analysis'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in analysis data"
                                }
                                print(f"❌ AI Analysis test failed - missing field '{field}'")
                                return False
                        
                        # Validate recommendation structure
                        recommendation = analysis['recommendation']
                        rec_fields = ['id', 'symbol', 'recommendation', 'confidence', 'reasoning', 'created_at']
                        for field in rec_fields:
                            if field not in recommendation:
                                self.test_results['ai_analysis'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in recommendation data"
                                }
                                print(f"❌ AI Analysis test failed - missing recommendation field '{field}'")
                                return False
                        
                        # Validate recommendation values
                        if recommendation['recommendation'] not in ['BUY', 'HOLD', 'SELL']:
                            self.test_results['ai_analysis'] = {
                                'status': 'fail',
                                'details': f"Invalid recommendation value: {recommendation['recommendation']}"
                            }
                            print(f"❌ AI Analysis test failed - invalid recommendation value")
                            return False
                        
                        if recommendation['confidence'] not in ['HIGH', 'MEDIUM', 'LOW']:
                            self.test_results['ai_analysis'] = {
                                'status': 'fail',
                                'details': f"Invalid confidence value: {recommendation['confidence']}"
                            }
                            print(f"❌ AI Analysis test failed - invalid confidence value")
                            return False
                        
                        symbols_analyzed.append(analysis['symbol'])
                    
                    self.test_results['ai_analysis'] = {
                        'status': 'pass',
                        'details': f"Successfully generated AI analysis for {len(data)} cryptocurrencies. Symbols: {symbols_analyzed}"
                    }
                    print(f"✅ AI Analysis test passed - {len(data)} cryptocurrencies analyzed")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.test_results['ai_analysis'] = {
                        'status': 'fail',
                        'details': f"HTTP {response.status}: {error_text}"
                    }
                    print(f"❌ AI Analysis test failed - HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.test_results['ai_analysis'] = {
                'status': 'fail',
                'details': f"Exception: {str(e)}"
            }
            print(f"❌ AI Analysis test failed - Exception: {str(e)}")
            return False

    async def test_individual_recommendation(self):
        """Test individual cryptocurrency recommendation endpoints"""
        print("🔍 Testing Individual Crypto Recommendations...")
        test_symbols = ['BTC', 'ETH']  # Test with Bitcoin and Ethereum
        
        for symbol in test_symbols:
            print(f"  Testing {symbol} recommendation...")
            try:
                async with self.session.get(f"{BACKEND_URL}/crypto/{symbol}/recommendation") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate recommendation structure
                        required_fields = ['id', 'symbol', 'recommendation', 'confidence', 'reasoning', 'created_at']
                        for field in required_fields:
                            if field not in data:
                                self.test_results['individual_recommendation'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in {symbol} recommendation"
                                }
                                print(f"❌ {symbol} recommendation test failed - missing field '{field}'")
                                return False
                        
                        # Validate values
                        if data['symbol'] != symbol:
                            self.test_results['individual_recommendation'] = {
                                'status': 'fail',
                                'details': f"Symbol mismatch: expected {symbol}, got {data['symbol']}"
                            }
                            print(f"❌ {symbol} recommendation test failed - symbol mismatch")
                            return False
                        
                        if data['recommendation'] not in ['BUY', 'HOLD', 'SELL']:
                            self.test_results['individual_recommendation'] = {
                                'status': 'fail',
                                'details': f"Invalid recommendation value for {symbol}: {data['recommendation']}"
                            }
                            print(f"❌ {symbol} recommendation test failed - invalid recommendation")
                            return False
                        
                        if data['confidence'] not in ['HIGH', 'MEDIUM', 'LOW']:
                            self.test_results['individual_recommendation'] = {
                                'status': 'fail',
                                'details': f"Invalid confidence value for {symbol}: {data['confidence']}"
                            }
                            print(f"❌ {symbol} recommendation test failed - invalid confidence")
                            return False
                        
                        print(f"  ✅ {symbol}: {data['recommendation']} ({data['confidence']} confidence)")
                        
                    else:
                        error_text = await response.text()
                        self.test_results['individual_recommendation'] = {
                            'status': 'fail',
                            'details': f"HTTP {response.status} for {symbol}: {error_text}"
                        }
                        print(f"❌ {symbol} recommendation test failed - HTTP {response.status}")
                        return False
                        
            except Exception as e:
                self.test_results['individual_recommendation'] = {
                    'status': 'fail',
                    'details': f"Exception for {symbol}: {str(e)}"
                }
                print(f"❌ {symbol} recommendation test failed - Exception: {str(e)}")
                return False
        
        self.test_results['individual_recommendation'] = {
            'status': 'pass',
            'details': f"Successfully tested individual recommendations for {test_symbols}"
        }
        print("✅ Individual recommendation tests passed")
        return True

    async def test_historical_data(self):
        """Test historical chart data endpoints"""
        print("🔍 Testing Historical Chart Data...")
        test_symbols = ['BTC', 'ETH']  # Test with Bitcoin and Ethereum
        
        for symbol in test_symbols:
            print(f"  Testing {symbol} historical data...")
            try:
                async with self.session.get(f"{BACKEND_URL}/crypto/{symbol}/history") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Validate response structure
                        required_fields = ['symbol', 'days', 'data']
                        for field in required_fields:
                            if field not in data:
                                self.test_results['historical_data'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in {symbol} historical data"
                                }
                                print(f"❌ {symbol} historical data test failed - missing field '{field}'")
                                return False
                        
                        # Validate symbol matches
                        if data['symbol'] != symbol:
                            self.test_results['historical_data'] = {
                                'status': 'fail',
                                'details': f"Symbol mismatch: expected {symbol}, got {data['symbol']}"
                            }
                            print(f"❌ {symbol} historical data test failed - symbol mismatch")
                            return False
                        
                        # Validate days (should be 7 by default)
                        if data['days'] != 7:
                            self.test_results['historical_data'] = {
                                'status': 'fail',
                                'details': f"Expected 7 days of data, got {data['days']}"
                            }
                            print(f"❌ {symbol} historical data test failed - incorrect days")
                            return False
                        
                        # Validate historical data array
                        historical_data = data['data']
                        if not isinstance(historical_data, list):
                            self.test_results['historical_data'] = {
                                'status': 'fail',
                                'details': f"Expected list for historical data, got {type(historical_data)}"
                            }
                            print(f"❌ {symbol} historical data test failed - data is not a list")
                            return False
                        
                        if len(historical_data) == 0:
                            self.test_results['historical_data'] = {
                                'status': 'fail',
                                'details': f"No historical data returned for {symbol}"
                            }
                            print(f"❌ {symbol} historical data test failed - no data returned")
                            return False
                        
                        # Validate data point structure
                        for i, point in enumerate(historical_data[:5]):  # Check first 5 points
                            required_point_fields = ['timestamp', 'date', 'price']
                            for field in required_point_fields:
                                if field not in point:
                                    self.test_results['historical_data'] = {
                                        'status': 'fail',
                                        'details': f"Missing field '{field}' in {symbol} historical data point {i}"
                                    }
                                    print(f"❌ {symbol} historical data test failed - missing field '{field}' in data point")
                                    return False
                            
                            # Validate price is a number
                            if not isinstance(point['price'], (int, float)):
                                self.test_results['historical_data'] = {
                                    'status': 'fail',
                                    'details': f"Invalid price type in {symbol} historical data: {type(point['price'])}"
                                }
                                print(f"❌ {symbol} historical data test failed - invalid price type")
                                return False
                        
                        print(f"  ✅ {symbol}: {len(historical_data)} data points retrieved")
                        
                    else:
                        error_text = await response.text()
                        self.test_results['historical_data'] = {
                            'status': 'fail',
                            'details': f"HTTP {response.status} for {symbol}: {error_text}"
                        }
                        print(f"❌ {symbol} historical data test failed - HTTP {response.status}")
                        return False
                        
            except Exception as e:
                self.test_results['historical_data'] = {
                    'status': 'fail',
                    'details': f"Exception for {symbol}: {str(e)}"
                }
                print(f"❌ {symbol} historical data test failed - Exception: {str(e)}")
                return False
        
        self.test_results['historical_data'] = {
            'status': 'pass',
            'details': f"Successfully tested historical data for {test_symbols}"
        }
        print("✅ Historical chart data tests passed")
        return True

    async def test_recommendation_history(self):
        """Test recommendation history endpoint"""
        print("🔍 Testing Recommendation History...")
        try:
            async with self.session.get(f"{BACKEND_URL}/crypto/recommendations/history") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not isinstance(data, list):
                        self.test_results['recommendation_history'] = {
                            'status': 'fail',
                            'details': f"Expected list, got {type(data)}"
                        }
                        print("❌ Recommendation history test failed - response is not a list")
                        return False
                    
                    # It's okay if history is empty initially
                    if len(data) == 0:
                        self.test_results['recommendation_history'] = {
                            'status': 'pass',
                            'details': "Recommendation history is empty (expected for new system)"
                        }
                        print("✅ Recommendation history test passed - empty history (expected)")
                        return True
                    
                    # If there are recommendations, validate structure
                    for rec in data:
                        required_fields = ['id', 'symbol', 'recommendation', 'confidence', 'reasoning', 'created_at']
                        for field in required_fields:
                            if field not in rec:
                                self.test_results['recommendation_history'] = {
                                    'status': 'fail',
                                    'details': f"Missing required field '{field}' in history record"
                                }
                                print(f"❌ Recommendation history test failed - missing field '{field}'")
                                return False
                    
                    self.test_results['recommendation_history'] = {
                        'status': 'pass',
                        'details': f"Successfully retrieved {len(data)} historical recommendations"
                    }
                    print(f"✅ Recommendation history test passed - {len(data)} records found")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.test_results['recommendation_history'] = {
                        'status': 'fail',
                        'details': f"HTTP {response.status}: {error_text}"
                    }
                    print(f"❌ Recommendation history test failed - HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.test_results['recommendation_history'] = {
                'status': 'fail',
                'details': f"Exception: {str(e)}"
            }
            print(f"❌ Recommendation history test failed - Exception: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting Crypto Investment Website Backend API Tests")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        # Test basic health first
        await self.test_basic_health()
        
        # Test CoinMarketCap integration
        await self.test_crypto_prices()
        
        # Test AI analysis (this might take longer due to OpenAI calls)
        await self.test_ai_analysis()
        
        # Test individual recommendations
        await self.test_individual_recommendation()
        
        # Test recommendation history
        await self.test_recommendation_history()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'pass' else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
            if result['details']:
                print(f"   Details: {result['details']}")
            
            if result['status'] == 'pass':
                passed += 1
            else:
                failed += 1
        
        print(f"\n📈 Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All backend API tests passed!")
            return True
        else:
            print("⚠️  Some backend API tests failed. Check details above.")
            return False

async def main():
    """Main test execution function"""
    async with CryptoAPITester() as tester:
        success = await tester.run_all_tests()
        return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)