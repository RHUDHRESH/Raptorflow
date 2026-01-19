'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { HardDrive, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react'

export default function SetupStorage() {
  const [isProvisioning, setIsProvisioning] = useState(true)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('Initializing storage...')
  const [error, setError] = useState('')
  const [storageDetails, setStorageDetails] = useState<any>(null)
  const router = useRouter()
  
  useEffect(() => {
    provisionStorage()
  }, [])
  
  async function provisionStorage() {
    try {
      // Simulate progress updates
      const progressSteps = [
        { progress: 20, status: 'Creating storage bucket...', delay: 500 },
        { progress: 40, status: 'Setting up permissions...', delay: 800 },
        { progress: 60, status: 'Configuring access policies...', delay: 600 },
        { progress: 80, status: 'Finalizing setup...', delay: 700 },
      ]
      
      for (const step of progressSteps) {
        setProgress(step.progress)
        setStatus(step.status)
        await new Promise(resolve => setTimeout(resolve, step.delay))
      }
      
      // Actually provision storage
      const response = await fetch('/api/onboarding/provision-storage', {
        method: 'POST',
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to provision storage')
      }
      
      setProgress(100)
      setStatus('Storage ready!')
      setStorageDetails(data.storage)
      setIsProvisioning(false)
      
      // Auto-advance after a moment
      setTimeout(() => {
        router.push('/onboarding/plans')
        router.refresh()
      }, 2000)
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setIsProvisioning(false)
    }
  }
  
  async function handleRetry() {
    setError('')
    setIsProvisioning(true)
    setProgress(0)
    setStatus('Retrying storage setup...')
    await provisionStorage()
  }
  
  if (error) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-2">
                  Storage Setup Failed
                </h1>
                <p className="text-gray-600">{error}</p>
              </div>
              <Button onClick={handleRetry} variant="outline">
                <RefreshCw className="mr-2 h-4 w-4" />
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
        
        <Alert>
          <AlertDescription>
            If the problem persists, please contact support at support@raptorflow.com
          </AlertDescription>
        </Alert>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
          <HardDrive className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-3xl font-bold text-gray-900">
          Setting Up Your Storage
        </h1>
        <p className="text-gray-600 max-w-md mx-auto">
          We're preparing your secure cloud storage. This will only take a moment.
        </p>
      </div>
      
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {isProvisioning ? (
              <>
                <div className="animate-spin">
                  <HardDrive className="w-5 h-5" />
                </div>
                Provisioning Storage
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5 text-green-600" />
                Storage Ready
              </>
            )}
          </CardTitle>
          <CardDescription>
            {isProvisioning ? 'Please wait while we set up your infrastructure' : 'Your storage is ready to use'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>{status}</span>
              <span>{progress}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
          
          {/* Storage Details */}
          {storageDetails && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h3 className="font-medium text-green-900 mb-2">Storage Details</h3>
              <dl className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <dt className="text-green-700">Location:</dt>
                  <dd className="font-mono text-green-900">{storageDetails.bucket}</dd>
                </div>
                <div>
                  <dt className="text-green-700">Capacity:</dt>
                  <dd className="text-green-900">5 GB (included)</dd>
                </div>
                <div>
                  <dt className="text-green-700">Region:</dt>
                  <dd className="text-green-900">Asia South (Mumbai)</dd>
                </div>
                <div>
                  <dt className="text-green-700">Status:</dt>
                  <dd className="text-green-900 font-medium">Active</dd>
                </div>
              </dl>
            </div>
          )}
          
          {/* Features */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-3">What you get:</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Secure cloud storage with 99.9% uptime
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Automatic backups and versioning
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                Global CDN for fast access
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                End-to-end encryption
              </li>
            </ul>
          </div>
          
          {!isProvisioning && (
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-4">
                Redirecting to plan selection...
              </p>
              <div className="inline-flex gap-2">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
