import React from 'react';

const ScoreCard = ({ item, onViewDetails }) => {
    // Parse inner score object if needed
    const scoreObj = (typeof item.score === 'object' && item.score !== null) ? item.score : { score: item.score };
    const score = scoreObj.score || "Unknown";
    const reason = item.reason || scoreObj.reason || "No reason provided";
    const improvement = item.improvement || scoreObj.improvement;
    const keyMessages = item.key_messages || scoreObj.key_messages || [];

    // Map score to CSS class
    let scoreClass = 'score-unknown';
    if (typeof score === 'string') {
        if (score.toLowerCase() === 'great') scoreClass = 'score-great';
        if (score.toLowerCase() === 'good') scoreClass = 'score-good';
        if (score.toLowerCase() === 'neutral') scoreClass = 'score-neutral';
        if (score.toLowerCase() === 'bad') scoreClass = 'score-bad';
        if (score.toLowerCase() === 'horrible') scoreClass = 'score-horrible';
    }

    const dateObj = item.created_at ? new Date(item.created_at) : null;
    const dateStr = dateObj ? dateObj.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '';

    return (
        <div className="score-card">
            <span className={`score-badge ${scoreClass}`}>{score}</span>
            <div className="d-flex justify-content-between align-items-center mb-1">
                <div className="chat-id">Chat #{item.chat_id}</div>
                <small style={{ fontSize: '0.75rem', color: '#00ff41', opacity: 0.7 }}>{dateStr}</small>
            </div>

            <div className="chat-reason" style={{ height: '60px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {reason}
            </div>
            <button
                className="btn btn-primary w-100 btn-sm"
                onClick={() => onViewDetails(item.chat_id, reason, improvement, keyMessages)}
            >
                View Transcript
            </button>
        </div>
    );
};

export default ScoreCard;
