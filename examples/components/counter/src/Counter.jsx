import React from "react";
import "./counter.css";

export default function Counter(props) {
  const { title = "Counter", count = 0, onIncrement } = props;
  return (
    <div className="ngr-counter">
      <h3>{title}</h3>
      <p className="ngr-count" data-testid="count">
        Count: {count}
      </p>
      <button className="ngr-button" onClick={() => onIncrement && onIncrement({ delta: 1 })}>
        Increment from React
      </button>
    </div>
  );
}
