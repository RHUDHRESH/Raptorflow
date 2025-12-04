import React, { useState, useEffect, lazy, Suspense } from 'react'
import { Helmet, HelmetProvider } from 'react-helmet-async'
import Preloader from '../components/Preloader'

// Lazy load components
const Header = lazy(() => import('./landing/Header'))
const Hero = lazy(() => import('./landing/Hero'))
const ValueStrip = lazy(() => import('./landing/ValueStrip'))
const TestimonialMarquee = lazy(() => import('./landing/TestimonialMarquee'))
const PullQuote = lazy(() => import('./landing/PullQuote'))
const Pricing = lazy(() => import('./landing/Pricing'))
const FAQ = lazy(() => import('./landing/FAQ'))
const Footer = lazy(() => import('./landing/Footer'))

// Loading fallback
const SectionLoader = () => (
  <div className="min-h-screen bg-black" />
)

// Main Landing component
const Landing: React.FC = () => {
  const [loading, setLoading] = useState(true)

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
        <title>Raptorflow | Strategy that ships</title>
        <meta name="description" content="Transform scattered ideas into a precision 90-day execution plan. The strategic methodology trusted by 500+ founders." />
        <meta name="theme-color" content="#000000" />
      </Helmet>

      {/* Preloader */}
      {loading && <Preloader onComplete={() => setLoading(false)} />}

      {/* Main content */}
      {!loading && (
        <div className="bg-black min-h-screen">
          <Suspense fallback={<SectionLoader />}>
            <Header />
            <Hero />
            <ValueStrip />
            <PullQuote />
            <TestimonialMarquee />
            <Pricing />
            <FAQ />
            <Footer />
          </Suspense>
        </div>
      )}
    </HelmetProvider>
  )
}

export default Landing
