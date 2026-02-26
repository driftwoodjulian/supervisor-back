import React, { useState, useEffect } from 'react';
import { getEvaluations } from '../api';
import { removeToken } from '../auth';
import ScoreCard from './ScoreCard';
import ModelSwitcher from './ModelSwitcher';
import ChatModal from './ChatModal';
import AgentStatsModal from './AgentStatsModal';

const Dashboard = ({ onLogout, onNavigateCuration, onNavigateConfig }) => {
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
                    <div className="header-controls d-flex align-items-center gap-3">
                        <button
                            onClick={onNavigateCuration}
                            className="btn btn-icon"
                            title="Curation Console"
                            style={{ borderColor: '#faed27', color: '#faed27' }} // Warning Yellow for Admin/Curation
                        >
                            <svg viewBox="0 0 16 16" fill="currentColor" style={{ fill: 'currentColor' }} xmlns="http://www.w3.org/2000/svg">
                                <path fillRule="evenodd" d="M5 11.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zm0-4a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3.854 2.146a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 1 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0zm0 4a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 1 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0zm0 4a.5.5 0 0 1 0 .708l-1.5 1.5a.5.5 0 0 1-.708 0l-.5-.5a.5.5 0 0 1 .708-.708l.146.147 1.146-1.147a.5.5 0 0 1 .708 0z" />
                            </svg>
                        </button>
                        <button
                            onClick={onNavigateConfig}
                            className="btn btn-icon"
                            title="Configuration Manager"
                            style={{ borderColor: '#b2dfdb', color: '#b2dfdb' }}
                        >
                            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.5a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
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
            </div >

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
