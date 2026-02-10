import { formatDate } from "../utils/helpers"

export default function MessageItem({ message, messageNumber, isHighlighted }) {
  return (
    <div
      id={`msg-${messageNumber}`}
      className={`message-item ${message.role === "customer" ? "message-customer" : "message-operator"}`}
      style={{
        position: 'relative',
        border: isHighlighted ? '2px solid #ff7300ff' : 'none',
        boxShadow: isHighlighted ? '0 0 15px rgba(255, 115, 0, 0.5)' : 'none',
        transition: 'all 0.3s ease-in-out'
      }}
    >
      <div className="message-header">
        <span className="message-role">{message.role}</span>
        <span>{formatDate(message.createdAt)}</span>
      </div>
      {message.author?.pushName && (
        <div style={{ fontSize: "14px", fontWeight: "bold", color: "#ff7300ff", textShadow: "0 0 5px #ff7300ff", marginBottom: "4px" }}>{message.author.pushName}</div>
      )}
      <div className="d-flex justify-content-between align-items-start">
        <div className="message-text" style={{ flex: 1 }}>{message.text}</div>
        <div style={{
          marginLeft: '10px',
          minWidth: '32px',
          height: '32px',
          backgroundColor: 'transparent',
          border: '1px solid #00ff41',
          borderRadius: '0px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '16px',
          fontWeight: 'bold',
          color: '#00ff41',
          textShadow: '0 0 5px #00ff41',
          boxShadow: 'inset 0 0 10px rgba(0, 255, 65, 0.2)'
        }}>
          {messageNumber}
        </div>
      </div>
    </div>
  )
}
