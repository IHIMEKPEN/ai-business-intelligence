# AI Business Intelligence System - Quick Start Guide

This guide will help you get the AI Business Intelligence system up and running quickly for demonstration purposes with **live market data**.

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Python 3.11+
- Docker and Docker Compose (for full deployment)
- Git

### 2. Clone and Setup
```bash
# Navigate to your project directory
cd "/Users/andrew/Downloads/organized/school docs/research/machineLearning/job hunt/ai-business-intelligence"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys (Optional)
For live data access, copy the example .env and add your API keys:
```bash
cp .env.example.py .env
# Edit config.py with your API keys
```

**Free API Keys Available:**
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (forex & stocks)
- **Finnhub**: https://finnhub.io/register (real-time stock data)
- **OpenAI**: https://platform.openai.com/api-keys (AI analysis)

### 4. Run the Live Data Demo
```bash
# Run with custom framework (default)
python demo.py

# Run with LangChain AI integration (requires OpenAI API key)
export OPENAI_API_KEY=your_openai_api_key_here
python demo.py --langchain

# Run with demo data (no API keys required)
python demo.py --demo
```

This will showcase **3 real-world scenarios**:
- ✅ **Tesla & Google Stock Analysis** - Live stock data with technical indicators
- ✅ **Forex Trading Analysis** - EUR/USD, GBP/USD, USD/JPY, USD/CHF
- ✅ **Cryptocurrency Analysis** - BTC, ETH, ADA, DOT with market metrics
- ✅ **Multi-agent AI system** with real-time data processing
- ✅ **Pattern recognition** and trend analysis
- ✅ **Anomaly detection** in market data
- ✅ **Agent communication** and coordination
- ✅ **Comprehensive insights** generation
- ✅ **AI-powered insights** (when using --langchain flag)

### 5. Start the API Server
```bash
# Start the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **System Status**: http://localhost:8000/status

## 🐳 Full Deployment with Docker

### 1. Start All Services
```bash
# Start the complete system with Docker Compose
docker-compose up -d
```

This will start:
- ✅ AI API Server (port 8000)
- ✅ PostgreSQL Database (port 5432)
- ✅ Redis Cache (port 6379)
- ✅ Prometheus Monitoring (port 9090)
- ✅ Grafana Dashboards (port 3000)
- ✅ Nginx Reverse Proxy (port 80)
- ✅ Celery Workers
- ✅ Flower Monitoring (port 5555)

### 2. Access Services
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Flower**: http://localhost:5555

## 📊 Live Data API Examples

### Stock Analysis
```bash
# Analyze Tesla and Google stocks
curl -X POST "http://localhost:8000/analysis/stocks" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["TSLA", "GOOGL"], "period": "1mo", "interval": "1d"}'
```

### Forex Analysis
```bash
# Analyze forex pairs
curl -X POST "http://localhost:8000/analysis/forex" \
  -H "Content-Type: application/json" \
  -d '{"pairs": ["EUR/USD", "GBP/USD"], "interval": "1min"}'
```

### Cryptocurrency Analysis
```bash
# Analyze cryptocurrencies
curl -X POST "http://localhost:8000/analysis/crypto" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["BTC-USD", "ETH-USD"], "period": "1mo"}'
```

## 🧪 Testing

### Run All Tests
```bash
# Run the complete test suite
pytest tests/ -v

# Run specific test categories
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
```

### Test Coverage
```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html
```

## 📈 Monitoring

### System Health
```bash
# Check system health
curl http://localhost:8000/health

# Get detailed status
curl http://localhost:8000/status

# List all agents
curl http://localhost:8000/agents
```

### Metrics and Dashboards
- **Grafana**: http://localhost:3000 (admin/admin)
  - Agent performance metrics
  - Task execution statistics
  - System resource usage
- **Prometheus**: http://localhost:9090
  - Raw metrics data
  - Query interface

## 🔧 Configuration

### Environment Variables
```bash
# Copy example configuration
cp config.example.py config.py

# Edit configuration
nano config.py
```

Key configuration options:
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key
- `FINNHUB_API_KEY`: Your Finnhub API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Database connection string
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level (debug, info, warning, error)

## 🎯 Key Features Demonstrated

### AI Development (40%)
- ✅ Multi-agent architecture with specialized capabilities
- ✅ LangChain integration for AI workflows
- ✅ Domain-specific business intelligence agents
- ✅ Real-time data processing and analysis
- ✅ Live market data integration (stocks, forex, crypto)

### Collaboration (20%)
- ✅ Seamless agent communication and coordination
- ✅ Message passing and task delegation
- ✅ Cross-agent data sharing and synchronization
- ✅ Distributed task processing

### Integration & Deployment (20%)
- ✅ Cloud-native Docker deployment
- ✅ Kubernetes-ready configuration
- ✅ Comprehensive monitoring and observability
- ✅ Scalable microservices architecture
- ✅ Real-time API integrations

### Continuous Learning (20%)
- ✅ Latest AI/ML technologies (LangChain, OpenAI)
- ✅ Automated testing and validation
- ✅ Performance monitoring and optimization
- ✅ Extensible agent framework
- ✅ Live market data analysis

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Collector│    │    Analyzer     │    │  Insight Gen.   │
│      Agent      │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Communication  │
                    │    Manager      │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   REST API      │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │    │   Prometheus    │
│   Database      │    │    Cache        │    │   Monitoring    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Live Data APIs │
                    │ (yfinance, etc.)│
                    └─────────────────┘
```

## 🚀 Next Steps

1. **Get API Keys**: Sign up for free API keys to access live data
2. **Customize Agents**: Add your own specialized agents
3. **Extend Analysis**: Implement additional analysis algorithms
4. **Add Data Sources**: Integrate with your preferred data sources
5. **Deploy to Cloud**: Deploy to AWS, Azure, or GCP
6. **Scale Up**: Add more agents and workers

## 📚 Documentation

- **API Documentation**: http://localhost:8000/docs
- **Project README**: [README.md](README.md)
- **Code Documentation**: Inline code comments
- **Architecture**: See above diagram

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `docker-compose.yml`
2. **Memory issues**: Increase Docker memory allocation
3. **API key errors**: Set proper environment variables in `config.py`
4. **Database connection**: Check PostgreSQL is running
5. **Live data errors**: Verify API keys and internet connection

### Logs
```bash
# View application logs
docker-compose logs ai-api

# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

## 🎉 Success!

You now have a fully functional AI Business Intelligence system that demonstrates:

- **Multi-agent AI architecture**
- **Real-time market data processing**
- **Live stock, forex, and crypto analysis**
- **Advanced analytics capabilities**
- **Cloud-native deployment**
- **Comprehensive monitoring**
- **Scalable design**

Perfect for showcasing AI engineering skills in job applications! 🚀 