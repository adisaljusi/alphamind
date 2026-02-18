import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import AgentsPage from "./pages/AgentsPage";
import SimulatePage from "./pages/SimulatePage";
import SimulationsPage from "./pages/SimulationsPage";
import SimulationDetail from "./pages/SimulationDetail";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/simulate" element={<SimulatePage />} />
        <Route path="/simulations" element={<SimulationsPage />} />
        <Route path="/simulations/:id" element={<SimulationDetail />} />
      </Routes>
    </Layout>
  );
}
