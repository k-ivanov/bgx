/**
 * Authentication utilities for managing JWT tokens and user state
 */

const TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_KEY = 'user'

/**
 * Save authentication tokens
 */
export const saveTokens = (accessToken, refreshToken) => {
  localStorage.setItem(TOKEN_KEY, accessToken)
  if (refreshToken) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
  }
}

/**
 * Get access token
 */
export const getAccessToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Get refresh token
 */
export const getRefreshToken = () => {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

/**
 * Save user data
 */
export const saveUser = (user) => {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

/**
 * Get user data
 */
export const getUser = () => {
  const user = localStorage.getItem(USER_KEY)
  return user ? JSON.parse(user) : null
}

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getAccessToken()
}

/**
 * Logout - clear all auth data
 */
export const logout = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * Parse JWT token to get expiry
 */
export const parseJwt = (token) => {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (e) {
    return null
  }
}

/**
 * Check if token is expired
 */
export const isTokenExpired = (token) => {
  if (!token) return true
  
  const payload = parseJwt(token)
  if (!payload || !payload.exp) return true
  
  // Check if token expires in the next 30 seconds
  const expiryTime = payload.exp * 1000
  const currentTime = Date.now()
  return currentTime >= expiryTime - 30000
}

