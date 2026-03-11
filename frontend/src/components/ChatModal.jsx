import React, { useState, useEffect, useRef } from 'react';
import { Modal, Button, Spinner } from 'react-bootstrap';
import { getChatDetails, sendVictorMessage } from '../api';
import DashboardImage from './DashboardImage';

const ChatModal = ({ show, onHide, chatId, initialData }) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [highlightedMsgId, setHighlightedMsgId] = useState(null);

    // Simulation state
    const [victorResponse, setVictorResponse] = useState(null);
    const [victorLoading, setVictorLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const { reason, improvement, keyMessages } = initialData || {};

    useEffect(() => {
        if (show && chatId) {
            setLoading(true);
            setHighlightedMsgId(null);
            setVictorResponse(null);
            setVictorLoading(false);

            getChatDetails(chatId)
                .then(chatData => {
                    setData(chatData);

                    // Always trigger simulation when opening the modal
                    if (chatData && chatData.messages && chatData.messages.length > 0) {
                        const messages = chatData.messages;
                        const lastMsg = messages[messages.length - 1];

                        if (lastMsg.role === 'customer' || lastMsg.role === 'user') {
                            setVictorLoading(true);

                            // Map history for Victor
                            const mappedHistory = messages.map(m => ({
                                role: (m.role === 'customer' || m.role === 'user') ? 'user' : 'assistant',
                                content: m.content
                            }));
                            const contextHistory = mappedHistory.slice(0, mappedHistory.length - 1);
                            const query = lastMsg.content;
                            const mockDomainContext = { domain: 'Simulated Context', server: 'N/A', plan_name: 'Simulation', status: 'Activo' };

                            sendVictorMessage(query, contextHistory, mockDomainContext)
                                .then(res => setVictorResponse(res.response))
                                .catch(err => {
                                    console.error("Simulation error: ", err);
                                    setVictorResponse("Error al simular la respuesta.");
                                })
                                .finally(() => {
                                    setVictorLoading(false);
                                    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
                                });
                        }
                    }
                })
                .catch(err => console.error("Failed to load details: ", err))
                .finally(() => setLoading(false));
        } else {
            setData(null);
            setVictorResponse(null);
            setVictorLoading(false);
        }
    }, [show, chatId]);

    // Helper to check for image tag
    const renderMessageContent = (content) => {
        if (!content) return null;

        // Split by lines to handle multiple images or text+image
        const lines = content.split('\n');

        return lines.map((line, idx) => {
            const imageRegex = /\[IMAGE_REF:\s*(.*?)\]/;
            const match = line.match(imageRegex);

            if (match) {
                const imagePath = match[1];
                const textContent = line.replace(imageRegex, '').trim();

                return (
                    <div key={idx}>
                        {textContent && <div>{textContent}</div>}
                        <DashboardImage path={imagePath} alt="Chat Attachment" />
                    </div>
                );
            }
            return <div key={idx}>{line}</div>;
        });
    };

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
                                                    <div className="message-text">{renderMessageContent(m.content)}</div>
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

                                    {/* Victor AI Simulation Block */}
                                    {(victorLoading || victorResponse) && (
                                        <div className="mt-4 pt-3 border-top" style={{ borderColor: 'rgba(255, 140, 0, 0.3) !important' }}>
                                            <div className="message-header mb-2 d-flex align-items-center gap-2">
                                                <svg viewBox="0 0 24 24" width="16" height="16" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ color: '#FF8C00' }}>
                                                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                                </svg>
                                                <span style={{ color: '#FF8C00', fontWeight: 'bold' }}>Victor (Suggested Response)</span>
                                            </div>

                                            {victorLoading ? (
                                                <div className="d-flex align-items-center gap-2" style={{ color: '#FF8C00', opacity: 0.8 }}>
                                                    <Spinner animation="grow" size="sm" variant="warning" />
                                                    <span style={{ fontStyle: 'italic', fontSize: '0.9rem' }}>Victor está analizando y escribiendo...</span>
                                                </div>
                                            ) : (
                                                <div
                                                    className="p-3 rounded"
                                                    style={{
                                                        backgroundColor: 'rgba(255, 140, 0, 0.1)',
                                                        border: '1px solid #FF8C00',
                                                        color: '#FF8C00',
                                                        whiteSpace: 'pre-line'
                                                    }}
                                                >
                                                    {victorResponse}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                    <div ref={messagesEndRef} />
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
