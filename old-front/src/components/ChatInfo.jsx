import { formatDate } from "../utils/helpers"

export default function ChatInfo({ chatDetails }) {
  return (
    <div className="chat-details-section">
      <h5>Chat Information</h5>
      <div className="detail-item">
        <span className="detail-label">Display Name:</span>
        <span className="detail-value">{chatDetails.displayname || "N/A"}</span>
      </div>
      <div className="detail-item">
        <span className="detail-label">Email:</span>
        <span className="detail-value">{chatDetails.custumer_metadata?.email || "N/A"}</span>
      </div>
      <div className="detail-item">
        <span className="detail-label">Area:</span>
        <span className="detail-value">{chatDetails.custumer_metadata?.area || "N/A"}</span>
      </div>
      <div className="detail-item">
        <span className="detail-label">Created At:</span>
        <span className="detail-value">{formatDate(chatDetails.created_at)}</span>
      </div>
      <div className="detail-item">
        <span className="detail-label">Duration:</span>
        <span className="detail-value">{chatDetails.chat_duration || "N/A"}</span>
      </div>
      <div className="detail-item">
        <span className="detail-label">Closed At:</span>
        <span className="detail-value">{chatDetails.closed_at ? formatDate(chatDetails.closed_at) : "Not closed"}</span>
      </div>
    </div>
  )
}
