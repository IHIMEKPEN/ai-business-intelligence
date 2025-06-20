"""
Data Collector Agent

Responsible for collecting data from various sources including:
- Web scraping
- API integrations
- Real-time data feeds
- Market data collection
"""

import asyncio
import aiohttp
import yfinance as yf
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import structlog
import pandas as pd
from datetime import datetime, timedelta
import json

from core.agent_framework import BaseAgent, AgentType, Task, Message
from core.communication import communication_manager

logger = structlog.get_logger(__name__)


class DataCollectorAgent(BaseAgent):
    """
    Data Collector Agent for gathering data from various sources
    
    Capabilities:
    - Web scraping with BeautifulSoup
    - API integrations (Alpha Vantage, Yahoo Finance)
    - Real-time market data collection
    - Data validation and cleaning
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or f"data_collector_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            agent_type=AgentType.DATA_COLLECTOR,
            name="Data Collector Agent"
        )
        
        self.capabilities = [
            "web_scraping",
            "api_integration", 
            "market_data_collection",
            "data_validation",
            "real_time_feeds"
        ]
        
        self.session = None
        self.data_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        logger.info(
            "Data Collector Agent initialized",
            agent_id=self.agent_id,
            capabilities=self.capabilities
        )
    
    async def start(self):
        """Start the agent and initialize HTTP session"""
        await super().start()
        
        # Initialize aiohttp session for web requests
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        logger.info("Data Collector Agent started", agent_id=self.agent_id)
    
    async def stop(self):
        """Stop the agent and close HTTP session"""
        await super().stop()
        
        if self.session:
            await self.session.close()
        
        logger.info("Data Collector Agent stopped", agent_id=self.agent_id)
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Process data collection tasks"""
        task_type = task.name
        parameters = task.parameters
        
        logger.info(
            "Processing data collection task",
            task_id=task.id,
            task_type=task_type,
            parameters=parameters
        )
        
        try:
            if task_type == "collect_market_data":
                return await self._collect_market_data(parameters)
            elif task_type == "web_scraping":
                return await self._web_scraping(parameters)
            elif task_type == "api_integration":
                return await self._api_integration(parameters)
            elif task_type == "collect_real_time_data":
                return await self._collect_real_time_data(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(
                "Task processing failed",
                task_id=task.id,
                task_type=task_type,
                error=str(e)
            )
            raise
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        message_type = message.message_type
        
        if message_type == "data_request":
            return await self._handle_data_request(message)
        elif message_type == "cache_invalidation":
            return await self._handle_cache_invalidation(message)
        else:
            logger.warning(
                "Unknown message type",
                message_type=message_type,
                agent_id=self.agent_id
            )
            return None
    
    async def _collect_market_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collect market data for given symbols"""
        symbols = parameters.get("symbols", [])
        period = parameters.get("period", "1d")
        interval = parameters.get("interval", "1m")
        
        if not symbols:
            raise ValueError("No symbols provided for market data collection")
        
        results = {}
        
        for symbol in symbols:
            try:
                # Check cache first
                cache_key = f"market_data_{symbol}_{period}_{interval}"
                if cache_key in self.data_cache:
                    cache_time, cache_data = self.data_cache[cache_key]
                    if (datetime.utcnow() - cache_time).seconds < self.cache_ttl:
                        results[symbol] = cache_data
                        continue
                
                # Fetch fresh data
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                # Convert to JSON-serializable format
                data_dict = {
                    "symbol": symbol,
                    "period": period,
                    "interval": interval,
                    "data": data.to_dict('records'),
                    "metadata": {
                        "last_updated": datetime.utcnow().isoformat(),
                        "rows": len(data),
                        "columns": list(data.columns)
                    }
                }
                
                # Cache the result
                self.data_cache[cache_key] = (datetime.utcnow(), data_dict)
                results[symbol] = data_dict
                
                logger.info(
                    "Market data collected",
                    symbol=symbol,
                    rows=len(data),
                    agent_id=self.agent_id
                )
                
            except Exception as e:
                logger.error(
                    "Failed to collect market data",
                    symbol=symbol,
                    error=str(e),
                    agent_id=self.agent_id
                )
                results[symbol] = {"error": str(e)}
        
        return {
            "task_type": "collect_market_data",
            "symbols": symbols,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _web_scraping(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web scraping on specified URLs"""
        urls = parameters.get("urls", [])
        selectors = parameters.get("selectors", {})
        extract_text = parameters.get("extract_text", True)
        
        if not urls:
            raise ValueError("No URLs provided for web scraping")
        
        results = {}
        
        for url in urls:
            try:
                # Check cache first
                cache_key = f"web_scraping_{hash(url)}"
                if cache_key in self.data_cache:
                    cache_time, cache_data = self.data_cache[cache_key]
                    if (datetime.utcnow() - cache_time).seconds < self.cache_ttl:
                        results[url] = cache_data
                        continue
                
                # Perform web scraping
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        scraped_data = {
                            "url": url,
                            "title": soup.title.string if soup.title else None,
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        
                        # Extract data based on selectors
                        if selectors:
                            for key, selector in selectors.items():
                                elements = soup.select(selector)
                                if extract_text:
                                    scraped_data[key] = [elem.get_text(strip=True) for elem in elements]
                                else:
                                    scraped_data[key] = [str(elem) for elem in elements]
                        
                        # Cache the result
                        self.data_cache[cache_key] = (datetime.utcnow(), scraped_data)
                        results[url] = scraped_data
                        
                        logger.info(
                            "Web scraping completed",
                            url=url,
                            agent_id=self.agent_id
                        )
                    else:
                        results[url] = {"error": f"HTTP {response.status}"}
                        
            except Exception as e:
                logger.error(
                    "Web scraping failed",
                    url=url,
                    error=str(e),
                    agent_id=self.agent_id
                )
                results[url] = {"error": str(e)}
        
        return {
            "task_type": "web_scraping",
            "urls": urls,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _api_integration(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate with external APIs"""
        api_type = parameters.get("api_type")
        endpoint = parameters.get("endpoint")
        api_key = parameters.get("api_key")
        params = parameters.get("params", {})
        
        if not all([api_type, endpoint]):
            raise ValueError("API type and endpoint are required")
        
        try:
            # Check cache first
            cache_key = f"api_{api_type}_{hash(endpoint + str(params))}"
            if cache_key in self.data_cache:
                cache_time, cache_data = self.data_cache[cache_key]
                if (datetime.utcnow() - cache_time).seconds < self.cache_ttl:
                    return cache_data
            
            # Prepare request parameters
            request_params = params.copy()
            if api_key:
                request_params["apikey"] = api_key
            
            # Make API request
            async with self.session.get(endpoint, params=request_params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = {
                        "api_type": api_type,
                        "endpoint": endpoint,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Cache the result
                    self.data_cache[cache_key] = (datetime.utcnow(), result)
                    
                    logger.info(
                        "API integration completed",
                        api_type=api_type,
                        endpoint=endpoint,
                        agent_id=self.agent_id
                    )
                    
                    return result
                else:
                    raise Exception(f"API request failed with status {response.status}")
                    
        except Exception as e:
            logger.error(
                "API integration failed",
                api_type=api_type,
                endpoint=endpoint,
                error=str(e),
                agent_id=self.agent_id
            )
            raise
    
    async def _collect_real_time_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Collect real-time data from various sources"""
        data_sources = parameters.get("data_sources", [])
        duration = parameters.get("duration", 60)  # seconds
        
        if not data_sources:
            raise ValueError("No data sources specified for real-time collection")
        
        results = {}
        start_time = datetime.utcnow()
        
        for source in data_sources:
            source_type = source.get("type")
            source_config = source.get("config", {})
            
            if source_type == "market_ticker":
                # Real-time market ticker data
                symbol = source_config.get("symbol")
                if symbol:
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        results[source_type] = {
                            "symbol": symbol,
                            "price": info.get("regularMarketPrice"),
                            "volume": info.get("volume"),
                            "market_cap": info.get("marketCap"),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    except Exception as e:
                        results[source_type] = {"error": str(e)}
            
            elif source_type == "web_socket":
                # WebSocket real-time data (placeholder)
                results[source_type] = {
                    "status": "not_implemented",
                    "message": "WebSocket integration not yet implemented"
                }
        
        return {
            "task_type": "collect_real_time_data",
            "data_sources": data_sources,
            "results": results,
            "collection_duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _handle_data_request(self, message: Message) -> Optional[Message]:
        """Handle data requests from other agents"""
        content = message.content
        data_type = content.get("data_type")
        parameters = content.get("parameters", {})
        
        try:
            if data_type == "market_data":
                result = await self._collect_market_data(parameters)
            elif data_type == "web_scraping":
                result = await self._web_scraping(parameters)
            elif data_type == "api_integration":
                result = await self._api_integration(parameters)
            else:
                result = {"error": f"Unknown data type: {data_type}"}
            
            # Send response message
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="data_response",
                content=result,
                correlation_id=message.id
            )
            
            return response
            
        except Exception as e:
            logger.error(
                "Data request handling failed",
                data_type=data_type,
                error=str(e),
                agent_id=self.agent_id
            )
            
            response = Message(
                sender=self.agent_id,
                recipient=message.sender,
                message_type="data_response",
                content={"error": str(e)},
                correlation_id=message.id
            )
            
            return response
    
    async def _handle_cache_invalidation(self, message: Message) -> Optional[Message]:
        """Handle cache invalidation requests"""
        content = message.content
        cache_keys = content.get("cache_keys", [])
        
        if cache_keys == ["all"]:
            # Clear all cache
            self.data_cache.clear()
            logger.info("All cache cleared", agent_id=self.agent_id)
        else:
            # Clear specific cache keys
            for key in cache_keys:
                if key in self.data_cache:
                    del self.data_cache[key]
            
            logger.info(
                "Cache keys cleared",
                keys=cache_keys,
                agent_id=self.agent_id
            )
        
        return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.data_cache),
            "cache_keys": list(self.data_cache.keys()),
            "cache_ttl": self.cache_ttl
        }
    
    async def clear_cache(self, keys: List[str] = None):
        """Clear cache entries"""
        if keys is None:
            self.data_cache.clear()
            logger.info("All cache cleared", agent_id=self.agent_id)
        else:
            for key in keys:
                if key in self.data_cache:
                    del self.data_cache[key]
            logger.info("Specific cache keys cleared", keys=keys, agent_id=self.agent_id)


# Factory function to create data collector agent
def create_data_collector_agent(agent_id: str = None) -> DataCollectorAgent:
    """Create and return a new Data Collector Agent instance"""
    return DataCollectorAgent(agent_id) 