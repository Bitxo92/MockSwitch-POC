from fastapi import APIRouter
from .router_agenda import agenda_router
from .router_enums import enumerations_router

public_router = APIRouter(prefix="/public")

public_router.include_router(agenda_router)
public_router.include_router(enumerations_router)
