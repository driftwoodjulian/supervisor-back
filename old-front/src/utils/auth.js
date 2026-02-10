"use client"

export const TOKEN_STORAGE_KEY = import.meta.env.VITE_AUTH_TOKEN_KEY || "ai_front_jwt"

export const AUTH_API_BASE_URL = import.meta.env.VITE_AUTH_API_BASE_URL || "http://10.10.1.180:5000"
export const AUTH_LOGIN_ENDPOINT = import.meta.env.VITE_AUTH_LOGIN_ENDPOINT || "/auth/login"
export const AUTH_CHECK_ENDPOINT = import.meta.env.VITE_AUTH_CHECK_ENDPOINT || "/auth/check"

export const checkAuthToken = async (token) => {
  const response = await fetch(`${AUTH_API_BASE_URL}${AUTH_CHECK_ENDPOINT}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (response.status === 401 || response.status === 404 || response.status === 500) {
    throw new Error("Token invalid")
  }

  if (response.ok) {
    return await response.json()
  }

  throw new Error("Auth check failed")
}


