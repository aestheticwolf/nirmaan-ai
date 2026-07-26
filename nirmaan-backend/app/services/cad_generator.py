import ezdxf
import os
from uuid import uuid4

FRONT_SETBACK = 3
SIDE_SETBACK = 1.5
REAR_SETBACK = 2


def generate_dxf(plot, building, layout=None):
    try:
        if not plot or not building:
            raise ValueError("Invalid input data")

        length = float(plot.get("length", 0))
        width = float(plot.get("width", 0))
        floors = building.get("floors", 1)

        rooms = []
        if layout and "rooms" in layout:
            rooms = layout["rooms"]
        

        if length <= 0 or width <= 0:
            raise ValueError("Invalid plot dimensions")

        filename = f"layout_{uuid4().hex}.dxf"
        os.makedirs("generated", exist_ok=True)
        filepath = os.path.join("generated", filename)

        doc = ezdxf.new()
        msp = doc.modelspace()

        # -----------------------
        # HELPER DRAW FUNCTIONS
        # -----------------------
        WALL_THICKNESS = 0.23

        def draw_wall(x1, y1, x2, y2):

            # outer wall
            msp.add_lwpolyline(
                [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)],
                dxfattribs={"layer": "WALLS"},
            )

            # inner wall
            msp.add_lwpolyline(
                [
                    (x1 + WALL_THICKNESS, y1 + WALL_THICKNESS),
                    (x2 - WALL_THICKNESS, y1 + WALL_THICKNESS),
                    (x2 - WALL_THICKNESS, y2 - WALL_THICKNESS),
                    (x1 + WALL_THICKNESS, y2 - WALL_THICKNESS),
                    (x1 + WALL_THICKNESS, y1 + WALL_THICKNESS),
                ],
                dxfattribs={"layer": "WALLS"},
            )

            # hatch for realistic walls
            hatch = msp.add_hatch(color=8)
            hatch.set_pattern_fill("ANSI31", scale=0.3)

            hatch.paths.add_polyline_path(
                [(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
                is_closed=True
            )



        def draw_door(x, y, width=1):

            msp.add_line(
                (x, y),
                (x + width, y),
                dxfattribs={"layer": "DOORS"},
            )

            msp.add_arc(
                center=(x, y),
                radius=width,
                start_angle=0,
                end_angle=90,
                dxfattribs={"layer": "DOORS"},
            )


        def draw_window(x, y, width=1.5):

            msp.add_line(
            (x, y),
            (x + width, y),
            dxfattribs={"layer": "WINDOWS"},
            )

            msp.add_line(
            (x, y + 0.1),
            (x + width, y + 0.1),
            dxfattribs={"layer": "WINDOWS"},
            )


        # -----------------------
        # FURNITURE FUNCTIONS
        # -----------------------
            
        def draw_bed(x, y):

            bed_w = 2
            bed_h = 1.8

            msp.add_lwpolyline(
            [
            (x, y),
            (x + bed_w, y),
            (x + bed_w, y + bed_h),
            (x, y + bed_h),
            (x, y),
            ],
            dxfattribs={"layer": "FURNITURE"},
            )


        def draw_sofa(x, y):

            msp.add_lwpolyline(
            [
            (x, y),
            (x + 2, y),
            (x + 2, y + 0.8),
            (x, y + 0.8),
            (x, y),
            ],
            dxfattribs={"layer": "FURNITURE"},
            )


        def draw_table(x, y):

            msp.add_circle(
            (x, y),
            0.8,
            dxfattribs={"layer": "FURNITURE"},
            )

        # -----------------------
        # Layers
        # -----------------------

        layer_data = {
"PLOT":7,
"SETBACK":3,
"WALLS":1,
"ROOMS":2,
"DOORS":5,
"WINDOWS":4,
"DIMENSIONS":6,
"TEXT":7,
"HATCH":8,
"BUILDING":1,
"TITLE":7,
"FURNITURE":5
}

        for name, color in layer_data.items():
            if name not in doc.layers:
                doc.layers.add(name, color=color)

        # -----------------------
        # PLOT BOUNDARY
        # -----------------------

        msp.add_lwpolyline(
            [(0, 0), (length, 0), (length, width), (0, width), (0, 0)],
            dxfattribs={"layer": "PLOT"},
        )

        # -----------------------
        # SETBACK
        # -----------------------

        build_x1 = SIDE_SETBACK
        build_y1 = FRONT_SETBACK
        build_x2 = length - SIDE_SETBACK
        build_y2 = width - REAR_SETBACK

        msp.add_lwpolyline(
            [
                (build_x1, build_y1),
                (build_x2, build_y1),
                (build_x2, build_y2),
                (build_x1, build_y2),
                (build_x1, build_y1),
            ],
            dxfattribs={"layer": "SETBACK"},
        )

        # -----------------------
        # BUILDING FOOTPRINT
        # -----------------------

        footprint_w = (build_x2 - build_x1) * 0.8
        footprint_h = (build_y2 - build_y1) * 0.8

        offset_x = build_x1 + ((build_x2 - build_x1) - footprint_w) / 2
        offset_y = build_y1 + ((build_y2 - build_y1) - footprint_h) / 2

        draw_wall(offset_x, offset_y, offset_x + footprint_w, offset_y + footprint_h)

        msp.add_lwpolyline(
            [
                (offset_x, offset_y),
                (offset_x + footprint_w, offset_y),
                (offset_x + footprint_w, offset_y + footprint_h),
                (offset_x, offset_y + footprint_h),
                (offset_x, offset_y),
            ],
            dxfattribs={"layer": "BUILDING"},
        )


  # -----------------------
        # ROOM AREA
        # -----------------------

        room_margin = 0.5

        bx1 = offset_x + room_margin
        by1 = offset_y + room_margin
        bx2 = offset_x + footprint_w - room_margin
        by2 = offset_y + footprint_h - room_margin

        building_width = bx2 - bx1
        building_height = by2 - by1

          
         # -----------------------
        # AI ROOM ZONING
        # -----------------------

        front_zone = []
        center_zone = []
        private_zone = []
        service_zone = []

        for r in rooms:

            name = r.get("name", "").lower()

            if "living" in name or "parking" in name:
                front_zone.append(r)

            elif "kitchen" in name or "dining" in name:
                center_zone.append(r)

            elif "bedroom" in name:
                private_zone.append(r)

            elif "bath" in name or "toilet" in name:
                service_zone.append(r)

            else:
                center_zone.append(r)

        zone_rooms = (
            front_zone +
            center_zone +
            private_zone +
            service_zone
        )

        total_rooms = max(len(zone_rooms), 1)

        cols = 2
        rows = (total_rooms + 1) // 2

        room_w = building_width / cols
        room_h = building_height / rows

        room_positions = []

        for i, r in enumerate(zone_rooms):

            col = i % cols
            row = i // cols

            x1 = bx1 + col * room_w
            y1 = by1 + row * room_h

            x2 = x1 + room_w
            y2 = y1 + room_h

            draw_wall(x1, y1, x2, y2)

            room_positions.append((x1, y1, x2, y2, r))


        # # -----------------------
        # # DOORS
        # # -----------------------

        # draw_door(split_x - 1, split_y)
        # draw_door(split_x + 1, split_y)

        # # -----------------------
        # # WINDOWS
        # # -----------------------

        # draw_window(bx1 + 1, by2)
        # draw_window(split_x + 1, by2)


        # -----------------------
        # ROOM LABELS + FURNITURE
        # -----------------------

        for i, (x1, y1, x2, y2, r) in enumerate (room_positions):

            name = r.get("name", "ROOM")

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        msp.add_text(
        name.upper(),
                dxfattribs={
                    "layer": "ROOMS",
                    "height": 0.8,
                    "insert": (cx - 1, cy),
            },
        )

        name_lower = name.lower()

        if "bedroom" in name_lower:
            draw_bed(x1 + 0.5, y1 + 0.5)

        elif "living" in name_lower:
            draw_sofa(x1 + 0.5, y1 + 0.5)

        elif "dining" in name_lower:
            draw_table((x1 + x2) / 2, (y1 + y2) / 2)


        # -----------------------
        # KITCHEN PLATFORM
        # -----------------------

        for x1, y1, x2, y2, r in room_positions:

            name = r.get("name", "").lower()

            if "kitchen" in name:

                platform_margin = 0.3
                platform_depth = 0.6

                px1 = x1 + platform_margin
                py1 = y2 - platform_depth - platform_margin

                px2 = x2 - platform_margin
                py2 = y2 - platform_margin

                msp.add_lwpolyline(
                    [
                        (px1, py1),
                        (px2, py1),
                        (px2, py2),
                        (px1, py2),
                        (px1, py1),
                    ],
                    dxfattribs={"layer": "BUILDING"},
                )

                msp.add_text(
                    "KITCHEN PLATFORM",
                    dxfattribs={
                        "layer": "TEXT",
                        "height": 0.4,
                        "insert": (px1 + 0.2, py1 - 0.2),
                    },
                )

        # -----------------------
        # BATHROOM FIXTURES
        # -----------------------

        for x1, y1, x2, y2, r in room_positions:

            name = r.get("name", "").lower()

            if "bath" in name or "toilet" in name:

                # WC circle
                wc_x = x1 + 0.8
                wc_y = y1 + 0.8

                msp.add_circle(
                    (wc_x, wc_y),
                    0.3,
                    dxfattribs={"layer": "BUILDING"},
                )

                # Basin rectangle
                basin_x1 = x2 - 0.8
                basin_y1 = y1 + 0.3

                basin_x2 = basin_x1 + 0.5
                basin_y2 = basin_y1 + 0.3

                msp.add_lwpolyline(
                    [
                        (basin_x1, basin_y1),
                        (basin_x2, basin_y1),
                        (basin_x2, basin_y2),
                        (basin_x1, basin_y2),
                        (basin_x1, basin_y1),
                    ],
                    dxfattribs={"layer": "BUILDING"},
                )

                msp.add_text(
                    "WC",
                    dxfattribs={
                        "layer": "TEXT",
                        "height": 0.3,
                        "insert": (wc_x - 0.2, wc_y - 0.6),
                    },
                )

        # -----------------------
        # INTERIOR DOORS
        # -----------------------

        for i in range(len(room_positions) - 1):

            x1, y1, x2, y2, r = room_positions[i]

            door_x = x2 - 0.5
            door_y = (y1 + y2) / 2

            draw_door(door_x, door_y)


        # -----------------------
        # EXTERIOR WINDOWS
        # -----------------------

        # bottom wall windows
        draw_window(bx1 + building_width * 0.25, by1)
        draw_window(bx1 + building_width * 0.65, by1)

        # top wall windows
        draw_window(bx1 + building_width * 0.25, by2)
        draw_window(bx1 + building_width * 0.65, by2)

        # left wall windows
        draw_window(bx1, by1 + building_height * 0.3)
        draw_window(bx1, by1 + building_height * 0.7)

        # right wall windows
        draw_window(bx2 - 1.5, by1 + building_height * 0.3)
        draw_window(bx2 - 1.5, by1 + building_height * 0.7)


        # -----------------------
        # PARKING AREA
        # -----------------------

        parking_width = 3
        parking_length = 5

        parking_x1 = build_x1 + 1
        parking_y1 = build_y1 - parking_length - 1

        msp.add_lwpolyline(
            [
                (parking_x1, parking_y1),
                (parking_x1 + parking_width, parking_y1),
                (parking_x1 + parking_width, parking_y1 + parking_length),
                (parking_x1, parking_y1 + parking_length),
                (parking_x1, parking_y1),
            ],
            dxfattribs={"layer": "BUILDING"},
        )

        msp.add_text(
            "PARKING",
            dxfattribs={
                "layer": "TEXT",
                "height": 0.6,
                "insert": (parking_x1 + 0.5, parking_y1 + parking_length / 2),
            },
        )


         # -----------------------
        # STAIRCASE (if multi-floor)
        # -----------------------

        if floors > 1:

            stair_w = 2
            stair_h = 4

            stair_x = bx2 - stair_w - 0.5
            stair_y = by1 + 0.5

            msp.add_lwpolyline(
                [
                    (stair_x, stair_y),
                    (stair_x + stair_w, stair_y),
                    (stair_x + stair_w, stair_y + stair_h),
                    (stair_x, stair_y + stair_h),
                    (stair_x, stair_y),
                ],
                dxfattribs={"layer": "BUILDING"},
            )

            # stair steps
            step_count = 6
            step_height = stair_h / step_count

            for i in range(step_count):

                y = stair_y + i * step_height

                msp.add_line(
                    (stair_x, y),
                    (stair_x + stair_w, y),
                    dxfattribs={"layer": "BUILDING"},
                )

            msp.add_text(
                "STAIR",
                dxfattribs={
                    "layer": "TEXT",
                    "height": 0.6,
                    "insert": (stair_x + 0.3, stair_y + stair_h + 0.2),
                },
            )



        # -----------------------
        # DIMENSIONS
        # -----------------------

        msp.add_linear_dim(
            base=(length / 2, -2),
            p1=(0, 0),
            p2=(length, 0),
            angle=0,
            dxfattribs={"layer": "DIMENSIONS"},
        ).render()

        msp.add_linear_dim(
            base=(-2, width / 2),
            p1=(0, 0),
            p2=(0, width),
            angle=90,
            dxfattribs={"layer": "DIMENSIONS"},
        ).render()

        # -----------------------
        # NORTH ARROW
        # -----------------------

        north_x = length + 5
        north_y = width - 2

        msp.add_line((north_x, north_y), (north_x, north_y + 3), dxfattribs={"layer": "TITLE"})
        msp.add_text(
            "N",
            dxfattribs={
                "layer": "TITLE",
                "height": 1,
                "insert": (north_x - 0.3, north_y + 3.5),
            },
        )

        # -----------------------
        # TITLE
        # -----------------------

        msp.add_text(
            f"Plot Size: {length}m x {width}m",
            dxfattribs={"layer": "TITLE", "height": 0.8, "insert": (0, width + 3)},
        )

        msp.add_text(
            f"Floors: {floors}",
            dxfattribs={"layer": "TITLE", "height": 0.8, "insert": (0, width + 2)},
        )

        doc.saveas(filepath)

        return {
            "design_id": str(uuid4()),
            "file": filepath,
            "plot": {"length": length, "width": width},
            "building": {
                "footprint_width": footprint_w,
                "footprint_height": footprint_h,
            },
        }

    except Exception as e:
        print("DXF GENERATION ERROR:", e)
        raise e