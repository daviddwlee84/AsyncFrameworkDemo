# Asynchronous Framework Demo

A complete demonstration of an asynchronous task processing framework featuring GraphQL, PostgreSQL triggers, async workers, and Stripe API integration.

**Inspired by:** [如何在架构层面解决90%的问题【让编程再次伟大#12】](https://www.youtube.com/watch?v=Y0688p1afBo)

## 🏗️ Architecture

```mermaid
graph LR
    User((User)) -->|HTTP| GraphQL[GraphQL API]
    GraphQL -->|SQL| PostgreSQL[(PostgreSQL + Supabase)]
    PostgreSQL -->|pg_notify| Worker1[Stripe Worker]
    PostgreSQL -->|trigger| Worker2[Worker 2]
    PostgreSQL -->|trigger| Worker3[Worker 3]
    PostgreSQL -->|trigger| Worker4[Worker N]
    
    Worker1 -.->|API calls| Stripe[Stripe API]
    Worker2 -.->|API calls| API[3rd Party APIs]
    Worker3 -.->|API calls| API
    Worker4 -.->|API calls| API
    
    subgraph Sync[Synchronous Layer]
        User
        GraphQL
        PostgreSQL
    end
    
    subgraph Async[Asynchronous Layer]
        Worker1
        Worker2
        Worker3
        Worker4
        Stripe
        API
    end
    
    classDef orange fill:#ff6600,stroke:#fff,stroke-width:2px,color:#fff
    classDef database fill:#ff9966,stroke:#fff,stroke-width:2px,color:#fff
    classDef user fill:#ff9966,stroke:#fff,stroke-width:2px,color:#000
    
    class GraphQL,Worker1,Worker2,Worker3,Worker4 orange
    class PostgreSQL database
    class User user
```

**Flow:** Client → GraphQL → PostgreSQL → Triggers → Workers → Third-party APIs

## ✨ Features

- 🚀 **GraphQL API** with Strawberry framework
- 🗄️ **PostgreSQL with triggers** for automatic task dispatch
- ⚡ **Async workers** listening to database notifications
- 💳 **Stripe API integration** for payment processing
- 🎨 **Streamlit frontend** for task management
- 📊 **Real-time task monitoring** and status updates
- 🔧 **uv package manager** for fast dependency management
- 🐳 **Supabase** for managed PostgreSQL with admin UI

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Strawberry GraphQL
- **Database:** PostgreSQL (Supabase), pg_notify/LISTEN
- **Workers:** asyncio, asyncpg
- **Third-party API:** Stripe
- **Frontend:** Streamlit
- **Package Manager:** uv

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** 
2. **uv package manager** - [Install uv](https://github.com/astral-sh/uv)
3. **Docker** - for Supabase local development
4. **Supabase CLI** - [Install guide](https://supabase.com/docs/guides/cli)

### Setup

1. **Clone and setup environment:**
   ```bash
   git clone <repo-url>
   cd AsyncFrameworkDemo
   
   # Run the setup script
   python scripts/setup_demo.py
   ```

2. **Configure environment (optional):**
   ```bash
   cp environment.example .env
   # Edit .env with your settings (Stripe keys, etc.)
   ```

### Running the Demo

Open **3 terminals** and run:

**Terminal 1 - Backend:**
```bash
python scripts/start_backend.py
```

**Terminal 2 - Workers:**
```bash
python scripts/start_workers.py
```

**Terminal 3 - Frontend:**
```bash
python scripts/start_frontend.py
```

### Access Points

- 🌐 **Frontend:** http://127.0.0.1:8501
- 📊 **GraphQL Playground:** http://127.0.0.1:8000/graphql
- 🗄️ **Supabase Studio:** http://127.0.0.1:54323

### Test the Demo

Run the automated demo script:
```bash
python scripts/demo.py
```

## 🎯 Demo Walkthrough

### 1. Create a Stripe Customer
- Open the Streamlit frontend
- Go to "👤 Create Customer" 
- Fill in email and name
- Submit → Task created and processed asynchronously

### 2. Create a Payment
- Go to "💳 Create Payment"
- Enter amount, currency, and customer ID
- Submit → Payment intent created via worker

### 3. Monitor Tasks
- Go to "📋 View Tasks"
- See real-time task status updates
- Filter by status, auto-refresh available

## 🔍 How It Works

### 1. Task Creation (Synchronous)
```python
# GraphQL mutation creates task in PostgreSQL
mutation {
  createStripeCustomerTask(email: "test@example.com", name: "Test") {
    id
    status
    type
  }
}
```

### 2. Database Trigger (Automatic)
```sql
-- PostgreSQL trigger fires on INSERT
CREATE TRIGGER notify_new_task_trigger
    AFTER INSERT ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION notify_new_task();
```

### 3. Worker Processing (Asynchronous)
```python
# Worker receives notification and processes task
async def _handle_notification(self, connection, pid, channel, payload):
    task_data = json.loads(payload)
    await self._process_task(task_data)
```

### 4. Third-party API Call
```python
# Stripe API call in worker
customer = stripe.Customer.create(
    email=email,
    name=name
)
```

## 📁 Project Structure

```
AsyncFrameworkDemo/
├── backend/                 # GraphQL API
│   ├── models/             # Pydantic models
│   ├── database/           # Database connections & repositories  
│   ├── graphql/            # GraphQL schema & resolvers
│   └── main.py             # FastAPI application
├── workers/                # Async task workers
│   ├── base_worker.py      # Abstract worker base class
│   ├── stripe_worker.py    # Stripe API worker
│   └── worker_manager.py   # Worker orchestration
├── frontend/               # Streamlit UI
│   └── streamlit_app.py    # Web interface
├── scripts/                # Utility scripts
│   ├── setup_demo.py       # Environment setup
│   ├── start_backend.py    # Start GraphQL server
│   ├── start_workers.py    # Start worker system
│   ├── start_frontend.py   # Start Streamlit
│   └── demo.py             # Automated demo
├── supabase/               # Database config & migrations
│   ├── config.toml         # Supabase configuration
│   ├── migrations/         # SQL migrations
│   └── seed.sql            # Test data
└── pyproject.toml          # uv package configuration
```

## 🔧 Configuration

### Environment Variables

Create `.env` file with:

```bash
# Supabase (auto-configured for local development)
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=your_key_here

# Database (auto-configured for local development)  
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Stripe (optional - works in simulation mode without keys)
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here

# Application
GRAPHQL_HOST=0.0.0.0
GRAPHQL_PORT=8000
FRONTEND_PORT=8501
```

### Task Types

Currently supported task types:
- `stripe_create_customer` - Create Stripe customer
- `stripe_create_payment` - Create payment intent  
- `stripe_refund_payment` - Refund payment

### Adding New Workers

1. Create worker class extending `BaseWorker`
2. Implement `can_handle_task()` and `execute_task()` 
3. Add to `WorkerManager` in `worker_manager.py`

## 🧪 Testing

### Manual Testing
- Use the Streamlit frontend 
- Use GraphQL Playground at http://127.0.0.1:8000/graphql
- Monitor Supabase Studio for database changes

### Automated Testing
```bash
python scripts/demo.py
```

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check if port 8000 is available
- Ensure dependencies are installed: `uv sync`

**Workers not processing tasks:**
- Check if Supabase is running: `supabase status`
- Verify database connection in worker logs

**Frontend connection errors:**
- Ensure backend is running on port 8000
- Check CORS settings if needed

**Supabase issues:**
- Restart Supabase: `supabase stop && supabase start`
- Check Docker is running
- Verify migrations: `supabase db reset`

### Logs

- Backend logs: Available in terminal running `start_backend.py`
- Worker logs: Available in terminal running `start_workers.py`  
- Supabase logs: `supabase logs`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add new workers or improve existing components
4. Test with the demo scripts
5. Submit a pull request

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Strawberry GraphQL](https://strawberry.rocks/)
- [Stripe API Reference](https://stripe.com/docs/api)
- [PostgreSQL LISTEN/NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html)

## ✅ Completed Features

- [x] GraphQL backend with FastAPI and Strawberry
- [x] PostgreSQL database with triggers and notifications  
- [x] Async worker system with pg_notify
- [x] Stripe API integration
- [x] Streamlit frontend for task management
- [x] Real-time task monitoring
- [x] Automated demo and setup scripts
- [x] Comprehensive documentation
