from fastapi import APIRouter, Depends
from typing import List, Dict, Optional
from api.database.public.crud.asyn import *
from api.resources import APIResponse

enumerations_router = APIRouter(
    prefix="/enums",
    tags=["Enumeraciones"]
)

