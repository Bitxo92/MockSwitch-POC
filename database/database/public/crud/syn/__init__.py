# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente

from __future__ import annotations
from typing import Optional
from .session_manager import SyncSessionManager
from .dtos import *
from .daos import *
from .utils import sqlalchemy_table_mapper

class PublicSyncDBAPI:
    """
    API principal para operaciones de base de datos síncronas.
    
    Esta clase proporciona acceso centralizado a todas las operaciones CRUD
    con gestión automática de sesiones SQLAlchemy. Implementa el patrón
    de fachada para simplificar el acceso a los diferentes modelos de datos.
    
    Características principales:
    - Gestión automática del ciclo de vida de sesiones
    - Acceso unificado a todos los modelos DAO
    - Soporte para operaciones transaccionales
    - Context managers para manejo de transacciones
    
    Atributos:
        session_manager (SyncSessionManager): Gestor de sesiones SQLAlchemy
        agenda (AgendaSyncDAO): Operaciones CRUD para Agenda
    
    Ejemplos de uso:
        ```python
        # Operaciones simples
        user = db_api.user.create(name="Juan", email="juan@email.com")
        found_user = db_api.user.find(email="juan@email.com")
        
        # Operaciones transaccionales
        with db_api.session_manager.get_session() as session:
            user = db_api.user.create(name="Ana", session=session)
            post = db_api.post.create(title="Post", author_id=user.id, session=session)
        ```
    """

    _instance: Optional[PublicSyncDBAPI] = None

    def __new__(cls) -> PublicSyncDBAPI:
        """Implementación del patrón Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa la API con un gestor de sesiones síncrono"""
        if not self._initialized:
            self._session_manager = SyncSessionManager()
            self._initialized = True
    
    @property
    def session_manager(self) -> SyncSessionManager:
        """
        Acceso al gestor de sesiones.
        
        El SessionManager proporciona:
        - get_session(): Context manager para sesiones individuales
        
        Returns:
            SyncSessionManager: Instancia del gestor de sesiones
        """
        return self._session_manager
    
    @property
    def agenda(self) -> AgendaSyncDAO:
        """
        Acceso a operaciones CRUD para el modelo Agenda.
        
        Operaciones disponibles:
        - `find`: Buscar un registro por filtros
        - `find_many`: Buscar múltiples registros
        - `create`: Crear un nuevo registro
        - `create_many`: Crear múltiples registros
        - `update`: Actualizar registro existente
        - `update_many`: Actualizar registros existentes
        - `upsert`: Inserta o actualiza un registro
        - `upsert_many`: Inserta o actualiza múltiples registros
        - `delete`: Eliminar un registro
        - `delete_many`: Eliminar varios registros
        
        Returns:
            AgendaSyncDAO: Instancia DAO para Agenda
        """
        return AgendaSyncDAO(self._session_manager)



# Instancia global para fácil acceso
public_api = PublicSyncDBAPI()

# Exportar tanto la clase como la instancia
__all__ = [
    'PublicSyncDBAPI',
    'public_api',
    'sqlalchemy_table_mapper',
    'AggregationResult',
    'RLS',
    'Agenda',
    'AgendaRead',
    'AgendaCreate',
    'AgendaFilter',
    'AgendaUpdate',
    'AgendaUpdateValues',
]