const API_BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// --- Types matching backend schemas ---

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  persona_prompt: string;
  model_provider: string;
  model_id: string;
  temperature: number;
  max_tokens: number;
  initial_capital: number;
}

export interface TradeDecision {
  agent_id: string;
  timestamp: string;
  ticker: string;
  action: "buy" | "sell" | "hold";
  quantity: number;
  confidence: number;
  reasoning: string;
  price_at_decision: number;
}

export interface PerformanceMetrics {
  total_return_pct: number;
  sharpe_ratio: number;
  max_drawdown_pct: number;
  win_rate: number;
  total_trades: number;
}

export interface AgentResult {
  agent_id: string;
  agent_name: string;
  portfolio: {
    cash: number;
    holdings: Record<string, { ticker: string; quantity: number; avg_cost: number }>;
  };
  trades: TradeDecision[];
  portfolio_history: number[];
  date_labels: string[];
  metrics: PerformanceMetrics;
}

export interface SimulationResult {
  id: string;
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  start_date: string;
  end_date: string;
  tickers: string[];
  agent_ids: string[];
  agent_results: Record<string, AgentResult>;
  error: string | null;
}

export interface SimulationSummary {
  id: string;
  status: string;
  created_at: string;
  start_date: string;
  end_date: string;
  tickers: string[];
  agent_ids: string[];
}

// --- API functions ---

export function fetchAgents(): Promise<AgentConfig[]> {
  return request("/agents");
}

export function fetchAgent(id: string): Promise<AgentConfig> {
  return request(`/agents/${id}`);
}

export function updateAgent(
  id: string,
  updates: Partial<AgentConfig>
): Promise<AgentConfig> {
  return request(`/agents/${id}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

export function fetchSimulations(): Promise<SimulationSummary[]> {
  return request("/simulations");
}

export function fetchSimulation(id: string): Promise<SimulationResult> {
  return request(`/simulations/${id}`);
}

export function createSimulation(params: {
  agent_ids: string[];
  tickers?: string[];
  start_date?: string;
  end_date?: string;
}): Promise<SimulationResult> {
  return request("/simulations", {
    method: "POST",
    body: JSON.stringify(params),
  });
}

export function fetchTrades(
  simId: string,
  agentId?: string
): Promise<TradeDecision[]> {
  const q = agentId ? `?agent_id=${agentId}` : "";
  return request(`/simulations/${simId}/trades${q}`);
}
