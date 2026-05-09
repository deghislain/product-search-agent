# Product Search Agent - AI-Powered Agentic System for Automated Product Discovery

An intelligent, autonomous AI agent that continuously monitors multiple online marketplaces to find products matching your criteria. Features adaptive learning, intelligent query optimization, and personalized recommendations. Built with Python, FastAPI, and LLM integration.

---

## 🎯 What It Does

Given a product name, description, and budget, this AI agent:

1. **Searches intelligently** with adaptive scheduling based on listing patterns
2. **Learns your preferences** from your interactions and feedback
3. **Optimizes queries** automatically using LLM-powered refinement
4. **Matches smartly** using NLP, fuzzy matching, and personalized scoring
5. **Notifies instantly** via web dashboard and email
6. **Adapts continuously** - gets better at finding what you want over time

### Example

**Input:**
```
Product: Toyota Camry
Description: 2015 model, good condition
Budget: $6,000
```

**Output:**
- Searches Craigslist, Facebook Marketplace, and eBay every 2 hours
- Finds matches with 70%+ similarity score
- Sends real-time notifications when matches are found
- Provides direct links to buy

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** | Get started in 5 minutes - setup, usage, and troubleshooting |
| **[product_search_agent_architecture.md](product_search_agent_architecture.md)** | Complete system architecture, workflows, and design decisions |
| **[project_structure_and_implementation.md](project_structure_and_implementation.md)** | Detailed implementation guide with code examples for all scrapers |
| **[email_notification_system.md](email_notification_system.md)** | Email notification setup, templates, and configuration |

---

## ✨ Key Features

### 🤖 Agentic AI Capabilities (Phase 1 Complete ✅)
- **Intelligent Query Refinement**: LLM-powered query optimization based on search results
- **Adaptive Scheduling**: Learns optimal search times for each platform
- **Preference Learning**: Tracks interactions to personalize results
- **Autonomous Decision Making**: Agent decides when and how to search
- **Continuous Improvement**: Gets smarter with every search

### 🎯 Intelligent Matching
- **Personalized Scoring**: Adapts to your preferences over time
- **Fuzzy text matching** for product names
- **NLP-based description analysis** with spaCy
- **Dynamic thresholds**: Automatically adjusts based on your feedback
- **Budget filtering** with price sensitivity learning
- **Duplicate detection** across platforms

### 🔔 Multi-Channel Notifications
- **Web Dashboard**: Real-time updates via WebSocket
- **Email**: Instant match notifications
- **Daily Digest**: Optional summary emails
- **Status Updates**: Search start/completion/error notifications

### 🌐 Multi-Platform Search
- **Craigslist** (US): Fast, location-based, RSS support
- **Facebook Marketplace** (Global): Large user base, recent listings
- **eBay** (Global): Global reach, Buy It Now + auctions
- **Kijiji** (Canada): 🍁 Canadian classified ads, no authentication required
- **Extensible Architecture**: Add new platforms in minutes - just drop a file!

### 📊 Web Dashboard
- Create and manage search requests
- View real-time match notifications
- Browse search history
- Configure preferences
- Mobile-responsive design

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd product-search-agent

# Start with Docker Compose
docker-compose up --build

# Access the application
# Backend API: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   User Interface Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     Web      │  │   REST API   │  │    Email     │     │
│  │  Dashboard   │  │              │  │    Client    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                Application Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Scheduler   │  │ Orchestrator │  │   Matching   │     │
│  │  (2 hours)   │─▶│   (Manages)  │─▶│   Engine     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Notification │  │    Email     │  │   Scraper    │     │
│  │   Service    │  │   Service    │  │   Registry   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│         Data Access Layer (Auto-Discovery)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Craigslist  │  │   Facebook   │  │     eBay     │     │
│  │   Scraper    │  │   Scraper    │  │   Scraper    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │    Kijiji    │  │   Generic    │  ← Add more easily!   │
│  │   Scraper    │  │   Scraper    │                       │
│  └──────────────┘  └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

**🎯 Extensible Architecture**: New scrapers are automatically discovered - just add a file!

---

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance async web framework
- **Groq API**: LLM integration for intelligent query optimization
- **APScheduler**: Adaptive job scheduling with pattern learning
- **BeautifulSoup4**: HTML parsing for static sites
- **Selenium**: JavaScript rendering for dynamic sites
- **SQLite/PostgreSQL**: Database with preference tracking
- **RapidFuzz**: Fast fuzzy string matching
- **spaCy**: Natural language processing for semantic analysis

### Frontend
- **React**: Component-based UI
- **Vite**: Fast build tool
- **WebSocket**: Real-time updates
- **Tailwind CSS**: Utility-first styling

### Email
- **aiosmtplib**: Async SMTP client
- **Jinja2**: HTML email templates
- **Gmail/SendGrid**: Free SMTP providers

### Deployment
- **Docker**: Containerization
- **Render/Railway/Fly.io**: Free cloud hosting
- **GitHub Actions**: CI/CD (optional)

---

## 📋 System Requirements

### Minimum
- Python 3.11+
- Node.js 18+
- 2GB RAM
- 1GB disk space

### Recommended
- Python 3.11+
- Node.js 20+
- 4GB RAM
- 5GB disk space
- Chrome/Chromium (for Selenium)

---

## 🔧 Configuration

### Environment Variables

```bash
# Application
SEARCH_INTERVAL_HOURS=2
MAX_CONCURRENT_SEARCHES=5
MATCH_THRESHOLD_DEFAULT=70.0

# Database
DATABASE_URL=sqlite:///./product_search.db

# Email (Optional)
ENABLE_EMAIL_NOTIFICATIONS=true
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Scrapers
CRAIGSLIST_DEFAULT_CITY=boston
SELENIUM_HEADLESS=true
```

See [`.env.example`](backend/.env.example) for all options.

---

## 📖 Usage Guide

### 1. Create a Search Request

**Via Web Dashboard:**
1. Open http://localhost:3000
2. Click "New Search"
3. Fill in the form:
   - Product Name: "Toyota Camry"
   - Description: "2015 model, good condition"
   - Budget: 6000
   - Location: "boston" (optional)
4. Click "Create"

**Via API:**
```bash
curl -X POST http://localhost:8000/api/search-requests \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Toyota Camry",
    "product_description": "2015 model, good condition",
    "budget": 6000,
    "location": "boston",
    "user_email": "your-email@example.com"
  }'
```

### 2. Monitor Results

- **Dashboard**: View real-time notifications
- **Email**: Receive instant match alerts
- **API**: Query matches programmatically

### 3. Manage Searches

- **Pause**: Temporarily stop searching
- **Resume**: Restart a paused search
- **Edit**: Update search criteria
- **Delete**: Remove search request

---

## 🎨 Matching Algorithm

The system scores each product using a weighted formula:

```
Match Score = (Title Similarity × 40%) + 
              (Description Similarity × 40%) + 
              (Price Attractiveness × 20%)
```

**Example:**
- Product: "2015 Toyota Camry LE - Excellent Condition"
- Your Search: "Toyota Camry 2015"
- Title Match: 90%
- Description Match: 85%
- Price: $5,500 (budget: $6,000) = 8.3% savings
- **Final Score: 87.5%** ✓ Match!

Products scoring above your threshold (default 70%) are considered matches.

---

## 🚢 Deployment

### Free Cloud Hosting Options

| Provider | Free Tier | Best For |
|----------|-----------|----------|
| **Render.com** | 750 hrs/month | Recommended - easy setup |
| **Railway.app** | $5 credit/month | Good performance |
| **Fly.io** | 3 VMs | Global deployment |

### Deploy to Render.com

1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy automatically on push

See [deployment guide](product_search_agent_architecture.md#deployment-architecture) for details.

---

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest app/tests/test_scrapers.py -v

# Test email service
pytest app/tests/test_email_service.py -v
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/api/health
```

### System Stats

```bash
curl http://localhost:8000/api/stats
```

### View Logs

```bash
# Docker
docker-compose logs -f backend

# Local
tail -f logs/app.log
```

---

## 🔒 Security

- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- Rate limiting on API and scrapers
- CORS configuration
- Environment variable protection
- No sensitive data in logs

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🐛 Troubleshooting

### Common Issues

**Scraper not finding results:**
- Check platform accessibility
- Verify search query isn't too specific
- Lower match threshold to 60%
- Check logs for errors

**Email not sending:**
- Verify SMTP credentials
- Check Gmail app password
- Ensure 2FA is enabled
- Test SMTP connection

**Database locked:**
- Reduce concurrent searches
- Consider PostgreSQL for production

See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#troubleshooting) for more solutions.

---

## 📞 Support

- **Documentation**: See docs folder
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

## 🗺️ Roadmap

### Phase 1: MVP ✅
- [x] Basic search orchestrator
- [x] Craigslist scraper
- [x] Simple matching algorithm
- [x] Web dashboard
- [x] SQLite database

### Phase 2: Multi-Platform ✅
- [x] Facebook Marketplace scraper
- [x] eBay scraper
- [x] Improved matching with NLP
- [x] WebSocket notifications
- [x] Email notifications
- [x] Kijiji.ca support (Canada) 🍁
- [x] Extensible scraper architecture

### Phase 3: Agentic AI Features ✅ (Phase 1 Complete)
- [x] **Intelligent Query Refinement**: LLM-powered query optimization
- [x] **Adaptive Search Scheduling**: Pattern-based timing optimization
- [x] **User Preference Learning**: Interaction tracking and personalization
- [x] **Personalized Scoring**: Dynamic match scoring based on preferences
- [x] **Query History Tracking**: Version control for search queries
- [ ] Multi-Agent Collaboration (Phase 2)
- [ ] Reasoning and Explanation Engine (Phase 2)
- [ ] Goal-Oriented Planning (Phase 2)

### Phase 4: Advanced AI Features (In Progress)
- [ ] Reinforcement Learning for search optimization
- [ ] Natural Language Interface for search creation
- [ ] Predictive Analytics for price trends
- [ ] User authentication
- [ ] Multiple users support
- [ ] Search analytics dashboard
- [ ] Mobile app
- [ ] More platforms (OfferUp, Letgo, Autotrader, etc.)
- [ ] Price history tracking
- [ ] Browser extension

### Phase 5: Enterprise (Future)
- [ ] PostgreSQL support (production-ready)
- [ ] Redis caching
- [ ] Horizontal scaling
- [ ] API rate limiting per user
- [ ] Webhook notifications
- [ ] Custom scraper builder

---

## 💡 Use Cases

1. **Car Shopping**: Find used cars within budget
2. **Electronics**: Monitor for deals on laptops, phones
3. **Furniture**: Search for specific furniture pieces
4. **Collectibles**: Track rare items across platforms
5. **Real Estate**: Monitor rental listings
6. **General Shopping**: Any product search automation

---

## 🎓 Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [BeautifulSoup Tutorial](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium Python Docs](https://selenium-python.readthedocs.io)
- [React Documentation](https://react.dev)
- [Web Scraping Best Practices](https://www.scrapehero.com/web-scraping-best-practices/)

---

## 📈 Performance

- **Search Speed**: 2-5 minutes per execution
- **Match Accuracy**: 85-90% with default settings
- **Uptime**: 99%+ (with proper deployment)
- **Scalability**: Handles 10+ concurrent searches

---

## 🌟 Features Comparison

| Feature | This System | Manual Search |
|---------|-------------|---------------|
| **Automation** | ✅ Every 2 hours | ❌ Manual |
| **Multi-Platform** | ✅ 3+ platforms | ❌ One at a time |
| **Smart Matching** | ✅ NLP + Fuzzy | ❌ Exact match only |
| **Notifications** | ✅ Real-time | ❌ None |
| **History** | ✅ Full tracking | ❌ None |
| **Cost** | ✅ Free | ✅ Free |
| **Time Saved** | ✅ Hours/week | ❌ N/A |

---

## 🙏 Acknowledgments

Built with amazing open-source tools:
- FastAPI by Sebastián Ramírez
- BeautifulSoup by Leonard Richardson
- Selenium by the Selenium Project
- React by Meta
- And many more...

---

## 📄 Summary

This system provides a complete, AI-powered agentic solution for automated product searching:

✅ **AI-Powered**: LLM-based query optimization and learning
✅ **Adaptive**: Learns from your behavior and preferences
✅ **Intelligent**: Personalized scoring and matching
✅ **Autonomous**: Makes decisions about when and how to search
✅ **Real-time**: Instant notifications via WebSocket
✅ **Multi-channel**: Web dashboard + Email
✅ **Scalable**: Easy to extend with new platforms
✅ **Well-documented**: Comprehensive guides and architecture docs

**Ready to start? See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)!**

---

## 🤖 Agentic AI Features (NEW!)

### What Makes This an "Agent"?

Unlike traditional automated systems, this is a true AI agent that:

1. **Learns Autonomously**: Tracks your interactions to understand preferences
2. **Makes Decisions**: Decides optimal search times based on platform patterns
3. **Adapts Continuously**: Refines queries using LLM analysis of results
4. **Personalizes Results**: Adjusts scoring based on what you actually click
5. **Explains Reasoning**: Can explain why it made certain decisions (Phase 2)

### Phase 1 Agentic Features ✅

#### 1. Intelligent Query Refinement
- Uses Groq LLM API to analyze search results
- Automatically improves queries based on what you click/ignore
- Tracks query evolution with version history
- Example: "Toyota Camry" → "Toyota Camry 2015-2018 LE SE under 100k miles"

#### 2. Adaptive Search Scheduling
- Learns when new listings appear on each platform
- Adjusts search timing for maximum efficiency
- Reduces unnecessary searches during low-activity periods
- Increases frequency during peak listing times

#### 3. User Preference Learning
- Tracks every interaction (views, clicks, ignores)
- Builds preference profile automatically
- Adjusts match scoring based on learned preferences
- Dynamically tunes match thresholds

**See [docs/AGENTIC_UPGRADE_PLAN.md](docs/AGENTIC_UPGRADE_PLAN.md) for full details on the AI agent architecture.**

---

Made with ❤️ by the Product Search Agent Team