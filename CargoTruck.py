import streamlit as st
import streamlit.components.v1 as components

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
#legend {
  position: absolute; bottom: 16px; right: 16px; z-index: 20;
  background: rgba(255,255,255,0.9); color: #111827; padding: 8px 10px; border-radius: 10px; font-size: 12px;
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
  <div id="legend">🟩 stored in trailer • 🔴 hover • 🟡 move arrows (double-click)</div>
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

/* Ground */
const grid = new THREE.GridHelper(30, 30, 0x444444, 0xaaaaaa);
scene.add(grid);

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

let trailer = null;       // THREE.Group containing the walls/floor/roof
let trailerVisible = true;
let trailerInterior = null; // invisible mesh for interior bounds (for Box3)
let trailerBox = null;    // THREE.Box3 of the interior usable volume

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
  if (trailer) { scene.remove(trailer); trailer = null; }
  trailer = new THREE.Group();

  // Base position: place floor on y=0 so boxes roll in on the grid
  const cx = 0, cy = FLOOR_T/2, cz = 0;

  // Floor
  const floor = new THREE.Mesh(
    new THREE.BoxGeometry(T_W + 2*WALL_T, FLOOR_T, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.1, roughness: 0.8 })
  );
  floor.position.set(cx, cy, cz);
  trailer.add(floor);

  // Roof
  const roof = new THREE.Mesh(
    new THREE.BoxGeometry(T_W + 2*WALL_T, WALL_T, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xdddddd, metalness: 0.1, roughness: 0.8, transparent: true, opacity: 0.4 })
  );
  roof.position.set(cx, T_H + FLOOR_T - WALL_T/2, cz);
  trailer.add(roof);

  // Left wall ( -x )
  const left = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xbfc7cf, transparent: true, opacity: 0.4 })
  );
  left.position.set(cx - (T_W/2 + WALL_T/2), FLOOR_T + T_H/2, cz);
  trailer.add(left);

  // Right wall ( +x )
  const right = new THREE.Mesh(
    new THREE.BoxGeometry(WALL_T, T_H, T_D + WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xbfc7cf, transparent: true, opacity: 0.4 })
  );
  right.position.set(cx + (T_W/2 + WALL_T/2), FLOOR_T + T_H/2, cz);
  trailer.add(right);

  // Front wall ( +z ) — closed
  const front = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, T_H, WALL_T),
    new THREE.MeshStandardMaterial({ color: 0xb5c1cd, transparent: true, opacity: 0.85 })
  );
  front.position.set(cx, FLOOR_T + T_H/2, cz + (T_D/2 + WALL_T/2));
  trailer.add(front);

  // Back is open ( -z ) to allow loading

  // Optional edges
  const edges = new THREE.EdgesGeometry(new THREE.BoxGeometry(T_W + 2*WALL_T, T_H + FLOOR_T + WALL_T, T_D + WALL_T));
  const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x444444 }));
  line.position.set(cx, FLOOR_T + (T_H)/2 - WALL_T/2, cz);
  trailer.add(line);

  // Invisible interior volume mesh (for Box3 containment checks)
  trailerInterior = new THREE.Mesh(
    new THREE.BoxGeometry(T_W, T_H, T_D),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  trailerInterior.position.set(cx, FLOOR_T + T_H/2, cz);
  trailer.add(trailerInterior);

  // A small ramp at the open back for visuals
  const rampGeom = new THREE.PlaneGeometry(T_W, 2);
  const rampMat = new THREE.MeshStandardMaterial({ color: 0x999999, side: THREE.DoubleSide });
  const ramp = new THREE.Mesh(rampGeom, rampMat);
  ramp.rotation.x = -Math.PI/6;
  ramp.position.set(cx, FLOOR_T/2, cz - (T_D/2 + 0.8));
  //trailer.add(ramp);

  scene.add(trailer);

  // Compute interior box
  trailerBox = new THREE.Box3().setFromObject(trailerInterior);
}

createTrailer();

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

  dragControls.addEventListener('drag', e => {
    const o = e.object;
    // Keep on ground by default
    o.position.y = Math.max(o.geometry.parameters.height / 2, o.position.y);

    // If currently inside trailer, clamp inside; else clamp to yard
    if (isInsideTrailerByPos(o)) {
      clampInsideTrailer(o);
    } else {
      clampYard(o);
    }

    // Prevent overlapping with other cubes
    if (detectCollision(o)) {
      // revert to previous position
      o.position.copy(o.userData.prevPos);
    } else {
      o.userData.prevPos.copy(o.position);
    }
  });

  dragControls.addEventListener('dragend', e => {
    orbit.enabled = true;
    updateStoredState(e.object);
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

/* Update stored state visuals + flag */
function updateStoredState(obj) {
  const nowInside = isInsideTrailer(obj);
  obj.userData.inTrailer = nowInside;

  const storedColor = 0x00aa00; // green
  const normalColor = obj.userData.baseColor || 0xffffff;

  obj.material.forEach(m => m.color.setHex(nowInside ? storedColor : normalColor));

  setCounts();
  refreshDragControls(); // update draggables if "lock when stored" is checked
}

/* Collision with other cubes */
function detectCollision(cube) {
  const a = new THREE.Box3().setFromObject(cube);
  return cubes.some(other => {
    if (other === cube) return false;
    const b = new THREE.Box3().setFromObject(other);
    return a.intersectsBox(b);
  });
}

/* Arrows */
function clearArrows() { arrows.forEach(a=>scene.remove(a)); arrows.length=0; }
function clearActiveCube(){ clearArrows(); activeCube=null; elDelete.style.display='none'; }

/* Hover highlight (red) */
window.addEventListener('mousemove', e=>{
  mouse.x=(e.clientX/window.innerWidth)*2-1;
  mouse.y=-(e.clientY/window.innerHeight)*2+1;
  if(hoverObj){ hoverObj.material.forEach(mat => mat.color.setHex(hoverObj.userData.inTrailer ? 0x00aa00 : (hoverObj.userData.baseColor || 0xffffff))); hoverObj=null; }
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
      scene.remove(activeCube);
      const idx = cubes.indexOf(activeCube);
      if (idx>=0) cubes.splice(idx,1);
      activeCube=null;
      btn.style.display='none';
      setCounts();
      refreshDragControls();
    }
  }
});

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

/* Add a random 1x1x1 box (non-overlapping) */
function addBox(){
  clearActiveCube();
  elForm.style.display='none';
  boxCount++;
  const size = 1;
  let cube = null;
  let tries = 0;
  const texts = Array(6).fill(`Box ${boxCount}`);

  do {
    cube = new THREE.Mesh(
      new THREE.BoxGeometry(size,size,size),
      createCubeFaceTextures(texts, null, 256, 256, {w:size,h:size,d:size})
    );
    cube.userData = {
      baseColor: 0xffffff,
      prevPos: new THREE.Vector3(),
      inTrailer: false
    };
    // spawn outside trailer by default
    cube.position.set((Math.random()-0.5)*16, size/2, (Math.random()-0.5)*16);
    clampYard(cube);
    tries++;
    if (tries > 80) break;
  } while (detectCollision(cube));

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

  let cube = null;
  let tries = 0;
  do {
    cube = new THREE.Mesh(
      new THREE.BoxGeometry(w,h,d),
      createCubeFaceTextures(Array(6).fill(text), color, 256, 256, {w,h,d})
    );
    cube.userData = {
      baseColor: parseInt(color.replace('#',''),16),
      prevPos: new THREE.Vector3(),
      inTrailer: false
    };
    cube.position.set((Math.random()-0.5)*16, h/2, (Math.random()-0.5)*16);
    clampYard(cube);
    tries++;
    if (tries>80) break;
  } while(detectCollision(cube));

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
''', height=500)
