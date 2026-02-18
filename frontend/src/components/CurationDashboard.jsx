import React, { useState, useEffect } from 'react';
import ChatViewer from './ChatViewer';
import EvaluationForm from './EvaluationForm';
import { getToken } from '../auth';

const CurationDashboard = ({ onBack }) => {
    const [chats, setChats] = useState([]);
    const [selectedChat, setSelectedChat] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // List & Filter State
    const [page, setPage] = useState(1);
    const [searchTerm, setSearchTerm] = useState('');

    // Evaluation State
    const [selectedIndices, setSelectedIndices] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Fetch Chats on Mount or when page/search changes
    useEffect(() => {
        fetchChats();
    }, [page, searchTerm]);

    // Reset selection when chat changes
    useEffect(() => {
        setSelectedIndices([]);
    }, [selectedChat]);

    const fetchChats = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = getToken();
            let url = `/api/curation/chats?page=${page}`;
            if (searchTerm) {
                // If searching by ID, validation ensures we don't send garbage
                // But the backend expects int.
                if (!isNaN(searchTerm)) {
                    url += `&chat_id=${searchTerm}`;
                }
            }

            const res = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const text = await res.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch (jsonErr) {
                console.error("Failed to parse JSON response:", text);
                throw new Error(`Server returned non-JSON response (${res.status}): ${text.substring(0, 100)}...`);
            }

            if (!res.ok) throw new Error(data.error || `API Error: ${res.statusText}`);

            setChats(data);
            // Optional: Auto-select first if none selected, or keep selection logic manual
            if (data.length > 0 && !selectedChat) {
                // setSelectedChat(data[0]); // User prefers choosing
            }
        } catch (e) {
            console.error("Fetch Error:", e);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleSearchChange = (e) => {
        setSearchTerm(e.target.value);
        setPage(1); // Reset to page 1 on search
    };

    const handleToggleMessage = (index) => {
        setSelectedIndices(prev => {
            if (prev.includes(index)) {
                return prev.filter(i => i !== index);
            } else {
                return [...prev, index];
            }
        });
    };

    const handleSubmitEvaluation = async (formData) => {
        if (!selectedChat) return;
        setIsSubmitting(true);

        const payload = {
            chat_id: selectedChat.id,
            ...formData,
            key_messages: selectedIndices
        };
        console.log("Submitting Evaluation:", payload);

        try {
            const token = getToken();
            const res = await fetch('/api/curation/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.details || errData.error || res.statusText);
            }

            // Success: Remove from local list or just clear selection?
            // "it should only present a list... chose one to evaluate"
            // Let's just deselect for now to let them pick another
            setSelectedChat(null);
            alert("Evaluation Submitted Successfully");
            // Optionally refresh list to see if we can mark it (backend doesn't support yet)
            fetchChats();
        } catch (e) {
            alert(`Submission Failed: ${e.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="curation-container pl-0 pr-0" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
            {/* Header - Matching Dashboard .app-header */}
            <div className="app-header" style={{ flexShrink: 0 }}>
                <div>
                    <h1><span className="text-warning-glow">HITL</span> CURATION CONSOLE</h1>
                    <p>Human-in-the-Loop Evaluation Stream</p>
                    <div className="header-controls d-flex align-items-center gap-3">
                        <div className="text-success small me-3">
                            {loading ? "Loading..." : `${chats.length} Pendings`}
                        </div>
                        <button onClick={onBack} className="btn btn-outline-success btn-sm">
                            EXIT CONSOLE
                        </button>
                    </div>
                </div>
            </div>

            {/* Main Layout: 3 Columns */}
            <div className="row m-0 flex-grow-1" style={{ overflow: 'hidden' }}>

                {/* Col 1: List / Sidebar (20%) */}
                <div className="col-md-3 p-0 border-end border-success d-flex flex-column" style={{ background: '#050505', height: '100%', overflow: 'hidden' }}>
                    {/* Search & Filter */}
                    <div className="p-3 border-bottom border-success">
                        <input
                            type="text"
                            className="form-control mb-2"
                            style={{ fontFamily: 'monospace' }}
                            placeholder="FILTER BY ID..."
                            value={searchTerm}
                            onChange={handleSearchChange}
                        />
                        <div className="d-flex justify-content-between align-items-center">
                            <button
                                className="btn btn-sm btn-outline-success"
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >&lt; PREV</button>
                            <span className="text-success small" style={{ fontFamily: 'monospace' }}>PAGE {page}</span>
                            <button
                                className="btn btn-sm btn-outline-success"
                                onClick={() => setPage(p => p + 1)}
                                disabled={chats.length < 50}
                            >NEXT &gt;</button>
                        </div>
                    </div>

                    {/* Chat List */}
                    <div className="flex-grow-1" style={{ overflowY: 'auto' }}>
                        {chats.map(chat => (
                            <div
                                key={chat.id}
                                onClick={() => setSelectedChat(chat)}
                                className={`p-3 border-bottom border-success cursor-pointer ${selectedChat && selectedChat.id === chat.id ? 'bg-success text-black' : 'text-success hover-bg-dark'}`}
                                style={{ cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'monospace' }}
                            >
                                <div className="fw-bold">CHAT #{chat.id}</div>
                                <div className="small opacity-75">
                                    FINISHED: {chat.finished_at ? new Date(chat.finished_at).toLocaleString() : 'N/A'}
                                </div>
                            </div>
                        ))}
                        {chats.length === 0 && !loading && (
                            <div className="text-center text-muted p-3" style={{ fontFamily: 'monospace' }}>NO CHATS FOUND</div>
                        )}
                    </div>
                </div>

                {/* Col 2: Chat Viewer (50%) */}
                <div className="col-md-5 p-0 border-end border-success d-flex flex-column" style={{ background: '#000', height: '100%', overflow: 'hidden' }}>
                    {selectedChat ? (
                        <div className="flex-grow-1 d-flex flex-column" style={{ overflow: 'hidden' }}>
                            <div className="p-2 border-bottom border-success text-success small text-center" style={{ fontFamily: 'monospace', background: '#050505' }}>
                                VIEWING CHAT #{selectedChat.id}
                            </div>
                            <div className="flex-grow-1" style={{ overflowY: 'auto' }}>
                                <ChatViewer
                                    rawPayload={selectedChat.raw_payload}
                                    selectable={true}
                                    selectedIndices={selectedIndices}
                                    onToggleMessage={handleToggleMessage}
                                />
                            </div>
                        </div>
                    ) : (
                        <div className="d-flex align-items-center justify-content-center h-100 text-muted" style={{ fontFamily: 'monospace' }}>
                            SELECT A CHAT FROM THE LIST
                        </div>
                    )}
                </div>

                {/* Col 3: Evaluation Form (30%) */}
                <div className="col-md-4 p-4 text-success d-flex flex-column" style={{ overflowY: 'auto', background: '#020202', height: '100%' }}>
                    {selectedChat ? (
                        <>
                            <h5 className="border-bottom border-success pb-2 mb-3" style={{ fontFamily: 'monospace' }}>EVALUATE #{selectedChat.id}</h5>
                            <EvaluationForm
                                onSubmit={handleSubmitEvaluation}
                                loading={isSubmitting}
                                selectedMessagesCount={selectedIndices.length}
                            />
                        </>
                    ) : (
                        <div className="text-center mt-5 text-muted" style={{ fontFamily: 'monospace' }}>
                            <span className="display-4 d-block mb-3">&larr;</span>
                            READY TO EVALUATE
                        </div>
                    )}
                </div>
            </div>

            {error && (
                <div className="alert alert-danger position-absolute bottom-0 start-0 m-3" role="alert" style={{ zIndex: 1000, fontFamily: 'monospace' }}>
                    {error}
                </div>
            )}
        </div>
    );
};

export default CurationDashboard;
