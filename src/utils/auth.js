export const checkAuthToken = async (token) => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}${import.meta.env.VITE_AUTH_CHECK_ENDPOINT}`, {
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

