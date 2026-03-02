from fastapi import APIRouter
from .public import public_router

database_router = APIRouter()

database_router.include_router(public_router)
