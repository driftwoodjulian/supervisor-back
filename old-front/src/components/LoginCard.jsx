"use client"

import { useState } from "react"
import { checkAuthToken, TOKEN_STORAGE_KEY, AUTH_API_BASE_URL, AUTH_LOGIN_ENDPOINT } from "../utils/auth"

export default function LoginCard({ onLogin }) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await fetch(`${AUTH_API_BASE_URL}${AUTH_LOGIN_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.status === 200 && data.jwt) {
        localStorage.setItem(TOKEN_STORAGE_KEY, data.jwt)
        const userData = await checkAuthToken(data.jwt)
        onLogin(userData)
      } else if (response.status === 401) {
        setError("Invalid credentials. Please try again.")
      } else {
        setError("Login failed. Please try again later.")
      }
    } catch (loginError) {
      console.error("Login error:", loginError)
      setError("Network error. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <h1 className="login-title">Satisfaction Dashboard</h1>
      <div className="card login-card">
        <div className="card-body">
          <form onSubmit={handleSubmit}>
            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}
            <div className="mb-3">
              <label htmlFor="username" className="form-label text-white">
                Username
              </label>
              <input
                type="text"
                className="form-control"
                id="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Enter username"
                required
              />
            </div>
            <div className="mb-3">
              <label htmlFor="password" className="form-label text-white">
                Password
              </label>
              <input
                type="password"
                className="form-control"
                id="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter password"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Logging in...
                </>
              ) : (
                "Login"
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}


