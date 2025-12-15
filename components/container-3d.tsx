"use client"

import { useRef } from "react"
import * as THREE from "three"

interface Container3DProps {
  items: any[]
}

export default function Container3D({ items }: Container3DProps) {
  const containerRef = useRef<THREE.Group>(null)

  // Container dimensions (scaled down for visualization)
  const containerWidth = 12
  const containerHeight = 2.4
  const containerDepth = 2.4

  return (
    <group ref={containerRef} position={[0, containerHeight / 2, 0]}>
      {/* Container Frame (wireframe) */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(containerWidth, containerHeight, containerDepth)]} />
        <lineBasicMaterial color="#666666" linewidth={2} />
      </lineSegments>

      {/* Container Walls (semi-transparent) */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[containerWidth, containerHeight, containerDepth]} />
        <meshPhongMaterial color="#e0e0e0" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>

      {/* Floor Platform */}
      <mesh position={[0, -containerHeight / 2 - 0.1, 0]} receiveShadow>
        <boxGeometry args={[containerWidth + 0.5, 0.2, containerDepth + 1]} />
        <meshStandardMaterial color="#555555" metalness={0.6} roughness={0.4} />
      </mesh>

      {/* Wheels */}
      <group position={[0, -containerHeight / 2 - 0.3, containerDepth / 2 + 0.3]}>
        <Wheel position={[-containerWidth / 2 + 1, 0, 0]} />
        <Wheel position={[-containerWidth / 2 + 2.5, 0, 0]} />
        <Wheel position={[containerWidth / 2 - 2.5, 0, 0]} />
        <Wheel position={[containerWidth / 2 - 1, 0, 0]} />
      </group>

      {/* Sample cargo items */}
      {items.length > 0 ? (
        items.map((item, index) => (
          <mesh
            key={index}
            position={[
              -containerWidth / 2 + (item.length || 1) / 2 + ((index * 1.5) % (containerWidth - 1)),
              -containerHeight / 2 + (item.height || 1) / 2,
              -containerDepth / 2 + (item.width || 1) / 2,
            ]}
            castShadow
          >
            <boxGeometry args={[item.length / 100 || 1, item.height / 100 || 1, item.width / 100 || 1]} />
            <meshStandardMaterial color={item.color || "#34D399"} metalness={0.1} roughness={0.5} />
          </mesh>
        ))
      ) : (
        // Default sample boxes if no items
        <>
          <mesh position={[-4, -containerHeight / 2 + 0.5, 0]} castShadow>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#34D399" metalness={0.1} roughness={0.5} />
          </mesh>
          <mesh position={[-2.5, -containerHeight / 2 + 0.5, 0]} castShadow>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#3B82F6" metalness={0.1} roughness={0.5} />
          </mesh>
          <mesh position={[-1, -containerHeight / 2 + 0.5, 0]} castShadow>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#F59E0B" metalness={0.1} roughness={0.5} />
          </mesh>
        </>
      )}
    </group>
  )
}

function Wheel({ position }: { position: [number, number, number] }) {
  return (
    <mesh position={position} rotation={[0, 0, Math.PI / 2]} castShadow>
      <cylinderGeometry args={[0.3, 0.3, 0.4, 16]} />
      <meshStandardMaterial color="#222222" metalness={0.8} roughness={0.3} />
    </mesh>
  )
}
