import { useEffect, useState } from "react";
import VideoTile from "./VideoTile";
import axios from "axios";

export default function VideoWall() {
  const [cams, setCams] = useState([]);

useEffect(() => {
  console.log("📡 STREAM ENV:", process.env.REACT_APP_STREAM);

  axios.get("http://192.168.1.26:5000/cameras")
    .then(res => {
      console.log("✅ CAMERAS:", res.data);
      setCams(res.data);
    })
    .catch(err => {
      console.error("❌ CAMERAS ERROR:", err);
    });
}, []);

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(2, 1fr)",
      gap: "10px"
    }}>
      {Object.entries(cams).map(([cam, modes]) => (
      <div key={cam} style={{ display: "contents" }}>
        
        {modes.yolo && (
          <VideoTile cam={cam} mode="yolo" />
        )}

        {modes.pose && (
          <VideoTile cam={cam} mode="pose" />
        )}

        </div>
      ))}
    </div>
  );
}