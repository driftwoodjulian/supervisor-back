import { useEffect, useState } from "react"
import SatisfactionDashboard from "./src/components/SatisfactionDashboard"
import LoginCard from "./src/components/LoginCard"
import LoadingSpinner from "./src/components/LoadingSpinner"
import { checkAuthToken, TOKEN_STORAGE_KEY } from "./src/utils/auth"

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const validateToken = async () => {
      const token = localStorage.getItem(TOKEN_STORAGE_KEY)

      if (!token) {
        setLoading(false)
        return
      }

      try {
        const userData = await checkAuthToken(token)
        setUser(userData)
        setIsAuthenticated(true)
      } catch (error) {
        console.error("Token validation failed:", error)
        localStorage.removeItem(TOKEN_STORAGE_KEY)
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
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setUser(null)
    setIsAuthenticated(false)
  }

  if (loading) {
    return <LoadingSpinner />
  }

  return isAuthenticated ? (
    <SatisfactionDashboard user={user} onLogout={handleLogout} />
  ) : (
    <LoginCard onLogin={handleLogin} />
  )
}

export default App
