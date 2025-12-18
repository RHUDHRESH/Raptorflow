import React from 'react'
import { motion } from 'framer-motion'
import { Star } from 'lucide-react'

const TestimonialCard = ({ quote, author, role, company, delay }) => (
  <motion.div 
    className="bg-zinc-900/30 border border-white/5 p-12 backdrop-blur-sm relative group hover:border-accent/30 transition-colors duration-500"
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.6, delay }}
  >
    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-accent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    
    <div className="flex gap-1 mb-8 text-accent">
      {[...Array(5)].map((_, i) => (
        <Star key={i} size={12} fill="currentColor" />
      ))}
    </div>

    <blockquote className="font-serif text-2xl leading-relaxed mb-8 text-zinc-200 italic">
      "{quote}"
    </blockquote>

    <div className="flex items-center gap-4">
      <div className="w-12 h-12 bg-zinc-800 rounded-full flex items-center justify-center font-serif text-accent text-xl">
        {author.charAt(0)}
      </div>
      <div>
        <div className="text-sm uppercase tracking-widest font-medium text-white">{author}</div>
        <div className="text-xs text-zinc-500 uppercase tracking-wide mt-1">{role}, {company}</div>
      </div>
    </div>
  </motion.div>
)

const LuxuryTestimonials = () => {
  const testimonials = [
    {
      quote: "Raptorflow isn't just a tool; it's a design philosophy applied to marketing operations. It forced us to think clearer.",
      author: "Elena V.",
      role: "CMO",
      company: "Auralux"
    },
    {
      quote: "The visual clarity it brings to our strategy is unmatched. Finally, a dashboard that looks as good as our product.",
      author: "Marcus J.",
      role: "Founder",
      company: "Velvet Systems"
    },
    {
      quote: "It elevated our entire team's output. The editorial approach to planning resonates deeply with creative minds.",
      author: "Sarah L.",
      role: "Director",
      company: "Noir Mode"
    }
  ]

  return (
    <section className="bg-background py-32 relative">
      <div className="container mx-auto px-6">
        <motion.div 
          className="mb-20"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-center font-serif text-4xl md:text-5xl mb-4">Voices of Industry</h2>
          <p className="text-center text-zinc-500 uppercase tracking-widest text-xs">Trusted by the vanguard</p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {testimonials.map((t, i) => (
            <TestimonialCard key={i} {...t} delay={i * 0.2} />
          ))}
        </div>
      </div>
    </section>
  )
}

export default LuxuryTestimonials

