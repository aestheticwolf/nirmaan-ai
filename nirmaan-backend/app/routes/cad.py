from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.cad import GenerateRequest
from app.database import SessionLocal
from app.models.plot import Plot
from app.models.building import Building
from app.services.cad_generator import generate_dxf
import os

router = APIRouter()


@router.post("/generate-cad")
def generate(request: GenerateRequest):
    try:
        db = SessionLocal()

        # Save Plot
        new_plot = Plot(
            length=request.plot.length,
            width=request.plot.width,
            road_width=request.plot.road_width
        )
        db.add(new_plot)
        db.commit()
        db.refresh(new_plot)

        # Save Building
        new_building = Building(
            floors=request.building.floors,
            plot_id=new_plot.id
        )
        db.add(new_building)
        db.commit()

        # Generate DXF
        path = generate_dxf(
            plot=request.plot.dict(),
            building=request.building.dict()
        )

        filename = os.path.basename(path)

        db.close()

        return {
            "status": "success",
            "file_name": filename,
            "download_url": f"/download/{filename}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("generated", filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type="application/dxf",
        filename=filename
    )