"use client"
import { useState } from "react"
import Navigation from "@/components/navigation"
import SpacesPanel from "@/components/spaces-panel"
import ItemsPanel from "@/components/items-panel"
import ViewportCanvas from "@/components/viewport-canvas"
import ShipmentPanel from "@/components/shipment-panel"
import { Button } from "@/components/ui/button"
import { Container, containers } from "@/components/types/container"
import { PlacedBox } from "@/components/types/placedBox"

type Tab = "spaces" | "items" | "shipments"
export function autoLoadItems(
  container: Container,
  items: any[],
  alreadyPlaced: PlacedBox[]
): { placed: PlacedBox[]; remainingItems: any[] } {
  const dims = container.dimensions
    .replace(" cm", "")
    .split("x")
    .map(v => parseFloat(v.trim()) / 100)

  const [containerLength, containerWidth, containerHeight] = dims

  let x = 0
  let y = 0
  let z = 0
  let maxRowHeight = 0

  const placed: PlacedBox[] = []
  const remainingItems = items.map(i => ({ ...i }))

  // Start stacking AFTER already placed boxes
  if (alreadyPlaced.length > 0) {
    const last = alreadyPlaced[alreadyPlaced.length - 1]
    x = last.x + last.length / 200 + containerLength / 2
    z = last.z + last.width / 200 + containerWidth / 2
    y = last.y - last.height / 200
  }

  for (const item of remainingItems) {
    const l = item.length / 100
    const w = item.width / 100
    const h = item.height / 100

    let countLeft = item.count

    while (countLeft > 0) {
      if (x + l > containerLength) {
        x = 0
        z += w
        maxRowHeight = 0
      }

      if (z + w > containerWidth) {
        z = 0
        y += maxRowHeight
        maxRowHeight = 0
      }

      if (y + h > containerHeight) {
        item.count = countLeft
        return { placed, remainingItems }
      }

      placed.push({
        id: `auto-${Date.now()}-${Math.random()}`,
        itemId: item.id,
        name: item.name,
        length: item.length,
        width: item.width,
        height: item.height,
        color: item.color,
        x: x + l / 2 - containerLength / 2,
        y: y + h / 2,
        z: z + w / 2 - containerWidth / 2,
        rotation: 0
      })

      x += l
      maxRowHeight = Math.max(maxRowHeight, h)
      countLeft--
    }

    item.count = countLeft
  }

  return { placed, remainingItems }
}


export default function CargoLoaderApp() {
  const [activeTab, setActiveTab] = useState<Tab>("spaces")
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedContainer, setSelectedContainer] = useState<Container | null>(null)
  const [items, setItems] = useState<any[]>([])
  const [placedBoxes, setPlacedBoxes] = useState<PlacedBox[]>([])
  const [selectedBoxId, setSelectedBoxId] = useState<string | null>(null)

  const handleSelectContainer = (id: string) => {
    const container = containers.find(c => c.id === id)
    setSelectedContainer(container || null)
  }
  const handlePlaceBox = (itemId: string, x: number, y: number, z: number) => {
    console.log("Placing box - itemId:", itemId, "at:", x, y, z)

    const item = items.find(i => i.id === itemId)
    if (!item) {
      console.warn("Item not found:", itemId)
      return
    }

    if (item.count <= 0) {
      console.warn("Item count is 0")
      return
    }

    // Create new placed box
    const newBox: PlacedBox = {
      id: `placed-${Date.now()}-${Math.random()}`,
      itemId: item.id,
      name: item.name,
      length: item.length,
      width: item.width,
      height: item.height,
      color: item.color,
      x,
      y,
      z,
      rotation: 0
    }

    console.log("Created new box:", newBox)

    // Add to placed boxes
    setPlacedBoxes([...placedBoxes, newBox])

    // Decrement count in items
    setItems(items.map(i =>
      i.id === itemId
        ? { ...i, count: i.count - 1 }
        : i
    ))
  }

  // Handle deleting a placed box
  const handleDeleteBox = (boxId: string) => {
    console.log("Deleting box:", boxId)

    const box = placedBoxes.find(b => b.id === boxId)
    if (!box) {
      console.warn("Box not found:", boxId)
      return
    }

    // Remove from placed boxes
    setPlacedBoxes(placedBoxes.filter(b => b.id !== boxId))

    // Increment count in items
    setItems(items.map(i =>
      i.id === box.itemId
        ? { ...i, count: i.count + 1 }
        : i
    ))

    setSelectedBoxId(null)
  }

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        {sidebarOpen && (
          <aside className="w-80 border-r border-gray-200 bg-white">
            {activeTab === "spaces" && (
              <SpacesPanel
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                selectedContainer={selectedContainer?.id || null}
                onSelectContainer={handleSelectContainer}
              />
            )}
            {activeTab === "items" && (
              <ItemsPanel
                onToggle={() => setSidebarOpen(!sidebarOpen)}
                items={items}
                onItemsChange={setItems}
              />
            )}
          </aside>
        )}

        {/* Main Content Area */}
        <main className="relative flex flex-1 flex-col">
          {/* Controls when box is selected */}
          {selectedBoxId && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-10 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3">
              <span className="font-semibold">Box Selected</span>
              <button
                onClick={() => handleDeleteBox(selectedBoxId)}
                className="px-4 py-1 bg-red-500 hover:bg-red-600 rounded text-sm transition-colors"
              >
                Delete
              </button>
              <button
                onClick={() => setSelectedBoxId(null)}
                className="px-4 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          )}

          {/* 3D Viewport */}
          <div className="flex-1 bg-gray-100">
            <ViewportCanvas
              container={selectedContainer}
              items={items}
              placedBoxes={placedBoxes}
              selectedBoxId={selectedBoxId}
              onPlaceBox={handlePlaceBox}
              onSelectBox={setSelectedBoxId}
            />
          </div>

          {/* Bottom Shipment Panel */}
          <ShipmentPanel container={selectedContainer} />

          {/* Load Button */}
          <Button
            size="lg"
            className="absolute bottom-32 right-8 h-24 w-24 rounded-full bg-blue-400 text-2xl font-semibold text-white shadow-lg hover:bg-blue-500"
            onClick={() => {
              if (!selectedContainer) return

              const { placed, remainingItems } = autoLoadItems(
                selectedContainer,
                items,
                placedBoxes
              )

              if (placed.length === 0) return

              setPlacedBoxes(prev => [...prev, ...placed])
              setItems(remainingItems)
              setSelectedBoxId(null)
            }}

          >
            Load
          </Button>
        </main>
      </div>
    </div>
  )
}