'use client'

import { useState, useEffect, useCallback } from 'react'
import { createClient } from '@/lib/auth-client'
import { 
  Permission, 
  UserPermission, 
  PermissionCheck, 
  PERMISSIONS,
  checkPermission as serverCheckPermission,
  getUserPermissions as serverGetUserPermissions
} from '@/lib/permissions'

// Client-side permission hook
export function usePermissions(userId?: string) {
  const [permissions, setPermissions] = useState<UserPermission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load user permissions
  const loadPermissions = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const supabase = createClient()
      if (!supabase) {
        throw new Error('Supabase client not available')
      }

      // Get current user if userId not provided
      let targetUserId = userId
      if (!targetUserId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) {
          setPermissions([])
          return
        }

        const { data: dbUser } = await supabase
          .from('users')
          .select('id')
          .eq('auth_user_id', user.id)
          .single()

        targetUserId = dbUser?.id
      }

      if (!targetUserId) {
        setPermissions([])
        return
      }

      // Get permissions from server function
      const userPermissions = await serverGetUserPermissions(targetUserId)
      setPermissions(userPermissions)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load permissions')
      console.error('Load permissions error:', err)
    } finally {
      setLoading(false)
    }
  }, [userId])

  // Check if user has specific permission
  const hasPermission = useCallback(async (permissionName: string): Promise<PermissionCheck> => {
    try {
      const supabase = createClient()
      if (!supabase) {
        return { hasPermission: false, source: 'none' }
      }

      // Get current user if userId not provided
      let targetUserId = userId
      if (!targetUserId) {
        const { data: { user } } = await supabase.auth.getUser()
        if (!user) {
          return { hasPermission: false, source: 'none' }
        }

        const { data: dbUser } = await supabase
          .from('users')
          .select('id')
          .eq('auth_user_id', user.id)
          .single()

        targetUserId = dbUser?.id
      }

      if (!targetUserId) {
        return { hasPermission: false, source: 'none' }
      }

      return await serverCheckPermission(permissionName, targetUserId)

    } catch (err) {
      console.error('Permission check error:', err)
      return { hasPermission: false, source: 'none' }
    }
  }, [userId])

  // Check if user has any of the specified permissions
  const hasAnyPermission = useCallback(async (permissionNames: string[]): Promise<PermissionCheck> => {
    for (const permission of permissionNames) {
      const check = await hasPermission(permission)
      if (check.hasPermission) {
        return check
      }
    }
    return { hasPermission: false, source: 'none' }
  }, [hasPermission])

  // Check if user has all specified permissions
  const hasAllPermissions = useCallback(async (permissionNames: string[]): Promise<PermissionCheck> => {
    for (const permission of permissionNames) {
      const check = await hasPermission(permission)
      if (!check.hasPermission) {
        return check
      }
    }
    return { hasPermission: true, source: 'user_specific' }
  }, [hasPermission])

  // Get permissions by category
  const getPermissionsByCategory = useCallback((category: string): UserPermission[] => {
    return permissions.filter(p => p.category === category)
  }, [permissions])

  // Check if user has permission for specific resource and action
  const hasResourcePermission = useCallback(async (
    resource: string, 
    action: string
  ): Promise<PermissionCheck> => {
    const permissionName = `${action}:${resource}`
    return await hasPermission(permissionName)
  }, [hasPermission])

  // Load permissions on mount
  useEffect(() => {
    loadPermissions()
  }, [loadPermissions])

  return {
    permissions,
    loading,
    error,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    getPermissionsByCategory,
    hasResourcePermission,
    reloadPermissions: loadPermissions
  }
}
