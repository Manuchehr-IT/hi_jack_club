// src/components/ui/PokerElements.jsx
export const PokerTable = ({ children, className = '' }) => (
  <div className={`poker-table ${className}`}>
    <div className="table-felt">
      {children}
    </div>
  </div>
);

export const Card = ({ children, className = '', style }) => (
  <div className={`poker-card ${className}`} style={style}>
    {children}
  </div>
);

export const ChipStack = ({ value }) => (
  <div className="chip-stack">
    <div className="chip chip-100" style={{backgroundColor: '#00B894'}}></div>
    <div className="chip chip-500" style={{backgroundColor: '#FDCB6E'}}></div>
    <div className="chip chip-1000" style={{backgroundColor: '#E84393'}}></div>
    <span className="chip-value">${value}</span>
  </div>
);