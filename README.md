---
title: TutorIA Plus
emoji: 🎓
colorFrom: green
colorTo: teal
sdk: docker
pinned: false
---

# 🎓 Generador de Guías de Estudio

Convierte PDFs, imágenes o texto en guías HTML interactivas con quiz adaptadas por nivel educativo.
Con ayuda de la IA puedes transformar una aburrida tarde de estudio
en una experiencia interactiva y desafiante.

---

## 📁 Estructura del proyecto

```
study-guide-app/
│
├── app.py                  ← Backend FastAPI (NO tocar la lógica)
├── requirements.txt        ← Dependencias Python
├── prompt_template.txt     ← ⭐ EL PROMPT (edita esto para cambiar el output)
│
└── static/
    ├── index.html          ← Frontend (UI del generador)
    └── html_template.txt   ← Plantilla CSS/JS fija que el modelo reutiliza
```

### ¿Qué archivo edito para cambiar qué?

| Quiero cambiar...              | Edito...                    |
|--------------------------------|-----------------------------|
| Los colores del HTML generado  | `static/html_template.txt`  |
| Las instrucciones al modelo    | `prompt_template.txt`       |
| La UI de la app                | `static/index.html`         |
| El modelo o parámetros API     | `app.py`                    |

---

## 🚀 Despliegue en Hugging Face Spaces (GRATIS)

### Paso 1 — Crea tu cuenta y espacio

1. Ve a https://huggingface.co y crea una cuenta gratuita
2. Haz clic en **"New Space"**
3. Configura:
   - **Space name**: `study-guide-generator` (o el nombre que quieras)
   - **SDK**: selecciona **"Docker"**  ← importante
   - **Visibility**: Public (gratis) o Private
4. Haz clic en **"Create Space"**

### Paso 2 — Añade tu API key de Anthropic

1. En tu Space, ve a **Settings → Variables and secrets**
2. Haz clic en **"New secret"**
3. Nombre: `ANTHROPIC_API_KEY`
4. Valor: tu API key de Anthropic (https://console.anthropic.com)
5. Guarda

> ⚠️ Nunca pongas la API key directamente en el código.

### Paso 3 — Sube los archivos

**Opción A — Desde la web de HuggingFace:**
1. En tu Space, haz clic en **"Files"** → **"Add file"**
2. Sube todos los archivos manteniendo la estructura de carpetas

### Paso 4 — Verifica que esté corriendo

HuggingFace construirá el contenedor automáticamente. En 2-3 minutos verás tu app en:
```
https://huggingface.co/spaces/TU_USUARIO/study-guide-generator
```

---

## 💻 Ejecutar en local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux/Mac
set ANTHROPIC_API_KEY=sk-ant-...        # Windows

# Arrancar
uvicorn app:app --reload --port 7860

# Abrir en el navegador
http://localhost:7860
```

---

## ✏️ Personalizar el prompt

El archivo `prompt_template.txt` usa estas variables que se rellenan automáticamente:

```
{nivel}       ← "Secundaria", "Universidad", etc.
{nivel_desc}  ← descripción detallada del nivel
{html_template} ← la plantilla CSS/JS fija
{contenido}   ← el texto extraído del PDF/imagen/texto
```

Puedes editar el texto alrededor de estas variables con total libertad.

---

## 🎨 Cambiar los colores del HTML generado

Abre `static/html_template.txt` y busca la línea `:root{...}`.
Cambia los valores hexadecimales:
- `--gd` → verde oscuro (headers, títulos)
- `--gm` → verde medio (botones, acentos)
- `--gp` → verde pálido (fondos suaves)

---

## ❓ Problemas frecuentes

**"ANTHROPIC_API_KEY no configurada"**
→ Añade el secret en HuggingFace Settings o el export en local

**El HTML generado viene con bloques ```html**
→ Ya está manejado en app.py con regex. Si persiste, añade al prompt: "No uses bloques de markdown"

**El PDF no extrae texto (PDF escaneado)**
→ Son imágenes dentro de un PDF. Usa el campo de imagen en su lugar, o activa OCR con `pytesseract`

**Error 500 en archivos grandes**
→ El límite actual es 12.000 caracteres de contenido. Puedes subirlo en `app.py` ajustando el slice `[:12000]`
