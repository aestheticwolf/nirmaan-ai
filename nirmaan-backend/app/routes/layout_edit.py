from fastapi import APIRouter
from app.services.layout_prompt_editor import edit_layout_with_prompt
from app.services.cad_generator import generate_dxf

router = APIRouter()


@router.post("/layout/edit")
def edit_layout(data: dict):

    layout = data.get("layout")
    prompt = data.get("prompt")
    plot = data.get("plot")
    building = data.get("building")

    updated_layout = edit_layout_with_prompt(layout, prompt)

    result = generate_dxf(plot, building, updated_layout)

    return {
        "message": "Layout updated",
        "layout": updated_layout,
        "file": result["file"]
    }