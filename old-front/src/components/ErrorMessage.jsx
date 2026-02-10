"use client"

export default function ErrorMessage({ error, onRetry }) {
  return (
    <div className="error-message">
      <h3>Error Loading Data</h3>
      <p>{error}</p>
      <button className="btn btn-primary" onClick={onRetry}>
        Retry
      </button>
    </div>
  )
}
