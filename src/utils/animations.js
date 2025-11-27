export const pageTransition = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
}

export const cardHover = {
    hover: {
        scale: 1.02,
        boxShadow: '0 20px 40px rgba(0,0,0,0.08)',
        borderColor: 'rgba(0,0,0,0.8)',
        transition: { duration: 0.2, ease: "easeOut" }
    },
    tap: {
        scale: 0.98,
        transition: { duration: 0.1 }
    }
}

export const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.05,
            delayChildren: 0.1
        }
    }
}

export const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    show: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] }
    }
}

export const fadeInScale = {
    hidden: { opacity: 0, scale: 0.95 },
    show: {
        opacity: 1,
        scale: 1,
        transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
    }
}

export const slideInRight = {
    hidden: { x: 20, opacity: 0 },
    show: {
        x: 0,
        opacity: 1,
        transition: { duration: 0.3, ease: [0.4, 0, 0.2, 1] }
    }
}

export const shimmer = {
    initial: { backgroundPosition: '-200% center' },
    animate: {
        backgroundPosition: '200% center',
        transition: {
            repeat: Infinity,
            duration: 2,
            ease: "linear",
            repeatDelay: 1
        }
    }
}
