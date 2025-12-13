import React, { useState, useEffect, lazy, Suspense } from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import Preloader from '../components/Preloader'

// Lazy load components for better performance
const Header = lazy(() => import('./landing/Header'))
const ParticleHero = lazy(() => import('./landing/ParticleHero'))
const ProblemStatement = lazy(() => import('./landing/ProblemStatement'))
const FeatureShowcase = lazy(() => import('./landing/FeatureShowcase'))
const InteractiveFlow = lazy(() => import('./landing/InteractiveFlow'))
const DashboardPreview = lazy(() => import('./landing/DashboardPreview'))
const Pricing = lazy(() => import('./landing/Pricing'))
const CTASection = lazy(() => import('./landing/CTASection'))
const FAQ = lazy(() => import('./landing/FAQ'))
const Footer = lazy(() => import('./landing/Footer'))

// Preload critical above-the-fold components
const preloadCritical = () => {
  import('./landing/Header')
  import('./landing/ParticleHero')
}

// Loading fallback
const SectionLoader = () => (
  <div className="min-h-[50vh] bg-background flex items-center justify-center">
    <div className="w-8 h-8 border-2 border-primary/30 border-t-primary animate-spin" />
  </div>
)

// Main Landing component
const Landing: React.FC = () => {
  const [loading, setLoading] = useState(true)

  // Start preloading critical components immediately
  useEffect(() => {
    preloadCritical()
  }, [])

  useEffect(() => {
    // Disable scrolling during preloader
    if (loading) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => { document.body.style.overflow = '' }
  }, [loading])

  return (
    <HelmetProvider>
      <Helmet>
        <title>Raptorflow | AI-First Marketing OS for Founders</title>
        <meta name="description" content="The AI-powered marketing operating system that turns chaos into clarity. Build strategy with precision, track with Radar, execute with confidence." />
        <meta name="theme-color" content="#000000" />
        <meta property="og:title" content="Raptorflow | AI-First Marketing OS" />
        <meta property="og:description" content="Stop guessing. Start executing. The marketing OS built for founders who demand results." />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
      </Helmet>

      {/* Preloader */}
      {loading && <Preloader onComplete={() => setLoading(false)} />}

      {/* Main content */}
      {!loading && (
        <div className="bg-background min-h-screen overflow-x-hidden">
          <Suspense fallback={<SectionLoader />}>
            {/* Navigation */}
            <Header />

            {/* Hero with particle effects */}
            <ParticleHero />

            {/* The Problem - why they need this */}
            <ProblemStatement />

            {/* How it works - simple 4-step flow */}
            <InteractiveFlow />

            {/* Feature showcase - the 6 pillars */}
            <FeatureShowcase />

            {/* Live dashboard preview */}
            <DashboardPreview />

            {/* Pricing - 30 day plans */}
            <Pricing />

            {/* FAQ */}
            <FAQ />

            {/* Strong CTA */}
            <CTASection />

            {/* Magnificent footer */}
            <Footer />
          </Suspense>
        </div>
      )}
    </HelmetProvider>
  )
}

export default Landing
