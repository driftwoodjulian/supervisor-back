export function getScoreClass(score) {
  const scoreValue = score || ""
  return `score-badge score-${scoreValue}`
}

export function formatDate(dateString) {
  if (!dateString) return "N/A"
  return new Date(dateString).toLocaleString()
}
