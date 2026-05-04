import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TelemetryPage from "./pages/TelemetryPage";

function App() {
  return (
    <Router>
      <div style={{ padding: "20px" }}>
        <h1>Industrial AI Platform</h1>

        {/* Navigation */}
        <nav style={{ marginBottom: "20px" }}>
          <Link to="/" style={{ marginRight: "20px" }}>Dashboard</Link>
          <Link to="/telemetry">Telemetry</Link>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/telemetry" element={<TelemetryPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;