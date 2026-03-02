from fastapi import APIRouter
from .database import database_router

main_router = APIRouter()

main_router.include_router(database_router)
