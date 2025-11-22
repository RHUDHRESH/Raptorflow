import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Info, Check, Loader2, ChevronLeft } from 'lucide-react';
import PropTypes from 'prop-types';
import { 
  generateMarketAlternatives, 
  generatePriceOptions, 
  generateServiceOptions, 
  generateSpecializationOptions,
  generatePriceReasoning,
  generateServiceReasoning
} from '../lib/ai';

// Pre-defined alternative positions on the map
const ALTERNATIVES = [
  { id: 'diy', label: 'DIY tools / software', x: -1.5, y: -1.8 },
  { id: 'courses', label: 'Courses / info products', x: -1.2, y: -1.5 },
  { id: 'freelancers', label: 'Freelancers / cheap agencies', x: -0.5, y: 0.3 },
  { id: 'agencies', label: 'Full-service agencies', x: 1.2, y: 1.5 },
  { id: 'nothing', label: 'Do nothing', x: -1.8, y: -1.2 },
];

// Price comparison options (maps to x-axis: -2 to +2)
const PRICE_OPTIONS = [
  { value: -2, label: 'Much cheaper' },
  { value: -1, label: 'A bit cheaper' },
  { value: 0, label: 'About the same' },
  { value: 1, label: 'A bit more expensive' },
  { value: 2, label: 'Much more expensive' },
];

// Service level options (maps to y-axis: -2 to +2)
const SERVICE_OPTIONS = [
  { value: -2, label: 'Mainly a self-serve tool' },
  { value: -1, label: 'Tool + some support' },
  { value: 0, label: 'Done-with-you' },
  { value: 2, label: 'Fully done-for-you / very high support' },
];

// Specialization options
const SPECIALIZATION_OPTIONS = [
  { value: 'broad', label: 'Works for almost anyone' },
  { value: 'medium', label: 'Works for lots of different businesses' },
  { value: 'niche', label: 'Built for a specific type of customer' },
];

// Validation helpers
const isValidAnswers = (answers) => {
  return answers && typeof answers === 'object';
};

const isValidPosition = (value) => {
  return typeof value === 'number' && value >= -2 && value <= 2;
};

const clampPosition = (value, min = -2, max = 2) => {
  return Math.max(min, Math.min(max, value));
};

// Calculate initial position from answers
const calculateInitialPosition = (answers) => {
  // Default to center
  let pricePos = 0;
  let servicePos = 0;
  
  // Validate answers object
  if (!isValidAnswers(answers)) {
    console.warn('Invalid answers provided to calculateInitialPosition');
    return { pricePos, servicePos };
  }
  
  // Safely access q2 with fallback
  const offerText = (answers?.q2 && typeof answers.q2 === 'string') 
    ? answers.q2.toLowerCase() 
    : '';
  
  // Price hints
  if (offerText.includes('cheap') || offerText.includes('affordable') || offerText.includes('low cost')) {
    pricePos = -1;
  } else if (offerText.includes('premium') || offerText.includes('expensive') || offerText.includes('high-end')) {
    pricePos = 1;
  } else if (offerText.includes('very cheap') || offerText.includes('budget')) {
    pricePos = -2;
  } else if (offerText.includes('very expensive') || offerText.includes('luxury')) {
    pricePos = 2;
  }
  
  // Service level hints
  if (offerText.includes('self-serve') || offerText.includes('diy') || offerText.includes('tool') || offerText.includes('software')) {
    servicePos = -1.5;
  } else if (offerText.includes('done-for-you') || offerText.includes('full service') || offerText.includes('managed')) {
    servicePos = 1.5;
  } else if (offerText.includes('retainer') || offerText.includes('ongoing')) {
    servicePos = 1;
  }
  
  // Safely access q7c with fallback
  const timeText = (answers?.q7c && typeof answers.q7c === 'string')
    ? answers.q7c.toLowerCase()
    : '';
  if (timeText.includes('team') || timeText.includes('10+')) {
    servicePos = Math.max(servicePos, 1);
  }
  
  // Clamp values to valid range
  return { 
    pricePos: clampPosition(pricePos), 
    servicePos: clampPosition(servicePos) 
  };
};

// Convert position to pixel coordinates on map (SVG coordinates)
const positionToPixels = (x, y, scaleMultiplier = 1) => {
  // SVG viewBox is 800x700, centered at (400, 350)
  // Map range is -2 to +2 on both axes
  const centerX = 400;
  const centerY = 350;
  const scale = 100 * scaleMultiplier; // Scale factor: 100px per unit (so -2 to +2 = 200px range)
  
  const pixelX = centerX + (x * scale);
  const pixelY = centerY - (y * scale); // Invert Y so positive is up
  
  return { x: pixelX, y: pixelY };
};

const MarketPositionSnapshot = ({ answers, onComplete, onBack }) => {
  const [stage, setStage] = useState('loading'); // loading, intro, animating, map-ready, price, service, specialization, complete
  const [pricePosition, setPricePosition] = useState(0);
  const [servicePosition, setServicePosition] = useState(0);
  const [specialization, setSpecialization] = useState('medium');
  const [animationStep, setAnimationStep] = useState(0);
  const [priceConfirmed, setPriceConfirmed] = useState(false);
  const [serviceConfirmed, setServiceConfirmed] = useState(false);
  const [hoveredAlternative, setHoveredAlternative] = useState(null);
  const [error, setError] = useState(null);
  const [isCompleting, setIsCompleting] = useState(false);
  const mapRef = useRef(null);
  
  // AI-generated options state
  const [alternatives, setAlternatives] = useState(ALTERNATIVES); // Start with fallback
  const [priceOptions, setPriceOptions] = useState(PRICE_OPTIONS);
  const [serviceOptions, setServiceOptions] = useState(SERVICE_OPTIONS);
  const [specializationOptions, setSpecializationOptions] = useState(SPECIALIZATION_OPTIONS);
  const [priceReasoning, setPriceReasoning] = useState('');
  const [serviceReasoning, setServiceReasoning] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Fixed SVG dimensions (matches viewBox)
  const SVG_WIDTH = 600;
  const SVG_HEIGHT = 500;
  
  // Calculate initial position from answers
  useEffect(() => {
    try {
      const initial = calculateInitialPosition(answers);
      setPricePosition(clampPosition(initial.pricePos));
      setServicePosition(clampPosition(initial.servicePos));
    } catch (err) {
      console.error('Error calculating initial position:', err);
      setError('Failed to calculate your market position. Using defaults.');
      // Use safe defaults
      setPricePosition(0);
      setServicePosition(0);
    }
  }, [answers]);
  
  // Generate AI options on mount
  useEffect(() => {
    const generateAllOptions = async () => {
      setIsGenerating(true);
      try {
        // Generate alternatives first (needed for other generations)
        const generatedAlternatives = await generateMarketAlternatives(answers);
        setAlternatives(generatedAlternatives);
        
        // Generate other options in parallel
        const [genPriceOptions, genServiceOptions, genSpecializationOptions] = await Promise.all([
          generatePriceOptions(answers, generatedAlternatives),
          generateServiceOptions(answers),
          generateSpecializationOptions(answers)
        ]);
        
        setPriceOptions(genPriceOptions);
        setServiceOptions(genServiceOptions);
        setSpecializationOptions(genSpecializationOptions);
        
        // Move to intro stage after generation
        setStage('intro');
      } catch (error) {
        console.error('Failed to generate market positioning options:', error);
        // Still allow user to proceed with fallback values
        setStage('intro');
      } finally {
        setIsGenerating(false);
      }
    };
    
    generateAllOptions();
  }, [answers]);
  
  // Animation sequence
  useEffect(() => {
    if (stage === 'animating') {
      const steps = [
        () => setAnimationStep(1), // Axes
        () => setTimeout(() => setAnimationStep(2), 500), // Alternatives
        () => setTimeout(() => setAnimationStep(3), 1000), // User dot
        () => setTimeout(() => setAnimationStep(4), 1500), // Callout
        () => {
          // After animation completes, go to map-ready stage
          setTimeout(() => {
            setStage('map-ready');
          }, 500);
        },
      ];
      
      steps.forEach((step, idx) => {
        setTimeout(step, idx * 100);
      });
    }
  }, [stage]);
  
  const handleShowMe = () => {
    setStage('animating');
  };

  const handleMapNext = async () => {
    // Generate initial price reasoning when entering price stage
    const reasoning = await generatePriceReasoning(answers, pricePosition, alternatives);
    setPriceReasoning(reasoning);
    setStage('price');
  };

  const handlePriceChange = (value) => {
    if (!isValidPosition(value)) {
      console.warn('Invalid price position:', value);
      return;
    }
    setPricePosition(clampPosition(value));
    setPriceConfirmed(false); // Reset confirmation when changed
  };

  const handlePriceConfirm = async () => {
    setPriceConfirmed(true);
    // Generate AI reasoning for price position
    const reasoning = await generatePriceReasoning(answers, pricePosition, alternatives);
    setPriceReasoning(reasoning);
    setTimeout(() => setStage('service'), 500);
  };

  const handleServiceChange = (value) => {
    if (!isValidPosition(value)) {
      console.warn('Invalid service position:', value);
      return;
    }
    setServicePosition(clampPosition(value));
    setServiceConfirmed(false); // Reset confirmation when changed
  };

  const handleServiceConfirm = async () => {
    setServiceConfirmed(true);
    // Generate AI reasoning for service position
    const reasoning = await generateServiceReasoning(answers, servicePosition);
    setServiceReasoning(reasoning);
    setTimeout(() => setStage('specialization'), 500);
  };

  const handleSpecializationChange = (value) => {
    const validValues = ['broad', 'medium', 'niche'];
    if (!validValues.includes(value)) {
      console.warn('Invalid specialization value:', value);
      return;
    }
    setSpecialization(value);
  };

  const handleBackNavigation = () => {
    // Navigate back based on current stage
    if (stage === 'map-ready') {
      setStage('intro');
    } else if (stage === 'price') {
      setStage('map-ready');
    } else if (stage === 'service') {
      setStage('price');
    } else if (stage === 'specialization') {
      setStage('service');
    }
  };

  const handleComplete = async () => {
    if (isCompleting) return; // Prevent double-submission
    
    try {
      setIsCompleting(true);
      setError(null);
      
      // Extract primary alternatives from answers (simplified - could be enhanced with AI)
      const primaryAlternatives = ['DIY tools', 'Freelancers / cheap agencies', 'Full-service agencies'];
      
      const marketData = {
        price_position: clampPosition(pricePosition),
        service_position: clampPosition(servicePosition),
        specialisation_level: specialization,
        primary_alternatives: primaryAlternatives,
      };
      
      await onComplete(marketData);
    } catch (err) {
      console.error('Error completing market position:', err);
      setError('Failed to save your market position. Please try again.');
    } finally {
      setIsCompleting(false);
    }
  };

  // Get reasoning for price position
  const getPriceReasoning = () => {
    const offerText = answers.q2?.toLowerCase() || '';
    if (pricePosition < -1) {
      return offerText.includes('cheap') || offerText.includes('affordable') 
        ? "You mentioned your pricing is affordable or low-cost in your offer description."
        : "Based on your answers, we placed you in the more affordable range.";
    } else if (pricePosition > 1) {
      return offerText.includes('premium') || offerText.includes('expensive')
        ? "You mentioned premium or high-end pricing in your offer description."
        : "Based on your answers, we placed you in the more expensive range.";
    } else {
      return "Based on your offer description, we placed you around the middle of the price range.";
    }
  };

  // Get reasoning for service position
  const getServiceReasoning = () => {
    const offerText = answers.q2?.toLowerCase() || '';
    if (servicePosition < -1) {
      return offerText.includes('self-serve') || offerText.includes('tool') || offerText.includes('software')
        ? "You described your offer as a self-serve tool or software solution."
        : "Based on your answers, we placed you in the self-serve range.";
    } else if (servicePosition > 1) {
      return offerText.includes('done-for-you') || offerText.includes('full service') || offerText.includes('managed')
        ? "You described your offer as done-for-you or full-service."
        : "Based on your answers, we placed you in the high-support range.";
    } else {
      return "Based on your offer description, we placed you around the middle of the service level range.";
    }
  };
  
  // Get label for current position
  const getPositionLabel = () => {
    const priceLabel = pricePosition < -1 ? 'budget' : pricePosition > 1 ? 'premium' : 'mid-priced';
    const serviceLabel = servicePosition < -1 ? 'self-serve' : servicePosition > 1 ? 'high-touch' : 'mid-support';
    const specLabel = specialization === 'niche' ? 'niche' : specialization === 'broad' ? 'broad' : 'focused';
    
    return `${serviceLabel}, ${priceLabel}, ${specLabel}`;
  };
  
  // Render loading state while generating AI options
  if (stage === 'loading') {
    return (
      <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[60vh] animate-in fade-in duration-1000">
        <Loader2 className="animate-spin text-black mb-6" size={48} />
        <div className="text-center space-y-2">
          <p className="font-serif text-2xl italic">Analyzing your market position...</p>
          <p className="font-sans text-[10px] uppercase tracking-widest text-neutral-400">
            Generating personalized alternatives and options
          </p>
        </div>
      </div>
    );
  }
  
  // Render intro state
  if (stage === 'intro') {
    return (
      <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
        <div className="text-center space-y-8">
          <h1 className="font-serif text-5xl md:text-6xl text-black leading-tight">
            Here's how you compare in the market
          </h1>
          <p className="font-sans text-lg text-neutral-600 max-w-2xl mx-auto">
            Based on what you just told us, this is where you sit compared to common alternatives. You can adjust it.
          </p>
          <button
            onClick={handleShowMe}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20 mt-8"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">
                Show me
              </span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  // Render map and controls
  const userPixelPos = positionToPixels(pricePosition, servicePosition, 1.2);
  
  // Animated map view (during initial animation sequence)
  if (stage === 'animating') {
    return (
      <motion.div 
        className="w-full max-w-7xl mx-auto space-y-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid-large-anim" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="quadrant1-anim" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2-anim" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              <filter id="glow-anim">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-large-anim)" />
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1-anim)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2-anim)" />
            
            {/* Center lines - smooth drawing animation */}
            <motion.path
              d="M 80 350 L 720 350"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            />
            <motion.path
              d="M 400 80 L 400 620"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            />
            
            {/* Axis labels - smooth fade in with improved alignment */}
            <motion.g
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5, ease: "easeOut" }}
            >
              <text 
                x="80" 
                y="380" 
                fontSize="12" 
                fill="#1a1a1a" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                fontWeight="500" 
                letterSpacing="0.3px"
              >
                More affordable
              </text>
              <text 
                x="720" 
                y="380" 
                fontSize="12" 
                fill="#1a1a1a" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                fontWeight="500" 
                textAnchor="end" 
                letterSpacing="0.3px"
              >
                More expensive
              </text>
              <text 
                x="385" 
                y="65" 
                fontSize="12" 
                fill="#1a1a1a" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                fontWeight="500" 
                textAnchor="start" 
                letterSpacing="0.3px"
              >
                Done-for-you / high support
              </text>
              <text 
                x="385" 
                y="655" 
                fontSize="12" 
                fill="#1a1a1a" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                fontWeight="500" 
                textAnchor="start" 
                letterSpacing="0.3px"
              >
                Self-serve / DIY
              </text>
            </motion.g>
            
            {/* Alternatives - smooth staggered entrance with luxe styling */}
            {alternatives.map((alt, idx) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              return (
                <motion.g 
                  key={alt.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ 
                    delay: 0.8 + idx * 0.1,
                    duration: 0.5,
                    ease: [0.22, 1, 0.36, 1]
                  }}
                >
                  <circle 
                    cx={pos.x} 
                    cy={pos.y} 
                    r="7" 
                    fill="#8a8a8a" 
                    opacity="0.8"
                  />
                  <rect 
                    x={pos.x - 65} 
                    y={pos.y - 32} 
                    width="130" 
                    height="20" 
                    rx="6" 
                    fill="rgba(255,255,255,0.95)"
                    stroke="#e5e5e5"
                    strokeWidth="1"
                  />
                  <text 
                    x={pos.x} 
                    y={pos.y - 17} 
                    fontSize="10" 
                    fill="#4a4a4a" 
                    fontFamily="system-ui, -apple-system, sans-serif" 
                    textAnchor="middle" 
                    fontWeight="400"
                    letterSpacing="0.1px"
                  >
                    {alt.label}
                  </text>
                </motion.g>
              );
            })}
            
            {/* User dot - smooth entrance */}
            <motion.g
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                delay: 1.3,
                type: "spring",
                stiffness: 300,
                damping: 20
              }}
            >
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="18" 
                fill="#000" 
                filter="url(#glow-anim)"
              />
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="15" 
                fill="#000"
              />
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="12" 
                fill="#fff"
              />
              <motion.text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 0.4 }}
              >
                YOU
              </motion.text>
            </motion.g>
          </svg>
        </div>
      </motion.div>
    );
  }
  
  // Map-only view (after animation, before controls)
  if (stage === 'map-ready') {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-8">
        {/* Map Container - Bigger and more interactive */}
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              {/* Grid pattern */}
              <pattern id="grid-large" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              {/* Gradient for quadrants */}
              <linearGradient id="quadrant1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              {/* Glow effect for user dot */}
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            {/* Background grid */}
            <rect width="100%" height="100%" fill="url(#grid-large)" />
            
            {/* Quadrant backgrounds for visual zones */}
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2)" />
            
            {/* Center lines - static (already animated in previous stage) */}
            <path
              d="M 80 350 L 720 350"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
            />
            <path
              d="M 400 80 L 400 620"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
            />
            
            {/* Axis labels - improved alignment and luxe styling */}
            <text 
              x="80" 
              y="380" 
              fontSize="12" 
              fill="#1a1a1a" 
              fontFamily="system-ui, -apple-system, sans-serif" 
              fontWeight="500" 
              letterSpacing="0.3px"
            >
              More affordable
            </text>
            <text 
              x="720" 
              y="380" 
              fontSize="12" 
              fill="#1a1a1a" 
              fontFamily="system-ui, -apple-system, sans-serif" 
              fontWeight="500" 
              textAnchor="end" 
              letterSpacing="0.3px"
            >
              More expensive
            </text>
            {/* Vertical labels - properly aligned */}
            <text 
              x="385" 
              y="65" 
              fontSize="12" 
              fill="#1a1a1a" 
              fontFamily="system-ui, -apple-system, sans-serif" 
              fontWeight="500" 
              textAnchor="start" 
              letterSpacing="0.3px"
            >
              Done-for-you / high support
            </text>
            <text 
              x="385" 
              y="655" 
              fontSize="12" 
              fill="#1a1a1a" 
              fontFamily="system-ui, -apple-system, sans-serif" 
              fontWeight="500" 
              textAnchor="start" 
              letterSpacing="0.3px"
            >
              Self-serve / DIY
            </text>
            
            {/* Alternatives - luxe styling */}
            {alternatives.map((alt) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              const isHovered = hoveredAlternative === alt.id;
              return (
                <g 
                  key={alt.id}
                  onMouseEnter={() => setHoveredAlternative(alt.id)}
                  onMouseLeave={() => setHoveredAlternative(null)}
                  style={{ cursor: 'pointer' }}
                >
                  {/* Hover circle - subtle */}
                  {isHovered && (
                    <circle 
                      cx={pos.x} 
                      cy={pos.y} 
                      r="32" 
                      fill="#000" 
                      opacity="0.08"
                      style={{ transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)' }}
                    />
                  )}
                  {/* Alternative dot */}
                  <circle 
                    cx={pos.x} 
                    cy={pos.y} 
                    r={isHovered ? "9" : "7"} 
                    fill={isHovered ? "#2a2a2a" : "#8a8a8a"} 
                    opacity={isHovered ? "1" : "0.8"}
                    style={{ 
                      transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                    }}
                  />
                  {/* Label with background - premium styling */}
                  <rect 
                    x={pos.x - 65} 
                    y={isHovered ? pos.y - 34 : pos.y - 32} 
                    width="130" 
                    height={isHovered ? "22" : "20"} 
                    rx="6" 
                    fill={isHovered ? "#000" : "rgba(255,255,255,0.95)"}
                    stroke={isHovered ? "#000" : "#e5e5e5"}
                    strokeWidth={isHovered ? "1.5" : "1"}
                    style={{ transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)' }}
                  />
                  <text 
                    x={pos.x} 
                    y={isHovered ? pos.y - 19 : pos.y - 17} 
                    fontSize={isHovered ? "11" : "10"} 
                    fill={isHovered ? "#fff" : "#4a4a4a"} 
                    fontFamily="system-ui, -apple-system, sans-serif" 
                    textAnchor="middle" 
                    fontWeight={isHovered ? "500" : "400"}
                    letterSpacing={isHovered ? "0.2px" : "0.1px"}
                    style={{ transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)' }}
                  >
                    {alt.label}
                  </text>
                </g>
              );
            })}
            
            {/* User dot - static (already animated) */}
            <g>
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="18" 
                fill="#000" 
                filter="url(#glow)"
                style={{ cursor: 'grab' }}
              />
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="15" 
                fill="#000"
              />
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="12" 
                fill="#fff"
              />
              <text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
              >
                YOU
              </text>
            </g>
          </svg>
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex justify-between items-center">
          <button
            onClick={handleBackNavigation}
            className="group flex items-center space-x-2 font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
          >
            <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform duration-500" />
            <span>Back</span>
          </button>
          <button
            onClick={handleMapNext}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">Next</span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  // Render interactive map with controls overlay
  const renderMapWithControls = () => (
    <div className="w-full max-w-7xl mx-auto space-y-8">
      {/* Map Container - Always visible */}
      <div className="relative w-full" style={{ height: '600px' }} ref={mapRef}>
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 800 700"
          className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <pattern id="grid-interactive" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
            </pattern>
            <linearGradient id="quadrant1-int" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="quadrant2-int" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
            </linearGradient>
            <filter id="glow-int">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#grid-interactive)" />
          <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1-int)" />
          <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2-int)" />
          
          {/* Axes */}
          <path d="M 80 350 L 720 350" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
          <path d="M 400 80 L 400 620" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
          
          {/* Axis labels */}
          <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            More affordable
          </text>
          <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
            More expensive
          </text>
          <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            Done-for-you / high support
          </text>
          <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            Self-serve / DIY
          </text>
          
          {/* Alternatives */}
          {ALTERNATIVES.map((alt) => {
            const pos = positionToPixels(alt.x, alt.y, 1.2);
            const isHovered = hoveredAlternative === alt.id;
            return (
              <g 
                key={alt.id}
                onMouseEnter={() => setHoveredAlternative(alt.id)}
                onMouseLeave={() => setHoveredAlternative(null)}
                style={{ cursor: 'pointer' }}
              >
                {isHovered && (
                  <circle cx={pos.x} cy={pos.y} r="32" fill="#000" opacity="0.08" />
                )}
                <circle 
                  cx={pos.x} 
                  cy={pos.y} 
                  r={isHovered ? "9" : "7"} 
                  fill={isHovered ? "#2a2a2a" : "#8a8a8a"} 
                  opacity={isHovered ? "1" : "0.8"}
                />
                <rect 
                  x={pos.x - 65} 
                  y={isHovered ? pos.y - 34 : pos.y - 32} 
                  width="130" 
                  height={isHovered ? "22" : "20"} 
                  rx="6" 
                  fill={isHovered ? "#000" : "rgba(255,255,255,0.95)"}
                  stroke={isHovered ? "#000" : "#e5e5e5"}
                  strokeWidth={isHovered ? "1.5" : "1"}
                />
                <text 
                  x={pos.x} 
                  y={isHovered ? pos.y - 19 : pos.y - 17} 
                  fontSize={isHovered ? "11" : "10"} 
                  fill={isHovered ? "#fff" : "#4a4a4a"} 
                  fontFamily="system-ui" 
                  textAnchor="middle" 
                  fontWeight={isHovered ? "500" : "400"}
                >
                  {alt.label}
                </text>
              </g>
            );
          })}
          
          {/* User dot - ANIMATED when position changes */}
          <motion.g
            animate={{ 
              x: userPixelPos.x - 400, 
              y: userPixelPos.y - 350 
            }}
            transition={{ 
              type: "spring", 
              stiffness: 200, 
              damping: 25,
              duration: 0.6 
            }}
          >
            <circle 
              cx={400} 
              cy={350} 
              r="22" 
              fill="#000" 
              filter="url(#glow-int)"
            />
            <circle cx={400} cy={350} r="18" fill="#000" />
            <circle cx={400} cy={350} r="14" fill="#fff" />
            <text 
              x={400} 
              y={310} 
              fontSize="13" 
              fill="#000" 
              fontFamily="system-ui" 
              textAnchor="middle" 
              fontWeight="700"
              letterSpacing="1.5px"
            >
              YOU
            </text>
          </motion.g>
        </svg>
      </div>

      {/* Controls overlay - Changes based on stage */}
      <AnimatePresence mode="wait">
        {stage === 'price' && (
          <motion.div
            key="price"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center justify-center min-h-[60vh] space-y-6 w-full max-w-4xl mx-auto"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg w-full">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How does your pricing compare to most alternatives?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {PRICE_OPTIONS.map((option, idx) => (
                  <motion.button
                    key={option.value}
                    onClick={() => handlePriceChange(option.value)}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05, type: "spring", stiffness: 200 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      pricePosition === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-sm text-neutral-600">
                  <span className="font-bold">Why we chose this:</span> {priceReasoning || 'Based on your offer description, we placed you at this price point relative to typical alternatives in your market.'}
                </p>
              </div>
              
              <div className="flex justify-center pt-2">
                <button
                  onClick={handlePriceConfirm}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Confirm & Continue</span>
                    <Check size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
        
        {stage === 'service' && (
          <motion.div
            key="service"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How hands-on are you compared to alternatives?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {serviceOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleServiceChange(option.value)}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      servicePosition === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-sm text-neutral-600">
                  <span className="font-bold">Why we chose this:</span> {serviceReasoning || 'Based on your offer description, we placed you at this service level relative to typical alternatives in your market.'}
                </p>
              </div>
              
              <div className="flex justify-center pt-2">
                <button
                  onClick={handleServiceConfirm}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Confirm & Continue</span>
                    <Check size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
        
        {stage === 'specialization' && (
          <motion.div
            key="specialization"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How specialised is your offer?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {specializationOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSpecializationChange(option.value)}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      specialization === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-base text-neutral-800">
                  <span className="font-bold">Got it — we'll treat you as a </span>
                  <span className="font-bold text-black">{getPositionLabel()}</span>
                  <span className="font-bold"> option.</span>
                </p>
              </div>
              
              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={handleBackNavigation}
                  className="group flex items-center space-x-2 font-sans text-xs font-bold uppercase tracking-widest text-neutral-500 hover:text-black transition-colors"
                >
                  <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform duration-500" />
                  <span>Back</span>
                </button>
                <button
                  onClick={handleComplete}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Complete</span>
                    <ArrowRight size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  // Render the appropriate stage
  if (stage === 'intro') {
    return (
      <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
        <div className="text-center space-y-8">
          <h1 className="font-serif text-5xl md:text-6xl text-black leading-tight">
            Here's how you compare in the market
          </h1>
          <p className="font-sans text-lg text-neutral-600 max-w-2xl mx-auto">
            Based on what you just told us, this is where you sit compared to common alternatives. You can adjust it.
          </p>
          <button
            onClick={handleShowMe}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20 mt-8"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">
                Show me
              </span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  if (stage === 'animating') {
    return (
      <motion.div 
        className="w-full max-w-7xl mx-auto space-y-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid-large-anim" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="quadrant1-anim" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2-anim" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              <filter id="glow-anim">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-large-anim)" />
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1-anim)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2-anim)" />
            
            <motion.path
              d="M 80 350 L 720 350"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            />
            <motion.path
              d="M 400 80 L 400 620"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            />
            
            <motion.g
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5, ease: "easeOut" }}
            >
              <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                More affordable
              </text>
              <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
                More expensive
              </text>
              <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                Done-for-you / high support
              </text>
              <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                Self-serve / DIY
              </text>
            </motion.g>
            
            {ALTERNATIVES.map((alt, idx) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              return (
                <motion.g 
                  key={alt.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ 
                    delay: 0.8 + idx * 0.1,
                    duration: 0.5,
                    ease: [0.22, 1, 0.36, 1]
                  }}
                >
                  <circle cx={pos.x} cy={pos.y} r="7" fill="#8a8a8a" opacity="0.8" />
                  <rect 
                    x={pos.x - 65} 
                    y={pos.y - 32} 
                    width="130" 
                    height="20" 
                    rx="6" 
                    fill="rgba(255,255,255,0.95)"
                    stroke="#e5e5e5"
                    strokeWidth="1"
                  />
                  <text 
                    x={pos.x} 
                    y={pos.y - 17} 
                    fontSize="10" 
                    fill="#4a4a4a" 
                    fontFamily="system-ui" 
                    textAnchor="middle" 
                    fontWeight="400"
                  >
                    {alt.label}
                  </text>
                </motion.g>
              );
            })}
            
            <motion.g
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                delay: 1.3,
                type: "spring",
                stiffness: 300,
                damping: 20
              }}
            >
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="18" fill="#000" filter="url(#glow-anim)" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="15" fill="#000" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="12" fill="#fff" />
              <motion.text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 0.4 }}
              >
                YOU
              </motion.text>
            </motion.g>
          </svg>
        </div>
      </motion.div>
    );
  }
  
  if (stage === 'map-ready') {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-8">
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid-large" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="quadrant1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-large)" />
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2)" />
            
            <path d="M 80 350 L 720 350" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
            <path d="M 400 80 L 400 620" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
            
            <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              More affordable
            </text>
            <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
              More expensive
            </text>
            <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              Done-for-you / high support
            </text>
            <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              Self-serve / DIY
            </text>
            
            {ALTERNATIVES.map((alt) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              const isHovered = hoveredAlternative === alt.id;
              return (
                <g 
                  key={alt.id}
                  onMouseEnter={() => setHoveredAlternative(alt.id)}
                  onMouseLeave={() => setHoveredAlternative(null)}
                  style={{ cursor: 'pointer' }}
                >
                  {isHovered && (
                    <circle cx={pos.x} cy={pos.y} r="32" fill="#000" opacity="0.08" />
                  )}
                  <circle 
                    cx={pos.x} 
                    cy={pos.y} 
                    r={isHovered ? "9" : "7"} 
                    fill={isHovered ? "#2a2a2a" : "#8a8a8a"} 
                    opacity={isHovered ? "1" : "0.8"}
                  />
                  <rect 
                    x={pos.x - 65} 
                    y={isHovered ? pos.y - 34 : pos.y - 32} 
                    width="130" 
                    height={isHovered ? "22" : "20"} 
                    rx="6" 
                    fill={isHovered ? "#000" : "rgba(255,255,255,0.95)"}
                    stroke={isHovered ? "#000" : "#e5e5e5"}
                    strokeWidth={isHovered ? "1.5" : "1"}
                  />
                  <text 
                    x={pos.x} 
                    y={isHovered ? pos.y - 19 : pos.y - 17} 
                    fontSize={isHovered ? "11" : "10"} 
                    fill={isHovered ? "#fff" : "#4a4a4a"} 
                    fontFamily="system-ui" 
                    textAnchor="middle" 
                    fontWeight={isHovered ? "500" : "400"}
                  >
                    {alt.label}
                  </text>
                </g>
              );
            })}
            
            <g>
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="18" fill="#000" filter="url(#glow)" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="15" fill="#000" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="12" fill="#fff" />
              <text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
              >
                YOU
              </text>
            </g>
          </svg>
        </div>
        
        <div className="flex justify-center">
          <button
            onClick={handleMapNext}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">Next</span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  // For price, service, and specialization stages
  if (stage === 'price' || stage === 'service' || stage === 'specialization') {
    return renderMapWithControls();
  }
  
  return null;
};

MarketPositionSnapshot.propTypes = {
  answers: PropTypes.object.isRequired,
  onComplete: PropTypes.func.isRequired,
  onBack: PropTypes.func
};

export default MarketPositionSnapshot; 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="15" 
                fill="#000"
              />
              <circle 
                cx={userPixelPos.x} 
                cy={userPixelPos.y} 
                r="12" 
                fill="#fff"
              />
              <text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui, -apple-system, sans-serif" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
              >
                YOU
              </text>
            </g>
          </svg>
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex justify-between items-center">
          <button
            onClick={handleBackNavigation}
            className="group flex items-center space-x-2 font-sans text-[10px] font-bold uppercase tracking-widest border-b border-transparent hover:border-black transition-all duration-500 pb-1 text-neutral-400 hover:text-black"
          >
            <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform duration-500" />
            <span>Back</span>
          </button>
          <button
            onClick={handleMapNext}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">Next</span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  // Render interactive map with controls overlay
  const renderMapWithControls = () => (
    <div className="w-full max-w-7xl mx-auto space-y-8">
      {/* Map Container - Always visible */}
      <div className="relative w-full" style={{ height: '600px' }} ref={mapRef}>
        <svg
          width="100%"
          height="100%"
          viewBox="0 0 800 700"
          className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <pattern id="grid-interactive" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
            </pattern>
            <linearGradient id="quadrant1-int" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
            </linearGradient>
            <linearGradient id="quadrant2-int" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
              <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
            </linearGradient>
            <filter id="glow-int">
              <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <rect width="100%" height="100%" fill="url(#grid-interactive)" />
          <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1-int)" />
          <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2-int)" />
          
          {/* Axes */}
          <path d="M 80 350 L 720 350" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
          <path d="M 400 80 L 400 620" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
          
          {/* Axis labels */}
          <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            More affordable
          </text>
          <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
            More expensive
          </text>
          <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            Done-for-you / high support
          </text>
          <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
            Self-serve / DIY
          </text>
          
          {/* Alternatives */}
          {ALTERNATIVES.map((alt) => {
            const pos = positionToPixels(alt.x, alt.y, 1.2);
            const isHovered = hoveredAlternative === alt.id;
            return (
              <g 
                key={alt.id}
                onMouseEnter={() => setHoveredAlternative(alt.id)}
                onMouseLeave={() => setHoveredAlternative(null)}
                style={{ cursor: 'pointer' }}
              >
                {isHovered && (
                  <circle cx={pos.x} cy={pos.y} r="32" fill="#000" opacity="0.08" />
                )}
                <circle 
                  cx={pos.x} 
                  cy={pos.y} 
                  r={isHovered ? "9" : "7"} 
                  fill={isHovered ? "#2a2a2a" : "#8a8a8a"} 
                  opacity={isHovered ? "1" : "0.8"}
                />
                <rect 
                  x={pos.x - 65} 
                  y={isHovered ? pos.y - 34 : pos.y - 32} 
                  width="130" 
                  height={isHovered ? "22" : "20"} 
                  rx="6" 
                  fill={isHovered ? "#000" : "rgba(255,255,255,0.95)"}
                  stroke={isHovered ? "#000" : "#e5e5e5"}
                  strokeWidth={isHovered ? "1.5" : "1"}
                />
                <text 
                  x={pos.x} 
                  y={isHovered ? pos.y - 19 : pos.y - 17} 
                  fontSize={isHovered ? "11" : "10"} 
                  fill={isHovered ? "#fff" : "#4a4a4a"} 
                  fontFamily="system-ui" 
                  textAnchor="middle" 
                  fontWeight={isHovered ? "500" : "400"}
                >
                  {alt.label}
                </text>
              </g>
            );
          })}
          
          {/* User dot - ANIMATED when position changes */}
          <motion.g
            animate={{ 
              x: userPixelPos.x - 400, 
              y: userPixelPos.y - 350 
            }}
            transition={{ 
              type: "spring", 
              stiffness: 200, 
              damping: 25,
              duration: 0.6 
            }}
          >
            <circle 
              cx={400} 
              cy={350} 
              r="22" 
              fill="#000" 
              filter="url(#glow-int)"
            />
            <circle cx={400} cy={350} r="18" fill="#000" />
            <circle cx={400} cy={350} r="14" fill="#fff" />
            <text 
              x={400} 
              y={310} 
              fontSize="13" 
              fill="#000" 
              fontFamily="system-ui" 
              textAnchor="middle" 
              fontWeight="700"
              letterSpacing="1.5px"
            >
              YOU
            </text>
          </motion.g>
        </svg>
      </div>

      {/* Controls overlay - Changes based on stage */}
      <AnimatePresence mode="wait">
        {stage === 'price' && (
          <motion.div
            key="price"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="flex flex-col items-center justify-center min-h-[60vh] space-y-6 w-full max-w-4xl mx-auto"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg w-full">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How does your pricing compare to most alternatives?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {PRICE_OPTIONS.map((option, idx) => (
                  <motion.button
                    key={option.value}
                    onClick={() => handlePriceChange(option.value)}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05, type: "spring", stiffness: 200 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      pricePosition === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </motion.button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-sm text-neutral-600">
                  <span className="font-bold">Why we chose this:</span> {priceReasoning || 'Based on your offer description, we placed you at this price point relative to typical alternatives in your market.'}
                </p>
              </div>
              
              <div className="flex justify-center pt-2">
                <button
                  onClick={handlePriceConfirm}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Confirm & Continue</span>
                    <Check size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
        
        {stage === 'service' && (
          <motion.div
            key="service"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How hands-on are you compared to alternatives?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {serviceOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleServiceChange(option.value)}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      servicePosition === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-sm text-neutral-600">
                  <span className="font-bold">Why we chose this:</span> {serviceReasoning || 'Based on your offer description, we placed you at this service level relative to typical alternatives in your market.'}
                </p>
              </div>
              
              <div className="flex justify-center pt-2">
                <button
                  onClick={handleServiceConfirm}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Confirm & Continue</span>
                    <Check size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
        
        {stage === 'specialization' && (
          <motion.div
            key="specialization"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4 }}
            className="space-y-6"
          >
            <div className="bg-white border-2 border-neutral-300 rounded-2xl p-8 space-y-6 shadow-lg">
              <label className="block font-sans text-base md:text-lg font-bold uppercase tracking-widest text-neutral-800 text-center">
                How specialised is your offer?
              </label>
              
              <div className="flex flex-wrap gap-3 justify-center">
                {specializationOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSpecializationChange(option.value)}
                    className={`px-6 py-3 rounded-lg border-2 transition-all font-sans text-sm font-medium ${
                      specialization === option.value
                        ? 'bg-black text-white border-black'
                        : 'bg-white text-neutral-700 border-neutral-300 hover:border-black'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
              
              <div className="text-center">
                <p className="font-sans text-base text-neutral-800">
                  <span className="font-bold">Got it — we'll treat you as a </span>
                  <span className="font-bold text-black">{getPositionLabel()}</span>
                  <span className="font-bold"> option.</span>
                </p>
              </div>
              
              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={handleBackNavigation}
                  className="group flex items-center space-x-2 font-sans text-xs font-bold uppercase tracking-widest text-neutral-500 hover:text-black transition-colors"
                >
                  <ChevronLeft size={14} className="group-hover:-translate-x-1 transition-transform duration-500" />
                  <span>Back</span>
                </button>
                <button
                  onClick={handleComplete}
                  className="group relative bg-black text-white px-10 py-4 overflow-hidden transition-all duration-500 hover:shadow-xl"
                >
                  <div className="relative z-10 flex items-center space-x-2">
                    <span className="font-sans text-xs font-bold tracking-widest uppercase">Complete</span>
                    <ArrowRight size={14} />
                  </div>
                  <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  // Render the appropriate stage
  if (stage === 'intro') {
    return (
      <div className="w-full max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-12 duration-1000">
        <div className="text-center space-y-8">
          <h1 className="font-serif text-5xl md:text-6xl text-black leading-tight">
            Here's how you compare in the market
          </h1>
          <p className="font-sans text-lg text-neutral-600 max-w-2xl mx-auto">
            Based on what you just told us, this is where you sit compared to common alternatives. You can adjust it.
          </p>
          <button
            onClick={handleShowMe}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20 mt-8"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">
                Show me
              </span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  if (stage === 'animating') {
    return (
      <motion.div 
        className="w-full max-w-7xl mx-auto space-y-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid-large-anim" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="quadrant1-anim" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2-anim" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              <filter id="glow-anim">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-large-anim)" />
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1-anim)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2-anim)" />
            
            <motion.path
              d="M 80 350 L 720 350"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            />
            <motion.path
              d="M 400 80 L 400 620"
              stroke="#000"
              strokeWidth="3"
              fill="none"
              opacity="0.8"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 0.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
            />
            
            <motion.g
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6, duration: 0.5, ease: "easeOut" }}
            >
              <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                More affordable
              </text>
              <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
                More expensive
              </text>
              <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                Done-for-you / high support
              </text>
              <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
                Self-serve / DIY
              </text>
            </motion.g>
            
            {ALTERNATIVES.map((alt, idx) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              return (
                <motion.g 
                  key={alt.id}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ 
                    delay: 0.8 + idx * 0.1,
                    duration: 0.5,
                    ease: [0.22, 1, 0.36, 1]
                  }}
                >
                  <circle cx={pos.x} cy={pos.y} r="7" fill="#8a8a8a" opacity="0.8" />
                  <rect 
                    x={pos.x - 65} 
                    y={pos.y - 32} 
                    width="130" 
                    height="20" 
                    rx="6" 
                    fill="rgba(255,255,255,0.95)"
                    stroke="#e5e5e5"
                    strokeWidth="1"
                  />
                  <text 
                    x={pos.x} 
                    y={pos.y - 17} 
                    fontSize="10" 
                    fill="#4a4a4a" 
                    fontFamily="system-ui" 
                    textAnchor="middle" 
                    fontWeight="400"
                  >
                    {alt.label}
                  </text>
                </motion.g>
              );
            })}
            
            <motion.g
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ 
                delay: 1.3,
                type: "spring",
                stiffness: 300,
                damping: 20
              }}
            >
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="18" fill="#000" filter="url(#glow-anim)" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="15" fill="#000" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="12" fill="#fff" />
              <motion.text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1.5, duration: 0.4 }}
              >
                YOU
              </motion.text>
            </motion.g>
          </svg>
        </div>
      </motion.div>
    );
  }
  
  if (stage === 'map-ready') {
    return (
      <div className="w-full max-w-7xl mx-auto space-y-8">
        <div className="relative w-full" style={{ height: '700px' }} ref={mapRef}>
          <svg
            width="100%"
            height="100%"
            viewBox="0 0 800 700"
            className="border-2 border-neutral-300 rounded-3xl bg-gradient-to-br from-white via-neutral-50 to-white shadow-2xl"
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid-large" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8e8e8" strokeWidth="0.5" />
              </pattern>
              <linearGradient id="quadrant1" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f0f9ff" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#e0f2fe" stopOpacity="0.1" />
              </linearGradient>
              <linearGradient id="quadrant2" x1="100%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor="#fef3c7" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#fde68a" stopOpacity="0.1" />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            
            <rect width="100%" height="100%" fill="url(#grid-large)" />
            <rect x="400" y="0" width="400" height="350" fill="url(#quadrant1)" />
            <rect x="0" y="0" width="400" height="350" fill="url(#quadrant2)" />
            
            <path d="M 80 350 L 720 350" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
            <path d="M 400 80 L 400 620" stroke="#000" strokeWidth="3" fill="none" opacity="0.8" />
            
            <text x="80" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              More affordable
            </text>
            <text x="720" y="380" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500" textAnchor="end">
              More expensive
            </text>
            <text x="385" y="65" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              Done-for-you / high support
            </text>
            <text x="385" y="655" fontSize="12" fill="#1a1a1a" fontFamily="system-ui" fontWeight="500">
              Self-serve / DIY
            </text>
            
            {ALTERNATIVES.map((alt) => {
              const pos = positionToPixels(alt.x, alt.y, 1.2);
              const isHovered = hoveredAlternative === alt.id;
              return (
                <g 
                  key={alt.id}
                  onMouseEnter={() => setHoveredAlternative(alt.id)}
                  onMouseLeave={() => setHoveredAlternative(null)}
                  style={{ cursor: 'pointer' }}
                >
                  {isHovered && (
                    <circle cx={pos.x} cy={pos.y} r="32" fill="#000" opacity="0.08" />
                  )}
                  <circle 
                    cx={pos.x} 
                    cy={pos.y} 
                    r={isHovered ? "9" : "7"} 
                    fill={isHovered ? "#2a2a2a" : "#8a8a8a"} 
                    opacity={isHovered ? "1" : "0.8"}
                  />
                  <rect 
                    x={pos.x - 65} 
                    y={isHovered ? pos.y - 34 : pos.y - 32} 
                    width="130" 
                    height={isHovered ? "22" : "20"} 
                    rx="6" 
                    fill={isHovered ? "#000" : "rgba(255,255,255,0.95)"}
                    stroke={isHovered ? "#000" : "#e5e5e5"}
                    strokeWidth={isHovered ? "1.5" : "1"}
                  />
                  <text 
                    x={pos.x} 
                    y={isHovered ? pos.y - 19 : pos.y - 17} 
                    fontSize={isHovered ? "11" : "10"} 
                    fill={isHovered ? "#fff" : "#4a4a4a"} 
                    fontFamily="system-ui" 
                    textAnchor="middle" 
                    fontWeight={isHovered ? "500" : "400"}
                  >
                    {alt.label}
                  </text>
                </g>
              );
            })}
            
            <g>
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="18" fill="#000" filter="url(#glow)" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="15" fill="#000" />
              <circle cx={userPixelPos.x} cy={userPixelPos.y} r="12" fill="#fff" />
              <text 
                x={userPixelPos.x} 
                y={userPixelPos.y - 35} 
                fontSize="12" 
                fill="#000" 
                fontFamily="system-ui" 
                textAnchor="middle" 
                fontWeight="600"
                letterSpacing="1.5px"
              >
                YOU
              </text>
            </g>
          </svg>
        </div>
        
        <div className="flex justify-center">
          <button
            onClick={handleMapNext}
            className="group relative bg-black text-white px-16 py-6 overflow-hidden transition-all duration-500 hover:shadow-2xl hover:shadow-neutral-500/20"
          >
            <div className="relative z-10 flex items-center space-x-4">
              <span className="font-sans text-xs font-bold tracking-widest uppercase">Next</span>
              <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform duration-500" />
            </div>
            <div className="absolute inset-0 bg-neutral-800 transform translate-y-full group-hover:translate-y-0 transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]"></div>
          </button>
        </div>
      </div>
    );
  }
  
  // For price, service, and specialization stages
  if (stage === 'price' || stage === 'service' || stage === 'specialization') {
    return renderMapWithControls();
  }
  
  return null;
};

MarketPositionSnapshot.propTypes = {
  answers: PropTypes.object.isRequired,
  onComplete: PropTypes.func.isRequired,
  onBack: PropTypes.func
};

export default MarketPositionSnapshot;
