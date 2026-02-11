import React, { useState, useEffect } from 'react';

const ChatViewer = ({ rawPayload, selectable = false, selectedIndices = [], onToggleMessage }) => {
    const [messages, setMessages] = useState([]);
    const [systemPrompt, setSystemPrompt] = useState("");
    const [parsedLines, setParsedLines] = useState([]);

    useEffect(() => {
        if (!rawPayload) return;
        try {
            const data = typeof rawPayload === 'string' ? JSON.parse(rawPayload) : rawPayload;

            const msgs = data.messages || [];
            const sys = msgs.find(m => m.role === 'system');
            const usr = msgs.find(m => m.role === 'user');

            setSystemPrompt(sys ? sys.content : "No System Prompt Found");

            const content = usr ? usr.content : "";
            setMessages(content);

            // Parse lines for interactivity
            // Limit to lines that look like messages (starts with number) or just split by newline
            if (content) {
                const lines = content.split('\n');
                setParsedLines(lines);
            } else {
                setParsedLines([]);
            }

        } catch (e) {
            console.error("Failed to parse payload", e);
            setMessages("Error parsing payload");
            setParsedLines([]);
        }
    }, [rawPayload]);

    const isSelected = (index) => selectedIndices.includes(index);

    // Helper to extract message index from line if possible, or just use line index
    // The requirement says "Key Messages: Array[Int] ... INDICES of Support Agent messages"
    // The format is "1 - Support agent..."
    // So we can try to extract the number.
    const getMessageIndex = (line) => {
        const match = line.match(/^(\d+)\s-/);
        return match ? parseInt(match[1]) : null;
    };

    return (
        <div className="chat-viewer h-100 d-flex flex-column" style={{ background: '#050505', border: '1px solid #00ff41', color: '#00ff41', fontFamily: 'monospace' }}>
            <div className="p-3 border-bottom border-success">
                <h5 className="m-0 text-uppercase"><i className="bi bi-eye-fill me-2"></i>AI Context View</h5>
                <small className="text-muted" style={{ color: '#00cc33' }}>Exact payload sent to LLM</small>
            </div>

            <div className="flex-grow-1 overflow-auto p-3" style={{ maxHeight: 'calc(100vh - 140px)' }}>
                <div className="mb-4">
                    <strong className="d-block mb-2 text-warning">SYSTEM PROMPT:</strong>
                    <pre className="p-2 border border-warning text-wrap" style={{ fontSize: '0.85rem', color: '#ffd700', whiteSpace: 'pre-wrap' }}>
                        {systemPrompt}
                    </pre>
                </div>

                <div>
                    <strong className="d-block mb-2 text-info">CONVERSATION HISTORY:</strong>
                    <div className="border border-info p-2" style={{ background: '#001111', minHeight: '200px' }}>
                        {parsedLines.map((line, idx) => {
                            const msgIndex = getMessageIndex(line);
                            const selected = msgIndex !== null && isSelected(msgIndex);
                            const canSelect = selectable && msgIndex !== null;

                            return (
                                <div
                                    key={idx}
                                    onClick={() => canSelect && onToggleMessage && onToggleMessage(msgIndex)}
                                    style={{
                                        cursor: canSelect ? 'pointer' : 'default',
                                        background: selected ? 'rgba(255, 136, 0, 0.3)' : 'transparent',
                                        padding: '2px 4px',
                                        borderLeft: selected ? '3px solid #ff8800' : '3px solid transparent',
                                        transition: 'all 0.1s',
                                        color: selected ? '#ffaa00' : '#00ffff'
                                    }}
                                    className="text-wrap"
                                    title={canSelect ? `Toggle Message #${msgIndex}` : ''}
                                >
                                    {line}
                                </div>
                            );
                        })}
                        {parsedLines.length === 0 && <span className="text-muted">{messages}</span>}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatViewer;
