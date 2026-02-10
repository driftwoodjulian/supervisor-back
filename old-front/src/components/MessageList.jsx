import MessageItem from "./MessageItem"

export default function MessageList({ messages, highlightedNumber }) {
  return (
    <div className="chat-details-section">
      <h5>Conversation ({messages.length} messages)</h5>
      {messages.map((message, index) => (
        <MessageItem
          key={message.id}
          message={message}
          messageNumber={index + 1}
          isHighlighted={highlightedNumber == (index + 1).toString()}
        />
      ))}
    </div>
  )
}
