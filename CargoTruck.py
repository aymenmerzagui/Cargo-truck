import streamlit as st
import streamlit.components.v1 as components
st.set_page_config(layout='wide')

components.html('''
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { overflow: hidden; height: 100%; }
#container { position: relative; width: 100%; height: 100%; }

/* Top-left control strip */
.toolbar {
  position: absolute; top: 16px; left: 16px; z-index: 20;
  display: flex; gap: 8px; flex-wrap: wrap;
  background: rgba(255,255,255,0.9); padding: 10px; border-radius: 10px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

.toolbar button, .toolbar label {
  font: 13px/1.2 system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

.toolbar button {
  padding: 6px 10px; border: 1px solid #e5e7eb; border-radius: 8px; background: white; cursor: pointer;
}
.toolbar button:hover { background: #f3f4f6; }

#customBoxForm {
  display: none; position:absolute; top: 90px; left: 16px; z-index: 21;
  background:white; padding:12px; border-radius:10px;
  box-shadow:0 10px 30px rgba(0,0,0,0.2);
  min-width: 260px;
}
#customBoxForm label { display:block; margin-bottom:6px; font-size: 13px; }
#customBoxForm input[type="number"],
#customBoxForm input[type="text"] { width: 100%; padding:6px; margin-top:2px; border:1px solid #e5e7eb; border-radius:6px; }
#customBoxForm .row { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
#customBoxForm .actions { display:flex; gap:8px; margin-top:8px; }
#statusPanel {
  position: absolute; bottom: 16px; left: 16px; z-index: 20;
  background: rgba(17,24,39,0.85); color: #e5e7eb; padding: 8px 10px; border-radius: 10px; font-size: 13px;
}
#legend { position: absolute; bottom: 16px; right: 16px; z-index: 20; background: rgba(255,255,255,0.9); color: #111827; padding: 8px 10px; border-radius: 10px; font-size: 12px; }

#groupsPanel {
  position: fixed;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 250px;
  transition: transform 0.3s;
  z-index: 10; /* groups behind custom panel */
}

#toggleGroupsBtn {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 0 8px 8px 0;
  background: white;
  cursor: pointer;
  font-weight: bold;
}

#groupsList {
  position: relative;
  left: -260px; /* hidden by default */
  width: 260px;
  background: #f9f9f9;
  border-radius: 0 8px 8px 0;
  box-shadow: 3px 3px 15px rgba(0,0,0,0.15);
  overflow-y: auto;
  max-height: 80vh;
  padding: 10px;
  gap: 6px;
  transition: left 0.3s ease;
}

#groupsList.show { left: 0; }

.group {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 6px;
  background: #fff;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.group.dragging {
  opacity: 0.6;
  transform: scale(0.995);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.groupHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
  margin-bottom: 4px;
}

.groupHeader .actions button {
  margin-left: 4px;
  padding: 2px 6px;
  font-size: 12px;
  border-radius: 4px;
  cursor: pointer;
}
.groupHeader .actions button.deleteBtn {
  background: #ff4d4d;
  color: white;
  font-weight: bold;
}

.groupContent {
  display: none;
  padding-left: 6px;
  font-size: 13px;
}


#customboxform {
  position: fixed;
  left: 0;
  top: 10%;
  width: 250px;
  transition: transform 0.3s;
  z-index: 20; /* custom panel above groups */
}
</style>

<div id="container">
  <div class="toolbar">
    <button id="addBoxBtn">Add Box</button>
    <button id="customBoxBtn">Custom Box</button>
    <button id="deleteBoxBtn" style="display:none;">Delete Cube</button>
    <button id="toggleTrailerBtn">Toggle Trailer</button>
    <button id="listStoredBtn">List Stored</button>
    <button id="emptyTrailerBtn">Empty Trailer</button>
    <label style="display:flex; align-items:center; gap:6px;">
      <input type="checkbox" id="lockStoredChk" />
      Lock when stored
    </label>
  </div>

  <div id="customBoxForm">
    <div class="row">
      <label>Width (w): <input type="number" id="boxWidth" value="1" step="0.1" min="0.1"></label>
      <label>Height (h): <input type="number" id="boxHeight" value="1" step="0.1" min="0.1"></label>
    </div>
    <div class="row">
      <label>Depth (d): <input type="number" id="boxDepth" value="1" step="0.1" min="0.1"></label>
      <label>Color: <input type="color" id="boxColor" value="#ff0000"></label>
    </div>
    <label>Text (optional): <input type="text" id="boxText" value=""></label>
    <div class="actions">
      <button id="createCustomBox">Create Box</button>
      <button id="cancelCustomBox">Cancel</button>
    </div>
  </div>

  <div id="statusPanel">Boxes: <span id="countAll">0</span> • Stored in trailer: <span id="countStored">0</span></div>
  <div id="legend"></div>
<div id="groupsPanel">
  <button id="toggleGroupsBtn">Groups ▸</button>
  <div id="groupsList">
    <button id="addGroupBtn">+ Add Group</button>
    <div id="groupItems"></div>
  </div>
</div>

</div>

<script type="module">
import * as THREE from 'https://cdn.skypack.dev/three@0.128.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.128.0/examples/jsm/controls/OrbitControls.js';
import { DragControls } from 'https://cdn.skypack.dev/three@0.128.0/examples/jsm/controls/DragControls.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color('#e6f2ff');
const camera = new THREE.PerspectiveCamera(45, window.innerWidth/window.innerHeight, 0.1, 200);
camera.position.set(10, 8, 14);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('container').appendChild(renderer.domElement);

/* Controls & lights */
const orbit = new OrbitControls(camera, renderer.domElement);
orbit.enableDamping = true;
scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(8, 12, 6);
scene.add(dirLight);
const floorColliders = [];
                
const groups = []; // array of { name, cubes: [] }

const toggleGroupsBtn = document.getElementById('toggleGroupsBtn');
const groupsList = document.getElementById('groupsList');
const addGroupBtn = document.getElementById('addGroupBtn');
const groupItems = document.getElementById('groupItems');

/* Ground */
const grid = new THREE.GridHelper(30, 30, 0x444444, 0xaaaaaa);
scene.add(grid);
                
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(30, 30),
  new THREE.MeshBasicMaterial({ visible: false })
);
ground.rotation.x = -Math.PI/2;
ground.position.y = 0;
scene.add(ground);
floorColliders.push(ground);
                
/* Globals */
const YARD_BOUND = 12;
const MIN = -YARD_BOUND, MAX = YARD_BOUND;
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
const cubes = [];
const arrows = [];
let hoverObj = null, activeCube = null;
let dragControls = null;
let boxCount = 0;

let trailer = null;
let trailerVisible = true;
let trailerInterior = null;
let trailerBox = null;

// NEW: store invisible wall colliders
const wallColliders = [];


/* Trailer dimensions (inner usable space) */
const T_W = 6;   // inner width (x)
const T_H = 3;   // inner height (y)
const T_D = 12;  // inner depth (z)
const WALL_T = 0.1; // wall thickness
const FLOOR_T = 0.2;

/* UI elements */
const elDelete = document.getElementById('deleteBoxBtn');
const elForm = document.getElementById('customBoxForm');
const elCountAll = document.getElementById('countAll');
const elCountStored = document.getElementById('countStored');
const lockWhenStored = document.getElementById('lockStoredChk');

/* Helpers */
function setCounts() {
  elCountAll.textContent = String(cubes.length);
  elCountStored.textContent = String(cubes.filter(c => c.userData.inTrailer).length);
}

function toHex(n){ return ('000000' + n.toString(16)).slice(-6); }

/* Create trailer (hollow, open at the back) */
function createTrailer() {
  // Remove previous trailer and its colliders from scene
  if (trailer) {
    scene.remove(trailer);
    trailer = null;
  }
  // remove old colliders from scene as well
  while (wallColliders.length) {
    const c = wallColliders.pop();
    if (c && c.parent) c.parent.remove(c);
  }

  trailer = new THREE.Group();

  // Base position: place floor on y=0 so boxes roll in on the grid
  const cx = 0, cy = FLOOR_T/2, cz = 0;

  // === FLOOR ===
  const floor = new THREE.Mesh(
    new THREE.BoxGeometry(T_W + 2*WALL_T, FLOOR_T, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.1, roughness: 0.8 })
  );
  floor.position.set(cx, cy, cz);
  trailer.add(floor);

// Floor collider
const floorBlocker = new THREE.Mesh(
  new THREE.BoxGeometry(T_W, FLOOR_T, T_D),
  new THREE.MeshBasicMaterial({ visible: false })
);
floorBlocker.position.set(cx, cy, cz);
scene.add(floorBlocker);

// ✅ Add to a separate array for floors
floorColliders.push(floorBlocker);


  // === ROOF ===
  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(T_W + 2*WALL_T, WALL_T, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xdddddd, transparent: true, opacity: 0.4 })
  );
  roof.position.set(cx, T_H + FLOOR_T - WALL_T/2, cz);
  trailer.add(roof);

  // Roof collider
  const roofBlocker = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, WALL_T, T_D),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  roofBlocker.position.copy(roof.position);
  scene.add(roofBlocker);
  wallColliders.push(roofBlocker);

  // === LEFT WALL ===
  const left = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xbfc7cf, transparent: true, opacity: 0.4 })
  );
  left.position.set(cx - (T_W/2 + WALL_T/2), FLOOR_T + T_H/2, cz);
  trailer.add(left);

  // Left collider
  const leftBlocker = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  leftBlocker.position.copy(left.position);
  scene.add(leftBlocker);
  wallColliders.push(leftBlocker);

  // === RIGHT WALL ===
  const right = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xbfc7cf, transparent: true, opacity: 0.4 })
  );
  right.position.set(cx + (T_W/2 + WALL_T/2), FLOOR_T + T_H/2, cz);
  trailer.add(right);

  // Right collider
  const rightBlocker = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  rightBlocker.position.copy(right.position);
  scene.add(rightBlocker);
  wallColliders.push(rightBlocker);

  // === FRONT WALL ===
  const front = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, T_H, WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xb5c1cd, transparent: true, opacity: 0.85 })
  );
  front.position.set(cx, FLOOR_T + T_H/2, cz + (T_D/2 + WALL_T/2));
  trailer.add(front);

  // Front collider
  const frontBlocker = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, T_H, WALL_T),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  frontBlocker.position.copy(front.position);
  scene.add(frontBlocker);
  wallColliders.push(frontBlocker);

  // === EDGES ===
  const edges = new THREE.EdgesGeometry(new THREE.BoxGeometry(T_W + 2*WALL_T, T_H + FLOOR_T + WALL_T, T_D + WALL_T));
  const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x444444 }));
  line.position.set(cx, FLOOR_T + (T_H)/2 - WALL_T/2, cz);
  trailer.add(line);

  // Invisible interior volume mesh (for containment checks)
  trailerInterior = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, T_H, T_D),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  trailerInterior.position.set(cx, FLOOR_T + T_H/2, cz);
  trailer.add(trailerInterior);

  // Optional ramp at back
  const rampGeom = new THREE.PlaneGeometry(T_W, 2);
  const rampMat = new THREE.MeshStandardMaterial({ color: 0x999999, side: THREE.DoubleSide });
  const ramp = new THREE.Mesh(rampGeom, rampMat);
  ramp.rotation.x = -Math.PI/6;
  ramp.position.set(cx, FLOOR_T/2, cz - (T_D/2 + 0.8));
  // trailer.add(ramp);

  scene.add(trailer);

  // Compute interior box
  trailerBox = new THREE.Box3().setFromObject(trailerInterior);
}


createTrailer();

function resolveCollision(cube) {
  const cubeBox = new THREE.Box3().setFromObject(cube);

  // Check against wall colliders
  for (let collider of wallColliders) {
    const wallBox = new THREE.Box3().setFromObject(collider);
    if (cubeBox.intersectsBox(wallBox)) {
      const cubeSize = cube.geometry.parameters;
      const halfSize = {
        x: cubeSize.width / 2,
        y: cubeSize.height / 2,
        z: cubeSize.depth / 2
      };

      // Compute overlap amounts in each axis
      const dx1 = wallBox.max.x - cubeBox.min.x;
      const dx2 = cubeBox.max.x - wallBox.min.x;
      const dy1 = wallBox.max.y - cubeBox.min.y;
      const dy2 = cubeBox.max.y - wallBox.min.y;
      const dz1 = wallBox.max.z - cubeBox.min.z;
      const dz2 = cubeBox.max.z - wallBox.min.z;

      // Find the smallest overlap (minimum push-out distance)
      const minOverlap = Math.min(dx1, dx2, dy1, dy2, dz1, dz2);

      if (minOverlap === dx1) cube.position.x += dx1;
      else if (minOverlap === dx2) cube.position.x -= dx2;
      else if (minOverlap === dy1) cube.position.y += dy1;
      else if (minOverlap === dy2) cube.position.y -= dy2;
      else if (minOverlap === dz1) cube.position.z += dz1;
      else if (minOverlap === dz2) cube.position.z -= dz2;

      // Recalculate cubeBox after pushing
      cubeBox.setFromObject(cube);
    }
  }
}

                
/* Drag system refresh */
function refreshDragControls() {
  if (dragControls) dragControls.dispose();
  const draggables = cubes.filter(c => !(lockWhenStored.checked && c.userData.inTrailer));
  dragControls = new DragControls(draggables, camera, renderer.domElement);

  dragControls.addEventListener('hoveron', e => {
    // keep orbit active; visual hover handled by our raycaster
  });

  dragControls.addEventListener('dragstart', e => {
    orbit.enabled = false;
    elDelete.style.display = 'none';
    clearArrows();
    elForm.style.display = 'none';
    e.object.userData.prevPos = e.object.position.clone();
  });
                
// Move cube from prevPos toward targetPos in small steps to avoid tunneling.
// Only XZ movement; Y is locked to cube half-height.
function moveWithSweep(cube, targetPos) {
  scene.updateMatrixWorld(true);

  const prev = cube.userData.prevPos ? cube.userData.prevPos.clone() : cube.position.clone();
  const delta = new THREE.Vector3(
    targetPos.x - prev.x,
    0, // Y handled separately
    targetPos.z - prev.z
  );

  const dist = delta.length();
  if (dist === 0) {
    cube.position.copy(prev);
    cube.userData.prevPos = prev.clone();
    return true;
  }

  const geom = cube.geometry.parameters;
  const halfH = (geom.height || geom.h || 1) / 2;
  const halfW = (geom.width || geom.w || 1) / 2;
  const halfD = (geom.depth || geom.d || geom.width || 1) / 2;

  const smallestDim = Math.min(geom.width || geom.w || 1, geom.height || geom.h || 1, geom.depth || geom.d || 1);
  const stepSize = Math.min(0.25, Math.max(0.08, smallestDim * 0.25));
  const steps = Math.max(1, Math.ceil(dist / stepSize));

  const step = delta.clone().divideScalar(steps);
  let cur = prev.clone();
  let lastSafe = prev.clone();

  // Compute trailer world center once
  let trailerWorldCenter = null;
  if (trailerInterior) {
    trailerInterior.updateWorldMatrix(true, false);
    trailerWorldCenter = new THREE.Vector3();
    trailerInterior.getWorldPosition(trailerWorldCenter);
  }

  for (let i = 1; i <= steps; i++) {
    cur.add(step);
    cube.position.x = cur.x;
    cube.position.z = cur.z;

    // --- Opening intersection test ---
    let isTouchingOpening = false;
    if (trailerWorldCenter) {
      const backZ = trailerWorldCenter.z - (T_D / 2);
      const OPEN_THICKNESS = 0.22;
      const openingMin = new THREE.Vector3(
        trailerWorldCenter.x - T_W / 2,
        trailerWorldCenter.y - T_H / 2,
        backZ - OPEN_THICKNESS / 2
      );
      const openingMax = new THREE.Vector3(
        trailerWorldCenter.x + T_W / 2,
        trailerWorldCenter.y + T_H / 2,
        backZ + OPEN_THICKNESS / 2
      );
      const openingBox = new THREE.Box3(openingMin, openingMax);
      const cubeBox = new THREE.Box3().setFromObject(cube);
      const movingInto = (prev.z - cur.z) > 0.0001;

      if (cubeBox.intersectsBox(openingBox) && movingInto) {
        isTouchingOpening = true;
      }
    }

    if (isTouchingOpening) {
      // Snap to trailer floor
      cube.position.y = FLOOR_T + halfH;
    } else {
      // --- Try stacking directly on another cube ---
      let stacked = false;
      for (let other of cubes) {
        if (other === cube) continue;

        const b = new THREE.Box3().setFromObject(other);

        const aMinX = cur.x - halfW;
        const aMaxX = cur.x + halfW;
        const aMinZ = cur.z - halfD;
        const aMaxZ = cur.z + halfD;

        const overlapX = (aMinX < b.max.x) && (aMaxX > b.min.x);
        const overlapZ = (aMinZ < b.max.z) && (aMaxZ > b.min.z);
        if (!overlapX || !overlapZ) continue;

        const otherTop = b.max.y;
        cube.position.y = otherTop + halfH;
        stacked = true;
        break;
      }

      if (!stacked) {
        // --- Raycast fallback: drop onto floor or cubes ---
        const rayOrigin = cube.position.clone();
        rayOrigin.y += Math.max(2, halfH + 0.5);
        const downRay = new THREE.Raycaster(rayOrigin, new THREE.Vector3(0, -1, 0));

        const surfaces = floorColliders.concat(cubes.filter(c => c !== cube));
        const intersects = downRay.intersectObjects(surfaces, true);

        if (intersects.length > 0) {
          let maxY = -Infinity;
          intersects.forEach(hit => { if (hit.point.y > maxY) maxY = hit.point.y; });
          cube.position.y = maxY + halfH;
        } else {
          cube.position.y = halfH;
        }
      }
    }

    // --- Clamp inside trailer or yard ---
    if (trailerVisible && trailerInterior && isInsideTrailerByPos(cube)) clampInsideTrailer(cube);
    else clampYard(cube);

    // --- Collision check (but allow stacking touch) ---
    if (detectCollision(cube)) {
      cube.position.copy(lastSafe);
      return false;
    }

    lastSafe.copy(cube.position);
  }

  cube.userData.prevPos = cube.position.clone();
  return true;
}


dragControls.addEventListener('drag', e => {
  const cube = e.object;
  const targetPos = cube.position.clone();

  // move in X/Z using existing sweep (this also sets Y via the new stacking/raycast logic)
  moveWithSweep(cube, targetPos);

  // removed forced Y assignment — moveWithSweep already places/stacks the cube

  // clamp and collisions
  if (trailerVisible && isInsideTrailerByPos(cube)) clampInsideTrailer(cube);
  else clampYard(cube);

  if (detectCollision(cube)) {
    cube.position.copy(cube.userData.prevPos);
  }
});




 dragControls.addEventListener('dragend', e => {
   try {
     updateStoredState(e.object);
   } catch (err) {
     console.error('dragend handler error:', err);
   } finally {
     orbit.enabled = true;
   }
 });

}

/* Yard clamp (global bounds) */
function clampYard(obj) {
  const box = new THREE.Box3().setFromObject(obj);
  const size = new THREE.Vector3(); box.getSize(size);
  const hx = size.x/2, hz = size.z/2;
  obj.position.x = Math.min(MAX - hx, Math.max(MIN + hx, obj.position.x));
  obj.position.z = Math.min(MAX - hz, Math.max(MIN + hz, obj.position.z));
  // Keep on floor
  obj.position.y = Math.max(obj.geometry.parameters.height/2, obj.position.y);
}

/* Trailer clamp (stay within interior usable box) */
function clampInsideTrailer(obj) {
  if (!trailerBox) return;
  const half = new THREE.Vector3(T_W/2, T_H/2, T_D/2);
  const center = trailerInterior.position.clone(); // already in world coords within group
  // convert trailer interior position to world
  trailerInterior.updateWorldMatrix(true, false);
  const worldCenter = new THREE.Vector3();
  trailerInterior.getWorldPosition(worldCenter);

  const min = worldCenter.clone().add(new THREE.Vector3(-half.x, -half.y, -half.z));
  const max = worldCenter.clone().add(new THREE.Vector3( half.x,  half.y,  half.z));

  const h = obj.geometry.parameters.height/2;
  const w = obj.geometry.parameters.width/2;
  const d = obj.geometry.parameters.depth/2;

  obj.position.x = Math.min(max.x - w, Math.max(min.x + w, obj.position.x));
  obj.position.y = Math.min(max.y - h, Math.max(min.y + h, obj.position.y));
  obj.position.z = Math.min(max.z - d, Math.max(min.z + d, obj.position.z));
}

/* Is cube inside trailer (by its Box3 fully contained) */
function isInsideTrailer(obj) {
  if (!trailerBox) return false;
  const b = new THREE.Box3().setFromObject(obj);
  return trailerBox.containsBox(b);
}

/* Quicker "by position" check (center within interior) */
function isInsideTrailerByPos(obj) {
  if (!trailerBox) return false;
  const p = new THREE.Vector3();
  obj.getWorldPosition(p);
  return trailerBox.containsPoint(p);
}

// is the cube near the trailer opening (back side)? threshold in world units
function isNearOpening(cube, threshold = 0.6) {
  if (!trailerInterior) return false;

  // get trailer interior world center
  trailerInterior.updateWorldMatrix(true, false);
  const worldCenter = new THREE.Vector3();
  trailerInterior.getWorldPosition(worldCenter);

  // open side is at backZ (negative z in your setup)
  const backZ = worldCenter.z - (T_D / 2);

  // cube center in world coords
  const cubeCenter = new THREE.Vector3();
  cube.getWorldPosition(cubeCenter);

  // check X within trailer width (with small margin)
  const halfW = T_W / 2;
  const withinX = cubeCenter.x >= (worldCenter.x - halfW - 0.001) && cubeCenter.x <= (worldCenter.x + halfW + 0.001);

  // optionally check vertical overlap — but we just use X+Z test
  const dz = Math.abs(cubeCenter.z - backZ);

  return withinX && dz <= threshold;
}

                
/* Update stored state visuals + flag */
function updateStoredState(obj) {
  const nowInside = isInsideTrailer(obj);
  obj.userData.inTrailer = nowInside;

 let hex = obj.userData.baseColor || 0xffffff;
 if (obj.userData.groupId !== undefined) {
   const group = groups.find(g => g.id === obj.userData.groupId);
   if (group) {
     const col = group.color && group.color.isColor
       ? group.color
       : new THREE.Color(group.color || 0xffffff);
     hex = col.getHex();
   }
 }
 obj.material.forEach(m => m.color.setHex(hex));
 setCounts();
 // rebuild after the event loop to avoid interfering with DragControls internals
 setTimeout(refreshDragControls, 0);
}

/* Collision with other cubes - volumetric test (allows face-touching).
   If cube.userData._stackState && lifted === true -> ignore cube–cube checks
   (we already performed a clearance check before lifting). */
function detectCollision(cube) {
  // ensure world matrices are up-to-date
  scene.updateMatrixWorld(true);

  const a = new THREE.Box3().setFromObject(cube);

  // tolerances
  const EPS_XZ = 1e-5;  // very small tolerance for horizontal overlap
  const EPS_Y  = 1e-3;  // slightly larger tolerance for vertical (stacking)

  // cube–cube collisions
  const collideCubes = cubes.some(other => {
    if (other === cube) return false;
    const b = new THREE.Box3().setFromObject(other);

    const overlapX = Math.min(a.max.x, b.max.x) - Math.max(a.min.x, b.min.x);
    const overlapY = Math.min(a.max.y, b.max.y) - Math.max(a.min.y, b.min.y);
    const overlapZ = Math.min(a.max.z, b.max.z) - Math.max(a.min.z, b.min.z);

    // allow "touching" on Y (stacking) without counting as collision
    return (overlapX > EPS_XZ && overlapZ > EPS_XZ && overlapY > EPS_Y);
  });

  // cube–wall collisions (ignore floor colliders)
  const collideWalls = wallColliders
    .filter(collider => !floorColliders.includes(collider))
    .some(collider => {
      const b = new THREE.Box3().setFromObject(collider);

      const overlapX = Math.min(a.max.x, b.max.x) - Math.max(a.min.x, b.min.x);
      const overlapY = Math.min(a.max.y, b.max.y) - Math.max(a.min.y, b.min.y);
      const overlapZ = Math.min(a.max.z, b.max.z) - Math.max(a.min.z, b.min.z);

      return (overlapX > EPS_XZ && overlapY > EPS_Y && overlapZ > EPS_XZ);
    });

  return collideCubes || collideWalls;
}


/* Arrows */
function clearArrows() { arrows.forEach(a=>scene.remove(a)); arrows.length=0; }
function clearActiveCube(){ clearArrows(); activeCube=null; elDelete.style.display='none'; }

/* Hover highlight (red) */
window.addEventListener('mousemove', e=>{
  mouse.x=(e.clientX/window.innerWidth)*2-1;
  mouse.y=-(e.clientY/window.innerHeight)*2+1;
  if(hoverObj){ hoverObj.material.forEach(mat => {
  let hex = hoverObj.userData.groupId !== undefined 
              ? groups.find(g => g.id === hoverObj.userData.groupId).color.getHex() 
              : hoverObj.userData.baseColor || 0xffffff;
  mat.color.setHex(hex);
}); hoverObj=null; }
  raycaster.setFromCamera(mouse,camera);
  const hits = raycaster.intersectObjects(cubes,false);
  if(hits.length>0){ hoverObj=hits[0].object; hoverObj.material.forEach(mat => mat.color.set(0xff0000)); }
});

/* Double click: select (arrows) + delete button */
renderer.domElement.addEventListener('dblclick', e=>{
  mouse.x=(e.clientX/window.innerWidth)*2-1;
  mouse.y=-(e.clientY/window.innerHeight)*2+1;
  raycaster.setFromCamera(mouse,camera);
  const hits=raycaster.intersectObjects(cubes,false);
  if(hits.length>0){
    activeCube=hits[0].object;
    showArrows(activeCube);
    const btn=elDelete;
    btn.style.display='block';
    btn.onclick=()=>{
clearArrows();

      // if the active cube belonged to a group, remove it from that group UI/state first
      if (activeCube && activeCube.userData && activeCube.userData.groupId !== undefined) {
        // clean up group membership & UI
        removeCubeFromGroup(activeCube);
      }

      // remove from scene & global cubes array
      if (activeCube && activeCube.parent) scene.remove(activeCube);
      const idx = activeCube ? cubes.indexOf(activeCube) : -1;
      if (idx >= 0) cubes.splice(idx, 1);

      activeCube = null;
      btn.style.display = 'none';
      setCounts();
      refreshDragControls();
      
    }
  }
  orbit.enabled = true;
});
                
toggleGroupsBtn.addEventListener('click', () => {
  groupsList.classList.toggle('show');
});

addGroupBtn.addEventListener('click', () => {
  const name = prompt("Group name:", "New Group");
  if (!name) return;
  addGroup(name);
});
function updateLegend() {
  const legendEl = document.getElementById('legend');
  legendEl.innerHTML = ''; // clear

  groups.forEach(g => {
    const count = g.cubes.length;
    const item = document.createElement('div');
    item.style.display = 'flex';
    item.style.alignItems = 'center';
    item.style.marginBottom = '4px';

    const colorBox = document.createElement('span');
    colorBox.style.display = 'inline-block';
    colorBox.style.width = '14px';
    colorBox.style.height = '14px';
    colorBox.style.background = '#' + g.color.getHexString();
    colorBox.style.marginRight = '6px';
    colorBox.style.borderRadius = '3px';

    const text = document.createElement('span');
    text.textContent = `${g.name} (${count})`;
    text.style.fontSize = '12px';

    item.appendChild(colorBox);
    item.appendChild(text);
    legendEl.appendChild(item);
  });
}

/* Helper: set visibility for all cubes in a group */
/* small helper: SVG eye / eye-off icons as HTML strings */
function eyeIconHtml(visible) {
  if (visible) {
    // eye (visible)
    return `
      <svg class="eyeIcon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`;
  } else {
    // eye-off (hidden)
    return `
      <svg class="eyeOffIcon" width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M17.94 17.94A10.94 10.94 0 0 1 12 19c-7 0-11-7-11-7a22.9 22.9 0 0 1 5.58-6.22" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M1 1l22 22" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>`;
  }
}

/* Helper: set visibility for all cubes in a group (updates icon too) */
function setGroupVisibility(group, visible) {
  group.visible = visible;
  group.cubes = group.cubes.filter(c => c && c.parent);

  // set each cube's visibility and update its per-list eye button if present
  group.cubes.forEach(c => {
    c.visible = visible;

    // update cube's group list item eye button (if exists)
    const item = c.userData.groupListItem;
    if (item) {
      const eyeBtn = item.querySelector('.cubeEyeBtn');
      if (eyeBtn) {
        eyeBtn.innerHTML = eyeIconHtml(Boolean(c.visible));
        eyeBtn.title = c.visible ? 'Hide cube' : 'Show cube';
      }
    }
  });

  // Update the group's toggle button icon & tooltip if present
  if (group.element) {
    const btn = group.element.querySelector('.toggleVisibleBtn');
    if (btn) {
      btn.innerHTML = eyeIconHtml(visible);
      btn.title = visible ? 'Hide group' : 'Show group';
      btn.setAttribute('aria-pressed', String(!visible));
    }
  }
}


/* Replacement addGroup function: creates per-group eye icon button */
/* small helper: plus SVG icon */
function plusIconHtml() {
  return `
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
}

// call to rebuild the `groups` array to match the DOM order in #groupItems
function reorderGroupsFromDOM() {
  // collect group DOM nodes in current order
  const domList = Array.from(groupItems.children);
  const newOrder = [];

  domList.forEach((div, idx) => {
    const oldId = parseInt(div.dataset.id, 10);
    const groupObj = groups.find(g => g.id === oldId);
    if (groupObj) {
      // update dataset id and group's id to reflect new position
      div.dataset.id = idx;
      groupObj.id = idx;
      newOrder.push(groupObj);
    }
  });

  // replace groups array contents
  groups.length = 0;
  newOrder.forEach(g => groups.push(g));

  // update legend and drag controls so order changes are visible in UI
  updateLegend();
  setTimeout(refreshDragControls, 0);
}
// create a list item in a group's cubeList with eye + remove controls
function createCubeListItem(group, cube, cubeList) {
  // wrapper
  const item = document.createElement('div');
  item.style.display = 'flex';
  item.style.alignItems = 'center';
  item.style.justifyContent = 'space-between';
  item.style.gap = '8px';
  item.style.padding = '4px 0';

  // label (cube name/text)
  const label = document.createElement('span');
  label.style.fontSize = '13px';
  label.textContent = cube.userData.texts && cube.userData.texts[0]
    ? cube.userData.texts[0]
    : `Box ${cubes.indexOf(cube) + 1}`;

  // controls container
  const controls = document.createElement('div');
  controls.style.display = 'flex';
  controls.style.gap = '6px';
  controls.style.alignItems = 'center';

  // eye button
  const eyeBtn = document.createElement('button');
  eyeBtn.className = 'cubeEyeBtn';
  eyeBtn.type = 'button';
  eyeBtn.innerHTML = eyeIconHtml(Boolean(cube.visible));
  eyeBtn.title = cube.visible ? 'Hide cube' : 'Show cube';
  eyeBtn.style.border = 'none';
  eyeBtn.style.background = 'transparent';
  eyeBtn.style.cursor = 'pointer';
  eyeBtn.addEventListener('click', (ev) => {
    ev.stopPropagation();
    // toggle visibility
    cube.visible = !cube.visible;
    eyeBtn.innerHTML = eyeIconHtml(Boolean(cube.visible));
    eyeBtn.title = cube.visible ? 'Hide cube' : 'Show cube';
  });

  // remove/unassign button (small 'x' or trash)
  const removeBtn = document.createElement('button');
  removeBtn.className = 'cubeRemoveBtn';
  removeBtn.type = 'button';
  removeBtn.title = 'Remove from group';
  removeBtn.textContent = '✖';
  removeBtn.style.border = 'none';
  removeBtn.style.background = 'transparent';
  removeBtn.style.cursor = 'pointer';
  removeBtn.style.fontSize = '14px';
  removeBtn.addEventListener('click', (ev) => {
    ev.stopPropagation();

    // use helper: remove cube from its group and clean up UI
    removeCubeFromGroup(cube);
  });

  controls.appendChild(eyeBtn);
  controls.appendChild(removeBtn);

  item.appendChild(label);
  item.appendChild(controls);
  cubeList.appendChild(item);

  // keep a reference so other code can update/remove the DOM item
  cube.userData.groupListItem = item;

  return item;
}

// remove cube from whatever group it belongs to (cleans UI + state)
function removeCubeFromGroup(cube) {
  if (!cube || cube.userData.groupId === undefined) return;

  const gid = cube.userData.groupId;
  const group = groups.find(g => g.id === gid);
  if (!group) {
    delete cube.userData.groupId;
    return;
  }

  // remove from group's cubes array
  group.cubes = group.cubes.filter(c => c !== cube);

  // remove list item DOM if present
  if (cube.userData.groupListItem) {
    try { cube.userData.groupListItem.remove(); } catch (e) { /* ignore */ }
    cube.userData.groupListItem = null;
  }

  // restore cube color to its base color (if present)
  const baseHex = cube.userData.baseColor || 0xffffff;
  setCubeColorMaterials(cube, '#' + ('000000' + baseHex.toString(16)).slice(-6));

  // make the cube visible (groups control visibility; leaving visible is safer)
  cube.visible = true;

  // clear assignment
  delete cube.userData.groupId;

  // update UI
  setCounts();
  updateLegend();
  setTimeout(refreshDragControls, 0);
}

/* Replacement addGroup: plus icon button that appears after one click (expand) and is bottom-right */
function addGroup(name) {
  const colorInputValue = "#ffcc00";
  const color = new THREE.Color(colorInputValue);

  const groupId = groups.length;
  const groupDiv = document.createElement('div');
  groupDiv.classList.add('group');
  groupDiv.dataset.id = groupId;

  // make groupDiv positioned so the bottom-right plus can be absolute inside it
  groupDiv.style.position = 'relative';
  groupDiv.style.paddingBottom = '44px'; // reserve space for the bottom-right button

  groupDiv.innerHTML = `
    <div class="groupHeader" style="display:flex; align-items:center; gap:8px; cursor:pointer;">
      <input type="color" class="groupColor" value="${colorInputValue}" title="Group color">
      <span class="groupName">${name}</span>
      <div class="actions" style="margin-left:auto; display:flex; gap:6px; align-items:center;">
        <button class="toggleVisibleBtn" title="Hide group" aria-pressed="false">${eyeIconHtml(true)}</button>
        <button class="renameBtn" title="Rename group">✏️</button>
        <button class="deleteBtn" title="Delete group">🗑️</button>
      </div>
    </div>
    <div class="groupContent" style="display:none; padding:8px 8px 36px 8px;">
      <div class="cubeList"></div>
    </div>
  `;

  groupItems.appendChild(groupDiv);
    // Make group draggable and add drag handlers
  groupDiv.draggable = true;

  groupDiv.addEventListener('dragstart', (ev) => {
    ev.stopPropagation();
    groupDiv.classList.add('dragging');
    // store the group's dataset id so we can find it later
    ev.dataTransfer.setData('text/plain', groupDiv.dataset.id);
    ev.dataTransfer.effectAllowed = 'move';
  });

  groupDiv.addEventListener('dragend', (ev) => {
    ev.stopPropagation();
    groupDiv.classList.remove('dragging');
    // DOM was rearranged during dragover/drop; sync groups array
    reorderGroupsFromDOM();
  });

  // Allow dropping between group items: on dragover we insert the dragged element
  groupDiv.addEventListener('dragover', (ev) => {
    ev.preventDefault(); // allow drop
    ev.dataTransfer.dropEffect = 'move';
    const draggingEl = document.querySelector('.group.dragging');
    if (!draggingEl || draggingEl === groupDiv) return;

    // compute where to insert: before or after target depending on pointer
    const rect = groupDiv.getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    const parent = groupDiv.parentElement;

    if (ev.clientY < midY) {
      // insert before target
      parent.insertBefore(draggingEl, groupDiv);
    } else {
      // insert after target
      parent.insertBefore(draggingEl, groupDiv.nextSibling);
    }
  });

  // optional: support drop (some browsers need drop handler)
  groupDiv.addEventListener('drop', (ev) => {
    ev.preventDefault();
    ev.stopPropagation();
    const draggingEl = document.querySelector('.group.dragging');
    if (!draggingEl) return;
    // ensure final position (dragover already handled visual insertion)
    reorderGroupsFromDOM();
  });

  const groupObj = { id: groupId, name, color, cubes: [], element: groupDiv, visible: true };
  groups.push(groupObj);

  const header = groupDiv.querySelector('.groupHeader');
  const content = groupDiv.querySelector('.groupContent');
  const cubeList = content.querySelector('.cubeList');
  const colorInputEl = groupDiv.querySelector('.groupColor');
  const toggleVisibleBtn = groupDiv.querySelector('.toggleVisibleBtn');

  // create the bottom-right plus icon button (initially hidden)
  const addBtn = document.createElement('button');
  addBtn.className = 'addCubeBtnIcon';
  addBtn.type = 'button';
  addBtn.title = 'Add cube to group';
  addBtn.innerHTML = plusIconHtml();
  // style it (you can tweak styles)
  addBtn.style.position = 'absolute';
  addBtn.style.bottom = '8px';
  addBtn.style.right = '8px';
  addBtn.style.width = '36px';
  addBtn.style.height = '36px';
  addBtn.style.borderRadius = '8px';
  addBtn.style.border = '1px solid #ddd';
  addBtn.style.background = 'white';
  addBtn.style.display = 'none'; // hidden until the group is expanded
  addBtn.style.cursor = 'pointer';
  addBtn.style.boxShadow = '0 4px 10px rgba(0,0,0,0.08)';
  addBtn.style.alignItems = 'center';
  addBtn.style.justifyContent = 'center';
  addBtn.style.padding = '6px';
  addBtn.style.lineHeight = '0';
  // ensure icon inherits color
  addBtn.querySelectorAll('svg').forEach(s => s.style.color = '#111');

  groupDiv.appendChild(addBtn);

  // header click toggles expand/collapse and also shows/hides the plus button
  header.addEventListener('click', e => {
    // ignore clicks on the color input or header buttons themselves
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.closest('.actions')) return;

    // toggle content
    const nowVisible = content.style.display !== 'block';
    // collapse other groups (same behavior you had before)
    document.querySelectorAll('.groupContent').forEach(c => {
      if (c !== content) {
        c.style.display = 'none';
        // hide their add buttons if present
        const p = c.parentElement;
        if (p) {
          const otherAdd = p.querySelector('.addCubeBtnIcon');
          if (otherAdd) otherAdd.style.display = 'none';
        }
      }
    });

    content.style.display = nowVisible ? 'block' : 'none';

    // show/hide this group's plus button accordingly (only when content is open)
    addBtn.style.display = nowVisible ? 'flex' : 'none';
  });

  groupDiv.querySelector('.renameBtn').addEventListener('click', e => {
    e.stopPropagation();
    const newName = prompt("Rename group:", name);
    if (newName) {
      if (groups.some(g => g.name === newName)) { alert("Group name exists!"); return; }
      groupDiv.querySelector('.groupName').textContent = newName;
      const group = groups.find(g => g.id === groupId);
      if (group) group.name = newName;
      updateLegend();
    }
  });

  groupDiv.querySelector('.deleteBtn').addEventListener('click', e => {
    e.stopPropagation();
    if (confirm(`Delete group "${name}"?`)) {
      const group = groups.find(g => g.id === groupId);
      if (group) {
        group.cubes.forEach(c => {
          if (!c) return;
          const baseHex = c.userData.baseColor || 0xffffff;
          setCubeColorMaterials(c, '#' + ('000000' + baseHex.toString(16)).slice(-6));
          delete c.userData.groupId;
          c.visible = true;
        });
      }
      groupDiv.remove();
      groups.splice(groups.findIndex(g => g.id === groupId), 1);
      refreshDragControls();
      updateLegend();
    }
  });

  colorInputEl.addEventListener('input', (ev) => {
    const val = ev.target.value;
    const group = groups.find(g => g.id === groupId);
    if (!group) return;
    group.color = new THREE.Color(val);
    group.cubes = group.cubes.filter(c => c && c.parent);
    group.cubes.forEach(c => {
      setCubeColorMaterials(c, val);
      c.userData.baseColor = parseInt(val.replace('#',''), 16);
      c.visible = (group.visible !== false);
    });
    setCounts();
    setTimeout(refreshDragControls, 0);
    updateLegend();
  });

  // show/hide button (eye icon) kept as before
  toggleVisibleBtn.addEventListener('click', (ev) => {
    ev.stopPropagation();
    const group = groups.find(g => g.id === groupId);
    if (!group) return;
    setGroupVisibility(group, !group.visible);
  });

  // clicking the plus icon: same add-cube behavior as before
  addBtn.addEventListener('click', e => {
    e.stopPropagation(); // avoid toggling the collapse when clicking the plus
    if (!activeCube) { alert("Double-click a cube first!"); return; }
    const group = groups.find(g => g.id === groupId);
    if (!group) return;

    if (activeCube.userData.groupId === groupId) {
      alert('Cube already in this group.');
      return;
    }

    if (activeCube.userData.groupId !== undefined) {
      const prevG = groups.find(g => g.id === activeCube.userData.groupId);
      if (prevG) prevG.cubes = prevG.cubes.filter(x => x !== activeCube);
    }

    clearArrows();

    activeCube.userData.groupId = groupId;
    group.cubes.push(activeCube);

    const colorHex = '#' + group.color.getHexString();
    setCubeColorMaterials(activeCube, colorHex);

    // match group's visibility
    activeCube.visible = (group.visible !== false);

    updateLegend();

    activeCube.userData.baseColor = parseInt(colorHex.replace('#',''), 16);

    // Add cube to group's UI list with controls
    createCubeListItem(group, activeCube, cubeList);


    updateStoredState(activeCube);

    orbit.enabled = true;
    activeCube = null;
    elDelete.style.display = 'none';
    setTimeout(refreshDragControls, 0);
  });

}



/* Arrow helpers (XZ move by 1 unit) */
renderer.domElement.addEventListener('click', e=>{
  raycaster.setFromCamera(mouse,camera);
  const arrowHits=raycaster.intersectObjects(arrows,true);
  if(arrowHits.length>0 && activeCube){
    const dir=arrowHits[0].object.parent.userData.dir.clone();
    const step = 1;
    const target = activeCube.position.clone().add(dir.multiplyScalar(step));
    const prev = activeCube.position.clone();
    activeCube.position.copy(target);
    // clamp according to context
    if (isInsideTrailerByPos(activeCube)) clampInsideTrailer(activeCube); else clampYard(activeCube);
    if(detectCollision(activeCube)) activeCube.position.copy(prev);
    updateStoredState(activeCube);
    elDelete.style.display='none';
    clearArrows();
    return;
  }
  const cubeHits=raycaster.intersectObjects(cubes,false);
  if(cubeHits.length===0) clearActiveCube();
});

function showArrows(obj){
  clearArrows();
  const box = new THREE.Box3().setFromObject(obj);
  const size = new THREE.Vector3();
  box.getSize(size);
  const origin = obj.position.clone();
  const dirs = [
    {dir: new THREE.Vector3(-1,0,0), length: Math.max(1.2, size.x/2 + 1)},
    {dir: new THREE.Vector3(1,0,0),  length: Math.max(1.2, size.x/2 + 1)},
    {dir: new THREE.Vector3(0,0,-1), length: Math.max(1.2, size.z/2 + 1)},
    {dir: new THREE.Vector3(0,0,1),  length: Math.max(1.2, size.z/2 + 1)}
  ];
  dirs.forEach(d=>{
    const arrow = new THREE.ArrowHelper(d.dir, origin, d.length, 0xffff00, 0.5, 0.3);
    arrow.userData={dir:d.dir.clone(),isHovered:false};
    arrows.push(arrow);
    scene.add(arrow);
  });
}

/* Arrow hover effect */
renderer.domElement.addEventListener('mousemove', ()=>{
  arrows.forEach(a=>{
    raycaster.setFromCamera(mouse,camera);
    const hits=raycaster.intersectObjects([a.line,a.cone],false);
    if(hits.length>0 && !a.userData.isHovered){a.userData.isHovered=true;a.setColor(0xff0000);}
    else if(!hits.length && a.userData.isHovered){a.userData.isHovered=false;a.setColor(0xffff00);}
  });
});

/* Cube face textures with per-face text & auto text color */
function createCubeFaceTextures(texts, faceColor=null, width=256, height=256, cubeDimensions={w:1,h:1,d:1}){
  const materials = [];
  const color = faceColor || '#' + Math.floor(Math.random()*16777215).toString(16);

  const r = parseInt(color.substr(1,2),16);
  const g = parseInt(color.substr(3,2),16);
  const b = parseInt(color.substr(5,2),16);
  const brightness = (r*299 + g*587 + b*114)/1000;
  const textColor = brightness > 128 ? 'black' : 'white';

  for(let i=0;i<6;i++){
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = color;
    ctx.fillRect(0,0,width,height);

    let faceW=1, faceH=1;
    switch(i){
      case 0: case 1: faceW = cubeDimensions.d; faceH = cubeDimensions.h; break; // left/right
      case 2: case 3: faceW = cubeDimensions.w; faceH = cubeDimensions.d; break; // front/back
      case 4: case 5: faceW = cubeDimensions.w; faceH = cubeDimensions.h; break; // top/bottom
    }
    const maxFaceDim = Math.max(faceW, faceH);
    const fontSize = Math.max(10, Math.floor(64 * maxFaceDim));

    ctx.fillStyle = textColor;
    ctx.font = `${fontSize}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(texts[i]||'', width/2, height/2);

    const texture = new THREE.CanvasTexture(canvas);
    materials.push(new THREE.MeshStandardMaterial({ map: texture }));
  }
  return materials;
}
        
// safely replace a cube's materials with new face textures and dispose old maps
function setCubeColorMaterials(cube, hexColor) {
  // dispose old materials & textures to avoid memory leaks
  const oldMats = Array.isArray(cube.material) ? cube.material : [cube.material];
  oldMats.forEach(m => {
    if (!m) return;
    if (m.map) { m.map.dispose(); m.map = null; }
    try { m.dispose(); } catch(e) {}
  });

  // geometry dims
  const geom = cube.geometry.parameters || {};
  const dims = { w: geom.width || geom.w || 1, h: geom.height || geom.h || 1, d: geom.depth || geom.d || 1 };
  const texts = cube.userData.texts || Array(6).fill('');

  // create new materials using same face texts but new color
  const newMats = createCubeFaceTextures(texts, hexColor, 256, 256, dims);

  cube.material = newMats;
  // ensure Three updates
  cube.material.forEach(m => m.needsUpdate = true);
}
                

function getRandomSpawnPositionOutsideTrailer(cubeSize) {
  const attempts = 100;
  let pos = new THREE.Vector3();

  for (let i = 0; i < attempts; i++) {
    // random X/Z in a larger area (bigger than the yard bounds)
    pos.x = (Math.random() - 0.5) * 30;
    pos.z = (Math.random() - 0.5) * 30;
    pos.y = cubeSize.height / 2; // sit on ground

    // ensure outside trailer
    if (trailerBox) {
      const cubeBox = new THREE.Box3().setFromCenterAndSize(
        pos,
        new THREE.Vector3(cubeSize.width, cubeSize.height, cubeSize.depth)
      );
      if (cubeBox.intersectsBox(trailerBox)) continue; // retry
    }

    // ensure no collision with existing cubes
    const collide = cubes.some(c => {
      const b = new THREE.Box3().setFromObject(c);
      const testBox = new THREE.Box3().setFromCenterAndSize(
        pos,
        new THREE.Vector3(cubeSize.width, cubeSize.height, cubeSize.depth)
      );
      return testBox.intersectsBox(b);
    });
    if (!collide) return pos; // valid position
  }

  // fallback: center if can't find empty spot
  return new THREE.Vector3(0, cubeSize.height / 2, 0);
}

/* Add a random 1x1x1 box (non-overlapping) */
function addBox(){
  clearActiveCube();
  elForm.style.display='none';
  boxCount++;
  const size = 1;
  let cube = null;
  const texts = Array(6).fill(`Box ${boxCount}`);

  cube = new THREE.Mesh(
    new THREE.BoxGeometry(size, size, size),
    createCubeFaceTextures(texts, null, 256, 256, {w:size,h:size,d:size})
  );
  cube.userData = { baseColor: 0xffffff, prevPos: new THREE.Vector3(), inTrailer: false };
  cube.userData.texts = texts;

  // spawn outside trailer & avoid overlapping
  const cubeSize = {width: size, height: size, depth: size};
  cube.position.copy(getRandomSpawnPositionOutsideTrailer(cubeSize));

  scene.add(cube);
  cubes.push(cube);
  setCounts();
  refreshDragControls();
}

addBox();

/* Custom Box UI */
document.getElementById('addBoxBtn').addEventListener('click', addBox);
document.getElementById('customBoxBtn').addEventListener('click', ()=>{
  clearActiveCube();
  elForm.style.display = (elForm.style.display==='block') ? 'none' : 'block';
});
document.getElementById('cancelCustomBox').addEventListener('click', ()=> elForm.style.display = 'none');
document.getElementById('createCustomBox').addEventListener('click', ()=>{
  const w = Math.max(0.1, parseFloat(document.getElementById('boxWidth').value));
  const h = Math.max(0.1, parseFloat(document.getElementById('boxHeight').value));
  const d = Math.max(0.1, parseFloat(document.getElementById('boxDepth').value));
  const color = document.getElementById('boxColor').value;
  let text = document.getElementById('boxText').value.trim();

  clearActiveCube();

  let cube = new THREE.Mesh(
    new THREE.BoxGeometry(w,h,d),
    createCubeFaceTextures(Array(6).fill(text), color, 256, 256, {w,h,d})
  );
  cube.userData = { baseColor: parseInt(color.replace('#',''),16), prevPos: new THREE.Vector3(), inTrailer: false };
  
  cube.userData.texts = Array(6).fill(text);

  // spawn outside trailer & avoid overlapping
  const cubeSize = {width: w, height: h, depth: d};
  cube.position.copy(getRandomSpawnPositionOutsideTrailer(cubeSize));

  scene.add(cube);
  cubes.push(cube);
  setCounts();
  refreshDragControls();
  elForm.style.display='none';
});

/* Trailer buttons */
document.getElementById('toggleTrailerBtn').addEventListener('click', ()=>{
  trailerVisible = !trailerVisible;
  trailer.visible = trailerVisible;
});

document.getElementById('listStoredBtn').addEventListener('click', ()=>{
  const stored = cubes.filter(c => c.userData.inTrailer);
  const names = stored.map((c,i)=> c.name || `#${i+1} (${c.geometry.parameters.width}×${c.geometry.parameters.height}×${c.geometry.parameters.depth})`);
  alert(`Stored in trailer (${stored.length}):\\n` + (names.length ? names.join('\\n') : '— none —'));
});

document.getElementById('emptyTrailerBtn').addEventListener('click', ()=>{
  // Move all stored boxes outside (just behind the trailer opening)
  const startX = -T_W/2 + 0.5;
  const startZ = -(T_D/2 + 1.5);
  let offset = 0;
  cubes.forEach(c=>{
    if (c.userData.inTrailer){
      const h = c.geometry.parameters.height/2;
      c.position.set(startX + (offset%Math.ceil(T_W))*1.2, Math.max(h, 0.5), startZ - Math.floor(offset/Math.ceil(T_W))*1.2);
      offset++;
      clampYard(c);
      c.userData.inTrailer = false;
      c.material.forEach(m => m.color.setHex(c.userData.baseColor || 0xffffff));
    }
  });
  setCounts();
  refreshDragControls();
});

/* Lock/unlock stored option affects drag targets */
lockWhenStored.addEventListener('change', refreshDragControls);

/* Hide custom form if clicked on canvas area (outside the form) */
renderer.domElement.addEventListener('click', e=>{
  if(elForm.style.display==='block'){
    const rect = elForm.getBoundingClientRect();
    if(!(e.clientX>=rect.left && e.clientX<=rect.right && e.clientY>=rect.top && e.clientY<=rect.bottom)){
      elForm.style.display='none';
    }
  }
});

renderer.domElement.addEventListener('click', e => {
  raycaster.setFromCamera(mouse, camera);
  const cubeHits = raycaster.intersectObjects(cubes, false);

  // If clicked on cube, do nothing here
  if (cubeHits.length === 0) {
    // Clicked empty space — hide active cube arrows
    clearActiveCube();
    
    // ✅ Also hide groups panel if it's shown
    if (groupsList.classList.contains('show')) {
      groupsList.classList.remove('show');
    }
  }
});


/* RENDER LOOP */
function animate(){
  requestAnimationFrame(animate);
  orbit.update();
  renderer.render(scene,camera);
}
animate();

/* Resize */
window.addEventListener('resize', ()=>{
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
</script>
''', height=600,scrolling=False)
