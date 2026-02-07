import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, ArrowLeft, Package, Plus, X, AlertCircle, DollarSign } from 'lucide-react'
import useOnboardingStore from '../../store/onboardingStore'

const productTypes = [
  { value: 'saas', label: 'SaaS Product', icon: '💻' },
  { value: 'service', label: 'Service / Agency', icon: '🤝' },
  { value: 'hybrid', label: 'Hybrid (Software + Service)', icon: '⚡' },
  { value: 'marketplace', label: 'Marketplace', icon: '🏪' },
  { value: 'other', label: 'Other', icon: '📦' },
]

const userRoles = [
  { value: 'founder', label: 'Founder / CEO' },
  { value: 'marketer', label: 'Marketing' },
  { value: 'sales', label: 'Sales' },
  { value: 'ops', label: 'Operations' },
  { value: 'developer', label: 'Developer / Engineering' },
  { value: 'finance', label: 'Finance' },
  { value: 'product', label: 'Product' },
  { value: 'other', label: 'Other' },
]

const pricingModels = [
  { value: 'one-time', label: 'One-time fee', desc: 'Single purchase' },
  { value: 'monthly', label: 'Monthly subscription', desc: 'Recurring' },
  { value: 'usage-based', label: 'Usage-based', desc: 'Pay per use' },
  { value: 'hybrid', label: 'Hybrid', desc: 'Base + usage' },
]

const StepProduct = () => {
  const navigate = useNavigate()
  const { product, updateProduct, addTier, removeTier, nextStep, prevStep } = useOnboardingStore()
  
  const [form, setForm] = useState({
    name: product.name || '',
    type: product.type || '',
    typeOther: product.typeOther || '',
    usedBy: product.usedBy || [],
    mainJob: product.mainJob || '',
    pricingModel: product.pricingModel || '',
    priceRange: product.priceRange || '',
    hasTiers: product.hasTiers || false,
  })
  
  const [tiers, setTiers] = useState(product.tiers || [])
  const [newTier, setNewTier] = useState({ name: '', forWho: '', price: '' })
  const [errors, setErrors] = useState({})

  // Sync to store
  useEffect(() => {
    const debounce = setTimeout(() => {
      updateProduct({ ...form, tiers })
    }, 500)
    return () => clearTimeout(debounce)
  }, [form, tiers])

  const updateField = (field, value) => {
    setForm(prev => ({ ...prev, [field]: value }))
    setErrors(prev => ({ ...prev, [field]: null }))
  }

  const toggleRole = (role) => {
    const newRoles = form.usedBy.includes(role)
      ? form.usedBy.filter(r => r !== role)
      : [...form.usedBy, role]
    updateField('usedBy', newRoles)
  }

  const handleAddTier = () => {
    if (newTier.name && newTier.price) {
      setTiers([...tiers, { ...newTier, id: Date.now() }])
      setNewTier({ name: '', forWho: '', price: '' })
    }
  }

  const handleRemoveTier = (id) => {
    setTiers(tiers.filter(t => t.id !== id))
  }

  const isValid = form.name && form.type && form.usedBy.length > 0 && form.mainJob && form.pricingModel

  const handleNext = () => {
    const newErrors = {}
    if (!form.name) newErrors.name = 'Product name is required'
    if (!form.type) newErrors.type = 'Please select a product type'
    if (form.usedBy.length === 0) newErrors.usedBy = 'Select at least one user role'
    if (!form.mainJob) newErrors.mainJob = 'Please describe the main job'
    if (!form.pricingModel) newErrors.pricingModel = 'Please select a pricing model'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    updateProduct({ ...form, tiers })
    nextStep()
    navigate('/onboarding/market')
  }

  const handleBack = () => {
    prevStep()
    navigate('/onboarding/company')
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
              <Package className="w-6 h-6 text-amber-400" />
            </div>
            <span className="text-xs uppercase tracking-[0.2em] text-amber-400/60">
              Step 3 of 8 · Product & Offer
            </span>
          </div>
          <h1 className="text-3xl md:text-4xl font-light text-white mb-3">
            What exactly are we <span className="italic text-amber-200">selling?</span>
          </h1>
          <p className="text-white/40 max-w-xl">
            Define your product, who uses it, and how you charge for it.
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
          {/* Form */}
          <div className="lg:col-span-3 space-y-8">
            {/* Product Identity */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="space-y-6"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40">
                Product Identity
              </h3>

              {/* Product Name */}
              <div>
                <label className="block text-sm text-white/60 mb-2">Product Name</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => updateField('name', e.target.value)}
                  placeholder="e.g., Acme Analytics"
                  className="w-full bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                />
                {errors.name && (
                  <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {errors.name}
                  </p>
                )}
              </div>

              {/* Product Type */}
              <div>
                <label className="block text-sm text-white/60 mb-3">What type of thing is it?</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {productTypes.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => updateField('type', type.value)}
                      className={`
                        p-4 rounded-xl border text-left transition-all
                        ${form.type === type.value
                          ? 'bg-amber-500/20 border-amber-500/50 text-white'
                          : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                        }
                      `}
                    >
                      <span className="text-xl mb-2 block">{type.icon}</span>
                      <span className="text-sm">{type.label}</span>
                    </button>
                  ))}
                </div>
                {form.type === 'other' && (
                  <input
                    type="text"
                    value={form.typeOther}
                    onChange={(e) => updateField('typeOther', e.target.value)}
                    placeholder="Describe your product type"
                    className="w-full mt-3 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                  />
                )}
                {errors.type && (
                  <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {errors.type}
                  </p>
                )}
              </div>
            </motion.div>

            {/* Who uses it */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="space-y-6"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40">
                Who Uses It
              </h3>

              <div>
                <label className="block text-sm text-white/60 mb-3">Who uses this day to day?</label>
                <div className="flex flex-wrap gap-2">
                  {userRoles.map((role) => (
                    <button
                      key={role.value}
                      onClick={() => toggleRole(role.value)}
                      className={`
                        px-4 py-2 rounded-full border text-sm transition-all
                        ${form.usedBy.includes(role.value)
                          ? 'bg-amber-500/20 border-amber-500/50 text-white'
                          : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                        }
                      `}
                    >
                      {role.label}
                    </button>
                  ))}
                </div>
                {errors.usedBy && (
                  <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {errors.usedBy}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  What's the main job your product does for them?
                </label>
                <textarea
                  value={form.mainJob}
                  onChange={(e) => updateField('mainJob', e.target.value)}
                  placeholder="e.g., 'Automates monthly financial reporting' or 'Gets more booked calls from website traffic'"
                  className="w-full h-28 bg-zinc-900/50 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 resize-none focus:outline-none focus:border-amber-500/50 transition-colors"
                />
                {errors.mainJob && (
                  <p className="text-red-400 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {errors.mainJob}
                  </p>
                )}
              </div>
            </motion.div>

            {/* Pricing */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="space-y-6"
            >
              <h3 className="text-sm uppercase tracking-[0.15em] text-white/40">
                The Offer
              </h3>

              <div>
                <label className="block text-sm text-white/60 mb-3">How do you charge for it?</label>
                <div className="grid grid-cols-2 gap-2">
                  {pricingModels.map((model) => (
                    <button
                      key={model.value}
                      onClick={() => updateField('pricingModel', model.value)}
                      className={`
                        p-4 rounded-xl border text-left transition-all
                        ${form.pricingModel === model.value
                          ? 'bg-amber-500/20 border-amber-500/50 text-white'
                          : 'bg-zinc-900/50 border-white/10 text-white/60 hover:border-white/20'
                        }
                      `}
                    >
                      <div className="font-medium text-sm">{model.label}</div>
                      <div className="text-xs text-white/40 mt-1">{model.desc}</div>
                    </button>
                  ))}
                </div>
                {errors.pricingModel && (
                  <p className="text-red-400 text-sm mt-2 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" /> {errors.pricingModel}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm text-white/60 mb-2">
                  Typical price range (per month or per project)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                  <input
                    type="text"
                    value={form.priceRange}
                    onChange={(e) => updateField('priceRange', e.target.value)}
                    placeholder="e.g., 300-800"
                    className="w-full bg-zinc-900/50 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50 transition-colors"
                  />
                </div>
              </div>

              {/* Tiers */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <label className="block text-sm text-white/60">
                    Do you have different plans or tiers?
                  </label>
                  <button
                    onClick={() => updateField('hasTiers', !form.hasTiers)}
                    className={`
                      w-12 h-6 rounded-full transition-colors relative
                      ${form.hasTiers ? 'bg-amber-500' : 'bg-white/10'}
                    `}
                  >
                    <div className={`
                      w-5 h-5 rounded-full bg-white absolute top-0.5 transition-all
                      ${form.hasTiers ? 'left-6' : 'left-0.5'}
                    `} />
                  </button>
                </div>

                {form.hasTiers && (
                  <div className="space-y-3 mt-4">
                    {tiers.map((tier) => (
                      <div key={tier.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
                        <div className="flex-1">
                          <span className="text-white text-sm font-medium">{tier.name}</span>
                          {tier.forWho && (
                            <span className="text-white/40 text-xs ml-2">for {tier.forWho}</span>
                          )}
                        </div>
                        <span className="text-amber-400 text-sm">${tier.price}</span>
                        <button
                          onClick={() => handleRemoveTier(tier.id)}
                          className="text-white/30 hover:text-red-400 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ))}

                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newTier.name}
                        onChange={(e) => setNewTier({ ...newTier, name: e.target.value })}
                        placeholder="Plan name"
                        className="flex-1 bg-zinc-900/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50"
                      />
                      <input
                        type="text"
                        value={newTier.forWho}
                        onChange={(e) => setNewTier({ ...newTier, forWho: e.target.value })}
                        placeholder="For who"
                        className="w-32 bg-zinc-900/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50"
                      />
                      <input
                        type="text"
                        value={newTier.price}
                        onChange={(e) => setNewTier({ ...newTier, price: e.target.value })}
                        placeholder="Price"
                        className="w-24 bg-zinc-900/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder:text-white/20 focus:outline-none focus:border-amber-500/50"
                      />
                      <button
                        onClick={handleAddTier}
                        className="p-2 bg-amber-500/20 hover:bg-amber-500/30 text-amber-400 rounded-lg transition-colors"
                      >
                        <Plus className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          {/* Preview */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="lg:col-span-2"
          >
            <div className="sticky top-6 p-6 bg-gradient-to-br from-zinc-900/80 to-zinc-900/40 border border-white/10 rounded-2xl">
              <h3 className="text-xs uppercase tracking-[0.2em] text-white/40 mb-4">
                Offer Snapshot
              </h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-xl font-light text-white">
                    {form.name || 'Product Name'}
                  </h4>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {form.type && (
                      <span className="px-3 py-1 bg-amber-500/10 text-amber-400/80 rounded-full text-xs">
                        {productTypes.find(t => t.value === form.type)?.label}
                      </span>
                    )}
                    {form.priceRange && (
                      <span className="px-3 py-1 bg-white/5 text-white/60 rounded-full text-xs">
                        ${form.priceRange}/mo
                      </span>
                    )}
                  </div>
                </div>

                {form.usedBy.length > 0 && (
                  <div>
                    <p className="text-xs text-white/30 mb-2">Used by</p>
                    <div className="flex flex-wrap gap-1">
                      {form.usedBy.map((role) => (
                        <span key={role} className="px-2 py-0.5 bg-white/5 rounded text-xs text-white/50">
                          {userRoles.find(r => r.value === role)?.label}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {form.mainJob && (
                  <div>
                    <p className="text-xs text-white/30 mb-2">Job</p>
                    <p className="text-sm text-white/60 italic">"{form.mainJob}"</p>
                  </div>
                )}

                {tiers.length > 0 && (
                  <div className="pt-4 border-t border-white/5">
                    <p className="text-xs text-white/30 mb-2">Tiers</p>
                    <div className="space-y-1">
                      {tiers.map((tier) => (
                        <div key={tier.id} className="flex justify-between text-sm">
                          <span className="text-white/60">{tier.name}</span>
                          <span className="text-amber-400">${tier.price}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Footer */}
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

export default StepProduct

