import React, { useState, useEffect } from 'react';
import ChatViewer from './ChatViewer';
import EvaluationForm from './EvaluationForm';

const CurationDashboard = ({ onBack }) => {
    const [chats, setChats] = useState([]);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Evaluation State
    const [selectedIndices, setSelectedIndices] = useState([]);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Fetch Chats on Mount
    useEffect(() => {
        fetchChats();
    }, []);

    // Reset selection when chat changes
    useEffect(() => {
        setSelectedIndices([]);
    }, [currentIndex]);

    const fetchChats = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/curation/chats?page=1', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!res.ok) throw new Error(`API Error: ${res.statusText}`);

            const data = await res.json();
            setChats(data);
            setCurrentIndex(0);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleNext = () => {
        if (currentIndex < chats.length - 1) {
            setCurrentIndex(prev => prev + 1);
        } else {
            // Fetch next page logic could go here
            alert("End of loaded batch");
        }
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
        setIsSubmitting(true);
        // Phase 4: POST /api/curation/submit
        const payload = {
            chat_id: chats[currentIndex].id,
            ...formData,
            key_messages: selectedIndices
        };
        console.log("Submitting Evaluation:", payload);

        try {
            const token = localStorage.getItem('token');
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

            // Success
            handleNext();
        } catch (e) {
            alert(`Submission Failed: ${e.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const currentChat = chats[currentIndex];

    return (
        <div className="container-fluid p-0" style={{ height: '100vh', background: '#000' }}>
            {/* Header */}
            <div className="d-flex justify-content-between align-items-center p-3 border-bottom border-success" style={{ background: '#000' }}>
                <div className="d-flex align-items-center gap-3">
                    <button onClick={onBack} className="btn btn-outline-success btn-sm">
                        &larr; BACK
                    </button>
                    <h4 className="m-0 text-success" style={{ fontFamily: 'Courier New' }}>
                        <span className="text-warning">HITL</span> CURATION CONSOLE
                    </h4>
                </div>
                <div className="text-success">
                    {loading ? "Loading..." : `${chats.length} Pendings`}
                </div>
            </div>

            {/* Main Content */}
            <div className="row m-0" style={{ height: 'calc(100vh - 70px)' }}>
                {/* Left: Context Viewer */}
                <div className="col-md-7 p-0 border-end border-success">
                    {currentChat ? (
                        <ChatViewer
                            rawPayload={currentChat.raw_payload}
                            selectable={true}
                            selectedIndices={selectedIndices}
                            onToggleMessage={handleToggleMessage}
                        />
                    ) : (
                        <div className="d-flex align-items-center justify-content-center h-100 text-muted">
                            {loading ? "Loading Chats..." : "No chats available for curation."}
                        </div>
                    )}
                </div>

                {/* Right: Evaluation Form */}
                <div className="col-md-5 p-4 text-success d-flex flex-column" style={{ overflowY: 'auto', background: '#020202' }}>
                    {currentChat ? (
                        <EvaluationForm
                            onSubmit={handleSubmitEvaluation}
                            loading={isSubmitting}
                            selectedMessagesCount={selectedIndices.length}
                        />
                    ) : (
                        <div className="text-center mt-5 text-muted">Select a chat to evaluate.</div>
                    )}
                </div>
            </div>

            {error && (
                <div className="alert alert-danger position-absolute bottom-0 start-0 m-3" role="alert">
                    {error}
                </div>
            )}
        </div>
    );
};

export default CurationDashboard;
