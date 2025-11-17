"""
main.py - Backend FastAPI para o Gerador/Avaliador de Senhas
Trabalho: Tópicos de Big Data em Python
Alunos: João Pedro, Maria Eduarda e Davi

Este arquivo expõe 2 endpoints principais:
- POST /avaliar  -> recebe {"senha": "..."} e retorna avaliação (pontuação, problemas, entropia, nível)
- GET  /gerar    -> parâmetros: tamanho (int) e simbolos (bool) -> retorna {"senha": "..."}

Observações de segurança:
- Este servidor NÃO armazena senhas.
- Sempre use HTTPS em produção.
- Considere limitar taxa de requisições (rate-limiting) para prevenir abuso.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import secrets
import string
import math
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Gerador e Avaliador de Senhas")

# Monta pasta estática para servir CSS/JS
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Lista de senhas muito comuns (pode ser aumentada)
SENHAS_COMUNS = {
    "123456", "senha", "12345678", "admin", "abc123", "qwerty",
    "111111", "123123", "admin123", "familia", "000000", "login",
    "senha123", "qwerty123", "flamengo"
}

class EntradaSenha(BaseModel):
    senha: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """Retorna o HTML principal (templates/index.html)."""
    return FileResponse(BASE_DIR / "templates" / "index.html")


def avaliar_senha(senha: str):
    """Avalia a senha e retorna: (pontuacao, problemas, nivel, entropia_bits)."""
    if senha is None:
        return 0, ["Senha vazia"], "Fraca", 0
    senha = senha.strip()
    if senha == "":
        return 0, ["Senha vazia"], "Fraca", 0

    problemas = []
    tamanho = len(senha)

    # Verifica tipos de caracteres
    minuscula = any(c.islower() for c in senha)
    maiuscula = any(c.isupper() for c in senha)
    numero = any(c.isdigit() for c in senha)
    simbolo = any(not c.isalnum() for c in senha)

    # Pontuação baseada em tamanho e variedade
    pontos_tamanho = (min(tamanho, 20) / 20) * 40
    pontos_variedade = (minuscula + maiuscula + numero + simbolo) * 10

    # Calcula entropia
    conjunto_caracteres = 0
    if minuscula:
        conjunto_caracteres += 26
    if maiuscula:
        conjunto_caracteres += 26
    if numero:
        conjunto_caracteres += 10
    if simbolo:
        conjunto_caracteres += 32

    entropia_bits = 0
    if conjunto_caracteres > 0:
        entropia_bits = int(tamanho * math.log2(conjunto_caracteres))

    bonus = min((entropia_bits / 60) * 20, 20)
    pontuacao = int(round(min(pontos_tamanho + pontos_variedade + bonus, 100)))

    # Problemas detectados
    if tamanho < 8:
        problemas.append("Muito curta (menos de 8)")
    if not minuscula:
        problemas.append("Sem letras minúsculas")
    if not maiuscula:
        problemas.append("Sem letras maiúsculas")
    if not numero:
        problemas.append("Sem números")
    if not simbolo:
        problemas.append("Sem símbolos")
    if senha.lower() in SENHAS_COMUNS:
        problemas.append("Senha extremamente comum")

    # Classificação
    if pontuacao < 40:
        nivel = "Fraca"
    elif pontuacao < 70:
        nivel = "Média"
    elif pontuacao < 90:
        nivel = "Boa"
    else:
        nivel = "Excelente"

    return pontuacao, problemas, nivel, entropia_bits


@app.post("/avaliar")
async def api_avaliar(payload: EntradaSenha):
    """Endpoint que recebe JSON {"senha": "..."} e retorna avaliação."""
    pont, problemas, nivel, bits = avaliar_senha(payload.senha)
    return {
        "pontuacao": pont,
        "problemas": problemas,
        "nivel": nivel,
        "entropia_bits": bits
    }


@app.get("/gerar")
async def api_gerar(tamanho: int = 16, simbolos: bool = True):
    """Gera senha segura com `secrets`.

    Parâmetros:
    - tamanho: int (4..128)
    - simbolos: bool (incluir símbolos)
    """
    if tamanho < 4 or tamanho > 128:
        raise HTTPException(status_code=400, detail="Tamanho deve ser entre 4 e 128")

    caracteres = string.ascii_letters + string.digits
    if simbolos:
        caracteres += "!@#$%^&*()_+-=[]{};:,.<>?"

    senha = ''.join(secrets.choice(caracteres) for _ in range(tamanho))
    return {"senha": senha}

