import React from 'react'

import PremiumHeader from './landing/premium/PremiumHeader'
import PremiumHero from './landing/premium/PremiumHero'
import PremiumFeatures from './landing/premium/PremiumFeatures'
import PremiumCTA from './landing/premium/PremiumCTA'

const PremiumLanding = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <PremiumHeader />
      <main>
        <PremiumHero />
        <PremiumFeatures />
        <PremiumCTA />
      </main>
    </div>
  )
}

export default PremiumLanding
