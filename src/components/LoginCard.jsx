"use client"

import { useState } from "react"

const LoginCard = ({ onLogin }) => {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_AUTH_LOGIN_ENDPOINT}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      })

      const data = await response.json()

      if (response.status === 200 && data.jwt) {
        localStorage.setItem("palatron_jwt", data.jwt)
        // Get user info after successful login
        const userResponse = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_AUTH_CHECK_ENDPOINT}`,
          {
            headers: {
              Authorization: `Bearer ${data.jwt}`,
            },
          },
        )

        if (userResponse.ok) {
          const userData = await userResponse.json()
          onLogin(userData)
        }
      } else if (response.status === 401) {
        setError("Please check your credentials")
      } else {
        setError("Login failed. Please try again.")
      }
    } catch (error) {
      console.error("Login error:", error)
      setError("Connection error. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <h1 className="login-title">Palatron 5000</h1>
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
                onChange={(e) => setUsername(e.target.value)}
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
                onChange={(e) => setPassword(e.target.value)}
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

export default LoginCard

