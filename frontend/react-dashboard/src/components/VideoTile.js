export default function VideoTile({ cam, mode }) {
  const base = "http://192.168.1.26:5000";
  const url =
    mode === "pose"
      ? `${base}/video_pose/${cam}`
      : `${base}/video/${cam}`;

  return (
    <div style={{ border: "1px solid #ccc" }}>
      <h4>{cam} - {mode}</h4>
      <img
        src={url}
        alt={cam}
        style={{ width: "100%" }}
        onError={(e) => {
          e.target.style.display = "none";
        }}
      />
    </div>
  );
}