import React from 'react'
import { motion } from 'framer-motion'

const logos = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Google_2015_logo.svg/2560px-Google_2015_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/IBM_logo.svg/2560px-IBM_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Airbnb_Logo_B%C3%A9lo.svg/2560px-Airbnb_Logo_B%C3%A9lo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Microsoft_logo_%282012%29.svg/2560px-Microsoft_logo_%282012%29.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/2560px-Netflix_2015_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Amazon_logo.svg/2560px-Amazon_logo.svg.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Apple_logo_black.svg/1667px-Apple_logo_black.svg.png"
]

export const LogoCloud = () => {
    return (
        <section className="py-12 bg-white border-b border-neutral-100 overflow-hidden">
            <div className="mx-auto max-w-7xl px-6 mb-8 text-center">
                <p className="text-sm font-bold uppercase tracking-widest text-neutral-400">Trusted by innovative teams at</p>
            </div>

            <div className="relative flex overflow-hidden group">
                <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white to-transparent z-10" />
                <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white to-transparent z-10" />

                <motion.div
                    animate={{ x: ["0%", "-50%"] }}
                    transition={{ duration: 30, ease: "linear", repeat: Infinity }}
                    className="flex items-center gap-16 px-8 whitespace-nowrap"
                >
                    {[...logos, ...logos, ...logos, ...logos].map((logo, i) => (
                        <img
                            key={i}
                            src={logo}
                            alt="Partner Logo"
                            className="h-8 w-auto object-contain opacity-40 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-300"
                        />
                    ))}
                </motion.div>
            </div>
        </section>
    )
}
