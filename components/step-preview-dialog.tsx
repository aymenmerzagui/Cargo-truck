"use client"

import { useEffect, useRef, useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Canvas } from "@react-three/fiber"
import { OrbitControls, PerspectiveCamera } from "@react-three/drei"
import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js"
import type * as THREE from "three"

interface StepPreviewDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  stlFile: string
  dimensions: { x: number; y: number; z: number }
  fileName: string
  onConfirm: (data: { name: string; length: number; width: number; height: number; weight: number }) => void
}

function STLModel({ url }: { url: string }) {
  const meshRef = useRef<THREE.Mesh>(null)
  const [geometry, setGeometry] = useState<THREE.BufferGeometry | null>(null)

  useEffect(() => {
    const loader = new STLLoader()
    loader.load(
      url,
      (loadedGeometry) => {
        loadedGeometry.center()
        loadedGeometry.computeVertexNormals()
        setGeometry(loadedGeometry)
      },
      undefined,
      (error) => {
        console.error("Error loading STL:", error)
      },
    )
  }, [url])

  if (!geometry) return null

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial color="#3B82F6" metalness={0.3} roughness={0.4} />
    </mesh>
  )
}
const to3 = (value: number) => Number(value.toFixed(3))
export default function StepPreviewDialog({
  open,
  onOpenChange,
  stlFile,
  dimensions,
  fileName,
  onConfirm,
}: StepPreviewDialogProps) {
  const [name, setName] = useState("")
  const [length, setLength] = useState(0)
  const [width, setWidth] = useState(0)
  const [height, setHeight] = useState(0)
  const [weight, setWeight] = useState(10)

  useEffect(() => {
    if (open) {
      setName(fileName.replace(".step", "").replace(".stp", ""))
      setLength(to3(dimensions.x))
      setWidth(to3(dimensions.y))
      setHeight(to3(dimensions.z))
      setWeight(10)
    }
  }, [open, dimensions, fileName])

  const stlUrl = `http://localhost:8000/download-stl/${stlFile}`

  const handleConfirm = () => {
    onConfirm({ name, length, width, height, weight })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>Preview STEP File</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* 3D Preview */}
          <div className="aspect-video w-full overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
            {stlFile ? (
              <Canvas>
                <PerspectiveCamera makeDefault position={[200, 200, 200]} />
                <OrbitControls enableDamping dampingFactor={0.05} />

                {/* Lighting */}
                <ambientLight intensity={0.5} />
                <directionalLight position={[10, 10, 5]} intensity={1} />
                <directionalLight position={[-10, -10, -5]} intensity={0.5} />

                {/* Grid */}
                <gridHelper args={[500, 20, "#94a3b8", "#cbd5e1"]} />

                {/* STL Model */}
                <STLModel url={stlUrl} />
              </Canvas>
            ) : (
              <div className="flex h-full items-center justify-center text-gray-500">
                Loading 3D model...
              </div>
            )}
          </div>

          {/* Item Details */}
          <div className="space-y-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Item Name</label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Enter item name" />
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Length (cm)</label>
                <Input 
                  type="number" 
                  value={length} 
                  onChange={(e) => setLength(Number(e.target.value))} 
                  step="0.1" 
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Width (cm)</label>
                <Input 
                  type="number" 
                  value={width} 
                  onChange={(e) => setWidth(Number(e.target.value))} 
                  step="0.1" 
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700">Height (cm)</label>
                <Input 
                  type="number" 
                  value={height} 
                  onChange={(e) => setHeight(Number(e.target.value))} 
                  step="0.1" 
                />
              </div>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Weight (kg)</label>
              <Input 
                type="number" 
                value={weight} 
                onChange={(e) => setWeight(Number(e.target.value))} 
                step="0.1" 
              />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleConfirm}>Add Item</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}