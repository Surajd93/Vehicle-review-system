import os
from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import google.generativeai as genai
import markdown

from prompt_templates import VEHICLE_FEATURE_PROMPT #prompt

app = FastAPI(title="Vehicle Feature and Comparison Guide")

# Set up templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Gemini API Config (✅ use environment variable instead of hardcoding)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Gemini API Key not found. Please set GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
DEFAULT_MODEL = "gemini-2.0-flash"


# -------------------- Home Page --------------------
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# -------------------- Vehicle Comparison --------------------
@app.post("/compare")
async def compare_vehicles(
    request: Request,
    vehicle1: str = Form(...),
    vehicle2: str = Form(...),
    include_features: bool = Form(True),
    tone: str = Form("informative"),
    model: str = Form(DEFAULT_MODEL)
):
    try:
        # Generate AI prompt
        prompt = VEHICLE_FEATURE_PROMPT.format(
            vehicle1=vehicle1,
            vehicle2=vehicle2,
            include_features="including detailed features" if include_features else "without features",
            tone=tone
        )

        # ✅ Correct Gemini usage
        gemini_model = genai.GenerativeModel(model_name=model) # to fetch the gemini model
        response = gemini_model.generate_content(prompt)

        generated_text = response.text if response else ""

        # ✅ Clean up text
        clean_text = (
            generated_text.replace("✅", "Yes")
            .replace("❌", "No")
            .replace("$", "₹")
            .replace("USD", "₹")
            .replace("INR", "₹")
        )

        # Convert markdown → HTML
        html_content = markdown.markdown(clean_text, extensions=["extra", "tables"])

        # ✅ Add Chart.js script if Price & Variants table exists
        if "Price & Variants" in clean_text:
            html_content += f"""
            <canvas id="priceChart" style="margin-top:20px;max-width:100%;height:400px;"></canvas>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
              const table = document.querySelector("table");
              if(table){{
                const rows = Array.from(table.rows).slice(1);
                let variants = [], prices1 = [], prices2 = [];
                rows.forEach(row => {{
                  const cols = row.querySelectorAll("td");
                  if(cols.length === 3){{
                    variants.push(cols[0].innerText.trim());
                    prices1.push(parseInt(cols[1].innerText.replace(/[^0-9]/g,"")) || 0);
                    prices2.push(parseInt(cols[2].innerText.replace(/[^0-9]/g,"")) || 0);
                  }}
                }});
                if(variants.length > 0){{
                  new Chart(document.getElementById("priceChart"), {{
                    type: "bar",
                    data: {{
                      labels: variants,
                      datasets: [
                        {{ label: "{vehicle1}", data: prices1, backgroundColor: "#2575fc" }},
                        {{ label: "{vehicle2}", data: prices2, backgroundColor: "#ff512f" }}
                      ]
                    }},
                    options: {{
                      responsive: true,
                      scales: {{ y: {{ beginAtZero: true, ticks: {{ callback: v => "₹ " + v.toLocaleString("en-IN") }} }} }}
                    }}
                  }});
                }}
              }}
            </script>
            """

        return JSONResponse(content={"success": True, "result": html_content})

    except Exception as e:
        print(f"Error comparing vehicles: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


# -------------------- Chatbot --------------------
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")

        if not user_message:
            return JSONResponse(content={"success": False, "error": "No message provided"}, status_code=400)

        # Use Gemini model
        gemini_model = genai.GenerativeModel(model_name=DEFAULT_MODEL)
        response = gemini_model.generate_content(user_message)
        reply = response.text if response else "⚠️ No response from AI."

        return JSONResponse(content={"success": True, "reply": reply})

    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


# -------------------- Run Server --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
