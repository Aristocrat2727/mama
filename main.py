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

# ТВОЙ API КЛЮЧ (уже вставлен)
OPENROUTER_API_KEY = "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"

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
    <title>Shadow AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 32px;
            padding: 32px;
            max-width: 700px;
            width: 100%;
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }
        h1 { 
            text-align: center; 
            color: #fff; 
            margin-bottom: 8px; 
            font-size: 42px;
            text-shadow: 0 0 20px rgba(255,255,255,0.3);
        }
        .subtitle { text-align: center; color: rgba(255,255,255,0.6); margin-bottom: 32px; }
        .input-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #fff; }
        textarea {
            width: 100%;
            padding: 16px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 16px;
            font-size: 16px;
            font-family: inherit;
            color: #fff;
            resize: vertical;
            min-height: 120px;
        }
        textarea:focus { outline: none; border-color: #667eea; }
        textarea::placeholder { color: rgba(255,255,255,0.4); }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 16px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }
        button:hover { opacity: 0.9; transform: scale(1.02); }
        button:active { transform: scale(0.98); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .result {
            margin-top: 24px;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 16px;
            display: none;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .result.show { display: block; }
        .result-label { font-weight: 600; color: #667eea; margin-bottom: 8px; }
        .result-text { font-size: 16px; line-height: 1.6; color: rgba(255,255,255,0.9); white-space: pre-wrap; }
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
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .error { color: #ff6b6b; margin-top: 12px; text-align: center; display: none; }
        .error.show { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖤 Shadow AI</h1>
        <div class="subtitle">Твой личный тёмный помощник</div>
        <div class="input-group">
            <label>Что хочешь спросить?</label>
            <textarea id="prompt" placeholder="Напиши свой вопрос..."></textarea>
        </div>
        <button id="generateBtn">⚡ Спросить Shadow</button>
        <div class="loading" id="loading">
            <span class="spinner"></span> Shadow думает...
        </div>
        <div class="result" id="result">
            <div class="result-label">🎭 Shadow отвечает:</div>
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
                showError('Напиши свой вопрос 😊');
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
                    throw new Error(`Ошибка ${response.status}`);
                }
                const data = await response.json();
                resultText.textContent = data.text || 'Shadow молчит... 🤔';
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
    """Отправляет запрос к OpenRouter"""
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": request.prompt}
        ],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Shadow получил: {request.prompt[:50]}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            data = response.json()
            
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
            logger.info(f"Shadow ответил")
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
