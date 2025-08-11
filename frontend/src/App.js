import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Cryptocurrency logo mapping using CoinGecko's API
const getCryptoLogoUrl = (symbol) => {
  const logoMap = {
    'BTC': 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
    'ETH': 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
    'XRP': 'https://assets.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png',
    'BNB': 'https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png',
    'SOL': 'https://assets.coingecko.com/coins/images/4128/large/solana.png',
    'DOGE': 'https://assets.coingecko.com/coins/images/5/large/dogecoin.png',
    'TRX': 'https://assets.coingecko.com/coins/images/1094/large/tron-logo.png',
    'ADA': 'https://assets.coingecko.com/coins/images/975/large/cardano.png',
    'HYPE': 'https://assets.coingecko.com/coins/images/37633/large/token.png',
    'LINK': 'https://assets.coingecko.com/coins/images/877/large/chainlink-new-logo.png',
    'XLM': 'https://assets.coingecko.com/coins/images/100/large/Stellar_symbol_black_RGB.png',
    'BCH': 'https://assets.coingecko.com/coins/images/780/large/bitcoin-cash-circle.png',
    'HBAR': 'https://assets.coingecko.com/coins/images/3441/large/Hedera_Hashgraph_Logo.png',
    'AVAX': 'https://assets.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png',
    'LTC': 'https://assets.coingecko.com/coins/images/2/large/litecoin.png'
  };
  
  return logoMap[symbol] || `https://via.placeholder.com/32/cccccc/000000?text=${symbol}`;
};

const PriceChart = ({ symbol, currentPrice }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API}/crypto/${symbol}/history?days=7`);
        const data = response.data.data;
        
        // Format data for recharts (show every 6 hours for cleaner display)
        const formattedData = data.filter((_, index) => index % 6 === 0).map((point, index) => ({
          time: new Date(point.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
          price: point.price,
          index: index
        }));
        
        setChartData(formattedData);
      } catch (e) {
        console.error(`Error fetching chart data for ${symbol}:`, e);
        setError('Chart data unavailable');
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [symbol]);

  if (loading) {
    return (
      <div className="h-24 bg-gray-50 rounded flex items-center justify-center">
        <div className="text-xs text-gray-500">Loading chart...</div>
      </div>
    );
  }

  if (error || chartData.length === 0) {
    return (
      <div className="h-24 bg-gray-50 rounded flex items-center justify-center">
        <div className="text-xs text-gray-500">Chart unavailable</div>
      </div>
    );
  }

  // Determine line color based on price trend
  const firstPrice = chartData[0]?.price || currentPrice;
  const lastPrice = chartData[chartData.length - 1]?.price || currentPrice;
  const lineColor = lastPrice >= firstPrice ? '#000000' : '#666666';

  return (
    <div className="h-24 bg-gray-50 rounded p-2">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <XAxis hide />
          <YAxis hide />
          <Tooltip 
            labelStyle={{ color: '#000' }}
            contentStyle={{ 
              backgroundColor: 'white', 
              border: '1px solid #ccc',
              borderRadius: '4px',
              fontSize: '12px'
            }}
            formatter={(value) => [`$${value.toFixed(4)}`, 'Price']}
            labelFormatter={(label) => `Date: ${label}`}
          />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke={lineColor}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 3, fill: lineColor }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

const CryptoCard = ({ crypto, recommendation, onAnalyzeClick, isAnalyzing }) => {
  const getRecommendationColor = (rec) => {
    switch (rec?.toUpperCase()) {
      case 'BUY': return 'text-black bg-white border-black';
      case 'SELL': return 'text-white bg-black border-black';
      case 'HOLD': return 'text-gray-600 bg-gray-100 border-gray-400';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence?.toUpperCase()) {
      case 'HIGH': return 'text-black bg-gray-200';
      case 'MEDIUM': return 'text-gray-700 bg-gray-100';
      case 'LOW': return 'text-gray-500 bg-gray-50';
      default: return 'text-gray-700 bg-gray-100';
    }
  };

  const formatPrice = (price) => {
    if (price >= 1) {
      return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    } else {
      return `$${price.toFixed(6)}`;
    }
  };

  const logoUrl = getCryptoLogoUrl(crypto.symbol);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-gray-200 hover:border-black hover:shadow-xl transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <img 
            src={logoUrl} 
            alt={`${crypto.symbol} logo`}
            className="w-10 h-10 rounded-full object-cover bg-gray-100 p-1 border border-gray-300"
            onError={(e) => {
              e.target.src = `https://via.placeholder.com/40/cccccc/000000?text=${crypto.symbol}`;
            }}
          />
          <div>
            <h3 className="text-xl font-bold text-black">{crypto.symbol}</h3>
            <p className="text-sm text-gray-600">{crypto.name}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-black">{formatPrice(crypto.price)}</p>
          <p className={`text-sm font-medium ${crypto.percent_change_24h >= 0 ? 'text-black' : 'text-gray-600'}`}>
            {crypto.percent_change_24h >= 0 ? '+' : ''}{crypto.percent_change_24h.toFixed(2)}%
          </p>
        </div>
      </div>
      
      {/* Price Chart */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-gray-600">7-Day Price Trend</span>
          <span className="text-xs text-gray-500">Hourly</span>
        </div>
        <PriceChart symbol={crypto.symbol} currentPrice={crypto.price} />
      </div>
      
      <div className="space-y-3">
        <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            <div>
              <span className="font-medium text-black">Market Cap:</span>
              <p className="text-gray-800">${(crypto.market_cap / 1000000000).toFixed(1)}B</p>
            </div>
            <div>
              <span className="font-medium text-black">24h Volume:</span>
              <p className="text-gray-800">${(crypto.volume_24h / 1000000).toFixed(1)}M</p>
            </div>
          </div>
        </div>

        {recommendation ? (
          <div className={`p-3 rounded-lg border-2 ${getRecommendationColor(recommendation.recommendation)}`}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold">AI Recommendation</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(recommendation.confidence)}`}>
                {recommendation.confidence} Confidence
              </span>
            </div>
            <div className="text-lg font-bold mb-2">
              {recommendation.recommendation}
            </div>
            {recommendation.price_target && (
              <div className="text-sm mb-2">
                <span className="font-medium">7-day Target: </span>
                {formatPrice(recommendation.price_target)}
              </div>
            )}
            <div className="bg-gray-100 p-2 rounded text-xs border border-gray-300">
              <p className="text-gray-800 leading-relaxed">
                {recommendation.reasoning}
              </p>
            </div>
            <div className="mt-2 text-xs text-gray-500">
              Generated: {new Date(recommendation.created_at).toLocaleString()}
            </div>
          </div>
        ) : (
          <button
            onClick={() => onAnalyzeClick(crypto.symbol)}
            disabled={isAnalyzing}
            className="w-full bg-black hover:bg-gray-800 disabled:bg-gray-400 text-white py-2 px-4 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2 border border-black"
          >
            {isAnalyzing ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Generating AI Analysis...
              </>
            ) : (
              <>
                🤖 Get AI Investment Analysis
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

const LoadingCard = () => (
  <div className="bg-white rounded-lg shadow-lg p-6 border-2 border-gray-200 animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gray-300 rounded-full border border-gray-300"></div>
        <div>
          <div className="h-5 bg-gray-300 rounded w-12 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
      <div className="text-right">
        <div className="h-7 bg-gray-300 rounded w-20 mb-1"></div>
        <div className="h-4 bg-gray-200 rounded w-12"></div>
      </div>
    </div>
    <div className="space-y-3">
      <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
        <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-3/4"></div>
      </div>
      <div className="h-10 bg-gray-300 rounded w-full border border-gray-400"></div>
    </div>
  </div>
);

const Home = () => {
  const [cryptoPrices, setCryptoPrices] = useState([]);
  const [recommendations, setRecommendations] = useState({});
  const [loading, setLoading] = useState(true);
  const [analyzingSymbols, setAnalyzingSymbols] = useState(new Set());
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchCryptoPrices = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/crypto/prices`);
      setCryptoPrices(response.data);
      setLastUpdate(new Date());
    } catch (e) {
      console.error('Error fetching crypto prices:', e);
      setError('Failed to fetch cryptocurrency prices. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const generateAIAnalysis = async (symbol) => {
    try {
      setAnalyzingSymbols(prev => new Set([...prev, symbol]));
      const response = await axios.get(`${API}/crypto/${symbol}/recommendation`);
      setRecommendations(prev => ({
        ...prev,
        [symbol]: response.data
      }));
    } catch (e) {
      console.error(`Error generating AI analysis for ${symbol}:`, e);
      setError(`Failed to generate AI analysis for ${symbol}. Please try again.`);
    } finally {
      setAnalyzingSymbols(prev => {
        const newSet = new Set(prev);
        newSet.delete(symbol);
        return newSet;
      });
    }
  };

  useEffect(() => {
    fetchCryptoPrices();
    
    // Set up auto-refresh every 5 minutes for prices only
    const interval = setInterval(fetchCryptoPrices, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="bg-black shadow-sm border-b border-gray-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">CoinSense</h1>
              <p className="text-lg font-semibold text-gray-200 mt-1">Trade Smarter</p>
              <p className="text-gray-300 mt-1 text-sm">Real-time cryptocurrency prices with on-demand AI investment analysis</p>
            </div>
            <button
              onClick={fetchCryptoPrices}
              disabled={loading}
              className="bg-white hover:bg-gray-100 disabled:bg-gray-400 text-black px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2 border border-white"
            >
              <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loading ? 'Updating Prices...' : 'Refresh Prices'}
            </button>
          </div>
          
          {lastUpdate && (
            <p className="text-sm text-gray-400 mt-2">
              Prices last updated: {lastUpdate.toLocaleString()}
            </p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Disclaimer */}
        <div className="bg-white border border-gray-300 rounded-lg p-4 mb-8">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-gray-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-black">Investment Disclaimer</h3>
              <p className="text-sm text-gray-700 mt-1">
                These AI recommendations are for informational purposes only and should not be considered as financial advice. 
                Cryptocurrency investments are highly volatile and risky. Always do your own research and consult with financial advisors.
              </p>
            </div>
          </div>
        </div>

        {/* Usage Instructions */}
        <div className="bg-white border border-gray-300 rounded-lg p-4 mb-8">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-black mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-black">How it works</h3>
              <p className="text-sm text-gray-700 mt-1">
                Click the "Get AI Investment Analysis" button below any cryptocurrency to receive personalized BUY/HOLD/SELL recommendations powered by OpenAI GPT-4.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-white border border-gray-400 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-gray-800 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-black">Error</h3>
                <p className="text-sm text-gray-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Crypto Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {loading ? (
            // Show loading cards
            Array.from({ length: 15 }).map((_, index) => (
              <LoadingCard key={index} />
            ))
          ) : (
            cryptoPrices.map((crypto) => (
              <CryptoCard 
                key={crypto.symbol} 
                crypto={crypto}
                recommendation={recommendations[crypto.symbol]}
                onAnalyzeClick={generateAIAnalysis}
                isAnalyzing={analyzingSymbols.has(crypto.symbol)}
              />
            ))
          )}
        </div>

        {cryptoPrices.length === 0 && !loading && !error && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-lg font-medium text-white mb-2">No data available</h3>
            <p className="text-gray-400">Click refresh to load cryptocurrency prices</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-black border-t border-gray-600 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-400">
            <p>Powered by CoinMarketCap API and OpenAI GPT-4</p>
            <p className="mt-1">© 2025 CoinSense. For educational purposes only.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <Home />
    </div>
  );
}

export default App;