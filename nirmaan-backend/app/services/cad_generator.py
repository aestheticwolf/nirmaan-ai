import ezdxf
import os
from uuid import uuid4

FRONT_SETBACK = 3
SIDE_SETBACK = 1.5
REAR_SETBACK = 2

def generate_dxf(plot, building):
    filename = f"layout_{uuid4().hex}.dxf"
    filepath = os.path.join("generated", filename)

    os.makedirs("generated", exist_ok=True)

    doc = ezdxf.new()
    msp = doc.modelspace()

    # Create layers
    doc.layers.add("PLOT", color=7)
    doc.layers.add("SETBACK", color=3)
    doc.layers.add("BUILDING", color=1)
    doc.layers.add("TEXT", color=5)

    length = plot["length"]
    width = plot["width"]

    # Plot boundary
    msp.add_lwpolyline([
        (0, 0),
        (length, 0),
        (length, width),
        (0, width),
        (0, 0)
    ], dxfattribs={"layer": "PLOT"})

    # Setback envelope
    build_x1 = SIDE_SETBACK
    build_y1 = FRONT_SETBACK
    build_x2 = length - SIDE_SETBACK
    build_y2 = width - REAR_SETBACK

    msp.add_lwpolyline([
        (build_x1, build_y1),
        (build_x2, build_y1),
        (build_x2, build_y2),
        (build_x1, build_y2),
        (build_x1, build_y1)
    ], dxfattribs={"layer": "SETBACK"})

    # Building footprint
    footprint_w = (build_x2 - build_x1) * 0.8
    footprint_h = (build_y2 - build_y1) * 0.8

    offset_x = build_x1 + ((build_x2 - build_x1) - footprint_w) / 2
    offset_y = build_y1 + ((build_y2 - build_y1) - footprint_h) / 2

    msp.add_lwpolyline([
        (offset_x, offset_y),
        (offset_x + footprint_w, offset_y),
        (offset_x + footprint_w, offset_y + footprint_h),
        (offset_x, offset_y + footprint_h),
        (offset_x, offset_y)
    ], dxfattribs={"layer": "BUILDING"})


    # ROOM SUBDIVISION
    room_margin = 0.5

    bx1 = offset_x + room_margin
    by1 = offset_y + room_margin
    bx2 = offset_x + footprint_w - room_margin
    by2 = offset_y + footprint_h - room_margin

    building_width = bx2 - bx1
    building_height = by2 - by1

    split_x = bx1 + building_width * 0.6
    split_y = by1 + building_height * 0.5

    msp.add_line((split_x, by1), (split_x, by2), dxfattribs={"layer": "BUILDING"})
    msp.add_line((bx1, split_y), (split_x, split_y), dxfattribs={"layer": "BUILDING"})

    # ROOM LABELS
    msp.add_text("LIVING", dxfattribs={"layer": "TEXT", "height": 0.8, "insert": (bx1 + 1, by2 - 2)})
    msp.add_text("BEDROOM", dxfattribs={"layer": "TEXT", "height": 0.8, "insert": (split_x + 1, by2 - 2)})
    msp.add_text("KITCHEN", dxfattribs={"layer": "TEXT", "height": 0.8, "insert": (bx1 + 1, by1 + 1)})
    msp.add_text("TOILET", dxfattribs={"layer": "TEXT", "height": 0.8, "insert": (split_x + 1, by1 + 1)})

    # Text annotations (INSIDE function)
    msp.add_text(
        f"Plot: {length}m x {width}m",
        dxfattribs={
            "layer": "TEXT",
            "height": 0.5,
            "insert": (0, width + 2)
        }
    )

    msp.add_text(
        f"Floors: {building['floors']}",
        dxfattribs={
            "layer": "TEXT",
            "height": 0.5,
            "insert": (0, width + 1)
        }
    )

    # -----------------------
    # DIMENSIONS
    # -----------------------

    msp.add_linear_dim(
        base=(length / 2, -2),
        p1=(0, 0),
        p2=(length, 0),
        angle=0,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()

    msp.add_linear_dim(
        base=(-2, width / 2),
        p1=(0, 0),
        p2=(0, width),
        angle=90,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()


      # -----------------------
    # SETBACK DIMENSIONS

    # Front setback
    msp.add_linear_dim(
        base=(length + 2, FRONT_SETBACK / 2),
        p1=(0, 0),
        p2=(0, FRONT_SETBACK),
        angle=90,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()

    # Rear setback
    msp.add_linear_dim(
        base=(length + 2, width - REAR_SETBACK / 2),
        p1=(0, width),
        p2=(0, width - REAR_SETBACK),
        angle=90,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()

    # Left side setback
    msp.add_linear_dim(
        base=(SIDE_SETBACK / 2, -4),
        p1=(0, 0),
        p2=(SIDE_SETBACK, 0),
        angle=0,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()

    # Right side setback
    msp.add_linear_dim(
        base=(length - SIDE_SETBACK / 2, -4),
        p1=(length, 0),
        p2=(length - SIDE_SETBACK, 0),
        angle=0,
        dimstyle="Standard",
        dxfattribs={"layer": "TEXT"}
    ).render()


        # -----------------------
    # NORTH ARROW
    # -----------------------

    north_x = length + 5
    north_y = width - 2

    # Arrow line
    msp.add_line(
        (north_x, north_y),
        (north_x, north_y + 3),
        dxfattribs={"layer": "TEXT"}
    )

    # Arrow head
    msp.add_lwpolyline([
        (north_x - 0.5, north_y + 2.5),
        (north_x, north_y + 3),
        (north_x + 0.5, north_y + 2.5),
        (north_x - 0.5, north_y + 2.5)
    ], dxfattribs={"layer": "TEXT"})

    # "N" text
    msp.add_text(
        "N",
        dxfattribs={
            "layer": "TEXT",
            "height": 1,
            "insert": (north_x - 0.3, north_y + 3.5)
        }
    )

        # -----------------------
    # TITLE BLOCK (A3 STYLE)
    # -----------------------

    sheet_width = length + 15
    sheet_height = width + 15

    # Outer border
    msp.add_lwpolyline([
        (-10, -10),
        (sheet_width, -10),
        (sheet_width, sheet_height),
        (-10, sheet_height),
        (-10, -10)
    ], dxfattribs={"layer": "PLOT"})

    # Title block box (bottom right)
    tb_x1 = sheet_width - 60
    tb_y1 = -10
    tb_x2 = sheet_width
    tb_y2 = 0

    msp.add_lwpolyline([
        (tb_x1, tb_y1),
        (tb_x2, tb_y1),
        (tb_x2, tb_y2),
        (tb_x1, tb_y2),
        (tb_x1, tb_y1)
    ], dxfattribs={"layer": "PLOT"})

    # Title text
    msp.add_text(
        "NIRMAAN AI - SITE LAYOUT",
        dxfattribs={
            "layer": "TEXT",
            "height": 1.2,
            "insert": (tb_x1 + 2, tb_y1 + 6)
        }
    )

    msp.add_text(
        f"Plot Size: {length}m x {width}m",
        dxfattribs={
            "layer": "TEXT",
            "height": 0.8,
            "insert": (tb_x1 + 2, tb_y1 + 4)
        }
    )

    msp.add_text(
        f"Floors: {building['floors']}",
        dxfattribs={
            "layer": "TEXT",
            "height": 0.8,
            "insert": (tb_x1 + 2, tb_y1 + 2)
        }
    )

    msp.add_text(
        "Scale: 1:100",
        dxfattribs={
            "layer": "TEXT",
            "height": 0.8,
            "insert": (tb_x1 + 35, tb_y1 + 2)
        }
    )

    doc.saveas(filepath)
    return filepath