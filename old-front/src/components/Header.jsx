export default function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div className="header-content">
        <div>
          <h1>Customer Satisfaction Dashboard</h1>
          <p>Monitor and analyze customer feedback</p>
        </div>
        {onLogout && (
          <div className="header-actions">
            {user?.username && <span className="header-user">Signed in as {user.username}</span>}
            <button className="btn btn-danger btn-sm" onClick={onLogout}>
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  )
}
