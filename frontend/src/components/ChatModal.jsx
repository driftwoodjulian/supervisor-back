import React, { useState, useEffect } from 'react';
import { Modal, Button } from 'react-bootstrap';
import { getChatDetails } from '../api';

const ChatModal = ({ show, onHide, chatId, initialData }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [highlightedMsgId, setHighlightedMsgId] = useState(null);

    useEffect(() => {
        if (show && chatId) {
            setLoading(true);
            setHighlightedMsgId(null); // Reset highlight on new open
            getChatDetails(chatId)
                .then(setData)
                .catch(err => console.error("Failed to load details: ", err))
                .finally(() => setLoading(false));
        } else {
            setData(null);
        }
    }, [show, chatId]);

    const { reason, improvement, keyMessages } = initialData || {};

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>
            <Modal.Header closeButton className="border-0">
                <Modal.Title className="text-success">Chat Analysis Details</Modal.Title>
            </Modal.Header>
            <Modal.Body className="bg-black text-success">
                {loading ? (
                    <div>Loading transcript...</div>
                ) : (
                    <>
                        {/* Chat Information Section */}
                        {data && (
                            <div className="chat-details-section mb-3">
                                <h5>Chat Information</h5>
                                <div className="row">
                                    <div className="col-md-6">
                                        <div className="detail-item"><span className="detail-label">Display Name:</span> {data.chat.display_name || "N/A"}</div>
                                        <div className="detail-item"><span className="detail-label">Email:</span> {data.chat.metadata?.email || "N/A"}</div>
                                        <div className="detail-item"><span className="detail-label">Area:</span> {data.chat.metadata?.area || "N/A"}</div>
                                    </div>
                                    <div className="col-md-6">
                                        <div className="detail-item"><span className="detail-label">Created At:</span> {new Date(data.chat.created_at).toLocaleString()}</div>
                                        <div className="detail-item"><span className="detail-label">Closed At:</span> {data.chat.closed_at ? new Date(data.chat.closed_at).toLocaleString() : "Active"}</div>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="chat-details-section">
                            <h5>Evaluation</h5>
                            <p className="chat-reason-modal">{reason}</p>
                            <div className="detail-item">
                                <span className="detail-label">Improvement:</span>
                                <span className="detail-value">{improvement || 'N/A'}</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">Key Points:</span>
                                <div className="detail-value key-messages-container">
                                    {keyMessages && keyMessages.length > 0 ? (
                                        <div className="d-flex flex-wrap gap-2">
                                            {keyMessages.map((msgIdx, i) => (
                                                <button
                                                    key={i}
                                                    className="btn btn-outline-warning btn-sm fw-bold"
                                                    onClick={() => {
                                                        setHighlightedMsgId(msgIdx);
                                                        const el = document.getElementById(`msg-${msgIdx}`);
                                                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                    }}
                                                >
                                                    {msgIdx}
                                                </button>
                                            ))}
                                        </div>
                                    ) : 'None identified'}
                                </div>
                            </div>
                        </div>

                        {data && (
                            <div className="chat-details-section">
                                <h5>Transcript (ID: {data.chat.id})</h5>
                                <div className="messages-list" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                                    {data.messages.map((m, idx) => {
                                        // Use backend index directly (null for pre-transfer messages)
                                        const msgNum = m.index;
                                        const isHighlighted = msgNum !== null && msgNum === highlightedMsgId;
                                        const isKeyMessage = msgNum !== null && keyMessages && keyMessages.includes(msgNum);

                                        return (
                                            <div
                                                key={idx}
                                                id={msgNum !== null ? `msg-${msgNum}` : undefined}
                                                className={`message-item ${m.role === 'customer' || m.role === 'user' ? 'message-customer' : 'message-operator'}`}
                                                style={{
                                                    position: 'relative',
                                                    border: isHighlighted ? '2px solid #FF5F1F' : 'none',
                                                    boxShadow: isHighlighted ? '0 0 15px #FF5F1F' : 'none',
                                                    transition: 'all 0.3s ease'
                                                }}
                                            >
                                                <div className="message-header">
                                                    <span className="message-role">
                                                        {m.role === 'customer' || m.role === 'user' ? 'Customer' : 'Agent'}
                                                        {m.author_name ? ` (${m.author_name})` : ''}
                                                    </span>
                                                    <span style={{ opacity: 0.6 }}>{new Date(m.created_at).toLocaleTimeString()}</span>
                                                </div>
                                                <div className="d-flex justify-content-between">
                                                    <div className="message-text">{m.content}</div>
                                                    {msgNum !== null && (
                                                        <div
                                                            className="message-number-badge"
                                                            style={{
                                                                backgroundColor: isKeyMessage ? '#FF5F1F' : undefined,
                                                                color: isKeyMessage ? 'white' : undefined,
                                                                fontWeight: isKeyMessage ? 'bold' : undefined,
                                                                border: isKeyMessage ? '1px solid white' : undefined
                                                            }}
                                                            title={isKeyMessage ? "Key Message referencing this score" : undefined}
                                                        >
                                                            {msgNum}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </>
                )}
            </Modal.Body>
            <Modal.Footer className="border-top border-success bg-black">
                <Button variant="secondary" onClick={onHide}>Close</Button>
            </Modal.Footer>
        </Modal>
    );
};

export default ChatModal;
