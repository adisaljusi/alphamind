import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useApi } from "@/hooks/useApi";
import { fetchSimulations, fetchAgents, type SimulationSummary, type AgentConfig } from "@/lib/api";
import { BarChart3, Bot, Play, TrendingUp } from "lucide-react";

export default function Dashboard() {
  const { data: simulations, loading: simsLoading } = useApi(fetchSimulations);
  const { data: agents, loading: agentsLoading } = useApi(fetchAgents);

  const completedSims = simulations?.filter((s) => s.status === "completed") ?? [];
  const recentSims = simulations?.slice(0, 5) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">AI-Assisted Trading Simulation Platform</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Agents"
          value={agentsLoading ? "..." : String(agents?.length ?? 0)}
          description="Configured trading personas"
          icon={<Bot className="h-4 w-4 text-gray-500" />}
        />
        <StatsCard
          title="Simulations"
          value={simsLoading ? "..." : String(simulations?.length ?? 0)}
          description="Total simulation runs"
          icon={<Play className="h-4 w-4 text-gray-500" />}
        />
        <StatsCard
          title="Completed"
          value={simsLoading ? "..." : String(completedSims.length)}
          description="Successfully completed"
          icon={<TrendingUp className="h-4 w-4 text-gray-500" />}
        />
        <StatsCard
          title="Models"
          value={agentsLoading ? "..." : String(new Set(agents?.map((a) => a.model_id)).size)}
          description="Unique LLM models"
          icon={<BarChart3 className="h-4 w-4 text-gray-500" />}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Agents overview */}
        <Card>
          <CardHeader>
            <CardTitle>Trading Agents</CardTitle>
            <CardDescription>Configured AI personas</CardDescription>
          </CardHeader>
          <CardContent>
            {agentsLoading ? (
              <p className="text-sm text-gray-500">Loading...</p>
            ) : (
              <div className="space-y-3">
                {agents?.map((agent: AgentConfig) => (
                  <div
                    key={agent.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div>
                      <p className="font-medium text-gray-900">{agent.name}</p>
                      <p className="text-xs text-gray-500">{agent.description}</p>
                    </div>
                    <Badge variant="secondary">{agent.model_id}</Badge>
                  </div>
                ))}
              </div>
            )}
            <Link to="/agents" className="mt-4 block">
              <Button variant="outline" size="sm" className="w-full">
                Manage Agents
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* Recent simulations */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Simulations</CardTitle>
            <CardDescription>Latest simulation runs</CardDescription>
          </CardHeader>
          <CardContent>
            {simsLoading ? (
              <p className="text-sm text-gray-500">Loading...</p>
            ) : recentSims.length === 0 ? (
              <p className="text-sm text-gray-500">No simulations yet. Start one!</p>
            ) : (
              <div className="space-y-3">
                {recentSims.map((sim: SimulationSummary) => (
                  <Link
                    key={sim.id}
                    to={`/simulations/${sim.id}`}
                    className="flex items-center justify-between rounded-lg border p-3 transition-colors hover:bg-gray-50"
                  >
                    <div>
                      <p className="font-mono text-sm font-medium">{sim.id}</p>
                      <p className="text-xs text-gray-500">
                        {sim.start_date} to {sim.end_date}
                      </p>
                    </div>
                    <StatusBadge status={sim.status} />
                  </Link>
                ))}
              </div>
            )}
            <Link to="/simulate" className="mt-4 block">
              <Button size="sm" className="w-full">
                New Simulation
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatsCard({
  title,
  value,
  description,
  icon,
}: {
  title: string;
  value: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-gray-500">{description}</p>
      </CardContent>
    </Card>
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
