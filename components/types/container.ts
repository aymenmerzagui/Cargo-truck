// types/container.ts or lib/containers.ts

export interface Container {
  id: string
  name: string
  type: string
  dimensions: string
  weight: string
  icon: string
}

export const containers: Container[] = [
  {
    id: "1",
    name: "Container 40' ...",
    type: "Container",
    dimensions: "1203.2 x 235.2 x 238.5 cm",
    weight: "26600 kg",
    icon: "/container-icon.png",
  },
  {
    id: "2",
    name: "Container 40' ...",
    type: "Container",
    dimensions: "1205.1 x 234 x 238 cm",
    weight: "27397 kg",
    icon: "/container-icon.png",
  },
  {
    id: "3",
    name: "Container 40' ...",
    type: "Container",
    dimensions: "1211.7 x 238.8 x 269.4 cm",
    weight: "29800 kg",
    icon: "/container-icon.png",
  },
  {
    id: "4",
    name: "Container 45' ...",
    type: "Container",
    dimensions: "1358.2 x 234.7 x 269 cm",
    weight: "28390 kg",
    icon: "/container-icon.png",
  },
  {
    id: "5",
    name: "US Container 2...",
    type: "Container",
    dimensions: "589.3 x 233.7 x 238.8 cm",
    weight: "22100 kg",
    icon: "/container-icon.png",
  },
  {
    id: "6",
    name: "US Container 4...",
    type: "Container",
    dimensions: "1193.8 x 233.7 x 238.8 cm",
    weight: "27397 kg",
    icon: "/container-icon.png",
  },
  {
    id: "7",
    name: "US Container 4...",
    type: "Container",
    dimensions: "1204 x 233.7 x 269.2 cm",
    weight: "29600 kg",
    icon: "/container-icon.png",
  },
  {
    id: "8",
    name: "US Container 4...",
    type: "Container",
    dimensions: "1358.9 x 236.2 x 269.2 cm",
    weight: "28390 kg",
    icon: "/container-icon.png",
  },
  {
    id: "9",
    name: "US Container 4...",
    type: "Container",
    dimensions: "1447.8 x 248.9 x 269.2 cm",
    weight: "26600 kg",
    icon: "/container-icon.png",
  },
  {
    id: "10",
    name: "Standard Mini ...",
    type: "Lorry\n2 Axle",
    dimensions: "420 x 180 x 184 cm",
    weight: "27000 kg",
    icon: "/truck-icon.png",
  },
]