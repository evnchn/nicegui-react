import React, { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./dashboard.css";

export default function Dashboard({
  title = "Dashboard",
  status = "idle",
  series = [],
  items = [],
  onAddItem,
  onRemoveItem,
  onRefresh,
}) {
  // React-internal state (the controlled input) coexists with Python-driven props.
  const [text, setText] = useState("");

  const submit = () => {
    const value = text.trim();
    if (!value) return;
    onAddItem && onAddItem({ label: value });
    setText("");
  };

  return (
    <div className="dash">
      <div className="dash-header">
        <h3>{title}</h3>
        <span className={`dash-status dash-status--${status}`}>{status}</span>
      </div>

      <div className="dash-chart">
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={series} margin={{ top: 8, right: 12, bottom: 0, left: -18 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" />
            <XAxis dataKey="t" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="value"
              stroke="#4f46e5"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="dash-controls">
        <input
          className="dash-input"
          value={text}
          placeholder="Add an item..."
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
        <button className="dash-btn" onClick={submit}>
          Add
        </button>
        <button className="dash-btn dash-btn--ghost" onClick={() => onRefresh && onRefresh({})}>
          Refresh chart
        </button>
      </div>

      <ul className="dash-list">
        {items.length === 0 && <li className="dash-empty">No items yet.</li>}
        {items.map((item) => (
          <li key={item.id} className="dash-item">
            <span>{item.label}</span>
            <button
              className="dash-remove"
              data-id={item.id}
              onClick={() => onRemoveItem && onRemoveItem({ id: item.id })}
            >
              ✕
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
