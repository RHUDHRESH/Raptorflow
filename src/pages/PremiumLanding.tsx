import React, { useEffect } from 'react'
import Lenis from 'lenis'
import { Helmet, HelmetProvider } from 'react-helmet-async'

import PremiumHeader from './landing/premium/PremiumHeader'
import PremiumHero from './landing/premium/PremiumHero'
import PremiumFeatures from './landing/premium/PremiumFeatures'
import LuxuryTestimonials from './landing/premium/LuxuryTestimonials'
import PremiumCTA from './landing/premium/PremiumCTA'
import MinimalFooter from './landing/premium/MinimalFooter'
import CustomCursor from './landing/premium/CustomCursor'

const PremiumLanding = () => {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      
      
      smooth: true,
      wheelMultiplier: 1,
      smoothTouch: false,
      touchMultiplier: 2,
    })

    function raf(time: number) {
      lenis.raf(time)
      requestAnimationFrame(raf)
    }

    requestAnimationFrame(raf)

    return () => {
      lenis.destroy()
    }
  }, [])

  return (
    <HelmetProvider>
      <Helmet>
        <title>Raptorflow | The Art of Strategy</title>
        <meta name="description" content="Elevate your marketing strategy with Raptorflow. The AI-first operating system designed for precision, clarity, and growth." />
        <style>{`
          ::selection {
            background-color: #f59e0b; /* Accent color */
            color: #000;
          }
          body {
            background-color: #0a0a0a;
            color: #fff;
          }
        `}</style>
      </Helmet>
      
      <div className="bg-background min-h-screen text-foreground selection:bg-accent selection:text-black cursor-none">
        <CustomCursor />
        <PremiumHeader />
        
        <main>
          <PremiumHero />
          <PremiumFeatures />
          <LuxuryTestimonials />
          <PremiumCTA />
        </main>

        <MinimalFooter />
      </div>
    </HelmetProvider>
  )}

export default PremiumLanding
