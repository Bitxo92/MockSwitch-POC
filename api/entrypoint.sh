#!/bin/sh

# Puerto dinámico (Azure proporciona PORT)
: "${PORT:=80}"

# Arranca la app con uvicorn; ajusta el módulo si tu app expone el FastAPI en otro sitio
exec uvicorn api.__main__:app --host 0.0.0.0 --port "$PORT"