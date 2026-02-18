import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useApi } from "@/hooks/useApi";
import { fetchAgents, updateAgent, type AgentConfig } from "@/lib/api";
import { Bot, Save, X } from "lucide-react";

export default function AgentsPage() {
  const { data: agents, loading, error, refetch } = useApi(fetchAgents);
  const [editingId, setEditingId] = useState<string | null>(null);

  if (loading) return <p className="text-gray-500">Loading agents...</p>;
  if (error) return <p className="text-red-500">Error: {error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Trading Agents</h1>
        <p className="text-gray-500">View and configure AI trading personas</p>
      </div>

      <div className="grid gap-4">
        {agents?.map((agent) => (
          <AgentCard
            key={agent.id}
            agent={agent}
            isEditing={editingId === agent.id}
            onEdit={() => setEditingId(agent.id)}
            onCancel={() => setEditingId(null)}
            onSave={async (updates) => {
              await updateAgent(agent.id, updates);
              setEditingId(null);
              refetch();
            }}
          />
        ))}
      </div>
    </div>
  );
}

function AgentCard({
  agent,
  isEditing,
  onEdit,
  onCancel,
  onSave,
}: {
  agent: AgentConfig;
  isEditing: boolean;
  onEdit: () => void;
  onCancel: () => void;
  onSave: (updates: Partial<AgentConfig>) => Promise<void>;
}) {
  const [form, setForm] = useState({
    persona_prompt: agent.persona_prompt,
    model_provider: agent.model_provider,
    model_id: agent.model_id,
    temperature: agent.temperature,
    initial_capital: agent.initial_capital,
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(form);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-100">
              <Bot className="h-5 w-5 text-gray-600" />
            </div>
            <div>
              <CardTitle>{agent.name}</CardTitle>
              <CardDescription>{agent.description}</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="secondary">{agent.model_provider}</Badge>
            <Badge variant="outline">{agent.model_id}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Persona Prompt
              </label>
              <textarea
                className="w-full rounded-md border border-gray-300 p-2 text-sm"
                rows={6}
                value={form.persona_prompt}
                onChange={(e) => setForm({ ...form, persona_prompt: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Model Provider
                </label>
                <input
                  className="w-full rounded-md border border-gray-300 p-2 text-sm"
                  value={form.model_provider}
                  onChange={(e) => setForm({ ...form, model_provider: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Model ID
                </label>
                <input
                  className="w-full rounded-md border border-gray-300 p-2 text-sm"
                  value={form.model_id}
                  onChange={(e) => setForm({ ...form, model_id: e.target.value })}
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Temperature
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="2"
                  className="w-full rounded-md border border-gray-300 p-2 text-sm"
                  value={form.temperature}
                  onChange={(e) =>
                    setForm({ ...form, temperature: parseFloat(e.target.value) })
                  }
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">
                  Initial Capital
                </label>
                <input
                  type="number"
                  className="w-full rounded-md border border-gray-300 p-2 text-sm"
                  value={form.initial_capital}
                  onChange={(e) =>
                    setForm({ ...form, initial_capital: parseFloat(e.target.value) })
                  }
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSave} disabled={saving}>
                <Save className="mr-1 h-4 w-4" />
                {saving ? "Saving..." : "Save"}
              </Button>
              <Button size="sm" variant="outline" onClick={onCancel}>
                <X className="mr-1 h-4 w-4" />
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <pre className="max-h-32 overflow-auto rounded-md bg-gray-50 p-3 text-xs text-gray-700">
              {agent.persona_prompt}
            </pre>
            <div className="flex items-center gap-4 text-sm text-gray-500">
              <span>Temp: {agent.temperature}</span>
              <span>Capital: ${agent.initial_capital.toLocaleString()}</span>
              <span>Max tokens: {agent.max_tokens}</span>
            </div>
            <Button size="sm" variant="outline" onClick={onEdit}>
              Edit Configuration
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
