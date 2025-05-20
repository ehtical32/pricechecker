from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PriceRequest(BaseModel):
    url: str

def get_amazon_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find(id="productTitle").get_text(strip=True)
    price = soup.find(class_="a-offscreen").get_text(strip=True)
    return {"title": title, "price": price}

scraper_map = {
    "amazon.com": get_amazon_price,
}

@app.post("/check-price")
def check_price(data: PriceRequest):
    domain = urlparse(data.url).netloc.replace("www.", "")
    for supported in scraper_map:
        if supported in domain:
            try:
                return scraper_map[supported](data.url)
            except Exception as e:
                return {"error": f"Scraper failed: {str(e)}"}
    return {"error": f"Unsupported domain: {domain}"}
