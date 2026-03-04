import os
import re
import base64
import anthropic
import fitz  # PyMuPDF

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# ──────────────────────────────────────────
# Cliente Anthropic (API key desde env var)
# ──────────────────────────────────────────
def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY no configurada")
    return anthropic.Anthropic(api_key=api_key)


# ──────────────────────────────────────────
# Cargar el prompt base desde archivo
# ──────────────────────────────────────────
def load_prompt() -> str:
    with open("prompt_template.txt", "r", encoding="utf-8") as f:
        return f.read()


def load_html_template() -> str:
    with open("static/html_template.txt", "r", encoding="utf-8") as f:
        return f.read()


# ──────────────────────────────────────────
# Página principal
# ──────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
def index():
    return FileResponse("static/index.html")


# ──────────────────────────────────────────
# Endpoint principal de generación
# ──────────────────────────────────────────
@app.post("/generar")
async def generar(
    texto: str = Form(default=""),
    nivel: str = Form(default="Secundaria"),
    archivo: UploadFile = File(default=None),
):
    client = get_client()
    prompt_base = load_prompt()
    html_template = load_html_template()

    # ── Construir el prompt final ──
    nivel_desc = {
        "Primaria":    "niños de 6-12 años: lenguaje muy simple, ejemplos de la vida cotidiana, preguntas muy fáciles y directas.",
        "Secundaria":  "estudiantes de 12-16 años: lenguaje claro y cercano, ejemplos reales, dificultad media.",
        "Bachillerato":"estudiantes de 16-18 años: términos técnicos básicos, razonamiento aplicado, preguntas más exigentes.",
        "Universidad": "estudiantes universitarios: terminología científica completa, conceptos avanzados, preguntas de análisis.",
        "Posgrado":    "especialistas: nivel avanzado, preguntas de síntesis, evaluación crítica y conexiones entre conceptos.",
    }.get(nivel, "estudiantes de 12-16 años.")

    # ── Procesar archivo si existe ──
    if archivo and archivo.filename:
        data = await archivo.read()
        content_type = archivo.content_type or ""

        # PDF → extraer texto
        if "pdf" in content_type or archivo.filename.lower().endswith(".pdf"):
            doc = fitz.open(stream=data, filetype="pdf")
            contenido_texto = "\n".join(page.get_text() for page in doc)

            if not contenido_texto.strip():
                raise HTTPException(status_code=400, detail="No se pudo extraer texto del PDF.")

            prompt_final = prompt_base.format(
                nivel=nivel,
                nivel_desc=nivel_desc,
                html_template=html_template,
                contenido=contenido_texto[:10000],  # límite seguro de tokens
            )
            messages = [{"role": "user", "content": prompt_final}]

        # Imagen → mandar a Claude Vision
        elif content_type.startswith("image/"):
            b64 = base64.b64encode(data).decode()
            prompt_final = prompt_base.format(
                nivel=nivel,
                nivel_desc=nivel_desc,
                html_template=html_template,
                contenido="[El contenido está en la imagen adjunta. Analízala completamente.]",
            )
            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64",
                        "media_type": content_type,
                        "data": b64,
                    }},
                    {"type": "text", "text": prompt_final},
                ],
            }]

        else:
            raise HTTPException(status_code=400, detail="Formato no soportado. Usa PDF, imagen o texto.")

    # Solo texto
    elif texto.strip():
        prompt_final = prompt_base.format(
            nivel=nivel,
            nivel_desc=nivel_desc,
            html_template=html_template,
            contenido=texto[:12000],
        )
        messages = [{"role": "user", "content": prompt_final}]

    else:
        raise HTTPException(status_code=400, detail="Debes proporcionar texto, PDF o imagen.")

    # ── Llamada a la API ──
    try:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=8000,
            messages=messages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al llamar a la API: {str(e)}")

    raw = response.content[0].text

    # Limpiar si el modelo devuelve bloques de código markdown
    html_match = re.search(r"```html\s*([\s\S]*?)```", raw)
    html_output = html_match.group(1).strip() if html_match else raw.strip()

    return JSONResponse({"html": html_output})
