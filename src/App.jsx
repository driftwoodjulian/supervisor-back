"use client"

import { useState, useEffect } from "react"
import LoginCard from "./components/LoginCard"
import MainDashboard from "./components/MainDashboard"
import { checkAuthToken } from "./utils/auth"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem("palatron_jwt")

      if (!token) {
        setLoading(false)
        return
      }

      try {
        const userData = await checkAuthToken(token)
        setUser(userData)
        setIsAuthenticated(true)
      } catch (error) {
        console.log("Token validation failed:", error)
        localStorage.removeItem("palatron_jwt")
      } finally {
        setLoading(false)
      }
    }

    validateToken()
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    localStorage.removeItem("palatron_jwt")
    setUser(null)
    setIsAuthenticated(false)
  }

  if (loading) {
    return (
      <div className="app-container d-flex justify-content-center align-items-center">
        <div className="spinner-border text-light" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="app-container">
      {isAuthenticated ? <MainDashboard user={user} onLogout={handleLogout} /> : <LoginCard onLogin={handleLogin} />}
    </div>
  )
}

export default App

