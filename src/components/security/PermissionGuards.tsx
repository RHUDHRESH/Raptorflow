'use client'

import React, { useState, useEffect } from 'react'
import { usePermissions } from '@/hooks/usePermissions'
import { PERMISSIONS } from '@/lib/permissions'

// Higher-order component for permission-based rendering
export function withPermission<T extends object>(
  Component: React.ComponentType<T>,
  requiredPermissions: string | string[],
  requireAll: boolean = false
) {
  return function PermissionWrapper(props: T) {
    const { hasAnyPermission, hasAllPermissions, loading } = usePermissions()
    const [hasRequiredPermission, setHasRequiredPermission] = useState(false)
    const [checking, setChecking] = useState(true)

    useEffect(() => {
      const checkPermissions = async () => {
        try {
          let hasPermission = false
          
          if (Array.isArray(requiredPermissions)) {
            if (requireAll) {
              const result = await hasAllPermissions(requiredPermissions)
              hasPermission = result.hasPermission
            } else {
              const result = await hasAnyPermission(requiredPermissions)
              hasPermission = result.hasPermission
            }
          } else {
            const result = await hasAnyPermission([requiredPermissions])
            hasPermission = result.hasPermission
          }
          
          setHasRequiredPermission(hasPermission)
        } catch (error) {
          console.error('Permission check error:', error)
          setHasRequiredPermission(false)
        } finally {
          setChecking(false)
        }
      }

      checkPermissions()
    }, [requiredPermissions, requireAll, hasAnyPermission, hasAllPermissions])

    if (loading || checking) {
      return <div>Loading permissions...</div>
    }

    if (!hasRequiredPermission) {
      return (
        <div className="flex items-center justify-center p-8 bg-red-50 border border-red-200 rounded-lg">
          <div className="text-center">
            <h3 className="text-lg font-medium text-red-800">Access Denied</h3>
            <p className="mt-2 text-sm text-red-600">
              You don't have permission to access this resource.
            </p>
            <p className="mt-1 text-xs text-red-500">
              Required permissions: {Array.isArray(requiredPermissions) ? requiredPermissions.join(', ') : requiredPermissions}
            </p>
          </div>
        </div>
      )
    }

    return <Component {...props} />
  }
}

// Permission guard component
interface PermissionGuardProps {
  children: React.ReactNode
  permissions: string | string[]
  requireAll?: boolean
  fallback?: React.ReactNode
  loadingComponent?: React.ReactNode
}

export function PermissionGuard({
  children,
  permissions,
  requireAll = false,
  fallback = null,
  loadingComponent = <div>Loading permissions...</div>
}: PermissionGuardProps) {
  const { hasAnyPermission, hasAllPermissions, loading } = usePermissions()
  const [hasRequiredPermission, setHasRequiredPermission] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    const checkPermissions = async () => {
      try {
        let hasPermission = false
        
        if (Array.isArray(permissions)) {
          if (requireAll) {
            const result = await hasAllPermissions(permissions)
            hasPermission = result.hasPermission
          } else {
            const result = await hasAnyPermission(permissions)
            hasPermission = result.hasPermission
          }
        } else {
          const result = await hasAnyPermission([permissions])
          hasPermission = result.hasPermission
        }
        
        setHasRequiredPermission(hasPermission)
      } catch (error) {
        console.error('Permission check error:', error)
        setHasRequiredPermission(false)
      } finally {
        setChecking(false)
      }
    }

    checkPermissions()
  }, [permissions, requireAll, hasAnyPermission, hasAllPermissions])

  if (loading || checking) {
    return <>{loadingComponent}</>
  }

  if (!hasRequiredPermission) {
    return <>{fallback}</>
  }

  return <>{children}</>
}

// Common permission guards for convenience
export function AdminGuard({ children }: { children: React.ReactNode }) {
  return (
    <PermissionGuard
      permissions={PERMISSIONS.ADMIN_READ_USERS}
      fallback={
        <div className="flex items-center justify-center p-8 bg-red-50 border border-red-200 rounded-lg">
          <div className="text-center">
            <h3 className="text-lg font-medium text-red-800">Admin Access Required</h3>
            <p className="mt-2 text-sm text-red-600">
              You need administrator privileges to access this area.
            </p>
          </div>
        </div>
      }
    >
      {children}
    </PermissionGuard>
  )
}

export function WorkspaceGuard({ children }: { children: React.ReactNode }) {
  return (
    <PermissionGuard
      permissions={PERMISSIONS.READ_OWN_WORKSPACE}
      fallback={
        <div className="flex items-center justify-center p-8 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="text-center">
            <h3 className="text-lg font-medium text-yellow-800">Workspace Access Required</h3>
            <p className="mt-2 text-sm text-yellow-600">
              You need to join or create a workspace to access this area.
            </p>
          </div>
        </div>
      }
    >
      {children}
    </PermissionGuard>
  )
}

export function BillingGuard({ children }: { children: React.ReactNode }) {
  return (
    <PermissionGuard
      permissions={[
        PERMISSIONS.BILLING_READ_SUBSCRIPTIONS,
        PERMISSIONS.ADMIN_MANAGE_SUBSCRIPTIONS
      ]}
      fallback={
        <div className="flex items-center justify-center p-8 bg-orange-50 border border-orange-200 rounded-lg">
          <div className="text-center">
            <h3 className="text-lg font-medium text-orange-800">Billing Access Required</h3>
            <p className="mt-2 text-sm text-orange-600">
              You need billing privileges to access this area.
            </p>
          </div>
        </div>
      }
    >
      {children}
    </PermissionGuard>
  )
}
