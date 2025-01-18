from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
import requests

# Configure the API Key
genai.configure(api_key="AIzaSyDCE7c8qcYCdXQ8uCwGn2y87xQkE9nfkp4")

# Initialize FastAPI app
app = FastAPI()

# Mount static files for CSS and JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Define function to fetch cryptocurrency data
def get_crypto_data(crypto_name: str):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto_name.lower()}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data["image"]["large"]
            launch_date = data.get("genesis_date", "Unknown")  # Get launch date, default to "Unknown"
            return image_url, launch_date
        else:
            return "https://via.placeholder.com/1920x1080?text=No+Image+Available", "Unknown"
    except Exception as e:
        return "https://via.placeholder.com/1920x1080?text=Error+Fetching+Image", "Unknown"

# Define the homepage route
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define the route to handle form submission
@app.post("/generate", response_class=HTMLResponse)
async def generate_topic(request: Request, topic: str = Form(...)):
    try:
        # Initialize the Generative AI model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate content for each section
        definition = model.generate_content(f"Provide the definition of {topic}.").text
        history = model.generate_content(f"Explain the history of {topic}.").text
        why_it_works = model.generate_content(f"Why does {topic} work?").text
        explain_like_5 = model.generate_content(f"Explain {topic} as if I am 5 years old.").text

        # Fetch cryptocurrency image and launch date
        image_url, launch_date = get_crypto_data(topic)

        # Structure the explanation under headings
        explanation = {
            "Definition": definition,
            "History": history,
            "Why It Works": why_it_works,
            "Explain Like I'm 5": explain_like_5,
            "Launch Date": launch_date,
        }

    except Exception as e:
        explanation = {"Error": f"Unable to generate explanation: {str(e)}"}
        image_url = "https://via.placeholder.com/1920x1080?text=Error"

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "topic": topic, "explanation": explanation, "image_url": image_url},
    )
