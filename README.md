# AI Trading Simulation Platform

A multi-agent AI trading simulation platform where different LLM-powered personas compete on the same market data. Compare strategies like value investing, momentum trading, contrarian approaches, and passive indexing — each driven by a different AI model.

## Architecture

```
trading-sim/
├── backend/
│   ├── pyproject.toml              # uv-managed Python project
│   ├── config/agents.yaml          # Agent/persona configuration
│   └── src/trading_sim/
│       ├── main.py                 # FastAPI app entry point
│       ├── config.py               # YAML config loader
│       ├── agents/                 # Pydantic AI agent definitions
│       ├── strategies/             # Persona prompts & market context
│       ├── models/                 # Pydantic schemas (trades, portfolios, results)
│       ├── simulation/             # Runner, market data, execution, metrics
│       └── api/                    # FastAPI route handlers
├── frontend/
│   ├── package.json
│   └── src/
│       ├── pages/                  # Dashboard, Agents, Simulate, History, Detail
│       ├── components/             # Layout + shadcn-style UI components
│       ├── hooks/                  # useApi hook
│       └── lib/                    # API client, utilities
└── README.md
```

## Stack

- **Backend:** Python 3.12+, FastAPI, Pydantic v2, Pydantic AI
- **Frontend:** React 18, TypeScript, Tailwind CSS, Recharts, shadcn/ui components
- **Package management:** `uv` (backend), `npm` (frontend)
- **Storage:** JSON files (no database required)

## Getting Started

### Backend

```bash
cd backend
uv sync
uv run uvicorn trading_sim.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. Interactive docs at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies API requests to the backend.

### Environment Variables

Set API keys for the LLM providers your agents use:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/agents` | List all configured agents |
| `GET` | `/api/agents/{id}` | Get agent details |
| `PUT` | `/api/agents/{id}` | Update agent configuration |
| `GET` | `/api/simulations` | List all simulation runs |
| `POST` | `/api/simulations` | Start a new simulation |
| `GET` | `/api/simulations/{id}` | Get simulation results |
| `GET` | `/api/simulations/{id}/trades` | Get trade log (optional `?agent_id=` filter) |

## Configured Agents

| Agent | Strategy | Default Model |
|-------|----------|---------------|
| Warren Buffett | Value investing — seeks undervalued companies with strong fundamentals | GPT-4o |
| Momentum Mike | Trend-following — rides winners and cuts losers fast | GPT-4o |
| Contrarian Carl | Goes against the crowd — buys fear, sells euphoria | Claude Sonnet |
| Index Irene | Passive index — buy and hold with minimal trading | Claude Sonnet |

Agents are fully configurable via `backend/config/agents.yaml` or the API/UI.

## How It Works

1. **Configure agents** with different trading personas, LLM models, and parameters
2. **Run a simulation** selecting agents, tickers, and a date range
3. **Mock market data** is generated using geometric Brownian motion (realistic OHLCV)
4. **Each agent** receives market snapshots and portfolio state, then outputs structured trade decisions via Pydantic AI
5. **Trades are executed** and portfolio values tracked over time
6. **Compare results** with charts (portfolio value curves) and metrics (return, Sharpe, drawdown, win rate)
7. **Review reasoning** — every trade includes the LLM's explanation
