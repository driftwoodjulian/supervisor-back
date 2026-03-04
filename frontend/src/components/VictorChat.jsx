import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button } from 'react-bootstrap';
import { sendVictorMessage } from '../api';

function VictorChat({ show, onHide }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: '¡Hola! Soy Victor, experto en soporte técnico. ¿En qué puedo ayudarte hoy?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        setInput('');

        // Add user message to UI
        const newHistory = [...messages, { role: 'user', content: userMsg }];
        setMessages(newHistory);
        setIsLoading(true);

        try {
            // Send exactly the history excluding the current query, but for simplicity we send all and API appends
            const response = await sendVictorMessage(userMsg, messages);
            setMessages([...newHistory, { role: 'assistant', content: response.response }]);
        } catch (error) {
            console.error("Chat Error:", error);
            setMessages([...newHistory, { role: 'assistant', content: "Hubo un error de conexión al intentar responder." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="lg" centered backdrop="static" className="victor-chat-modal">
            <Modal.Header closeButton className="border-bottom border-success bg-black">
                <Modal.Title className="text-success" style={{ fontFamily: 'monospace' }}>Chat Autónomo: Victor (Histórico)</Modal.Title>
            </Modal.Header>
            <Modal.Body className="bg-black p-0">
                <div className="victor-chat-container" style={{ height: '600px', padding: 0, marginTop: 0 }}>
                    <div className="chat-window" style={{ border: 'none', borderRadius: 0, marginTop: 0 }}>
                        <div className="messages-area">
                            {messages.map((msg, idx) => (
                                <div key={idx} className={`message-bubble-wrapper ${msg.role === 'user' ? 'user' : 'agent'}`}>
                                    <div className={`message-bubble ${msg.role === 'user' ? 'customer-msg' : 'agent-msg'}`}>
                                        <strong>{msg.role === 'user' ? 'Tú' : 'Victor'}</strong>
                                        <p style={{ whiteSpace: 'pre-line', margin: 0 }}>{msg.content}</p>
                                    </div>
                                </div>
                            ))}
                            {isLoading && (
                                <div className="message-bubble-wrapper agent">
                                    <div className="message-bubble agent-msg typing-indicator">
                                        Victor está escribiendo...
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        <form className="chat-input-area" onSubmit={handleSend}>
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Escribe tu consulta aquí..."
                                disabled={isLoading}
                            />
                            <button type="submit" className="btn action-btn send-btn" disabled={isLoading || !input.trim()}>
                                Enviar
                            </button>
                        </form>
                    </div>
                </div>
            </Modal.Body>
            <Modal.Footer className="border-top border-success bg-black">
                <Button variant="secondary" onClick={onHide}>Cerrar Chat</Button>
            </Modal.Footer>
        </Modal>
    );
}

export default VictorChat;
