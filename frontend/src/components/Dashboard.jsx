import React, { useState, useEffect } from 'react';
import { getEvaluations } from '../api';
import { removeToken } from '../auth';
import ScoreCard from './ScoreCard';
import ModelSwitcher from './ModelSwitcher';
import ChatModal from './ChatModal';
import AgentStatsModal from './AgentStatsModal';

const Dashboard = ({ onLogout }) => {
    const [evals, setEvals] = useState([]);
    const [modalState, setModalState] = useState({ show: false, chatId: null, data: {} });
    const [showStats, setShowStats] = useState(false);

    // Collapsible Logic
    const [collapsedSections, setCollapsedSections] = useState({});

    const toggleSection = (section) => {
        setCollapsedSections(prev => ({
            ...prev,
            [section]: !prev[section]
        }));
    };

    // Polling logic
    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await getEvaluations();
                // Ensure data is an array
                if (Array.isArray(data)) {
                    setEvals(data);
                }
            } catch (err) {
                if (err.status === 401) {
                    removeToken();
                    onLogout(); // Trigger parent logout
                }
            }
        };

        fetchData(); // Initial load
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, [onLogout]);

    const handleViewDetails = (chatId, reason, improvement, keyMessages) => {
        setModalState({
            show: true,
            chatId,
            data: { reason, improvement, keyMessages }
        });
    };

    const handleCloseModal = () => {
        setModalState(prev => ({ ...prev, show: false }));
    };

    // Grouping Logic
    const groups = {
        Great: [], Good: [], Neutral: [], Bad: [], Horrible: [], Unknown: []
    };

    evals.forEach(item => {
        let score = (typeof item.score === 'object' && item.score) ? item.score.score : item.score;
        if (typeof score !== 'string') score = 'Unknown';

        let capScore = score.charAt(0).toUpperCase() + score.slice(1).toLowerCase();
        if (groups[capScore]) groups[capScore].push(item);
        else groups.Unknown.push(item);
    });

    const sections = ['Great', 'Good', 'Neutral', 'Bad', 'Horrible', 'Unknown'];

    return (
        <>
            <div className="app-header">
                <div>
                    <h1>SUPERVISOR AI</h1>
                    <p>Live B2B/B2C Evaluation Stream</p>
                </div>
                <div className="header-controls d-flex align-items-center gap-3">
                    <ModelSwitcher />
                    <button
                        onClick={() => setShowStats(true)}
                        className="btn btn-icon"
                        title="Agent Stats"
                    >
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 20V10M12 20V4M6 20V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>
                    <button
                        onClick={() => { removeToken(); onLogout(); }}
                        className="btn btn-icon btn-icon-danger"
                        title="Logout"
                    >
                        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>
                </div>
            </div>

            <div className="score-container">
                {evals.length === 0 && <div className="loading-spinner">Initializing Uplink...</div>}

                {sections.map(key => {
                    const items = groups[key];
                    if (!items || items.length === 0) return null;
                    const isCollapsed = collapsedSections[key];

                    return (
                        <div key={key} className="score-section">
                            <div className="score-section-header clickable-header" onClick={() => toggleSection(key)} style={{ cursor: 'pointer', userSelect: 'none' }}>
                                <div className="d-flex align-items-center gap-2">
                                    <span style={{ fontSize: '1.2rem', color: '#00ff41' }}>{isCollapsed ? '[+]' : '[-]'}</span>
                                    <span className={`score-badge score-${key.toLowerCase()} mb-0`}>{key}</span>
                                </div>
                                <span>{items.length} Chats</span>
                            </div>
                            {!isCollapsed && (
                                <div className="score-cards-grid">
                                    {items.map((item, idx) => (
                                        <ScoreCard
                                            key={idx}
                                            item={item}
                                            onViewDetails={handleViewDetails}
                                        />
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div >

            <ChatModal
                show={modalState.show}
                onHide={handleCloseModal}
                chatId={modalState.chatId}
                initialData={modalState.data}
            />

            <AgentStatsModal
                show={showStats}
                onHide={() => setShowStats(false)}
            />
        </>
    );
};

export default Dashboard;
