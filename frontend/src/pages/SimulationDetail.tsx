import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useApi } from "@/hooks/useApi";
import { fetchSimulation, type SimulationResult, type AgentResult, type TradeDecision } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { RefreshCw } from "lucide-react";

const AGENT_COLORS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed", "#0891b2"];

export default function SimulationDetail() {
  const { id } = useParams<{ id: string }>();
  const { data: sim, loading, error, refetch } = useApi(
    () => fetchSimulation(id!),
    [id]
  );

  // Auto-refresh while running
  const [autoRefresh, setAutoRefresh] = useState(true);
  useEffect(() => {
    if (!autoRefresh || !sim || sim.status === "completed" || sim.status === "failed") return;
    const interval = setInterval(refetch, 3000);
    return () => clearInterval(interval);
  }, [autoRefresh, sim, refetch]);

  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  if (loading && !sim) return <p className="text-gray-500">Loading simulation...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;
  if (!sim) return <p className="text-gray-500">Simulation not found</p>;

  const agentResults = Object.values(sim.agent_results);
  const isRunning = sim.status === "running" || sim.status === "pending";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Simulation <span className="font-mono">{sim.id}</span>
          </h1>
          <p className="text-gray-500">
            {sim.start_date} to {sim.end_date} | {sim.tickers.join(", ")}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={sim.status} />
          {isRunning && (
            <Button size="sm" variant="outline" onClick={refetch}>
              <RefreshCw className="mr-1 h-4 w-4 animate-spin" />
              Refreshing...
            </Button>
          )}
        </div>
      </div>

      {sim.error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="py-4">
            <p className="text-sm text-red-600">{sim.error}</p>
          </CardContent>
        </Card>
      )}

      {agentResults.length > 0 && (
        <>
          {/* Portfolio value chart */}
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Value Over Time</CardTitle>
              <CardDescription>Comparative performance of all agents</CardDescription>
            </CardHeader>
            <CardContent>
              <PortfolioChart agentResults={agentResults} />
            </CardContent>
          </Card>

          {/* Metrics comparison */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
              <CardDescription>Side-by-side comparison</CardDescription>
            </CardHeader>
            <CardContent>
              <MetricsComparison agentResults={agentResults} />
            </CardContent>
          </Card>

          {/* Metrics bar chart */}
          <Card>
            <CardHeader>
              <CardTitle>Return Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <ReturnBarChart agentResults={agentResults} />
            </CardContent>
          </Card>

          {/* Trade log */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Trade Log</CardTitle>
                  <CardDescription>Decision history with LLM reasoning</CardDescription>
                </div>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant={selectedAgent === null ? "default" : "outline"}
                    onClick={() => setSelectedAgent(null)}
                  >
                    All
                  </Button>
                  {agentResults.map((ar) => (
                    <Button
                      key={ar.agent_id}
                      size="sm"
                      variant={selectedAgent === ar.agent_id ? "default" : "outline"}
                      onClick={() => setSelectedAgent(ar.agent_id)}
                    >
                      {ar.agent_name}
                    </Button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <TradeLog
                agentResults={agentResults}
                filterAgentId={selectedAgent}
              />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function PortfolioChart({ agentResults }: { agentResults: AgentResult[] }) {
  if (agentResults.length === 0) return null;

  // Build chart data: array of { date, agent1_value, agent2_value, ... }
  const maxLen = Math.max(...agentResults.map((ar) => ar.portfolio_history.length));
  const labels = agentResults[0]?.date_labels ?? [];

  const data = Array.from({ length: maxLen }, (_, i) => {
    const point: Record<string, string | number> = {
      date: labels[i] ?? String(i),
    };
    for (const ar of agentResults) {
      point[ar.agent_name] = ar.portfolio_history[i] ?? 0;
    }
    return point;
  });

  // Sample data points if too many (show ~100 points max)
  const step = Math.max(1, Math.floor(data.length / 100));
  const sampled = data.filter((_, i) => i % step === 0 || i === data.length - 1);

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={sampled}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fontSize: 11 }}
          tickFormatter={(v: number) => `$${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip
          formatter={(value: number) => [`$${value.toLocaleString()}`, ""]}
          labelStyle={{ fontWeight: "bold" }}
        />
        <Legend />
        {agentResults.map((ar, i) => (
          <Line
            key={ar.agent_id}
            type="monotone"
            dataKey={ar.agent_name}
            stroke={AGENT_COLORS[i % AGENT_COLORS.length]}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

function MetricsComparison({ agentResults }: { agentResults: AgentResult[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-left text-gray-500">
            <th className="pb-2 pr-4 font-medium">Agent</th>
            <th className="pb-2 pr-4 font-medium">Total Return</th>
            <th className="pb-2 pr-4 font-medium">Sharpe Ratio</th>
            <th className="pb-2 pr-4 font-medium">Max Drawdown</th>
            <th className="pb-2 pr-4 font-medium">Win Rate</th>
            <th className="pb-2 font-medium">Total Trades</th>
          </tr>
        </thead>
        <tbody>
          {agentResults.map((ar, i) => (
            <tr key={ar.agent_id} className="border-b last:border-0">
              <td className="py-3 pr-4">
                <div className="flex items-center gap-2">
                  <div
                    className="h-3 w-3 rounded-full"
                    style={{ backgroundColor: AGENT_COLORS[i % AGENT_COLORS.length] }}
                  />
                  <span className="font-medium">{ar.agent_name}</span>
                </div>
              </td>
              <td className="py-3 pr-4">
                <span
                  className={
                    ar.metrics.total_return_pct >= 0 ? "text-green-600" : "text-red-600"
                  }
                >
                  {ar.metrics.total_return_pct >= 0 ? "+" : ""}
                  {ar.metrics.total_return_pct.toFixed(2)}%
                </span>
              </td>
              <td className="py-3 pr-4">{ar.metrics.sharpe_ratio.toFixed(2)}</td>
              <td className="py-3 pr-4 text-red-600">
                -{ar.metrics.max_drawdown_pct.toFixed(2)}%
              </td>
              <td className="py-3 pr-4">{ar.metrics.win_rate.toFixed(1)}%</td>
              <td className="py-3">{ar.metrics.total_trades}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReturnBarChart({ agentResults }: { agentResults: AgentResult[] }) {
  const data = agentResults.map((ar, i) => ({
    name: ar.agent_name,
    return: ar.metrics.total_return_pct,
    fill: AGENT_COLORS[i % AGENT_COLORS.length],
  }));

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={(v: number) => `${v}%`} />
        <Tooltip formatter={(value: number) => [`${value.toFixed(2)}%`, "Return"]} />
        <Bar dataKey="return" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <rect key={index} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function TradeLog({
  agentResults,
  filterAgentId,
}: {
  agentResults: AgentResult[];
  filterAgentId: string | null;
}) {
  const allTrades: (TradeDecision & { agent_name: string })[] = [];
  for (const ar of agentResults) {
    if (filterAgentId && ar.agent_id !== filterAgentId) continue;
    for (const t of ar.trades) {
      allTrades.push({ ...t, agent_name: ar.agent_name });
    }
  }
  allTrades.sort((a, b) => a.timestamp.localeCompare(b.timestamp));

  if (allTrades.length === 0) {
    return <p className="text-sm text-gray-500">No trades recorded.</p>;
  }

  return (
    <div className="max-h-96 space-y-3 overflow-y-auto">
      {allTrades.map((trade, i) => (
        <div key={i} className="rounded-lg border p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  trade.action === "buy"
                    ? "success"
                    : trade.action === "sell"
                      ? "destructive"
                      : "secondary"
                }
              >
                {trade.action.toUpperCase()}
              </Badge>
              <span className="font-mono text-sm font-medium">{trade.ticker}</span>
              {trade.quantity > 0 && (
                <span className="text-sm text-gray-500">x{trade.quantity}</span>
              )}
              <span className="text-sm text-gray-400">@ ${trade.price_at_decision.toFixed(2)}</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Badge variant="outline">{trade.agent_name}</Badge>
              <span>{new Date(trade.timestamp).toLocaleDateString()}</span>
              <span>Conf: {(trade.confidence * 100).toFixed(0)}%</span>
            </div>
          </div>
          <p className="mt-2 text-sm text-gray-600">{trade.reasoning}</p>
        </div>
      ))}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const variant =
    status === "completed"
      ? "success"
      : status === "running"
        ? "warning"
        : status === "failed"
          ? "destructive"
          : "secondary";
  return <Badge variant={variant}>{status}</Badge>;
}
