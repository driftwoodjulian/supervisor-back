import React, { useState, useRef, useEffect } from 'react';
import { Modal, Button, Form, Spinner, Alert } from 'react-bootstrap';
import { sendVictorMessage, verifyDomain, getChatDetails } from '../api';

function VictorChat({ show, onHide, simulateChatId = null }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: '¡Hola! Soy Victor, experto en soporte técnico. ¿En qué puedo ayudarte hoy?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Domain Gateway State
    const [domainInput, setDomainInput] = useState('');
    const [domainContext, setDomainContext] = useState(null);
    const [domainError, setDomainError] = useState('');
    const [isVerifying, setIsVerifying] = useState(false);

    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (domainContext) {
            scrollToBottom();
        }
    }, [messages, domainContext]);

    // Reset state when modal closes or load simulation context
    useEffect(() => {
        if (!show) {
            setDomainContext(null);
            setDomainInput('');
            setDomainError('');
            setMessages([
                { role: 'assistant', content: '¡Hola! Soy Victor, experto en soporte técnico. ¿En qué puedo ayudarte hoy?' }
            ]);
        } else if (simulateChatId) {
            // Load simulation context
            const loadContext = async () => {
                try {
                    setDomainContext({ domain: 'Simulated Context', server: 'N/A', plan_name: 'Simulation', status: 'Activo' });
                    const chatData = await getChatDetails(simulateChatId);

                    if (chatData && chatData.messages) {
                        const mappedHistory = chatData.messages.map(m => ({
                            role: m.role === 'customer' ? 'user' : 'assistant',
                            content: m.content
                        }));

                        setMessages(mappedHistory);

                        // Auto-query if the last message is from the customer
                        if (mappedHistory.length > 0 && mappedHistory[mappedHistory.length - 1].role === 'user') {
                            const lastMsg = mappedHistory[mappedHistory.length - 1].content;
                            // Remove the last message from history passed as context to avoid duplication in Victor's memory for this exact query
                            const contextHistory = mappedHistory.slice(0, mappedHistory.length - 1);

                            setIsLoading(true);
                            try {
                                const response = await sendVictorMessage(lastMsg, contextHistory, { domain: 'Simulated Context', server: 'N/A', plan_name: 'Simulation', status: 'Activo' });
                                setMessages(prev => [...prev, { role: 'assistant', content: response.response }]);
                            } catch (error) {
                                console.error("Auto-query Error:", error);
                                setMessages(prev => [...prev, { role: 'assistant', content: "Hubo un error de conexión al intentar responder." }]);
                            } finally {
                                setIsLoading(false);
                            }
                        }
                    }
                } catch (error) {
                    console.error("Failed to load generic chat context", error);
                    setDomainError('Error loading simulation context.');
                }
            };
            loadContext();
        }
    }, [show, simulateChatId]);

    const handleVerifyDomain = async (e) => {
        e.preventDefault();
        setDomainError('');
        if (!domainInput.trim()) {
            setDomainError('Por favor ingresa un dominio válido.');
            return;
        }

        setIsVerifying(true);
        try {
            const result = await verifyDomain(domainInput.trim());
            setDomainContext(result.context);
        } catch (error) {
            setDomainError(error.message || 'Error al verificar el dominio con Nexus.');
        } finally {
            setIsVerifying(false);
        }
    };

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
            const response = await sendVictorMessage(userMsg, messages, domainContext);
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
                <Modal.Title className="text-success" style={{ fontFamily: 'monospace' }}>
                    Chat Autónomo: Victor {domainContext && `(${domainContext.domain})`}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body className="bg-black p-0">
                {!domainContext ? (
                    // GATEWAY VIEW
                    <div className="p-4" style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        <h4 className="text-success mb-3 text-center">Verificación de Contexto</h4>
                        <p className="text-muted text-center mb-4">
                            Ingresa el dominio del cliente. Victor verificará el estado de cuenta en Nexus para brindar una mejor asistencia.
                        </p>

                        <Form onSubmit={handleVerifyDomain} className="w-75 mx-auto">
                            <Form.Group className="mb-3">
                                <Form.Control
                                    type="text"
                                    placeholder="ejemplo.com"
                                    value={domainInput}
                                    onChange={(e) => setDomainInput(e.target.value)}
                                    disabled={isVerifying}
                                    className="bg-dark text-white border-success"
                                    autoFocus
                                />
                            </Form.Group>

                            {domainError && <Alert variant="danger">{domainError}</Alert>}

                            <Button
                                variant="outline-success"
                                type="submit"
                                className="w-100"
                                disabled={isVerifying}
                            >
                                {isVerifying ? <Spinner size="sm" animation="border" /> : 'Verificar Dominio'}
                            </Button>
                        </Form>
                    </div>
                ) : (
                    // CHAT VIEW
                    <div className="victor-chat-container" style={{ height: '600px', padding: 0, marginTop: 0 }}>
                        <div className="chat-window d-flex flex-column" style={{ border: 'none', borderRadius: 0, marginTop: 0, height: '100%' }}>

                            {/* Context Header */}
                            <div className="bg-dark text-success p-2 small border-bottom border-secondary d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>Servidor:</strong> {domainContext.server} | <strong>Plan:</strong> {domainContext.plan_name}
                                </div>
                                <div>
                                    <span className={`badge ${domainContext.status === 'Activo' ? 'bg-success' : 'bg-danger'}`}>
                                        {domainContext.status}
                                    </span>
                                </div>
                            </div>

                            <div className="messages-area flex-grow-1">
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

                            <form className="chat-input-area mt-auto" onSubmit={handleSend}>
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    placeholder="Escribe tu consulta aquí..."
                                    disabled={isLoading}
                                    autoFocus
                                />
                                <button type="submit" className="btn action-btn send-btn" disabled={isLoading || !input.trim()}>
                                    Enviar
                                </button>
                            </form>
                        </div>
                    </div>
                )}
            </Modal.Body>
        </Modal>
    );
}

export default VictorChat;
