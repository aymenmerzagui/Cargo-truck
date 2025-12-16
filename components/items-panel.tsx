"use client"

import type React from "react"
import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ChevronRight, Trash2, RotateCcw, Check, Upload, Plus } from "lucide-react"
import StepPreviewDialog from "@/components/step-preview-dialog"

export interface Item {
  id: string
  name: string
  color: string
  length: number
  width: number
  height: number
  weight: number
  count: number
  stackable: boolean
  turnable: boolean
  tiltable: boolean
}

interface ItemsPanelProps {
  onToggle: () => void
  items: Item[]
  onItemsChange: (items: Item[]) => void
  selectedItemId?: string | null
  onSelectItem?: (itemId: string | null) => void
}

export default function ItemsPanel({ 
  onToggle, 
  items, 
  onItemsChange,
  selectedItemId = null,
  onSelectItem = () => {}
}: ItemsPanelProps) {
  const [selectedItem, setSelectedItem] = useState<string | null>(null)
  const [inputMode, setInputMode] = useState<"manual" | "file">("manual")
  
  // STEP preview dialog state
  const [previewOpen, setPreviewOpen] = useState(false)
  const [uploadedFileName, setUploadedFileName] = useState("")
  const [stlFile, setStlFile] = useState("")
  const [dimensions, setDimensions] = useState({ x: 0, y: 0, z: 0 })

  const handleConfirmItem = (data: {
    name: string
    length: number
    width: number
    height: number
    weight: number
  }) => {
    const newItem: Item = {
      id: `item-${Date.now()}`,
      name: data.name,
      color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
      length: data.length,
      width: data.width,
      height: data.height,
      weight: data.weight,
      count: 1,
      stackable: false,
      turnable: false,
      tiltable: false,
    }

    onItemsChange([...items, newItem])
    setSelectedItem(newItem.id)
  }

  const addManualItem = () => {
    const newItem: Item = {
      id: `item-${Date.now()}`,
      name: `Item ${items.length + 1}`,
      color: `#${Math.floor(Math.random() * 16777215).toString(16)}`,
      length: 100,
      width: 100,
      height: 100,
      weight: 10,
      count: 1,
      stackable: false,
      turnable: false,
      tiltable: false,
    }

    onItemsChange([...items, newItem])
    setSelectedItem(newItem.id)
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    console.log("Uploading STEP file:", file.name)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch("http://localhost:8000/upload-step", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const data = await response.json()
      console.log("Upload response:", data)

      // Check if we got valid data
      if (!data.stl_file) {
        throw new Error("Invalid response from server")
      }

      // Backend returns "bounding_box" with x, y, z (in mm)
      // Convert mm to cm for our UI
      const bbox = data.bounding_box || { x: 100, y: 100, z: 100 }
      
      // Open preview dialog with the data
      setUploadedFileName(file.name)
      setStlFile(data.stl_file)
      setDimensions({
        x: bbox.x / 10, // mm to cm
        y: bbox.y / 10, // mm to cm
        z: bbox.z / 10, // mm to cm
      })
      setPreviewOpen(true)

    } catch (error) {
      console.error("Error uploading file:", error)
      console.error("Full error details:", error)
      
      // More helpful error message
      const errorMessage = error instanceof Error ? error.message : "Unknown error"
      alert(`Failed to upload STEP file: ${errorMessage}\n\nMake sure:\n- Backend server is running on http://localhost:8000\n- STEP file is valid\n- Server has proper STEP parsing libraries installed`)
    }

    // Reset file input
    event.target.value = ""
  }

  const updateItem = (itemId: string, field: keyof Item, value: any) => {
    onItemsChange(
      items.map((item) => (item.id === itemId ? { ...item, [field]: value } : item))
    )
  }

  const deleteItem = (itemId: string) => {
    onItemsChange(items.filter((item) => item.id !== itemId))
    if (selectedItem === itemId) {
      setSelectedItem(null)
    }
  }

  const handleSelectItemClick = (itemId: string) => {
    const newSelection = selectedItemId === itemId ? null : itemId
    onSelectItem(newSelection)
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">Items</h2>
        <Button variant="ghost" size="icon" onClick={onToggle}>
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      {/* Instruction Banner - shows when item is selected */}
      {selectedItemId && (
        <div className="border-b border-blue-200 bg-blue-50 p-3">
          <p className="text-sm font-medium text-blue-900">
            📦 Click inside the container to place "{items.find(i => i.id === selectedItemId)?.name}"
          </p>
        </div>
      )}

      {/* Input Mode Selector and Action Buttons */}
      <div className="border-b border-gray-200 p-4">
        <div className="mb-3 flex gap-2">
          <Button
            variant={inputMode === "manual" ? "default" : "outline"}
            size="sm"
            className="flex-1"
            onClick={() => setInputMode("manual")}
          >
            Manual Input
          </Button>
          <Button
            variant={inputMode === "file" ? "default" : "outline"}
            size="sm"
            className="flex-1"
            onClick={() => setInputMode("file")}
          >
            Upload STEP File
          </Button>
        </div>

        {inputMode === "manual" ? (
          <Button onClick={addManualItem} className="w-full" size="sm">
            <Plus className="mr-2 h-4 w-4" />
            Add New Item
          </Button>
        ) : (
          <div className="relative">
            <input
              type="file"
              accept=".step,.stp"
              onChange={handleFileUpload}
              className="absolute inset-0 z-10 cursor-pointer opacity-0"
              id="step-file-input"
            />
            <Button className="w-full" size="sm" asChild>
              <label htmlFor="step-file-input" className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                Upload STEP File (.step, .stp)
              </label>
            </Button>
          </div>
        )}
      </div>

      {/* Items List */}
      <div className="flex-1 overflow-y-auto p-4">
        {items.length === 0 ? (
          <div className="flex h-full items-center justify-center text-center text-gray-500">
            <div>
              <p className="mb-2 text-sm">No items yet</p>
              <p className="text-xs">
                {inputMode === "manual"
                  ? 'Click "Add New Item" to get started'
                  : 'Upload a STEP file to get started'}
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {items.map((item) => (
              <div
                key={item.id}
                onClick={() => handleSelectItemClick(item.id)}
                className={`rounded-lg border bg-white p-3 transition-all cursor-pointer ${
                  selectedItemId === item.id 
                    ? "border-blue-400 shadow-md ring-2 ring-blue-200" 
                    : "border-gray-200 hover:border-blue-200"
                }`}
              >
                <div className="mb-3 flex items-center gap-2">
                  <input
                    type="color"
                    value={item.color}
                    onChange={(e) => {
                      e.stopPropagation()
                      updateItem(item.id, "color", e.target.value)
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="h-8 w-8 cursor-pointer rounded border border-gray-300"
                  />
                  <Input
                    value={item.name}
                    onChange={(e) => {
                      e.stopPropagation()
                      updateItem(item.id, "name", e.target.value)
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1"
                    placeholder="Item name"
                  />
                  {selectedItemId === item.id && (
                    <Check className="h-5 w-5 text-blue-500" />
                  )}
                </div>

                {/* Orientation Options */}
                <div className="mb-3 flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="outline"
                    size="icon"
                    className={`h-9 w-9 ${item.stackable ? "bg-blue-50 border-blue-300" : ""}`}
                    onClick={() => updateItem(item.id, "stackable", !item.stackable)}
                    title="Stackable"
                  >
                    <div className="flex flex-col gap-0.5">
                      <div className="h-1 w-4 bg-current" />
                      <div className="h-1 w-4 bg-current" />
                    </div>
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className={`h-9 w-9 ${item.turnable ? "bg-blue-50 border-blue-300" : ""}`}
                    onClick={() => updateItem(item.id, "turnable", !item.turnable)}
                    title="Turnable"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    className={`h-9 w-9 ${item.tiltable ? "bg-blue-50 border-blue-300" : ""}`}
                    onClick={() => updateItem(item.id, "tiltable", !item.tiltable)}
                    title="Tiltable"
                  >
                    <div className="h-4 w-4 rotate-45 border-2 border-current" />
                  </Button>
                </div>

                {/* Dimensions */}
                <div className="mb-3 grid grid-cols-3 gap-2" onClick={(e) => e.stopPropagation()}>
                  <div>
                    <label className="mb-1 block text-xs text-gray-600">Length(cm)</label>
                    <Input
                      type="number"
                      value={item.length}
                      onChange={(e) => updateItem(item.id, "length", Number(e.target.value))}
                      className="h-9"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-gray-600">Width(cm)</label>
                    <Input
                      type="number"
                      value={item.width}
                      onChange={(e) => updateItem(item.id, "width", Number(e.target.value))}
                      className="h-9"
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs text-gray-600">Height(cm)</label>
                    <Input
                      type="number"
                      value={item.height}
                      onChange={(e) => updateItem(item.id, "height", Number(e.target.value))}
                      className="h-9"
                    />
                  </div>
                </div>

                {/* Weight and Count */}
                <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                  <div className="flex-1">
                    <label className="mb-1 block text-xs text-gray-600">Weight(kg)</label>
                    <Input
                      type="number"
                      value={item.weight}
                      onChange={(e) => updateItem(item.id, "weight", Number(e.target.value))}
                      className="h-9"
                    />
                  </div>
                  <div className="w-24">
                    <label className="mb-1 block text-xs text-gray-600">Count</label>
                    <div className="flex items-center gap-1">
                      <Input
                        type="number"
                        value={item.count}
                        onChange={(e) => updateItem(item.id, "count", Math.max(0, Number(e.target.value)))}
                        className="h-9"
                      />
                      <div className="flex flex-col gap-0.5">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-4 w-4 p-0"
                          onClick={() => updateItem(item.id, "count", item.count + 1)}
                        >
                          ▲
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-4 w-4 p-0"
                          onClick={() => updateItem(item.id, "count", Math.max(0, item.count - 1))}
                        >
                          ▼
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-end">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-9 w-9 text-red-500 hover:bg-red-50 hover:text-red-600"
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteItem(item.id)
                      }}
                      title="Delete item"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* STEP Preview Dialog */}
      <StepPreviewDialog
        open={previewOpen}
        onOpenChange={setPreviewOpen}
        stlFile={stlFile}
        dimensions={dimensions}
        fileName={uploadedFileName}
        onConfirm={handleConfirmItem}
      />
    </div>
  )
}