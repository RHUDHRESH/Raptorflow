import { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function ThreeBackground() {
    const containerRef = useRef(null)

    useEffect(() => {
        console.log('[ThreeBackground] Initializing...')
        if (!containerRef.current) {
            console.error('[ThreeBackground] Container ref is null')
            return
        }

        try {
            // Setup Scene, Camera, Renderer
            console.log('[ThreeBackground] Setting up scene...')
            const scene = new THREE.Scene()
            scene.fog = new THREE.FogExp2(0x000000, 0.0015)

            const camera = new THREE.PerspectiveCamera(
                75,
                window.innerWidth / window.innerHeight,
                0.1,
                1000
            )
            camera.position.z = 5

            const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
            renderer.setSize(window.innerWidth, window.innerHeight)
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
            containerRef.current.appendChild(renderer.domElement)
            console.log('[ThreeBackground] Renderer attached')

            // Create Stars with varying sizes and brightness
            const particleCount = 3000
            const geometry = new THREE.BufferGeometry()
            const positions = []
            const velocities = []
            const sizes = []
            const alphas = []
            const twinkleSpeed = []

            for (let i = 0; i < particleCount; i++) {
                positions.push((Math.random() * 2 - 1) * 600) // x
                positions.push((Math.random() * 2 - 1) * 600) // y
                positions.push((Math.random() * 2 - 1) * 600) // z

                // Varying velocities for depth
                velocities.push(Math.random() * 0.4 + 0.1)

                // Varying sizes - some stars are bigger
                sizes.push(Math.random() * 3 + 0.5)

                // Random starting opacity for twinkling
                alphas.push(Math.random())

                // Different twinkle speeds
                twinkleSpeed.push(Math.random() * 0.05 + 0.01)
            }

            geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3))
            geometry.setAttribute('velocity', new THREE.Float32BufferAttribute(velocities, 1))
            geometry.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1))
            geometry.setAttribute('alpha', new THREE.Float32BufferAttribute(alphas, 1))
            geometry.setAttribute('twinkleSpeed', new THREE.Float32BufferAttribute(twinkleSpeed, 1))

            // Custom shader for twinkling stars
            const material = new THREE.ShaderMaterial({
                uniforms: {
                    time: { value: 0 }
                },
                vertexShader: `
            attribute float size;
            attribute float alpha;
            varying float vAlpha;
            
            void main() {
              vAlpha = alpha;
              vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
              gl_PointSize = size * (300.0 / -mvPosition.z);
              gl_Position = projectionMatrix * mvPosition;
            }
          `,
                fragmentShader: `
            uniform float time;
            varying float vAlpha;
            
            void main() {
              // Create circular stars
              vec2 center = gl_PointCoord - vec2(0.5);
              float dist = length(center);
              if (dist > 0.5) discard;
              
              // Soft edges with glow
              float strength = 1.0 - (dist * 2.0);
              strength = pow(strength, 3.0);
              
              // Twinkling effect
              float twinkle = vAlpha;
              
              gl_FragColor = vec4(1.0, 1.0, 1.0, strength * twinkle);
            }
          `,
                transparent: true,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            })

            const particles = new THREE.Points(geometry, material)
            scene.add(particles)

            // Create constellation lines (connecting nearby stars)
            const lineGeometry = new THREE.BufferGeometry()
            const lineMaterial = new THREE.LineBasicMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.1,
                blending: THREE.AdditiveBlending
            })
            const lines = new THREE.LineSegments(lineGeometry, lineMaterial)
            scene.add(lines)

            // Mouse interaction
            const mouse = new THREE.Vector2()
            let targetMouseX = 0
            let targetMouseY = 0
            const windowHalfX = window.innerWidth / 2
            const windowHalfY = window.innerHeight / 2

            const onMouseMove = (event) => {
                mouse.x = event.clientX - windowHalfX
                mouse.y = event.clientY - windowHalfY
            }

            const onTouchMove = (event) => {
                if (event.touches.length === 1) {
                    mouse.x = event.touches[0].pageX - windowHalfX
                    mouse.y = event.touches[0].pageY - windowHalfY
                }
            }

            document.addEventListener('mousemove', onMouseMove)
            document.addEventListener('touchmove', onTouchMove, { passive: true })

            // Animation Loop
            let animationId
            let time = 0
            const animate = () => {
                animationId = requestAnimationFrame(animate)
                time += 0.01

                const positionsAttr = geometry.attributes.position
                const velocitiesAttr = geometry.attributes.velocity
                const alphasAttr = geometry.attributes.alpha
                const twinkleSpeedAttr = geometry.attributes.twinkleSpeed

                // Update shader time for twinkling
                material.uniforms.time.value = time

                // Smooth camera parallax
                targetMouseX += (mouse.x - targetMouseX) * 0.05
                targetMouseY += (mouse.y - targetMouseY) * 0.05
                camera.position.x += (targetMouseX - camera.position.x) * 0.015
                camera.position.y += (-targetMouseY - camera.position.y) * 0.015
                camera.lookAt(scene.position)

                // Update particles
                for (let i = 0; i < particleCount; i++) {
                    // Move stars forward
                    let z = positionsAttr.getZ(i)
                    z += velocitiesAttr.getX(i)

                    if (z > 100) {
                        z = -500
                        // Reset position randomly when looping
                        positionsAttr.setX(i, (Math.random() * 2 - 1) * 600)
                        positionsAttr.setY(i, (Math.random() * 2 - 1) * 600)
                    }
                    positionsAttr.setZ(i, z)

                    // Twinkling effect
                    const twinkle = Math.sin(time * twinkleSpeedAttr.getX(i) * 100) * 0.5 + 0.5
                    alphasAttr.setX(i, twinkle * 0.8 + 0.2)

                    // Mouse interaction - push stars away dramatically
                    const x = positionsAttr.getX(i)
                    const y = positionsAttr.getY(i)
                    const dx = mouse.x - x
                    const dy = -mouse.y - y
                    const dist = Math.sqrt(dx * dx + dy * dy)

                    if (dist < 200) {
                        const force = (200 - dist) / 200
                        positionsAttr.setX(i, x - (dx / dist) * force * 8)
                        positionsAttr.setY(i, y - (dy / dist) * force * 8)
                    }
                }

                // Create constellation lines between nearby stars
                const linePositions = []
                const maxDistance = 100
                for (let i = 0; i < Math.min(particleCount, 500); i++) {
                    const x1 = positionsAttr.getX(i)
                    const y1 = positionsAttr.getY(i)
                    const z1 = positionsAttr.getZ(i)

                    // Only check nearby stars for performance
                    for (let j = i + 1; j < Math.min(i + 5, particleCount); j++) {
                        const x2 = positionsAttr.getX(j)
                        const y2 = positionsAttr.getY(j)
                        const z2 = positionsAttr.getZ(j)

                        const dx = x2 - x1
                        const dy = y2 - y1
                        const dz = z2 - z1
                        const distance = Math.sqrt(dx * dx + dy * dy + dz * dz)

                        if (distance < maxDistance) {
                            linePositions.push(x1, y1, z1)
                            linePositions.push(x2, y2, z2)
                        }
                    }
                }

                lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3))

                positionsAttr.needsUpdate = true
                alphasAttr.needsUpdate = true
                renderer.render(scene, camera)
            }

            // Handle resize
            const handleResize = () => {
                camera.aspect = window.innerWidth / window.innerHeight
                camera.updateProjectionMatrix()
                renderer.setSize(window.innerWidth, window.innerHeight)
            }

            window.addEventListener('resize', handleResize)
            animate()
            console.log('[ThreeBackground] Animation started')

            // Cleanup
            return () => {
                console.log('[ThreeBackground] Cleaning up...')
                cancelAnimationFrame(animationId)
                document.removeEventListener('mousemove', onMouseMove)
                document.removeEventListener('touchmove', onTouchMove)
                window.removeEventListener('resize', handleResize)
                if (containerRef.current && renderer.domElement.parentNode) {
                    containerRef.current.removeChild(renderer.domElement)
                }
                geometry.dispose()
                lineGeometry.dispose()
                material.dispose()
                lineMaterial.dispose()
                renderer.dispose()
            }
        } catch (err) {
            console.error('[ThreeBackground] Error:', err)
        }
    }, [])

    return (
        <div
            ref={containerRef}
            className="fixed inset-0 z-0"
            style={{
                background: 'radial-gradient(circle at center, #0a0a0a 0%, #000000 100%)'
            }}
        />
    )
}
