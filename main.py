from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import os
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ТВОИ ИСПРАВЛЕННЫЕ ДАННЫЕ
YANDEX_API_KEY = "AQVN3IMaT2ojhFtddMWiE2DMNR429bX_bb7Vbu-w"
YANDEX_FOLDER_ID = "b1g1fditm7vaa4rqgp1p"  # ← ПРАВИЛЬНЫЙ (из ошибки)

class PromptRequest(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 500

HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ДайВарик с нейросетью</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 24px;
            padding: 32px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 { text-align: center; color: #333; margin-bottom: 24px; font-size: 32px; }
        .input-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #555; }
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            min-height: 100px;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:hover { opacity: 0.9; }
        button:active { transform: scale(0.98); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .result {
            margin-top: 24px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 16px;
            display: none;
        }
        .result.show { display: block; }
        .result-label { font-weight: 600; color: #667eea; margin-bottom: 8px; }
        .result-text { font-size: 18px; line-height: 1.5; color: #333; white-space: pre-wrap; }
        .loading {
            text-align: center;
            color: #667eea;
            margin-top: 20px;
            display: none;
        }
        .loading.show { display: block; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #e0e0e0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error { color: #dc3545; margin-top: 12px; text-align: center; display: none; }
        .error.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 ДайВарик с ИИ</h1>
        <div class="input-group">
            <label>Что хочешь предложить нейросети?</label>
            <textarea id="prompt" placeholder="Например: Предложи вариант ужина на сегодня..."></textarea>
        </div>
        <button id="generateBtn">✨ Дай Варик!</button>
        <div class="loading" id="loading">
            <span class="spinner"></span> Нейросеть думает...
        </div>
        <div class="result" id="result">
            <div class="result-label">🎲 Тебе выпало:</div>
            <div class="result-text" id="resultText"></div>
        </div>
        <div class="error" id="error"></div>
    </div>
    <script>
        const API_URL = '/generate';
        const promptInput = document.getElementById('prompt');
        const generateBtn = document.getElementById('generateBtn');
        const loadingDiv = document.getElementById('loading');
        const resultDiv = document.getElementById('result');
        const resultText = document.getElementById('resultText');
        const errorDiv = document.getElementById('error');

        generateBtn.addEventListener('click', async () => {
            const prompt = promptInput.value.trim();
            if (!prompt) {
                showError('Напиши свой вопрос или запрос 😊');
                return;
            }
            resultDiv.classList.remove('show');
            errorDiv.classList.remove('show');
            loadingDiv.classList.add('show');
            generateBtn.disabled = true;

            try {
                const response = await fetch(API_URL, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ prompt: prompt, temperature: 0.8, max_tokens: 500 })
                });
                if (!response.ok) {
                    const err = await response.text();
                    throw new Error(`Ошибка ${response.status}: ${err}`);
                }
                const data = await response.json();
                resultText.textContent = data.text || 'Нейросеть ничего не ответила 🤔';
                resultDiv.classList.add('show');
            } catch (error) {
                showError(`Ошибка: ${error.message}`);
            } finally {
                loadingDiv.classList.remove('show');
                generateBtn.disabled = false;
            }
        });

        function showError(message) {
            errorDiv.textContent = message;
            errorDiv.classList.add('show');
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE

@app.post("/generate")
async def generate_text(request: PromptRequest):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    
    payload = {
        "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": request.temperature,
            "maxTokens": request.max_tokens
        },
        "messages": [
            {"role": "user", "text": request.prompt}
        ]
    }
    
    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Запрос: {request.prompt[:50]}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            text = data.get("result", {}).get("alternatives", [{}])[0].get("message", {}).get("text", "Нет ответа")
            logger.info(f"Ответ: {text[:50]}...")
            return {"text": text}
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Ошибка API: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
