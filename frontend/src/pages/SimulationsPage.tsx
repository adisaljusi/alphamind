import { Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useApi } from "@/hooks/useApi";
import { fetchSimulations, type SimulationSummary } from "@/lib/api";

export default function SimulationsPage() {
  const { data: simulations, loading, error } = useApi(fetchSimulations);

  if (loading) return <p className="text-gray-500">Loading simulations...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Simulation History</h1>
        <p className="text-gray-500">View past simulation runs and results</p>
      </div>

      {simulations?.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center">
            <p className="text-gray-500">No simulations yet.</p>
            <Link to="/simulate" className="text-sm text-blue-600 hover:underline">
              Run your first simulation
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {simulations?.map((sim: SimulationSummary) => (
            <Link key={sim.id} to={`/simulations/${sim.id}`}>
              <Card className="transition-colors hover:bg-gray-50">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="font-mono text-base">{sim.id}</CardTitle>
                      <CardDescription>
                        {sim.start_date} to {sim.end_date} | {sim.agent_ids.length} agent
                        {sim.agent_ids.length !== 1 ? "s" : ""} | {sim.tickers.length} ticker
                        {sim.tickers.length !== 1 ? "s" : ""}
                      </CardDescription>
                    </div>
                    <StatusBadge status={sim.status} />
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex gap-1">
                    {sim.tickers.map((t) => (
                      <Badge key={t} variant="secondary" className="text-xs">
                        {t}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
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
