"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ChevronRight, Filter } from "lucide-react"

import { Container, containers  } from "@/components/types/container"



interface SpacesPanelProps {
  onToggle: () => void
  selectedContainer: string | null
  onSelectContainer: (id: string) => void
}

export default function SpacesPanel({ onToggle, selectedContainer, onSelectContainer }: SpacesPanelProps) {
  const [searchQuery, setSearchQuery] = useState("")

  const filteredContainers = containers.filter(
    (container) =>
      container.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      container.dimensions.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">Spaces</h2>
        <Button variant="ghost" size="icon" onClick={onToggle}>
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      {/* Search and Filter */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex gap-2">
          <Input
            type="text"
            placeholder="Search Spaces..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1"
          />
          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Container List */}
      <div className="flex-1 overflow-y-auto">
        {filteredContainers.map((container) => (
          <button
            key={container.id}
            onClick={() => onSelectContainer(container.id)}
            className={`flex w-full items-center gap-3 border-b border-gray-100 p-4 text-left transition-colors hover:bg-gray-50 ${
              selectedContainer === container.id ? "bg-blue-50" : ""
            }`}
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
              <div className="h-8 w-8 rounded bg-blue-700" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <h3 className="truncate text-sm font-semibold text-gray-900">{container.name}</h3>
                <span className="shrink-0 text-xs text-gray-500">{container.type}</span>
              </div>
              <p className="text-xs text-gray-600">{container.dimensions}</p>
              <p className="text-xs text-gray-500">{container.weight}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
