"""
. - Main Application
Generado automáticamente por tai-api

Este es el archivo principal de la aplicación FastAPI.
Estado: Proyecto completo con autenticación y API de base de datos
"""
from pathlib import Path
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.resources import setup_exception_handlers
from fastapi.staticfiles import StaticFiles
from api.routers import main_router
description = """
<details>
<summary>Diagrama ER: public</summary>

![ER](/diagrams/public.png)

</details>
"""

app = FastAPI(
    title=".",
    version="0.1.0",
    description=description,
    
)

@app.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}

# Montar carpeta estática de diagramas
app.mount("/diagrams", StaticFiles(directory=Path(__file__).parent / "diagrams"), name="diagrams")


# Incluir router de API generada
app.include_router(main_router)


# Configurar manejadores de excepciones
setup_exception_handlers(app)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configurar según ambiente
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

