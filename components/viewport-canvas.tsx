"use client"
import { Canvas, useThree, useFrame } from "@react-three/fiber"
import { OrbitControls, Grid, PerspectiveCamera, Text } from "@react-three/drei"
import { Suspense, useRef, useState, useEffect } from "react"
import * as THREE from "three"
import { PlacedBox } from "./types/placedBox"

interface Container {
  id: string
  name: string
  type: string
  dimensions: string
  weight: string
  icon: string
}

interface ViewportCanvasProps {
  container: Container | null
  items: any[]
  placedBoxes: PlacedBox[]
  selectedBoxId: string | null
  onPlaceBox: (itemId: string, x: number, y: number, z: number) => void
  onSelectBox: (boxId: string | null) => void
}

function parseDimensions(dimensions: string) {
  const cleaned = dimensions.replace(' cm', '').trim()
  const parts = cleaned.split('x').map(s => parseFloat(s.trim()))
  
  if (parts.length === 3) {
    return {
      length: parts[0] / 100,
      width: parts[1] / 100,
      height: parts[2] / 100
    }
  }
  
  return { length: 12, width: 2.4, height: 2.4 }
}

export default function ViewportCanvas({ 
  container, 
  items, 
  placedBoxes,
  selectedBoxId,
  onPlaceBox,
  onSelectBox
}: ViewportCanvasProps) {
  const [targetPosition, setTargetPosition] = useState<[number, number, number] | null>(null)
  const [draggingBox, setDraggingBox] = useState<{
    itemId: string
    index: number
    dimensions: { length: number; width: number; height: number }
    color: string
  } | null>(null)

  const handleStartDrag = (itemId: string, index: number, item: any) => {
    console.log("Starting drag:", itemId, "index:", index)
    setDraggingBox({
      itemId,
      index,
      dimensions: {
        length: item.length / 100,
        width: item.width / 100,
        height: item.height / 100
      },
      color: item.color
    })
  }

  const handleStopDrag = () => {
    console.log("Stopping drag")
    setDraggingBox(null)
  }

  return (
    <div className="h-full w-full relative">
      <Canvas shadows>
        <CameraController targetPosition={targetPosition} />
        <PerspectiveCamera makeDefault position={[15, 10, 15]} fov={50} />
        <OrbitControls makeDefault enableDamping dampingFactor={0.05} enabled={!draggingBox} />
        
        {/* Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow shadow-mapSize={[2048, 2048]} />
        <directionalLight position={[-10, 10, -5]} intensity={0.3} />
        
        {/* Grid Floor */}
        <Grid
          args={[50, 50]}
          cellSize={1}
          cellThickness={0.5}
          cellColor="#cccccc"
          sectionSize={5}
          sectionThickness={1}
          sectionColor="#999999"
          fadeDistance={50}
          fadeStrength={1}
          position={[0, 0, 0]}
        />
        
        {/* 3D Container and Items */}
        <Suspense fallback={null}>
          {container ? (
            <>
              <Container3D 
                container={container} 
                items={items}
                placedBoxes={placedBoxes}
                selectedBoxId={selectedBoxId}
                draggingBox={draggingBox}
                onPlaceBox={onPlaceBox}
                onSelectBox={onSelectBox}
                onStopDrag={handleStopDrag}
              />
              <StagingArea 
                items={items} 
                draggingBox={draggingBox}
                onStartDrag={handleStartDrag}
              />
            </>
          ) : (
            <EmptyState />
          )}
        </Suspense>
        
        {/* Measurement Axis */}
        <group position={[-8, 0, -8]}>
          <mesh position={[1.5, 0.05, 0]} rotation={[0, 0, Math.PI / 2]}>
            <cylinderGeometry args={[0.02, 0.02, 3]} />
            <meshBasicMaterial color="#ff0000" />
          </mesh>
          <mesh position={[3, 0.05, 0]} rotation={[0, 0, -Math.PI / 2]}>
            <coneGeometry args={[0.08, 0.2]} />
            <meshBasicMaterial color="#ff0000" />
          </mesh>
          
          <mesh position={[0, 1.55, 0]}>
            <cylinderGeometry args={[0.02, 0.02, 3]} />
            <meshBasicMaterial color="#00ff00" />
          </mesh>
          <mesh position={[0, 3.1, 0]}>
            <coneGeometry args={[0.08, 0.2]} />
            <meshBasicMaterial color="#00ff00" />
          </mesh>
          
          <mesh position={[0, 0.05, 1.5]} rotation={[Math.PI / 2, 0, 0]}>
            <cylinderGeometry args={[0.02, 0.02, 3]} />
            <meshBasicMaterial color="#0000ff" />
          </mesh>
          <mesh position={[0, 0.05, 3]} rotation={[Math.PI / 2, 0, 0]}>
            <coneGeometry args={[0.08, 0.2]} />
            <meshBasicMaterial color="#0000ff" />
          </mesh>
          
          <Suspense fallback={null}>
            <Text position={[3.5, 0.05, 0]} fontSize={0.3} color="#ff0000">X</Text>
            <Text position={[0, 3.5, 0]} fontSize={0.3} color="#00ff00">Y</Text>
            <Text position={[0, 0.05, 3.5]} fontSize={0.3} color="#0000ff">Z</Text>
          </Suspense>
        </group>
      </Canvas>
      
      <ViewCube onViewChange={setTargetPosition} />
      
      {draggingBox && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-blue-600 text-white px-6 py-3 rounded-lg shadow-lg">
          <div className="font-semibold">Drag box into container and release</div>
          <div className="text-sm text-blue-100">Green = valid position | Red = invalid</div>
        </div>
      )}
    </div>
  )
}

function CameraController({ targetPosition }: { targetPosition: [number, number, number] | null }) {
  const { camera } = useThree()
  
  useEffect(() => {
    if (targetPosition) {
      camera.position.set(...targetPosition)
      camera.lookAt(0, 0, 0)
      camera.updateProjectionMatrix()
    }
  }, [targetPosition, camera])
  
  return null
}

function ViewCube({ onViewChange }: { onViewChange: (position: [number, number, number]) => void }) {
  const views: { name: string; position: [number, number, number] }[] = [
    { name: 'Front', position: [0, 5, 15] },
    { name: 'Back', position: [0, 5, -15] },
    { name: 'Left', position: [-15, 5, 0] },
    { name: 'Right', position: [15, 5, 0] },
    { name: 'Top', position: [0, 20, 0.1] },
    { name: 'Bottom', position: [0, -20, 0.1] },
  ]

  return (
    <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-2 border border-gray-200">
      <div className="grid grid-cols-3 gap-1">
        <div></div>
        <button onClick={() => onViewChange(views[4].position)} className="w-12 h-12 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs font-semibold text-blue-700 transition-colors">Top</button>
        <div></div>
        <button onClick={() => onViewChange(views[2].position)} className="w-12 h-12 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs font-semibold text-blue-700 transition-colors">Left</button>
        <button onClick={() => onViewChange(views[0].position)} className="w-12 h-12 bg-blue-100 hover:bg-blue-200 border-2 border-blue-400 rounded text-xs font-semibold text-blue-800 transition-colors">Front</button>
        <button onClick={() => onViewChange(views[3].position)} className="w-12 h-12 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs font-semibold text-blue-700 transition-colors">Right</button>
        <div></div>
        <button onClick={() => onViewChange(views[5].position)} className="w-12 h-12 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs font-semibold text-blue-700 transition-colors">Bot</button>
        <button onClick={() => onViewChange(views[1].position)} className="w-12 h-12 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded text-xs font-semibold text-blue-700 transition-colors">Back</button>
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <Text position={[0, 2, 0]} fontSize={0.8} color="#999999" anchorY="middle" anchorX="center">
      Select a container to begin
    </Text>
  )
}

function DraggableGhost({ 
  draggingBox, 
  containerDimensions,
  placedBoxes,
  onRelease
}: { 
  draggingBox: any
  containerDimensions: { length: number; width: number; height: number }
  placedBoxes: PlacedBox[]
  onRelease: (x: number, y: number, z: number, isValid: boolean) => void
}) {
  const { camera, raycaster, pointer, scene } = useThree()
  const [ghostPosition, setGhostPosition] = useState<THREE.Vector3>(new THREE.Vector3(0, 5, 0))
  const [isValid, setIsValid] = useState(false)
  const [finalPosition, setFinalPosition] = useState<{ x: number; y: number; z: number } | null>(null)
  const meshRef = useRef<THREE.Mesh>(null)

  useFrame(() => {
    if (!draggingBox) return

    raycaster.setFromCamera(pointer, camera)
    const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)
    const intersectPoint = new THREE.Vector3()
    raycaster.ray.intersectPlane(plane, intersectPoint)
    
    if (intersectPoint) {
      setGhostPosition(intersectPoint)
      const validPos = findValidPosition(
        intersectPoint.x,
        intersectPoint.z,
        draggingBox.dimensions.length,
        draggingBox.dimensions.width,
        draggingBox.dimensions.height,
        containerDimensions.length,
        containerDimensions.width,
        containerDimensions.height,
        placedBoxes
      )
      
      setFinalPosition(validPos)
      setIsValid(validPos !== null)
    }
  })

  useEffect(() => {
    const handleMouseUp = () => {
      if (finalPosition && isValid) {
        onRelease(finalPosition.x, finalPosition.y, finalPosition.z, true)
      } else {
        onRelease(0, 0, 0, false)
      }
    }

    window.addEventListener('mouseup', handleMouseUp)
    return () => window.removeEventListener('mouseup', handleMouseUp)
  }, [finalPosition, isValid, onRelease])

  if (!draggingBox || !finalPosition) return null

  return (
    <mesh 
      ref={meshRef}
      position={[finalPosition.x, finalPosition.y, finalPosition.z]}
    >
      <boxGeometry args={[
        draggingBox.dimensions.length,
        draggingBox.dimensions.height,
        draggingBox.dimensions.width
      ]} />
      <meshStandardMaterial 
        color={isValid ? "#4CAF50" : "#f44336"}
        transparent 
        opacity={0.5}
        emissive={isValid ? "#4CAF50" : "#f44336"}
        emissiveIntensity={0.3}
      />
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(
          draggingBox.dimensions.length,
          draggingBox.dimensions.height,
          draggingBox.dimensions.width
        )]} />
        <lineBasicMaterial 
          color={isValid ? "#4CAF50" : "#f44336"} 
          linewidth={2}
        />
      </lineSegments>
    </mesh>
  )
}

function Container3D({ 
  container, 
  items,
  placedBoxes,
  selectedBoxId,
  draggingBox,
  onPlaceBox,
  onSelectBox,
  onStopDrag
}: { 
  container: Container
  items: any[]
  placedBoxes: PlacedBox[]
  selectedBoxId: string | null
  draggingBox: any
  onPlaceBox: (itemId: string, x: number, y: number, z: number) => void
  onSelectBox: (boxId: string | null) => void
  onStopDrag: () => void
}) {
  const { length, width, height } = parseDimensions(container.dimensions)

  const handleGhostRelease = (x: number, y: number, z: number, isValid: boolean) => {
    if (isValid && draggingBox) {
      console.log("Placing box at:", x, y, z)
      onPlaceBox(draggingBox.itemId, x, y, z)
    }
    onStopDrag()
  }

  return (
    <group position={[0, height / 2, 0]}>
      <mesh>
        <boxGeometry args={[length, height, width]} />
        <meshStandardMaterial color="#4a90e2" transparent opacity={0.15} />
      </mesh>
      
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(length, height, width)]} />
        <lineBasicMaterial color="#2c5aa0" linewidth={2} />
      </lineSegments>
      
      <mesh position={[0, -height / 2 + 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[length, width]} />
        <meshStandardMaterial 
          color={draggingBox ? "#c8e6c9" : "#e8e8e8"} 
          side={2}
          opacity={draggingBox ? 0.8 : 1}
          transparent={draggingBox ? true : false}
        />
      </mesh>
      
      <Text position={[0, height / 2 + 0.5, 0]} fontSize={0.4} color="#2c5aa0" anchorY="bottom">
        {container.name}
      </Text>
      
      <Text position={[0, height / 2 + 0.2, 0]} fontSize={0.25} color="#666666" anchorY="bottom">
        {container.dimensions} • {container.weight}
      </Text>
      
      <Text position={[0, -height / 2 - 0.3, width / 2 + 0.3]} fontSize={0.3} color="#ff0000">
        L: {(length * 100).toFixed(1)} cm
      </Text>
      
      <Text position={[length / 2 + 0.3, -height / 2 - 0.3, 0]} fontSize={0.3} color="#0000ff" rotation={[0, Math.PI / 2, 0]}>
        W: {(width * 100).toFixed(1)} cm
      </Text>
      
      <Text position={[length / 2 + 0.3, 0, width / 2 + 0.3]} fontSize={0.3} color="#00ff00">
        H: {(height * 100).toFixed(1)} cm
      </Text>
      
      {placedBoxes.map((box) => (
        <PlacedBox3D 
          key={box.id} 
          box={box} 
          containerHeight={height}
          isSelected={box.id === selectedBoxId}
          onSelect={() => onSelectBox(box.id)}
        />
      ))}
      
      {draggingBox && (
        <DraggableGhost 
          draggingBox={draggingBox}
          containerDimensions={{ length, width, height }}
          placedBoxes={placedBoxes}
          onRelease={handleGhostRelease}
        />
      )}
    </group>
  )
}

function findValidPosition(
  targetX: number,
  targetZ: number,
  itemLength: number,
  itemWidth: number,
  itemHeight: number,
  containerLength: number,
  containerWidth: number,
  containerHeight: number,
  placedBoxes: PlacedBox[]
): { x: number; y: number; z: number } | null {
  
  const halfLength = itemLength / 2
  const halfWidth = itemWidth / 2
  const halfHeight = itemHeight / 2
  
  const maxX = containerLength / 2 - halfLength
  const minX = -containerLength / 2 + halfLength
  const maxZ = containerWidth / 2 - halfWidth
  const minZ = -containerWidth / 2 + halfWidth
  
  let x = Math.max(minX, Math.min(maxX, targetX))
  let z = Math.max(minZ, Math.min(maxZ, targetZ))
  
  let y = halfHeight
  
  for (const box of placedBoxes) {
    const boxLength = box.length / 100
    const boxWidth = box.width / 100
    const boxHeight = box.height / 100
    
    const xOverlap = Math.abs(x - box.x) < (halfLength + boxLength / 2)
    const zOverlap = Math.abs(z - box.z) < (halfWidth + boxWidth / 2)
    
    if (xOverlap && zOverlap) {
      const topOfBox = box.y + boxHeight / 2
      const proposedY = topOfBox + halfHeight
      
      if (proposedY > y) {
        y = proposedY
      }
    }
  }
  
  if (y + halfHeight > containerHeight) {
    return null
  }
  
  const hasCollision = placedBoxes.some(box => {
    const boxLength = box.length / 100
    const boxWidth = box.width / 100
    const boxHeight = box.height / 100
    
    const xOverlap = Math.abs(x - box.x) < (halfLength + boxLength / 2)
    const yOverlap = Math.abs(y - box.y) < (halfHeight + boxHeight / 2)
    const zOverlap = Math.abs(z - box.z) < (halfWidth + boxWidth / 2)
    
    return xOverlap && yOverlap && zOverlap
  })
  
  if (hasCollision) {
    return null
  }
  
  return { x, y, z }
}

function PlacedBox3D({ 
  box, 
  containerHeight,
  isSelected,
  onSelect
}: { 
  box: PlacedBox
  containerHeight: number
  isSelected: boolean
  onSelect: () => void
}) {
  const [hovered, setHovered] = useState(false)
  
  const itemLength = box.length / 100
  const itemWidth = box.width / 100
  const itemHeight = box.height / 100
  
  const y = box.y - containerHeight / 2
  
  return (
    <mesh 
      position={[box.x, y, box.z]} 
      castShadow 
      receiveShadow
      onClick={(e) => {
        e.stopPropagation()
        onSelect()
      }}
      onPointerEnter={() => setHovered(true)}
      onPointerLeave={() => setHovered(false)}
    >
      <boxGeometry args={[itemLength, itemHeight, itemWidth]} />
      <meshStandardMaterial 
        color={isSelected ? "#ffeb3b" : box.color}
        emissive={hovered ? "#00ff00" : isSelected ? "#ffc107" : "#000000"}
        emissiveIntensity={hovered ? 0.3 : isSelected ? 0.2 : 0}
      />
      
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(itemLength, itemHeight, itemWidth)]} />
        <lineBasicMaterial 
          color={isSelected ? "#ff9800" : hovered ? "#00ff00" : "#000000"} 
          opacity={isSelected ? 1 : 0.3} 
          transparent 
          linewidth={isSelected ? 3 : 1}
        />
      </lineSegments>
    </mesh>
  )
}

function StagingArea({ 
  items,
  draggingBox,
  onStartDrag
}: { 
  items: any[]
  draggingBox: any
  onStartDrag: (itemId: string, index: number, item: any) => void
}) {
  const itemsPerRow = 3
  let boxIndex = 0
  
  return (
    <>
      {items.map((item, itemIndex) => {
        const itemLength = (item.length || 100) / 100
        const itemWidth = (item.width || 100) / 100
        const itemHeight = (item.height || 100) / 100
        const color = item.color || '#4a90e2'
        const count = item.count || 0
        
        const boxes = []
        for (let i = 0; i < count; i++) {
          const row = Math.floor(boxIndex / itemsPerRow)
          const col = boxIndex % itemsPerRow
          
          const cellSize = 2
          const z = 8 + row * cellSize
          const x = col * cellSize - ((itemsPerRow - 1) * cellSize) / 2
          const y = itemHeight / 2
          
          const isDragging = draggingBox?.itemId === item.id && draggingBox?.index === i
          
          boxes.push(
            <StagingBox3D
              key={`${item.id}-${i}`}
              position={[x, y, z]}
              dimensions={[itemLength, itemHeight, itemWidth]}
              color={color}
              name={item.name}
              count={count}
              showLabel={i === 0}
              isDragging={isDragging}
              onMouseDown={() => onStartDrag(item.id, i, item)}
            />
          )
          boxIndex++
        }
        
        return boxes
      })}
    </>
  )
}

function StagingBox3D({
  position,
  dimensions,
  color,
  name,
  count,
  showLabel,
  isDragging,
  onMouseDown
}: {
  position: [number, number, number]
  dimensions: [number, number, number]
  color: string
  name: string
  count: number
  showLabel: boolean
  isDragging: boolean
  onMouseDown: () => void
}) {
  const [hovered, setHovered] = useState(false)
  
  if (isDragging) return null
  
  return (
    <group>
      <mesh 
        position={position}
        castShadow 
        receiveShadow
        onPointerDown={(e) => {
          e.stopPropagation()
          onMouseDown()
        }}
        onPointerEnter={() => setHovered(true)}
        onPointerLeave={() => setHovered(false)}
      >
        <boxGeometry args={dimensions} />
        <meshStandardMaterial 
          color={color}
          emissive={hovered ? "#4CAF50" : "#000000"}
          emissiveIntensity={hovered ? 0.4 : 0}
        />
        
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(...dimensions)]} />
          <lineBasicMaterial 
            color={hovered ? "#4CAF50" : "#000000"} 
            opacity={hovered ? 0.8 : 0.3} 
            transparent 
          />
        </lineSegments>
      </mesh>
      
      {showLabel && (
        <Text
          position={[position[0], position[1] + dimensions[1] / 2 + 0.3, position[2]]}
          fontSize={0.2}
          color="#333333"
          anchorY="bottom"
        >
          {name} {count > 1 ? `(x${count})` : ''}
        </Text>
      )}
    </group>
  )
}