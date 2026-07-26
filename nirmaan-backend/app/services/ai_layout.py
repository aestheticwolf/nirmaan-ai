import re
import os
import google.generativeai as genai
from app.services.ai_limiter import wait_if_needed

USE_AI = False


def generate_layout_from_prompt(prompt: str):

    # -----------------------
    # Prompt Protection
    # -----------------------

    if len(prompt) > 200:
        prompt = prompt[:200]

    prompt = prompt.lower()

    # -----------------------
    # OPTIONAL GEMINI AI
    # -----------------------

    if USE_AI:

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")

        wait_if_needed()

        response = model.generate_content(f"""
        Generate a residential house layout.

        Return JSON only.

        Example:
        {{
          "rooms":[
            {{"name":"Living Room"}},
            {{"name":"Kitchen"}},
            {{"name":"Bedroom"}},
            {{"name":"Bathroom"}}
          ]
        }}

        Prompt: {prompt}
        """)

        return response.text

    # -----------------------
    # RULE BASED LAYOUT
    # -----------------------

    layout = []

    # Detect bedroom count
    bedroom_match = re.search(r"(\d+)\s*bed", prompt)

    if bedroom_match:
        bedroom_count = int(bedroom_match.group(1))
    else:
        bedroom_count = 2

    # FRONT ZONE
    if "parking" in prompt or "garage" in prompt:
        layout.append({"name": "Parking", "zone": "front"})

    layout.append({"name": "Living Room", "zone": "front"})

    # CENTER ZONE
    if "dining" in prompt:
        layout.append({"name": "Dining", "zone": "center"})

    layout.append({"name": "Kitchen", "zone": "center"})

    # PRIVATE ZONE
    for i in range(bedroom_count):
        layout.append({"name": "Bedroom", "zone": "private"})

    # SERVICE ZONE
    layout.append({"name": "Bathroom", "zone": "service"})

    if "study" in prompt:
        layout.append({"name": "Study Room", "zone": "private"})

    if "office" in prompt:
        layout.append({"name": "Home Office", "zone": "private"})

    if "store" in prompt:
        layout.append({"name": "Store Room", "zone": "service"})

    return {
        "rooms": layout
    }