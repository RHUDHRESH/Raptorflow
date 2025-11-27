import { useEffect, useRef } from 'react'

/**
 * Particle System Component
 * Creates an animated particle field with physics and mouse interaction
 */
export default function ParticleSystem({ count = 50, color = '0, 0, 0' }) {
    const canvasRef = useRef(null)
    const particlesRef = useRef([])
    const mouseRef = useRef({ x: 0, y: 0 })
    const animationRef = useRef(null)

    useEffect(() => {
        const canvas = canvasRef.current
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        let width = window.innerWidth
        let height = window.innerHeight

        canvas.width = width
        canvas.height = height

        // Particle class
        class Particle {
            constructor() {
                this.reset()
                this.y = Math.random() * height
            }

            reset() {
                this.x = Math.random() * width
                this.y = -10
                this.vx = (Math.random() - 0.5) * 0.5
                this.vy = Math.random() * 0.5 + 0.2
                this.size = Math.random() * 2 + 1
                this.opacity = Math.random() * 0.5 + 0.2
            }

            update() {
                // Mouse interaction - attract particles
                const dx = mouseRef.current.x - this.x
                const dy = mouseRef.current.y - this.y
                const distance = Math.sqrt(dx * dx + dy * dy)

                if (distance < 150) {
                    const force = (150 - distance) / 150
                    this.vx += (dx / distance) * force * 0.2
                    this.vy += (dy / distance) * force * 0.2
                }

                // Apply velocity
                this.x += this.vx
                this.y += this.vy

                // Damping
                this.vx *= 0.98
                this.vy *= 0.98

                // Gravity
                this.vy += 0.02

                // Reset if out of bounds
                if (this.y > height + 10 || this.x < -10 || this.x > width + 10) {
                    this.reset()
                }
            }

            draw(ctx) {
                ctx.beginPath()
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
                ctx.fillStyle = `rgba(${color}, ${this.opacity})`
                ctx.fill()
            }
        }

        // Initialize particles
        particlesRef.current = Array.from({ length: count }, () => new Particle())

        // Animation loop
        function animate() {
            ctx.clearRect(0, 0, width, height)

            particlesRef.current.forEach(particle => {
                particle.update()
                particle.draw(ctx)
            })

            animationRef.current = requestAnimationFrame(animate)
        }

        animate()

        // Mouse move handler
        const handleMouseMove = (e) => {
            mouseRef.current = {
                x: e.clientX,
                y: e.clientY
            }
        }

        // Resize handler
        const handleResize = () => {
            width = window.innerWidth
            height = window.innerHeight
            canvas.width = width
            canvas.height = height

            // Reinitialize particles on resize
            particlesRef.current.forEach(particle => {
                particle.reset()
                particle.y = Math.random() * height
            })
        }

        window.addEventListener('mousemove', handleMouseMove)
        window.addEventListener('resize', handleResize)

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current)
            }
            window.removeEventListener('mousemove', handleMouseMove)
            window.removeEventListener('resize', handleResize)
        }
    }, [count, color])

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-none"
            style={{ opacity: 0.6 }}
        />
    )
}
