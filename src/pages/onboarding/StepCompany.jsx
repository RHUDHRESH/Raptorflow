import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Building2, Globe, Users, Rocket, MapPin, AlertCircle, Loader2 } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const employeeSizes = [
  { value: '1-10', label: '1-10', desc: 'Just starting' },
  { value: '11-50', label: '11-50', desc: 'Early stage' },
  { value: '51-200', label: '51-200', desc: 'Growing' },
  { value: '201-1000', label: '201-1000', desc: 'Scaling' },
  { value: '1000+', label: '1000+', desc: 'Enterprise' },
]

const stages = [
  { value: 'bootstrap', label: 'Bootstrap', desc: 'Self-funded' },
  { value: 'pre-seed', label: 'Pre-seed', desc: 'Early funding' },
  { value: 'seed', label: 'Seed', desc: 'Building PMF' },
  { value: 'series-a', label: 'Series A', desc: 'Scaling' },
  { value: 'series-b+', label: 'Series B+', desc: 'Growth stage' },
  { value: 'established-sme', label: 'SME', desc: 'Established' },
  { value: 'enterprise', label: 'Enterprise', desc: 'Large org' },
]

const industries = [
  'Software / SaaS',
  'Fintech',
  'E-commerce / Retail',
  'Healthcare / MedTech',
  'EdTech',
  'Manufacturing',
  'Professional Services',
  'Marketing / Advertising',
  'Real Estate / PropTech',
  'Logistics / Supply Chain',
  'Media / Entertainment',
  'Travel / Hospitality',
  'Other',
]

const StepCompany = () => {
  const navigate = useNavigate()
  const { company, updateCompany, setEnrichedData, nextStep, prevStep } = useOnboardingStore()
  
  const [form, setForm] = useState({
    name: company.name || '',
    website: company.website || '',
    country: company.country || 'India',
    city: company.city || '',
    employeeCount: company.employeeCount || '',
    industry: company.industry || '',
    industryOther: company.industryOther || '',
    stage: company.stage || '',
  })
  
  const [isEnriching, setIsEnriching] = useState(false)
  const [enrichmentDone, setEnrichmentDone] = useState(false)
  const [errors, setErrors] = useState({})

  // Trigger enrichment when website changes
  useEffect(() => {
    if (form.website && form.website.includes('.') && !enrichmentDone) {
      const timer = setTimeout(() => {
        // Simulate enrichment - in reality, this would call an API
        setIsEnriching(true)
        setTimeout(() => {
          setIsEnriching(false)
          setEnrichmentDone(true)
          // Mock enriched data
          setEnrichedData({
            techStack: ['Google Analytics', 'React', 'AWS'],
            linkedInUrl: `https://linkedin.com/company/${form.website.replace(/https?:\/\/|www\./g, '').split('.')[0]}`,
          })
        }, 1500)
      }, 1000)
      return () => clearTimeout(timer)
    }
  }, [form.website])

  // Sync to store
  useEffect(() => {
    const debounce = setTimeout(() => {
      updateCompany(form)
    }, 500)
    return () => clearTimeout(debounce)
  }, [form])

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  const isValid = form.name && form.website && form.employeeCount && form.industry && form.stage

  const handleNext = () => {
    const newErrors = {}
    if (!form.name) newErrors.name = 'Company name is required'
    if (!form.website) newErrors.website = 'Website is required'
    if (!form.employeeCount) newErrors.employeeCount = 'Please select company size'
    if (!form.industry) newErrors.industry = 'Please select an industry'
    if (form.industry === 'Other' && !form.industryOther) newErrors.industryOther = 'Please specify'
    if (!form.stage) newErrors.stage = 'Please select a stage'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    updateCompany(form)
    nextStep()
    navigate('/onboarding/product')
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/positioning')
  }

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col">
      <div className="flex-1 max-w-5xl mx-auto w-full px-6 py-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-amber-500/10 rounded-xl">
              <Building2 className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 2 of 8 · Company Context
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            Who are we doing this <span className="italic text-amber-200">for?</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Tell us about your company. We'll enrich this with additional data automatically.
          </p>
        </motion.div>

        {/* Two column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Form column */}
          <div className="lg:col-span-3 space-y-6">
            {/* Company Name */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <label className="block text-sm text-white/60 mb-2">Company Name</label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="Acme Corp"
                className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
              />
              {errors.name && (
                <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.name}
                </p>
              )}
            </motion.div>

            {/* Website */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <label className="block text-sm text-white/60 mb-2">Website</label>
              <div className="relative">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type="text"
                  value={form.website}
                  onChange={(e) => updateField('website', e.target.value)}
                  placeholder="acme.com"
                  className="w-full bg-zinc-900/50 border border-white/10 rounded-xl pl-11 pr-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                />
                {isEnriching && (
                  <div className="absolute right-4 top-1/2 -translate-y-1/2">
                    <Loader2 className="w-4 h-4 text-amber-400 animate-spin" />
                  </div>
                )}
              </div>
              {errors.website && (
                <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.website}
                </p>
              )}
              {enrichmentDone && (
                <p className="text-emerald-400/60 text-xs mt-1">
                  ✓ Company data enriched
                </p>
              )}
            </motion.div>

            {/* Location */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid grid-cols-2 gap-4"
            >
              <div>
                <label className="block text-sm text-white/60 mb-2">Country</label>
                <select
                  value={form.country}
                  onChange={(e) => updateField('country', e.target.value)}
                  className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-amber-500/50 transition-colors appearance-none"
                >
                  <option value="India">India</option>
                  <option value="United States">United States</option>
                  <option value="United Kingdom">United Kingdom</option>
                  <option value="Germany">Germany</option>
                  <option value="Singapore">Singapore</option>
                  <option value="Australia">Australia</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-white/60 mb-2">City</label>
                <input
                  type="text"
                  value={form.city}
                  onChange={(e) => updateField('city', e.target.value)}
                  placeholder="Bangalore"
                  className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                />
              </div>
            </motion.div>

            {/* Company Size */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
            >
              <label className="block text-sm text-white/60 mb-3">Company Size</label>
              <div className="grid grid-cols-5 gap-2">
                {employeeSizes.map((size) => (
                  <button
                    key={size.value}
                    onClick={() => updateField('employeeCount', size.value)}
                    className={`
                      p-3 rounded-xl border text-center transition-all
                      ${form.employeeCount === size.value
                        ? 'bg-amber-500/20 border-amber-500/50 text-white'
                        : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                      }
                    `}
                  >
                    <div className="font-medium text-sm">{size.label}</div>
                    <div className="text-xs text-white/40 mt-0.5">{size.desc}</div>
                  </button>
                ))}
              </div>
              {errors.employeeCount && (
                <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.employeeCount}
                </p>
              )}
            </motion.div>

            {/* Industry */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <label className="block text-sm text-white/60 mb-2">Industry</label>
              <select
                value={form.industry}
                onChange={(e) => updateField('industry', e.target.value)}
                className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-amber-500/50 transition-colors appearance-none"
              >
                <option value="">Select industry...</option>
                {industries.map((ind) => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
              {form.industry === 'Other' && (
                <input
                  type="text"
                  value={form.industryOther}
                  onChange={(e) => updateField('industryOther', e.target.value)}
                  placeholder="Specify your industry"
                  className="w-full mt-3 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                />
              )}
              {errors.industry && (
                <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.industry}
                </p>
              )}
            </motion.div>

            {/* Stage */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
            >
              <label className="block text-sm text-white/60 mb-3">Company Stage</label>
              <div className="flex flex-wrap gap-2">
                {stages.map((stage) => (
                  <button
                    key={stage.value}
                    onClick={() => updateField('stage', stage.value)}
                    className={`
                      px-4 py-2 rounded-full border text-sm transition-all
                      ${form.stage === stage.value
                        ? 'bg-amber-500/20 border-amber-500/50 text-white'
                        : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                      }
                    `}
                  >
                    {stage.label}
                  </button>
                ))}
              </div>
              {errors.stage && (
                <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {errors.stage}
                </p>
              )}
            </motion.div>
          </div>

          {/* Preview card column */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2"
          >
            <div className="sticky top-6 p-6 bg-gradient-to-br from-zinc-900/80 to-zinc-900/40 border border-white/10 rounded-2xl">
              <h3 className="text-xs uppercase tracking-[0.2em] text-white/40 mb-4">
                Company Card Preview
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-xl font-light text-white">
                    {form.name || 'Company Name'}
                  </h4>
                  {form.website && (
                    <p className="text-amber-400/80 text-sm">{form.website}</p>
                  )}
                </div>

                <div className="flex flex-wrap gap-2">
                  {form.industry && (
                    <span className="px-3 py-1 bg-white/5 rounded-full text-xs text-white/60">
                      {form.industry}
                    </span>
                  )}
                  {form.employeeCount && (
                    <span className="px-3 py-1 bg-white/5 rounded-full text-xs text-white/60">
                      <Users className="w-3 h-3 inline mr-1" />
                      {form.employeeCount} employees
                    </span>
                  )}
                  {form.stage && (
                    <span className="px-3 py-1 bg-white/5 rounded-full text-xs text-white/60">
                      <Rocket className="w-3 h-3 inline mr-1" />
                      {stages.find(s => s.value === form.stage)?.label}
                    </span>
                  )}
                </div>

                {(form.city || form.country) && (
                  <p className="text-white/40 text-sm flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    {[form.city, form.country].filter(Boolean).join(', ')}
                  </p>
                )}

                {enrichmentDone && (
                  <div className="pt-4 border-t border-white/5">
                    <p className="text-xs text-white/30 mb-2">Detected Tech Stack</p>
                    <div className="flex flex-wrap gap-1">
                      {company.enriched?.techStack?.map((tech, i) => (
                        <span key={i} className="px-2 py-0.5 bg-white/5 rounded text-xs text-white/50">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer navigation */}
      <div className="border-t border-white/5 bg-zinc-950/80 backdrop-blur-xl sticky bottom-0">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center gap-2 text-white/40 hover:text-white text-sm transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <button
            onClick={handleNext}
            disabled={!isValid}
            className={`
              flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all
              ${isValid
                ? 'bg-amber-500 hover:bg-amber-400 text-black'
                : 'bg-white/10 text-white/30 cursor-not-allowed'
              }
            `}
          >
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default StepCompany

