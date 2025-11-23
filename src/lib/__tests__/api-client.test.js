/**
 * Tests for enhanced API client with retry logic
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import apiClient, { APIClient, APIError } from '../api-client'

// Mock fetch
global.fetch = vi.fn()

describe('APIClient', () => {
  let client

  beforeEach(() => {
    client = new APIClient('http://localhost:8000')
    global.fetch.mockClear()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('request method', () => {
    it('should make successful GET request', async () => {
      const mockResponse = { data: 'test' }
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse
      })

      const result = await client.get('/test')

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledTimes(1)
    })

    it('should make successful POST request', async () => {
      const mockResponse = { id: '123' }
      const postData = { name: 'test' }

      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse
      })

      const result = await client.post('/test', postData)

      expect(result).toEqual(mockResponse)
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/test',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(postData)
        })
      )
    })

    it('should add Content-Type header by default', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      await client.get('/test')

      const call Args = global.fetch.mock.calls[0][1]
      expect(callArgs.headers['Content-Type']).toBe('application/json')
    })

    it('should throw APIError for 4xx errors', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' })
      })

      await expect(client.get('/test')).rejects.toThrow(APIError)
      await expect(client.get('/test')).rejects.toThrow('Not found')
    })

    it('should retry on 5xx errors', async () => {
      // First two calls fail with 500
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({})
      })
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({})
      })
      // Third call succeeds
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ data: 'success' })
      })

      const result = await client.get('/test', { maxRetries: 3 })

      expect(result).toEqual({ data: 'success' })
      expect(global.fetch).toHaveBeenCalledTimes(3)
    }, 10000) // Increase timeout for retry delays

    it('should fail after max retries', async () => {
      // All calls fail
      global.fetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({})
      })

      await expect(client.get('/test', { maxRetries: 3 })).rejects.toThrow()
      expect(global.fetch).toHaveBeenCalledTimes(3)
    }, 10000)

    it('should not retry on network errors that are 4xx', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' })
      })

      await expect(client.get('/test', { maxRetries: 3 })).rejects.toThrow(APIError)
      expect(global.fetch).toHaveBeenCalledTimes(1) // No retries
    })
  })

  describe('request interceptors', () => {
    it('should apply request interceptors', async () => {
      const interceptor = vi.fn(async (opts) => {
        opts.headers['X-Custom'] = 'test'
        return opts
      })

      client.addRequestInterceptor(interceptor)

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      await client.get('/test')

      expect(interceptor).toHaveBeenCalled()
      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.headers['X-Custom']).toBe('test')
    })

    it('should apply multiple request interceptors in order', async () => {
      const order = []

      client.addRequestInterceptor(async (opts) => {
        order.push(1)
        return opts
      })

      client.addRequestInterceptor(async (opts) => {
        order.push(2)
        return opts
      })

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      await client.get('/test')

      expect(order).toEqual([1, 2])
    })
  })

  describe('response interceptors', () => {
    it('should apply response interceptors', async () => {
      const interceptor = vi.fn(async (response) => response)

      client.addResponseInterceptor(interceptor)

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: 'test' })
      })

      await client.get('/test')

      expect(interceptor).toHaveBeenCalled()
    })
  })

  describe('HTTP methods', () => {
    beforeEach(() => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: async () => ({})
      })
    })

    it('should support PUT method', async () => {
      await client.put('/test', { data: 'test' })

      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.method).toBe('PUT')
    })

    it('should support DELETE method', async () => {
      await client.delete('/test')

      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.method).toBe('DELETE')
    })

    it('should support PATCH method', async () => {
      await client.patch('/test', { data: 'test' })

      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.method).toBe('PATCH')
    })
  })

  describe('authentication', () => {
    it('should add Authorization header when token is available', async () => {
      // Mock getAuthToken to return a token
      client.getAuthToken = vi.fn().mockResolvedValue('test-token-123')

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      await client.get('/test')

      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.headers['Authorization']).toBe('Bearer test-token-123')
    })

    it('should skip auth when skipAuth is true', async () => {
      client.getAuthToken = vi.fn().mockResolvedValue('test-token-123')

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({})
      })

      await client.get('/test', { skipAuth: true })

      expect(client.getAuthToken).not.toHaveBeenCalled()
      const callArgs = global.fetch.mock.calls[0][1]
      expect(callArgs.headers['Authorization']).toBeUndefined()
    })
  })
})

describe('APIError', () => {
  it('should create error with message, status, and data', () => {
    const error = new APIError('Test error', 404, { detail: 'Not found' })

    expect(error.message).toBe('Test error')
    expect(error.status).toBe(404)
    expect(error.data).toEqual({ detail: 'Not found' })
    expect(error.name).toBe('APIError')
  })
})

describe('singleton apiClient', () => {
  it('should have default interceptors configured', () => {
    expect(apiClient.interceptors.request.length).toBeGreaterThan(0)
    expect(apiClient.interceptors.response.length).toBeGreaterThan(0)
  })

  it('should add correlation ID header', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({})
    })

    await apiClient.get('/test')

    const callArgs = global.fetch.mock.calls[0][1]
    expect(callArgs.headers['X-Correlation-ID']).toMatch(/^web-/)
  })
})
