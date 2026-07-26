from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.schemas.cad import GenerateRequest
from app.database import SessionLocal
from app.models.plot import Plot
from app.models.building import Building
from app.services.cad_generator import generate_dxf
from app.services.ai_layout import generate_layout_from_prompt
import os

router = APIRouter()


@router.post("/generate-cad")
def generate(request: GenerateRequest):

    db = SessionLocal()

    try:
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
        result = generate_dxf(
            plot=request.plot.dict(),
            building=request.building.dict()
        )

        filename = os.path.basename(result["file"])

        return {
            "status": "success",
            "file_name": filename,
            "download_url": f"/download/{filename}",
            "layout": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


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


@router.post("/cad/generate")
def generate_layout(data: dict):

    plot = data["plot"]
    building = data["building"]

    result = generate_dxf(plot, building)

    return result


@router.post("/generate-ai-layout")
def generate_ai_layout(data: dict):

    prompt = data.get("prompt")

    if not prompt:
        return {"error": "Prompt required"}

    layout = generate_layout_from_prompt(prompt)

    return {
        "message": "AI layout generated",
        "layout": layout
    }


@router.post("/generate-ai-cad")
def generate_ai_cad(data: dict):

    prompt = data.get("prompt")
    plot = data.get("plot")
    building = data.get("building")

    if not prompt:
        return {"error": "Prompt required"}

    layout = generate_layout_from_prompt(prompt)

    result = generate_dxf(
        plot=plot,
        building=building,
        layout=layout
    )

    filename = os.path.basename(result["file"])

    return {
        "message": "AI CAD generated",
        "layout": layout,
        "file_name": filename,
        "download_url": f"/download/{filename}"
    }
