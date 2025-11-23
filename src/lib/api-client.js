/**
 * Enhanced API client with retry logic, error handling, and interceptors.
 */

import { supabase } from './supabase'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Sleep utility for retry delays
 */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms))

/**
 * Calculate exponential backoff delay
 */
function calculateBackoff(attempt, baseDelay = 1000, maxDelay = 10000) {
  const delay = Math.min(baseDelay * Math.pow(2, attempt), maxDelay)
  // Add jitter to prevent thundering herd
  return delay * (0.5 + Math.random() * 0.5)
}

/**
 * API Error class
 */
export class APIError extends Error {
  constructor(message, status, data) {
    super(message)
    this.name = 'APIError'
    this.status = status
    this.data = data
  }
}

/**
 * Enhanced fetch with retry logic
 */
async function fetchWithRetry(url, options, maxRetries = 3) {
  let lastError

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = await fetch(url, options)

      // Success - return response
      if (response.ok) {
        return response
      }

      // Client errors (4xx) - don't retry
      if (response.status >= 400 && response.status < 500) {
        const errorData = await response.json().catch(() => ({}))
        throw new APIError(
          errorData.detail || 'Client error',
          response.status,
          errorData
        )
      }

      // Server errors (5xx) - retry
      if (response.status >= 500) {
        throw new Error(`Server error: ${response.status}`)
      }

      // Other errors
      throw new Error(`HTTP ${response.status}`)

    } catch (error) {
      lastError = error

      // Don't retry on client errors
      if (error instanceof APIError) {
        throw error
      }

      // Last attempt - throw error
      if (attempt === maxRetries - 1) {
        console.error(`API call failed after ${maxRetries} attempts:`, error)
        throw error
      }

      // Calculate backoff and retry
      const delay = calculateBackoff(attempt)
      console.warn(`API call failed (attempt ${attempt + 1}/${maxRetries}), retrying in ${Math.round(delay)}ms...`)
      await sleep(delay)
    }
  }

  throw lastError
}

/**
 * Main API client
 */
class APIClient {
  constructor(baseURL) {
    this.baseURL = baseURL
    this.interceptors = {
      request: [],
      response: []
    }
  }

  /**
   * Add request interceptor
   */
  addRequestInterceptor(interceptor) {
    this.interceptors.request.push(interceptor)
  }

  /**
   * Add response interceptor
   */
  addResponseInterceptor(interceptor) {
    this.interceptors.response.push(interceptor)
  }

  /**
   * Get authentication token
   */
  async getAuthToken() {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token || null
  }

  /**
   * Make API request
   */
  async request(endpoint, options = {}) {
    const {
      method = 'GET',
      headers = {},
      body,
      maxRetries = 3,
      skipAuth = false,
      ...otherOptions
    } = options

    // Build URL
    const url = `${this.baseURL}${endpoint}`

    // Build headers
    const requestHeaders = {
      'Content-Type': 'application/json',
      ...headers
    }

    // Add authentication
    if (!skipAuth) {
      const token = await this.getAuthToken()
      if (token) {
        requestHeaders['Authorization'] = `Bearer ${token}`
      }
    }

    // Build request options
    let requestOptions = {
      method,
      headers: requestHeaders,
      ...otherOptions
    }

    // Add body for non-GET requests
    if (body && method !== 'GET') {
      requestOptions.body = JSON.stringify(body)
    }

    // Apply request interceptors
    for (const interceptor of this.interceptors.request) {
      requestOptions = await interceptor(requestOptions)
    }

    // Make request with retry
    let response = await fetchWithRetry(url, requestOptions, maxRetries)

    // Apply response interceptors
    for (const interceptor of this.interceptors.response) {
      response = await interceptor(response)
    }

    // Parse JSON response
    const data = await response.json().catch(() => null)

    return data
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' })
  }

  /**
   * POST request
   */
  async post(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'POST', body })
  }

  /**
   * PUT request
   */
  async put(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PUT', body })
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' })
  }

  /**
   * PATCH request
   */
  async patch(endpoint, body, options = {}) {
    return this.request(endpoint, { ...options, method: 'PATCH', body })
  }
}

// Create singleton instance
const apiClient = new APIClient(API_BASE_URL)

// Add default interceptors

// Request interceptor: Add correlation ID
apiClient.addRequestInterceptor(async (options) => {
  const correlationId = `web-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  options.headers['X-Correlation-ID'] = correlationId
  return options
})

// Response interceptor: Log errors to PostHog
apiClient.addResponseInterceptor(async (response) => {
  if (!response.ok && window.posthog) {
    window.posthog.capture('api_error', {
      status: response.status,
      url: response.url,
      statusText: response.statusText
    })
  }
  return response
})

export default apiClient
export { APIClient }
