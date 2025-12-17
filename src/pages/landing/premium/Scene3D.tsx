import React, { useRef } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { MeshDistortMaterial, Float, Environment, Stars } from '@react-three/drei'
import * as THREE from 'three'

const LiquidChrome = (props) => {
  const meshRef = useRef()
  
  useFrame((state) => {
    if (!meshRef.current) return
    const time = state.clock.getElapsedTime()
    // Subtle rotation
    meshRef.current.rotation.x = time * 0.1
    meshRef.current.rotation.y = time * 0.05
  })

  return (
    <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.5}>
      <mesh ref={meshRef} {...props} scale={2.5}>
        <sphereGeometry args={[1, 64, 64]} />
        {/* High-end "Liquid Chrome" Material */}
        <MeshDistortMaterial
          color="#1a1a1a"
          envMapIntensity={1.5}
          clearcoat={1}
          clearcoatRoughness={0}
          metalness={0.9}
          roughness={0.1}
          distort={0.4} // The "liquid" effect
          speed={1.5} // Speed of the distortion
        />
      </mesh>
    </Float>
  )
}

const BackgroundParticles = () => {
  const ref = useRef()
  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.x -= delta / 10
      ref.current.rotation.y -= delta / 15
    }
  })
  return (
    <group rotation={[0, 0, Math.PI / 4]}>
      <Points ref={ref} stride={3} positions={new Float32Array(2000 * 3)} />
    </group>
  )
}

// Simple custom points implementation if not using drei's specialized ones or to keep it light
const Points = React.forwardRef(({ positions, stride = 3 }, ref) => {
  const pointsRef = useRef()
  
  // Generate random points on mount
  const p = React.useMemo(() => {
    const temp = new Float32Array(1500 * 3)
    for (let i = 0; i < 1500; i++) {
      const x = (Math.random() - 0.5) * 20
      const y = (Math.random() - 0.5) * 20
      const z = (Math.random() - 0.5) * 10 - 5
      temp[i * 3] = x
      temp[i * 3 + 1] = y
      temp[i * 3 + 2] = z
    }
    return temp
  }, [])

  useFrame((state, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.05
    }
  })

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={p.length / 3}
          array={p}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.03}
        color="#f59e0b"
        sizeAttenuation={true}
        transparent={true}
        opacity={0.6}
      />
    </points>
  )
})

const Scene3D = () => {
  return (
    <div className="absolute inset-0 z-0 pointer-events-none">
      <Canvas camera={{ position: [0, 0, 8], fov: 35 }} dpr={[1, 2]}>
        <color attach="background" args={['#050505']} />
        
        {/* Lighting Setup for Drama */}
        <ambientLight intensity={0.2} />
        <spotLight position={[10, 10, 10]} angle={0.15} penumbra={1} intensity={1} color="#fff" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#f59e0b" /> {/* Accent color backlight */}
        
        {/* The Hero Object */}
        <LiquidChrome position={[2.5, 0, 0]} />
        
        {/* Atmosphere */}
        <Points />
        
        {/* High quality environment map for reflections */}
        <Environment preset="city" />
        
        {/* Post-processing fog for depth */}
        <fog attach="fog" args={['#050505', 5, 20]} />
      </Canvas>
    </div>
  )
}

export default Scene3D
