def edit_layout_with_prompt(layout, prompt):

    prompt = prompt.lower()

    rooms = layout.get("rooms", [])

    # Add bedroom
    if "add bedroom" in prompt:
        rooms.append({
            "name": "Bedroom",
            "width": 4,
            "height": 4
        })

    # Make kitchen bigger
    if "bigger kitchen" in prompt:
        for r in rooms:
            if "kitchen" in r["name"].lower():

                # create width if missing
                if "width" not in r:
                    r["width"] = 3

                if "height" not in r:
                    r["height"] = 3

                r["width"] += 1
                r["height"] += 1

    # Add parking
    if "parking" in prompt:
        rooms.append({
            "name": "Parking",
            "width": 5,
            "height": 3
        })

    layout["rooms"] = rooms

    return layout