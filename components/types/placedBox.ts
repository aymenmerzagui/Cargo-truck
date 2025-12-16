export interface PlacedBox {
  id: string // unique ID for this placed box instance
  itemId: string // reference to the original item
  name: string
  length: number // in cm
  width: number // in cm
  height: number // in cm
  color: string
  x: number // position in meters (3D space)
  y: number // position in meters (3D space)
  z: number // position in meters (3D space)
  rotation: number // rotation in radians around Y axis
}