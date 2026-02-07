import React from 'react'
import { motion } from 'framer-motion'

const IntegrationGrid = () => {
  const integrations = [
    { name: "Notion", icon: "https://upload.wikimedia.org/wikipedia/commons/4/45/Notion_app_logo.png" },
    { name: "Google", icon: "https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg" },
    { name: "Slack", icon: "https://upload.wikimedia.org/wikipedia/commons/d/d5/Slack_icon_2019.svg" },
    { name: "HubSpot", icon: "https://upload.wikimedia.org/wikipedia/commons/1/15/HubSpot_Logo.png" },
    { name: "Stripe", icon: "https://upload.wikimedia.org/wikipedia/commons/b/ba/Stripe_Logo%2C_revised_2016.svg" },
    { name: "Intercom", icon: "https://upload.wikimedia.org/wikipedia/commons/8/87/Intercom_logo.svg" },
    { name: "Airtable", icon: "https://upload.wikimedia.org/wikipedia/commons/4/4b/Airtable_Logo.png" },
    { name: "Linear", icon: "https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Linear_Inc._Logo.svg/1200px-Linear_Inc._Logo.svg.png" }
  ]

  // Duplicate for marquee
  const marqueeItems = [...integrations, ...integrations]

  return (
    <section className="py-24 border-b border-line bg-canvas relative overflow-hidden">
      <div className="max-w-6xl mx-auto px-6 md:px-8 lg:px-12 relative z-10">
        <div className="text-center mb-16">
          <p className="text-[10px] uppercase tracking-[0.3em] text-charcoal/40 font-bold mb-4">
            The Ecosystem
          </p>
          <h2 className="font-serif text-3xl md:text-4xl text-charcoal">
            Connects with your<br />current brain.
          </h2>
        </div>

        <div className="relative">
            {/* Fade Masks */}
            <div className="absolute left-0 top-0 bottom-0 w-24 bg-gradient-to-r from-canvas to-transparent z-20 pointer-events-none"></div>
            <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-canvas to-transparent z-20 pointer-events-none"></div>

            <motion.div 
                className="flex gap-16 items-center whitespace-nowrap"
                animate={{ x: ["0%", "-50%"] }}
                transition={{ duration: 30, ease: "linear", repeat: Infinity }}
            >
                {marqueeItems.map((item, i) => (
                    <div key={i} className="flex-shrink-0 opacity-40 hover:opacity-100 transition-opacity duration-300 grayscale hover:grayscale-0">
                        {/* Using text placeholder if images fail, but img tags for logos */}
                        <div className="h-12 w-32 flex items-center justify-center">
                            {item.name === "Stripe" || item.name === "HubSpot" ? (
                                 <img src={item.icon} alt={item.name} className="h-8 object-contain" />
                            ) : (
                                <div className="flex items-center gap-2">
                                    <img src={item.icon} alt="" className="h-8 w-8 object-contain" onError={(e) => e.target.style.display = 'none'} />
                                    <span className="font-sans font-semibold text-xl">{item.name}</span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}
            </motion.div>
        </div>
      </div>
    </section>
  )
}

export default IntegrationGrid
