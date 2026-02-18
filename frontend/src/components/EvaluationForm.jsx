import React, { useState, useEffect } from 'react';

const SCORES = ['Great', 'Good', 'Neutral', 'Bad', 'Horrible'];

const EvaluationForm = ({ onSubmit, loading, selectedMessagesCount }) => {
    const [score, setScore] = useState('');
    const [reason, setReason] = useState('');
    const [improvement, setImprovement] = useState('');
    const [touched, setTouched] = useState(false);

    // Validation
    const isReasonValid = reason.length > 0 && reason.length <= 500;
    const isImprovementValid = improvement.length >= 10 && improvement.length <= 1000;
    const isKeyMessagesValid = (score === 'Bad' || score === 'Horrible') ? selectedMessagesCount > 0 : true;

    const isValid = score && isReasonValid && isImprovementValid && isKeyMessagesValid;

    const handleSubmit = (e) => {
        e.preventDefault();
        setTouched(true);
        if (isValid) {
            onSubmit({ score, reason, improvement });
        }
    };

    return (
        <form onSubmit={handleSubmit} className="text-success h-100 d-flex flex-column">
            <h5 className="mb-3 text-uppercase border-bottom border-success pb-2">Evaluation Form</h5>

            {/* Score Selection */}
            <div className="mb-4">
                <label className="d-block mb-2 font-monospace">1. SCORE</label>
                <div className="d-flex gap-2 flex-wrap">
                    {SCORES.map(s => (
                        <button
                            key={s}
                            type="button"
                            onClick={() => setScore(s)}
                            className={`btn btn-sm ${score === s ? 'btn-success' : 'btn-outline-success'}`}
                            style={{ minWidth: '80px' }}
                        >
                            {s.toUpperCase()}
                        </button>
                    ))}
                </div>
                {touched && !score && <div className="text-danger small mt-1">Score is required.</div>}
            </div>

            {/* Reason */}
            <div className="mb-3">
                <label className="d-block mb-2 font-monospace">
                    2. REASON <span className="text-orange-glow small">({reason.length}/500)</span>
                </label>
                <textarea
                    className="form-control"
                    rows="3"
                    value={reason}
                    onChange={e => setReason(e.target.value)}
                    maxLength={500}
                    placeholder="Explain the score (Spanish)..."
                />
                {touched && !isReasonValid && <div className="text-danger small mt-1">Reason is required (max 500 chars).</div>}
            </div>

            {/* Improvement */}
            <div className="mb-3">
                <label className="d-block mb-2 font-monospace">
                    3. IMPROVEMENT <span className="text-orange-glow small">({improvement.length}/1000)</span>
                </label>
                <textarea
                    className="form-control bg-dark text-success border-success"
                    rows="4"
                    value={improvement}
                    onChange={e => setImprovement(e.target.value)}
                    maxLength={1000}
                    placeholder="How can the agent improve? (Spanish, min 10 chars)..."
                />
                {touched && !isImprovementValid && <div className="text-danger small mt-1">Improvement is required (10-1000 chars).</div>}
            </div>

            {/* Key Messages Validation Info */}
            <div className="mb-4">
                <label className="d-block mb-2 font-monospace">4. KEY MESSAGES</label>
                <div className={`p-2 border ${isKeyMessagesValid ? 'border-success text-success' : 'border-danger text-danger'}`} style={{ background: '#001100' }}>
                    <small>
                        {selectedMessagesCount} messages selected from Context View.
                        {(score === 'Bad' || score === 'Horrible') && (
                            <span className="d-block mt-1 fw-bold">
                                * Mandatory for Bad/Horrible scores.
                            </span>
                        )}
                    </small>
                </div>
            </div>

            {/* Submit */}
            <div className="mt-auto">
                <button
                    type="submit"
                    className="btn btn-success w-100 fw-bold"
                    disabled={!isValid || loading}
                >
                    {loading ? "SUBMITTING..." : "SUBMIT EVALUATION"}
                </button>
            </div>
        </form>
    );
};

export default EvaluationForm;
