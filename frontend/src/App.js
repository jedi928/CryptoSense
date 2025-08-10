import React, { useEffect, useState } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CryptoCard = ({ analysis }) => {
  const getRecommendationColor = (recommendation) => {
    switch (recommendation?.toUpperCase()) {
      case 'BUY': return 'text-green-600 bg-green-50 border-green-200';
      case 'SELL': return 'text-red-600 bg-red-50 border-red-200';
      case 'HOLD': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence?.toUpperCase()) {
      case 'HIGH': return 'text-green-700 bg-green-100';
      case 'MEDIUM': return 'text-yellow-700 bg-yellow-100';
      case 'LOW': return 'text-red-700 bg-red-100';
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

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-gray-800">{analysis.symbol}</h3>
          <p className="text-sm text-gray-500">Current Price</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">{formatPrice(analysis.current_price)}</p>
          <p className={`text-sm font-medium ${analysis.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {analysis.price_change_24h >= 0 ? '+' : ''}{analysis.price_change_24h.toFixed(2)}%
          </p>
        </div>
      </div>
      
      <div className="space-y-3">
        <div className={`p-3 rounded-lg border ${getRecommendationColor(analysis.recommendation?.recommendation)}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">AI Recommendation</span>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(analysis.recommendation?.confidence)}`}>
              {analysis.recommendation?.confidence} Confidence
            </span>
          </div>
          <div className="text-lg font-bold mb-2">
            {analysis.recommendation?.recommendation}
          </div>
          {analysis.recommendation?.price_target && (
            <div className="text-sm">
              <span className="font-medium">7-day Target: </span>
              {formatPrice(analysis.recommendation.price_target)}
            </div>
          )}
        </div>
        
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm font-medium text-gray-700 mb-1">Analysis</p>
          <p className="text-sm text-gray-600 leading-relaxed">
            {analysis.recommendation?.reasoning}
          </p>
        </div>
      </div>
      
      <div className="mt-4 text-xs text-gray-400 text-center">
        Last updated: {new Date(analysis.recommendation?.created_at).toLocaleString()}
      </div>
    </div>
  );
};

const LoadingCard = () => (
  <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-100 animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div>
        <div className="h-5 bg-gray-300 rounded w-12 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-20"></div>
      </div>
      <div className="text-right">
        <div className="h-7 bg-gray-300 rounded w-20 mb-1"></div>
        <div className="h-4 bg-gray-200 rounded w-12"></div>
      </div>
    </div>
    <div className="space-y-3">
      <div className="p-3 rounded-lg bg-gray-100">
        <div className="h-4 bg-gray-300 rounded w-32 mb-2"></div>
        <div className="h-6 bg-gray-300 rounded w-16"></div>
      </div>
      <div className="bg-gray-50 p-3 rounded-lg">
        <div className="h-3 bg-gray-300 rounded w-full mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-4/5"></div>
      </div>
    </div>
  </div>
);

const Home = () => {
  const [marketAnalysis, setMarketAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchMarketAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${API}/crypto/analysis`);
      setMarketAnalysis(response.data);
      setLastUpdate(new Date());
    } catch (e) {
      console.error('Error fetching market analysis:', e);
      setError('Failed to fetch market analysis. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketAnalysis();
    
    // Set up auto-refresh every 5 minutes
    const interval = setInterval(fetchMarketAnalysis, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Crypto Investment AI</h1>
              <p className="text-gray-600 mt-1">AI-powered cryptocurrency investment recommendations</p>
            </div>
            <button
              onClick={fetchMarketAnalysis}
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center gap-2"
            >
              <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {loading ? 'Updating...' : 'Refresh'}
            </button>
          </div>
          
          {lastUpdate && (
            <p className="text-sm text-gray-500 mt-2">
              Last updated: {lastUpdate.toLocaleString()}
            </p>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Disclaimer */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <div>
              <h3 className="text-sm font-medium text-yellow-800">Investment Disclaimer</h3>
              <p className="text-sm text-yellow-700 mt-1">
                These AI recommendations are for informational purposes only and should not be considered as financial advice. 
                Cryptocurrency investments are highly volatile and risky. Always do your own research and consult with financial advisors.
              </p>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-red-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
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
            marketAnalysis.map((analysis) => (
              <CryptoCard key={analysis.symbol} analysis={analysis} />
            ))
          )}
        </div>

        {marketAnalysis.length === 0 && !loading && !error && (
          <div className="text-center py-12">
            <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No data available</h3>
            <p className="text-gray-500">Click refresh to load cryptocurrency analysis</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-100 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-sm text-gray-500">
            <p>Powered by CoinMarketCap API and OpenAI GPT-4</p>
            <p className="mt-1">© 2025 Crypto Investment AI. For educational purposes only.</p>
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