import React, { useState, useRef, useEffect } from 'react';
import { sendVictorMessage } from '../api';

function VictorChat({ onBack }) {
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
        <div className="victor-chat-container">
            <header className="curation-header">
                <h2>Chat con Agente Histórico (Victor)</h2>
                <div className="curation-actions">
                    <button className="btn back-btn" onClick={onBack}>← Volver al Dashboard</button>
                </div>
            </header>

            <div className="chat-window">
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
    );
}

export default VictorChat;
