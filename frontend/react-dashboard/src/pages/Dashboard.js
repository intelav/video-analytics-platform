import React, { useEffect, useState } from "react";
import axios from "axios";
import VideoWall from "../components/VideoWall";

function Dashboard() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/events")
      .then(res => setEvents(res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div style={{ display: "flex", gap: "20px" }}>
      <div style={{ width: "40%" }}>
        <h2>VideoWall</h2>

        <table border="1" width="100%">
          <thead>
            <tr>
              <th>Time</th>
              <th>Camera</th>
              <th>Object</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e, i) => (
              <tr key={i}>
                <td>{e.time}</td>
                <td>{e.camera}</td>
                <td>{e.object}</td>
                <td>{e.confidence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ width: "60%" }}>
        <h2>Live Cameras</h2>
        <VideoWall />
      </div>
    </div>
  );
}

export default Dashboard;