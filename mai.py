from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Optional

app = FastAPI()

# Разрешаем CORS для любых фронтов (можно засунуть любой домен)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для тестов, в проде замени на свой домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Твой API ключ (лучше через переменную окружения на Railway)
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "AQVNxQfbrDomM2y58QHVDb541C2u_IFgLQai2x4R")

# Модель запроса от фронта
class PromptRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

# Модель ответа от Яндекса (упрощённо)
class YandexResponse(BaseModel):
    text: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "Прокси для YandexGPT работает"}

@app.post("/generate")
async def generate_text(request: PromptRequest):
    """Принимает запрос с фронта, шлёт в YandexGPT, возвращает ответ"""
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    # Формируем тело запроса для YandexGPT (по документации)
    payload = {
        "modelUri": "gpt://b1g3nfqrfn1e3b5e3r5d/yandexgpt-lite",  # замени на свой folder ID
        "completionOptions": {
            "stream": False,
            "temperature": request.temperature,
            "maxTokens": request.max_tokens
        },
        "messages": [
            {
                "role": "user",
                "text": request.prompt
            }
        ]
    }
    
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            # Извлекаем текст из ответа Яндекса (структура может отличаться)
            text = data.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Нет ответа")
            
            return {"text": text}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# Если нужен стриминг (для чатов с постепенным выводом) — могу добавить