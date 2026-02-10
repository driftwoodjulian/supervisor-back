
import { useState, useRef } from "react"
import ChatInfo from "./ChatInfo"
import MessageList from "./MessageList"

export default function ChatDetailsModal({ chatId, chatDetails, chatMessages, chatReasons, chatImprovement, chatKeyMessages }) {
  const [highlightedNumber, setHighlightedNumber] = useState(null);
  const [showAnalysisDetails, setShowAnalysisDetails] = useState(false);
  const [showReason, setShowReason] = useState(false);
  const [showImprovement, setShowImprovement] = useState(false);
  const [showKeyMessages, setShowKeyMessages] = useState(false);

  const handleKeyMessageClick = (msgNum) => {
    setHighlightedNumber(msgNum);
    const elementId = `msg-${msgNum}`;
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  return (
    <div className="modal fade" id="chatModal" tabIndex="-1" aria-labelledby="chatModalLabel" aria-hidden="true">
      <div className="modal-dialog modal-lg modal-dialog-scrollable">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title" id="chatModalLabel">
              Chat Details - ID: {chatId}

              <div className="analysis-summary mt-3">
                {/* Reason Section */}
                <div className="analysis-section mb-2">
                  <div
                    className="analysis-header"
                    onClick={() => setShowReason(!showReason)}
                    style={{ cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem', userSelect: 'none' }}
                  >
                    {showReason ? '▼' : '▶'} Reason
                  </div>
                  {showReason && (
                    <div className="analysis-content ps-3 mt-1" style={{ fontSize: '0.9rem' }}>
                      {chatReasons}
                    </div>
                  )}
                </div>

                {/* Improvement Section */}
                <div className="analysis-section mb-2">
                  <div
                    className="analysis-header"
                    onClick={() => setShowImprovement(!showImprovement)}
                    style={{ cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem', color: 'rgba(255, 166, 0, 1)', userSelect: 'none' }}
                  >
                    {showImprovement ? '▼' : '▶'} Improvement
                  </div>
                  {showImprovement && (
                    <div className="analysis-content ps-3 mt-1" style={{ fontSize: '0.9rem', textShadow: '0 0 5px rgba(196, 127, 0, 0.5)' }}>
                      {chatImprovement}
                    </div>
                  )}
                </div>

                {/* Key Messages Section */}
                {chatKeyMessages && chatKeyMessages.length > 0 && (
                  <div className="analysis-section mb-2">
                    <div
                      className="analysis-header"
                      onClick={() => setShowKeyMessages(!showKeyMessages)}
                      style={{ cursor: 'pointer', fontWeight: 'bold', fontSize: '0.9rem', userSelect: 'none' }}
                    >
                      {showKeyMessages ? '▼' : '▶'} Key Messages
                    </div>
                    {showKeyMessages && (
                      <div className="key-messages-container ps-3 mt-1" style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {chatKeyMessages.map((msgNum) => (
                          <button
                            key={msgNum}
                            onClick={() => handleKeyMessageClick(msgNum)}
                            style={{
                              backgroundColor: 'transparent',
                              border: '1px solid #ff7300ff',
                              color: '#ff7300ff',
                              borderRadius: '4px',
                              padding: '2px 8px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              fontWeight: 'bold',
                              boxShadow: '0 0 5px #ff7300ff',
                              transition: 'all 0.2s ease-in-out'
                            }}
                            onMouseEnter={(e) => {
                              e.target.style.backgroundColor = '#ff7300ff';
                              e.target.style.color = 'black';
                            }}
                            onMouseLeave={(e) => {
                              e.target.style.backgroundColor = 'transparent';
                              e.target.style.color = '#ff7300ff';
                            }}
                          >
                            {msgNum}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </h5>
            <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div className="modal-body">
            {chatDetails && <ChatInfo chatDetails={chatDetails} />}
            {chatMessages && chatMessages.length > 0 && <MessageList messages={chatMessages} highlightedNumber={highlightedNumber} />}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
