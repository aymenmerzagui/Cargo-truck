from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import cadquery as cq
import tempfile
import shutil
import os
import uuid
import pandas as pd
app = FastAPI()

# Enable CORS so React frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace "*" with your frontend domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

STL_DIR = "stl_files"
EXCEL_DIR="excel_files"
os.makedirs(EXCEL_DIR, exist_ok=True)
os.makedirs(STL_DIR, exist_ok=True)

@app.post("/upload-step")
async def upload_step(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".step", ".stp")):
        raise HTTPException(status_code=400, detail="Only STEP/STP files are allowed")

    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".step") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        shape = cq.importers.importStep(tmp_path)
        bbox = shape.val().BoundingBox()
        bbox_dims = {
            "x": round(bbox.xlen, 2),
            "y": round(bbox.ylen, 2),
            "z": round(bbox.zlen, 2),
        }

        # Convert to STL
        stl_filename = f"{uuid.uuid4().hex}.stl"
        stl_path = os.path.join(STL_DIR, stl_filename)
        cq.exporters.export(shape, stl_path)

        return {
            "bounding_box": bbox_dims,
            "stl_file": stl_filename,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing STEP file: {e}")

    finally:
        # Clean up temporary STEP file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/create-stl")
def create_stl(length: float = 10.0, width: float = 10.0, height: float = 10.0):
    # Generate unique filename with UUID
    unique_id = str(uuid.uuid4())
    filename = f"{unique_id}.stl"

    # Create a simple box shape
    shape = cq.Workplane("XY").box(length, width, height)

    # Export to STL
    stl_path = os.path.join(STL_DIR, filename)
    try:
        cq.exporters.export(shape, stl_path)
        return {"message": "STL file created", "stl_file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating STL file: {e}")
    
@app.get("/download-stl/{filename}")
def download_stl(filename: str):
    stl_path = os.path.join(STL_DIR, filename)
    if not os.path.exists(stl_path):
        raise HTTPException(status_code=404, detail="STL file not found")
    return FileResponse(stl_path, media_type="model/stl")

@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed")

    try:
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Load with pandas
        df = pd.read_excel(tmp_path)

        # Expect columns: Name, Width, Height, Depth, Unit
        required_cols = {"Name", "Width", "Height", "Depth", "Unit"}
        if not required_cols.issubset(set(df.columns)):
            raise HTTPException(
                status_code=400,
                detail=f"Excel file must contain columns: {', '.join(required_cols)}"
            )

        # Convert rows to list of dicts
        boxes = df.to_dict(orient="records")

        return {"boxes": boxes, "count": len(boxes)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing Excel file: {e}")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/download-excel/{filename}")
def download_excel(filename: str):
    excel_path = os.path.join(EXCEL_DIR, filename)
    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="Excel file not found")
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )