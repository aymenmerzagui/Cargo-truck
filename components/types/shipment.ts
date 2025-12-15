import { Container } from "./container"
import { PlacedBox } from "./placedBox"

export interface Shipment {
  id: string
  name: string
  container: Container | null
  placedBoxes: PlacedBox[]
  createdAt: Date
}