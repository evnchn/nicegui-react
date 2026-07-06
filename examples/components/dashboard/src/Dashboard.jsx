import React, { useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./dashboard.css";

export default function Dashboard({
  title = "Live signal",
  unit = "%",
  waveform = "Sine",
  series = [],
  items = [],
  onAddItem,
  onRemoveItem,
}) {
  // React-internal state (the controlled input) coexists with Python-driven props.
  const [text, setText] = useState("");
  const current = series.length ? series[series.length - 1].value : 0;

  const submit = () => {
    const value = text.trim();
    if (!value) return;
    onAddItem && onAddItem({ label: value });
    setText("");
  };

  return (
    <div className="dash">
      <div className="dash-header">
        <div>
          <h3 className="dash-title">{title}</h3>
          <div className="dash-sub">
            <span className="dash-dot" />
            {waveform} wave · streamed live from Python
          </div>
        </div>
        <div className="dash-readout">
          <span className="dash-value">{current.toFixed(1)}</span>
          <span className="dash-unit">{unit}</span>
        </div>
      </div>

      <div className="dash-chart">
        <ResponsiveContainer width="100%" height={190}>
          <AreaChart data={series} margin={{ top: 10, right: 8, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="dashFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#4f46e5" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#eef0f4" vertical={false} />
            <XAxis dataKey="t" hide />
            <YAxis
              domain={[0, 100]}
              ticks={[0, 25, 50, 75, 100]}
              tick={{ fontSize: 11 }}
              tickFormatter={(v) => `${v}${unit}`}
              width={46}
            />
            <Tooltip
              formatter={(v) => [`${Number(v).toFixed(1)}${unit}`, "signal"]}
              labelFormatter={() => ""}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#4f46e5"
              strokeWidth={2}
              fill="url(#dashFill)"
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="dash-controls">
        <input
          className="dash-input"
          value={text}
          placeholder="Add a metric to watch..."
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
        <button className="dash-btn" onClick={submit}>
          Add
        </button>
      </div>

      <ul className="dash-list">
        {items.length === 0 && <li className="dash-empty">No metrics yet.</li>}
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
