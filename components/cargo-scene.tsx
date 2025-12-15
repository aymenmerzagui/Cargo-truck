"use client"

import { useRef } from "react"
import { useFrame } from "@react-three/fiber"
import { Box, RoundedBox } from "@react-three/drei"
import * as THREE from "three"

function CargoBox({
  position,
  color,
  size = [1, 1, 1],
}: { position: [number, number, number]; color: string; size?: [number, number, number] }) {
  return (
    <RoundedBox args={size} position={position} radius={0.05} smoothness={4}>
      <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
    </RoundedBox>
  )
}

function Container() {
  return (
    <group>
      {/* Container walls */}
      <Box args={[6, 0.1, 3]} position={[0, 0, 0]}>
        <meshStandardMaterial color="#444444" metalness={0.6} roughness={0.3} />
      </Box>

      {/* Back wall */}
      <Box args={[6, 3, 0.1]} position={[0, 1.5, -1.5]}>
        <meshStandardMaterial color="#555555" metalness={0.6} roughness={0.3} side={THREE.DoubleSide} />
      </Box>

      {/* Side walls */}
      <Box args={[0.1, 3, 3]} position={[-3, 1.5, 0]}>
        <meshStandardMaterial color="#555555" metalness={0.6} roughness={0.3} opacity={0.3} transparent />
      </Box>
      <Box args={[0.1, 3, 3]} position={[3, 1.5, 0]}>
        <meshStandardMaterial color="#555555" metalness={0.6} roughness={0.3} opacity={0.3} transparent />
      </Box>
    </group>
  )
}

export default function CargoScene() {
  const groupRef = useRef<THREE.Group>(null)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.1
    }
  })

  return (
    <group ref={groupRef}>
      <Container />

      {/* Cargo boxes in organized layout */}
      {/* Bottom layer - Red boxes */}
      <CargoBox position={[-2, 0.55, 0]} color="#ef4444" size={[1.2, 1, 1]} />
      <CargoBox position={[-0.5, 0.55, 0]} color="#ef4444" size={[1.2, 1, 1]} />
      <CargoBox position={[1, 0.55, 0]} color="#ef4444" size={[1.2, 1, 1]} />

      {/* Middle layer - Blue boxes */}
      <CargoBox position={[-2, 1.55, 0]} color="#3b82f6" size={[1, 1, 1.2]} />
      <CargoBox position={[-0.5, 1.55, 0.6]} color="#3b82f6" size={[1.2, 1, 0.8]} />
      <CargoBox position={[1.2, 1.55, 0]} color="#3b82f6" size={[1, 1, 1.2]} />

      {/* Top layer - Green boxes */}
      <CargoBox position={[-1.5, 2.55, 0.2]} color="#10b981" size={[0.8, 1, 0.8]} />
      <CargoBox position={[0, 2.55, -0.2]} color="#10b981" size={[0.8, 1, 0.8]} />

      {/* Yellow accent box */}
      <CargoBox position={[1.5, 2.55, 0.3]} color="#eab308" size={[0.8, 1, 0.8]} />

      {/* Back row - Orange boxes */}
      <CargoBox position={[-1.5, 0.55, -0.8]} color="#f97316" size={[1, 1, 0.8]} />
      <CargoBox position={[0.5, 0.55, -0.8]} color="#f97316" size={[1, 1, 0.8]} />

      {/* Grid helper */}
      <gridHelper args={[10, 10, "#666666", "#444444"]} position={[0, 0, 0]} />
    </group>
  )
}
