import React from "react";
import "./clock.css";

export default function Clock({ label = "Clock", time = "--:--:--" }) {
  return (
    <div className="ngr-clock">
      <div className="ngr-clock-label">{label}</div>
      <div className="ngr-clock-time" data-testid="time">
        {time}
      </div>
    </div>
  );
}
