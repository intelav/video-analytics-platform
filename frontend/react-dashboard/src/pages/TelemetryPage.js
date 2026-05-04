import React, { useEffect, useState } from "react";
import axios from "axios";

function TelemetryPage() {
  const [telemetry, setTelemetry] = useState([]);

  useEffect(() => {
    fetchTelemetry();

    const interval = setInterval(fetchTelemetry, 3000); // auto-refresh
    return () => clearInterval(interval);
  }, []);

  const fetchTelemetry = () => {
    axios.get("http://localhost:8000/telemetry")
      .then(res => setTelemetry(res.data))
      .catch(err => console.error(err));
  };

  return (
    <div>
      <h2>Telemetry Data (All Protocols)</h2>

      <table border="1" width="100%">
        <thead>
          <tr>
            <th>Time</th>
            <th>Device</th>
            <th>Protocol</th>
            <th>Metrics</th>
          </tr>
        </thead>
        <tbody>
          {telemetry.map((t, i) => (
            <tr key={i}>
              <td>{t.time}</td>
              <td>{t.device}</td>
              <td>{t.protocol}</td>
              <td>
                <pre style={{ margin: 0 }}>
                  {JSON.stringify(t.metrics, null, 2)}
                </pre>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TelemetryPage;