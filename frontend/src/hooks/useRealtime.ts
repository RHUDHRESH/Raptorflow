// Real-time hook for Redis pub/sub functionality
// Provides WebSocket-like real-time updates using Redis pub/sub

import { useEffect, useState, useCallback } from 'react'
import { redisClient } from '@/lib/redis-client'

interface UseRealtimeOptions {
  autoConnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

interface RealtimeState<T> {
  data: T | null
  isConnected: boolean
  error: string | null
  lastUpdate: Date | null
}

export function useRealtime<T = any>(
  channel: string, 
  options: UseRealtimeOptions = {}
): RealtimeState<T> & { disconnect: () => void; reconnect: () => void } {
  const {
    autoConnect = true,
    reconnectInterval = 5000,
    maxReconnectAttempts = 10,
  } = options

  const [state, setState] = useState<RealtimeState<T>>({
    data: null,
    isConnected: false,
    error: null,
    lastUpdate: null,
  })

  const [reconnectAttempts, setReconnectAttempts] = useState(0)
  const [shouldReconnect, setShouldReconnect] = useState(autoConnect)

  const disconnect = useCallback(() => {
    setShouldReconnect(false)
    setReconnectAttempts(0)
    setState(prev => ({ ...prev, isConnected: false }))
  }, [])

  const reconnect = useCallback(() => {
    setShouldReconnect(true)
    setReconnectAttempts(0)
  }, [])

  const subscribe = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null, isConnected: true }))
      
      // For Upstash Redis, we need to poll for new messages
      // since true pub/sub isn't available in the edge runtime
      const pollMessages = async () => {
        try {
          const messages = await redisClient.lrange(`${channel}:messages`, 0, -1)
          if (messages && messages.length > 0) {
            const latestMessage = messages[messages.length - 1]
            if (latestMessage) {
              try {
                const data = JSON.parse(latestMessage)
                setState(prev => ({
                  ...prev,
                  data,
                  lastUpdate: new Date(),
                }))
                
                // Clear processed messages
                await redisClient.del(`${channel}:messages`)
              } catch (parseError) {
                console.error('Failed to parse message:', parseError)
              }
            }
          }
        } catch (error) {
          console.error('Error polling messages:', error)
          setState(prev => ({
            ...prev,
            error: error instanceof Error ? error.message : 'Unknown error',
            isConnected: false,
          }))
        }
        
        // Continue polling if should reconnect
        if (shouldReconnect && reconnectAttempts < maxReconnectAttempts) {
          setTimeout(pollMessages, reconnectInterval)
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          setState(prev => ({
            ...prev,
            error: 'Max reconnection attempts reached',
            isConnected: false,
          }))
        }
      }

      // Start polling
      pollMessages()
      
    } catch (error) {
      console.error('Error setting up real-time subscription:', error)
      setState(prev => ({
        ...prev,
        error: error instanceof Error ? error.message : 'Failed to connect',
        isConnected: false,
      }))
    }
  }, [channel, shouldReconnect, reconnectAttempts, maxReconnectAttempts, reconnectInterval])

  // Handle connection lifecycle
  useEffect(() => {
    if (shouldReconnect) {
      subscribe()
    }
  }, [subscribe, shouldReconnect])

  // Auto-reconnect logic
  useEffect(() => {
    if (!state.isConnected && shouldReconnect && reconnectAttempts > 0) {
      const timer = setTimeout(() => {
        setReconnectAttempts(prev => prev + 1)
      }, reconnectInterval)
      
      return () => clearTimeout(timer)
    }
  }, [state.isConnected, shouldReconnect, reconnectAttempts, reconnectInterval])

  return {
    ...state,
    disconnect,
    reconnect,
  }
}

// Hook for publishing messages to Redis channels
export function useRealtimePublisher() {
  const publish = useCallback(async <T>(channel: string, message: T): Promise<boolean> => {
    try {
      const messageString = JSON.stringify(message)
      await redisClient.lpush(`${channel}:messages`, messageString)
      
      // Set expiry to prevent memory leaks
      await redisClient.expire(`${channel}:messages`, 3600) // 1 hour
      
      return true
    } catch (error) {
      console.error('Error publishing message:', error)
      return false
    }
  }, [])

  return { publish }
}

// Hook for real-time collaboration (multiple users)
export function useRealtimeCollaboration<T = any>(
  channelId: string,
  userId: string,
  options?: UseRealtimeOptions
) {
  const realtime = useRealtime<T>(channelId, options)
  const { publish } = useRealtimePublisher()

  const sendUpdate = useCallback(async (data: T) => {
    const message = {
      data,
      userId,
      timestamp: new Date().toISOString(),
      type: 'update'
    }
    return await publish(channelId, message)
  }, [publish, channelId, userId])

  const sendPresence = useCallback(async (status: 'online' | 'offline' | 'away') => {
    const message = {
      userId,
      status,
      timestamp: new Date().toISOString(),
      type: 'presence'
    }
    return await publish(`${channelId}:presence`, message)
  }, [publish, channelId, userId])

  return {
    ...realtime,
    sendUpdate,
    sendPresence,
  }
}
