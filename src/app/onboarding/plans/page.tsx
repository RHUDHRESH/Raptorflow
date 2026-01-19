'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Check, Zap, Star, Shield, Loader2 } from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

interface Plan {
  id: string
  name: string
  description: string
  price_monthly_paise: number
  price_yearly_paise: number
  features: Record<string, any>
  popular?: boolean
  storage_limit_bytes: number
}

// =============================================================================
// PLANS PAGE
// =============================================================================

export default function ChoosePlan() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const router = useRouter()

  useEffect(() => {
    fetchPlans()
  }, [])

  async function fetchPlans() {
    try {
      const response = await fetch('/api/plans')
      const data = await response.json()
      setPlans(data.plans || [])
    } catch (err) {
      setError('Failed to load plans')
    }
  }

  async function handleSelectPlan() {
    if (!selectedPlan) return

    setIsLoading(true)
    setError('')

    try {
      const response = await fetch('/api/onboarding/select-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          planId: selectedPlan,
          billingCycle,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to select plan')
      }

      router.push('/onboarding/payment')
      router.refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  function formatPrice(paise: number): string {
    return `₹${(paise / 100).toLocaleString('en-IN')}`
  }

  function formatStorage(bytes: number): string {
    const gb = bytes / (1024 * 1024 * 1024)
    if (gb >= 1000) {
      return `${(gb / 1024).toFixed(0)} TB`
    }
    return `${gb.toFixed(0)} GB`
  }

  function getPlanIcon(planId: string) {
    switch (planId) {
      case 'starter':
        return <Zap className="w-6 h-6" />
      case 'pro':
        return <Star className="w-6 h-6" />
      case 'enterprise':
        return <Shield className="w-6 h-6" />
      default:
        return <Zap className="w-6 h-6" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">Choose Your Plan</h1>
        <p className="text-muted-foreground max-w-md mx-auto">
          Select the plan that best fits your needs. You can upgrade or downgrade anytime.
        </p>
      </div>

      {/* Billing Toggle */}
      <div className="flex justify-center">
        <div className="bg-muted p-1 rounded-lg inline-flex">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${billingCycle === 'monthly'
                ? 'bg-background shadow text-foreground'
                : 'text-muted-foreground hover:text-foreground'
              }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${billingCycle === 'yearly'
                ? 'bg-background shadow text-foreground'
                : 'text-muted-foreground hover:text-foreground'
              }`}
          >
            Yearly <span className="text-primary font-semibold">(Save 17%)</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const price = billingCycle === 'monthly'
            ? plan.price_monthly_paise
            : Math.round(plan.price_monthly_paise * 10 / 12)

          const yearlyPrice = billingCycle === 'yearly'
            ? plan.price_yearly_paise
            : plan.price_monthly_paise * 12

          const isSelected = selectedPlan === plan.id

          return (
            <Card
              key={plan.id}
              onClick={() => setSelectedPlan(plan.id)}
              className={`relative cursor-pointer transition-all hover:shadow-lg ${isSelected ? 'ring-2 ring-primary' : ''
                } ${plan.popular ? 'scale-[1.02] shadow-lg' : ''}`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-primary text-primary-foreground">
                    Most Popular
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pt-8">
                <div className={`inline-flex items-center justify-center w-12 h-12 rounded-full mx-auto mb-2 ${isSelected ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary'
                  }`}>
                  {getPlanIcon(plan.id)}
                </div>
                <CardTitle className="text-xl">{plan.name}</CardTitle>
                <CardDescription>{plan.description}</CardDescription>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Price */}
                <div className="text-center">
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-3xl font-bold">{formatPrice(price)}</span>
                    <span className="text-muted-foreground text-sm">/month</span>
                  </div>
                  {billingCycle === 'yearly' && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Billed as {formatPrice(yearlyPrice)} per year
                    </p>
                  )}
                </div>

                {/* Features */}
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <Check className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                    <span className="text-sm">
                      <strong>{formatStorage(plan.storage_limit_bytes)}</strong> storage
                    </span>
                  </li>

                  {plan.features.projects !== undefined && (
                    <li className="flex items-start gap-3">
                      <Check className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <span className="text-sm">
                        <strong>{plan.features.projects === -1 ? 'Unlimited' : plan.features.projects}</strong> projects
                      </span>
                    </li>
                  )}

                  {plan.features.team_members !== undefined && (
                    <li className="flex items-start gap-3">
                      <Check className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <span className="text-sm">
                        <strong>{plan.features.team_members === -1 ? 'Unlimited' : plan.features.team_members}</strong> team members
                      </span>
                    </li>
                  )}

                  {plan.features.support && (
                    <li className="flex items-start gap-3">
                      <Check className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                      <span className="text-sm capitalize">{plan.features.support} support</span>
                    </li>
                  )}
                </ul>

                {/* Select Button */}
                <Button
                  className="w-full"
                  variant={isSelected ? 'default' : 'outline'}
                >
                  {isSelected ? 'Selected' : 'Select Plan'}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-destructive/10 border border-destructive rounded-lg">
          <p className="text-sm text-destructive">{error}</p>
        </div>
      )}

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleSelectPlan}
          disabled={!selectedPlan || isLoading}
          size="lg"
          className="px-12"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Processing...
            </>
          ) : (
            'Continue to Payment'
          )}
        </Button>
      </div>

      {/* Trust */}
      <div className="text-center pt-6 border-t">
        <p className="text-sm text-muted-foreground mb-4">
          Trusted by founders building the next generation of companies
        </p>
        <div className="flex justify-center items-center gap-8 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4" />
            <span>Secure Payments</span>
          </div>
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            <span>Instant Access</span>
          </div>
        </div>
      </div>
    </div>
  )
}
