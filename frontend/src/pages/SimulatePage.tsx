import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useApi } from "@/hooks/useApi";
import { fetchAgents, createSimulation, type AgentConfig } from "@/lib/api";
import { Play, Check } from "lucide-react";

const AVAILABLE_TICKERS = [
  "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "JPM", "JNJ", "SPY", "BND",
];

export default function SimulatePage() {
  const navigate = useNavigate();
  const { data: agents, loading } = useApi(fetchAgents);

  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set());
  const [selectedTickers, setSelectedTickers] = useState<Set<string>>(
    new Set(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"])
  );
  const [startDate, setStartDate] = useState("2024-01-02");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleAgent = (id: string) => {
    const next = new Set(selectedAgents);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    setSelectedAgents(next);
  };

  const toggleTicker = (ticker: string) => {
    const next = new Set(selectedTickers);
    if (next.has(ticker)) next.delete(ticker);
    else next.add(ticker);
    setSelectedTickers(next);
  };

  const handleRun = async () => {
    if (selectedAgents.size === 0) {
      setError("Select at least one agent");
      return;
    }
    if (selectedTickers.size === 0) {
      setError("Select at least one ticker");
      return;
    }

    setRunning(true);
    setError(null);
    try {
      const result = await createSimulation({
        agent_ids: Array.from(selectedAgents),
        tickers: Array.from(selectedTickers),
        start_date: startDate,
        end_date: endDate,
      });
      navigate(`/simulations/${result.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start simulation");
      setRunning(false);
    }
  };

  if (loading) return <p className="text-gray-500">Loading...</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Run Simulation</h1>
        <p className="text-gray-500">Configure and launch a multi-agent trading simulation</p>
      </div>

      {/* Agent selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Agents</CardTitle>
          <CardDescription>Choose which AI personas to include</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            {agents?.map((agent: AgentConfig) => (
              <button
                key={agent.id}
                onClick={() => toggleAgent(agent.id)}
                className={`flex items-center gap-3 rounded-lg border p-3 text-left transition-colors ${
                  selectedAgents.has(agent.id)
                    ? "border-gray-900 bg-gray-50"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <div
                  className={`flex h-5 w-5 items-center justify-center rounded border ${
                    selectedAgents.has(agent.id)
                      ? "border-gray-900 bg-gray-900 text-white"
                      : "border-gray-300"
                  }`}
                >
                  {selectedAgents.has(agent.id) && <Check className="h-3 w-3" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{agent.name}</p>
                  <p className="text-xs text-gray-500">{agent.description}</p>
                </div>
                <Badge variant="secondary" className="text-xs">
                  {agent.model_id}
                </Badge>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Ticker selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Tickers</CardTitle>
          <CardDescription>Choose stocks to include in the simulation</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_TICKERS.map((ticker) => (
              <button
                key={ticker}
                onClick={() => toggleTicker(ticker)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  selectedTickers.has(ticker)
                    ? "bg-gray-900 text-white"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {ticker}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Date range */}
      <Card>
        <CardHeader>
          <CardTitle>Date Range</CardTitle>
          <CardDescription>Simulation time period</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Start</label>
              <input
                type="date"
                className="rounded-md border border-gray-300 p-2 text-sm"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">End</label>
              <input
                type="date"
                className="rounded-md border border-gray-300 p-2 text-sm"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {error && <p className="text-sm text-red-500">{error}</p>}

      <Button size="lg" onClick={handleRun} disabled={running}>
        <Play className="mr-2 h-4 w-4" />
        {running ? "Starting..." : "Run Simulation"}
      </Button>
    </div>
  );
}
