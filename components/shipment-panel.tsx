"use client"

import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Save, FileText } from "lucide-react"
import { Container } from "@/components/types/container"
interface ShipmentPanelProps {
  container: Container | null
}

export default function ShipmentPanel({ container }: ShipmentPanelProps) {
  return (
    <div className="border-t border-gray-200 bg-white">
      <div className="flex items-center gap-4 px-6 py-4">
        {/* Shipment Name Input */}
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" className="h-12 w-12 bg-blue-100 hover:bg-blue-200">
            <Save className="h-5 w-5 text-blue-600" />
          </Button>
          <div className="flex-1">
            <Input
              placeholder="Shipment Name"
              className="h-12 min-w-[200px] border-gray-300"
              defaultValue="Shipment Name"
            />
          </div>
        </div>

        {/* Container Info */}
        <div className="ml-auto flex items-center gap-6 rounded-lg border border-gray-200 bg-gray-50 px-6 py-3">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="h-12 w-12 bg-white">
              <FileText className="h-5 w-5 text-gray-600" />
            </Button>
            <div>
              <div className="text-sm font-semibold text-gray-900">Container 20'</div>
              <div className="text-xs text-gray-600">Container</div>
            </div>
          </div>

          <div className="h-10 w-px bg-gray-300" />

          <div className="grid grid-cols-4 gap-6 text-sm">
            <div>
              <div className="text-xs text-gray-500">Length</div>
              <div className="font-semibold text-gray-900">575.6 cm</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Width</div>
              <div className="font-semibold text-gray-900">235.2 cm</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Height</div>
              <div className="font-semibold text-gray-900">238.5 cm</div>
            </div>
            <div>
              <div className="text-xs text-gray-500">Max Load</div>
              <div className="font-semibold text-gray-900">28200 kg</div>
            </div>
          </div>

          <div className="h-10 w-px bg-gray-300" />

          <div>
            <div className="text-xs text-gray-500">Volume</div>
            <div className="font-semibold text-gray-900">
              32.2 m<sup>3</sup>
            </div>
          </div>

          <Button variant="ghost" size="icon" className="h-10 w-10 bg-blue-100 hover:bg-blue-200">
            <FileText className="h-5 w-5 text-blue-600" />
          </Button>
        </div>
      </div>

      {/* Upload Button */}
      <div className="absolute bottom-4 left-8">
        <Button variant="outline" size="lg" className="h-12 gap-2 rounded-lg bg-blue-100 hover:bg-blue-200">
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
        </Button>
      </div>
    </div>
  )
}
