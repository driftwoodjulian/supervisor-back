"use client"

import { getScoreClass } from "../utils/helpers"

export default function ScoreCard({ chatId, score, onViewDetails, loading, timeSt, reason, improvement, keyMessages }) {
  // Check if score is an error object
  const isError = score && typeof score === 'object' && 'error' in score;
  const errorMessage = isError ? score.error : null;
  const displayScore = isError ? null : score;

  return (
    <div className="score-card">
      {isError ? (
        <div className="score-error">
          <div className="text-danger">Error</div>
          <div className="error-message">{errorMessage || "Error with the score query"}</div>
        </div>
      ) : (
        <div className={getScoreClass(displayScore)}>{displayScore || "Unknown"}</div>
      )}
      <div className="chat-id">Chat ID: {chatId}</div>
      <div className="chat-id">Time of evaluation: {timeSt}</div>
      <div className="chat-reason">Reason: {reason}</div>
      <button className="btn btn-primary w-100" onClick={() => onViewDetails(chatId, reason, improvement, keyMessages)} disabled={loading}>
        {loading ? (
          <>
            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            Loading...
          </>
        ) : (
          "View Details"
        )}
      </button>
    </div>
  )
}
