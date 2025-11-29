export const pageTransition = {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] }
}

export const cardHover = {
    hover: {
        y: -2,
        boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
        transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] }
    },
    tap: {
        scale: 0.99,
        transition: { duration: 0.1 }
    }
}

export const staggerContainer = {
    hidden: { opacity: 0 },
    show: {
        opacity: 1,
        transition: {
            staggerChildren: 0.03,
            delayChildren: 0
        }
    }
}

export const fadeInUp = {
    hidden: { opacity: 0, y: 10 },
    show: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.3 }
    }
}

export const fadeInScale = {
    hidden: { opacity: 0, scale: 0.98 },
    show: {
        opacity: 1,
        scale: 1,
        transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] }
    }
}

export const slideInRight = {
    hidden: { x: 10, opacity: 0 },
    show: {
        x: 0,
        opacity: 1,
        transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] }
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
