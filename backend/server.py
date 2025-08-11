from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import aiohttp
import asyncio
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class CryptoPrice(BaseModel):
    id: str
    symbol: str
    name: str
    price: float
    percent_change_24h: float
    market_cap: float
    volume_24h: float
    last_updated: datetime

class AIRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str
    recommendation: str  # BUY, HOLD, SELL
    confidence: str  # HIGH, MEDIUM, LOW
    reasoning: str
    price_target: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MarketAnalysis(BaseModel):
    symbol: str
    current_price: float
    price_change_24h: float
    recommendation: AIRecommendation

# CoinMarketCap API configuration
CMC_API_KEY = os.environ.get('COINMARKETCAP_API_KEY')
CMC_BASE_URL = "https://pro-api.coinmarketcap.com/v1"

# OpenAI configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Target cryptocurrencies
TARGET_CRYPTOS = ['BTC', 'ETH', 'XRP', 'BNB', 'SOL', 'DOGE', 'TRX', 'ADA', 'HYPE', 'LINK', 'XLM', 'BCH', 'HBAR', 'AVAX', 'LTC']

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Crypto Investment AI API"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

async def fetch_crypto_prices() -> List[CryptoPrice]:
    """Fetch cryptocurrency prices from CoinMarketCap API"""
    if not CMC_API_KEY:
        raise HTTPException(status_code=500, detail="CoinMarketCap API key not configured")
    
    symbols = ",".join(TARGET_CRYPTOS)
    
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }
    
    params = {
        'symbol': symbols,
        'convert': 'USD'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{CMC_BASE_URL}/cryptocurrency/quotes/latest",
            headers=headers,
            params=params
        ) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Failed to fetch crypto prices")
            
            data = await response.json()
            
            crypto_prices = []
            for symbol in TARGET_CRYPTOS:
                if symbol in data['data']:
                    crypto_data = data['data'][symbol]
                    quote = crypto_data['quote']['USD']
                    
                    crypto_price = CryptoPrice(
                        id=str(crypto_data['id']),
                        symbol=crypto_data['symbol'],
                        name=crypto_data['name'],
                        price=quote['price'],
                        percent_change_24h=quote['percent_change_24h'] or 0,
                        market_cap=quote['market_cap'] or 0,
                        volume_24h=quote['volume_24h'] or 0,
                        last_updated=datetime.fromisoformat(quote['last_updated'].replace('Z', '+00:00'))
                    )
                    crypto_prices.append(crypto_price)
            
            return crypto_prices

async def generate_ai_recommendation(crypto: CryptoPrice) -> AIRecommendation:
    """Generate AI-powered investment recommendation"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    # Create AI analysis prompt
    analysis_prompt = f"""
    As a crypto investment analyst, analyze {crypto.name} ({crypto.symbol}) and provide a recommendation.
    
    Current Data:
    - Price: ${crypto.price:.4f}
    - 24h Change: {crypto.percent_change_24h:.2f}%
    - Market Cap: ${crypto.market_cap:,.0f}
    - 24h Volume: ${crypto.volume_24h:,.0f}
    
    Please provide:
    1. Recommendation (BUY/HOLD/SELL)
    2. Confidence level (HIGH/MEDIUM/LOW)
    3. Brief reasoning (2-3 sentences)
    4. Price target for next 7 days (optional)
    
    Format your response as:
    RECOMMENDATION: [BUY/HOLD/SELL]
    CONFIDENCE: [HIGH/MEDIUM/LOW]
    REASONING: [Your analysis]
    PRICE_TARGET: [Dollar amount or NONE]
    
    Consider market trends, technical indicators, and risk factors. Always include risk disclaimers.
    """
    
    try:
        # Initialize LLM chat
        chat = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"crypto-analysis-{crypto.symbol}",
            system_message="You are a professional cryptocurrency investment analyst. Provide balanced, data-driven investment recommendations with appropriate risk warnings."
        ).with_model("openai", "gpt-4o")
        
        # Create user message
        user_message = UserMessage(text=analysis_prompt)
        
        # Get AI response
        response = await chat.send_message(user_message)
        
        # Parse the response
        lines = response.strip().split('\n')
        recommendation_data = {}
        
        for line in lines:
            if line.startswith('RECOMMENDATION:'):
                recommendation_data['recommendation'] = line.split(':', 1)[1].strip()
            elif line.startswith('CONFIDENCE:'):
                recommendation_data['confidence'] = line.split(':', 1)[1].strip()
            elif line.startswith('REASONING:'):
                recommendation_data['reasoning'] = line.split(':', 1)[1].strip()
            elif line.startswith('PRICE_TARGET:'):
                target_str = line.split(':', 1)[1].strip()
                if target_str.upper() != 'NONE':
                    try:
                        recommendation_data['price_target'] = float(target_str.replace('$', '').replace(',', ''))
                    except:
                        recommendation_data['price_target'] = None
        
        return AIRecommendation(
            symbol=crypto.symbol,
            recommendation=recommendation_data.get('recommendation', 'HOLD'),
            confidence=recommendation_data.get('confidence', 'MEDIUM'),
            reasoning=recommendation_data.get('reasoning', 'Analysis pending'),
            price_target=recommendation_data.get('price_target')
        )
        
    except Exception as e:
        logger.error(f"Error generating AI recommendation for {crypto.symbol}: {str(e)}")
        return AIRecommendation(
            symbol=crypto.symbol,
            recommendation='HOLD',
            confidence='LOW',
            reasoning=f'Unable to generate analysis due to technical error. Please try again later.'
        )

@api_router.get("/crypto/prices", response_model=List[CryptoPrice])
async def get_crypto_prices():
    """Get current cryptocurrency prices"""
    try:
        return await fetch_crypto_prices()
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cryptocurrency prices")

@api_router.get("/crypto/analysis", response_model=List[MarketAnalysis])
async def get_market_analysis():
    """Get market analysis with AI recommendations for all cryptocurrencies"""
    try:
        crypto_prices = await fetch_crypto_prices()
        market_analysis = []
        
        # Generate AI recommendations for each crypto
        for crypto in crypto_prices:
            recommendation = await generate_ai_recommendation(crypto)
            
            # Save recommendation to database
            await db.recommendations.insert_one(recommendation.dict())
            
            analysis = MarketAnalysis(
                symbol=crypto.symbol,
                current_price=crypto.price,
                price_change_24h=crypto.percent_change_24h,
                recommendation=recommendation
            )
            market_analysis.append(analysis)
        
        return market_analysis
        
    except Exception as e:
        logger.error(f"Error generating market analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate market analysis")

@api_router.get("/crypto/{symbol}/recommendation", response_model=AIRecommendation)
async def get_crypto_recommendation(symbol: str):
    """Get AI recommendation for a specific cryptocurrency"""
    symbol = symbol.upper()
    if symbol not in TARGET_CRYPTOS:
        raise HTTPException(status_code=404, detail=f"Cryptocurrency {symbol} not supported")
    
    try:
        # Fetch current price data
        crypto_prices = await fetch_crypto_prices()
        crypto = next((c for c in crypto_prices if c.symbol == symbol), None)
        
        if not crypto:
            raise HTTPException(status_code=404, detail=f"Price data not found for {symbol}")
        
        # Generate AI recommendation
        recommendation = await generate_ai_recommendation(crypto)
        
        # Save to database
        await db.recommendations.insert_one(recommendation.dict())
        
        return recommendation
        
    except Exception as e:
        logger.error(f"Error getting recommendation for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendation")

@api_router.get("/crypto/recommendations/history", response_model=List[AIRecommendation])
async def get_recommendation_history(limit: int = 100):
    """Get historical AI recommendations"""
    try:
        recommendations = await db.recommendations.find().sort("created_at", -1).limit(limit).to_list(limit)
        return [AIRecommendation(**rec) for rec in recommendations]
    except Exception as e:
        logger.error(f"Error fetching recommendation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recommendation history")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()