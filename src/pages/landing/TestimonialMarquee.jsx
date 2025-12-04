import React from 'react'
import { motion } from 'framer-motion'
import { Quote } from 'lucide-react'

// Featured testimonial cards - Masterclass style
const TestimonialMarquee = () => {
  const testimonials = [
    {
      quote: "Raptorflow gave me the clarity I'd been searching for. In one weekend, I had a battle plan that my entire team could rally behind.",
      name: "Arjun Mehta",
      title: "Founder & CEO",
      company: "Stackwise",
      initials: "AM"
    },
    {
      quote: "I've worked with McKinsey. I've worked with BCG. This is what strategy should feel like—actionable, clear, no bullshit.",
      name: "Priya Sharma",
      title: "Ex-Partner, BCG",
      company: "Now Building",
      initials: "PS"
    },
    {
      quote: "We went from 47 scattered ideas to 5 focused moves. Revenue up 34% in one quarter. The ROI is insane.",
      name: "Vikram Singh",
      title: "Co-founder",
      company: "Metric Labs",
      initials: "VS"
    },
  ]

  return (
    <section className="relative py-32 bg-black overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-zinc-950 to-black" />
      
      {/* Decorative lines */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        
        {/* Section header */}
        <div className="text-center mb-20">
          <motion.span
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-[10px] uppercase tracking-[0.4em] text-amber-400/60"
          >
            Testimonials
          </motion.span>
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="mt-6 text-3xl md:text-4xl font-light text-white"
          >
            Trusted by founders who
            <span className="italic font-normal text-amber-200"> ship</span>
          </motion.h2>
        </div>

        {/* Testimonial cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15 }}
              className="group relative"
            >
              <div className="relative p-8 bg-zinc-900/50 border border-white/[0.05] hover:border-white/[0.1] transition-all duration-500">
                
                {/* Quote icon */}
                <div className="mb-6">
                  <Quote className="w-8 h-8 text-amber-500/30" />
                </div>

                {/* Quote */}
                <blockquote className="text-white/70 text-lg font-light leading-relaxed mb-8">
                  "{testimonial.quote}"
                </blockquote>

                {/* Author */}
                <div className="flex items-center gap-4">
                  {/* Avatar */}
                  <div className="w-12 h-12 bg-gradient-to-br from-amber-500/20 to-amber-700/20 border border-amber-500/30 flex items-center justify-center">
                    <span className="text-amber-400 font-medium text-sm">{testimonial.initials}</span>
                  </div>
                  
                  <div>
                    <div className="text-white font-medium">{testimonial.name}</div>
                    <div className="text-white/40 text-sm">{testimonial.title}, {testimonial.company}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Stats bar */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.5 }}
          className="mt-20 flex flex-wrap justify-center gap-12 md:gap-20"
        >
          {[
            { value: '500+', label: 'Founders' },
            { value: '₹2.4Cr', label: 'Revenue Generated' },
            { value: '47%', label: 'Faster GTM' },
          ].map((stat, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl md:text-4xl font-light text-white">{stat.value}</div>
              <div className="text-[10px] uppercase tracking-[0.2em] text-white/40 mt-2">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}

export default TestimonialMarquee
