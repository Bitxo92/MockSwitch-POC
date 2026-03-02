# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente
from __future__ import annotations
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Literal,
    Any,
    TYPE_CHECKING
)
from datetime import datetime, date, time
from sqlalchemy.orm import Session
from sqlalchemy import (
    select,
    update,
    delete,
    func,
    or_,
    and_
)
from .session_manager import SyncSessionManager
from .dtos import *
from .utils import (
    error_handler,
    get_loading_options,
    load_relationships_from_dto,
    RLSQueryApplicator,
    ExpressionParser,
    RLS
)
from database.public.models import *
from tai_alphi import Alphi


if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]

# Logger
logger = Alphi.get_logger_by_name("tai-sql")


class AgendaSyncDAO:
    """
    Clase DAO síncrona para el modelo Agenda.
    
    Proporciona operaciones completas de Create, Read, Update y Delete
    para el modelo Agenda con soporte para gestión automática
    y manual de sesiones SQLAlchemy.
    
    Características principales:
    - Soporte dual: sesiones automáticas o compartidas
    - Type hints completos para mejor experiencia de desarrollo
    - Manejo robusto de errores con rollback automático
    - Operaciones optimizadas con flush para obtener IDs
    - Filtros flexibles en todas las operaciones de búsqueda
    
    Métodos de lectura:
        find(**filters, session=None): Busca un único registro
        find_many(limit, offset, order_by, order, **filters, session=None): Busca múltiples registros
        count(**filters, session=None): Cuenta registros
    
    Métodos de escritura:
        create(**data, session=None): Crea un nuevo registro
        create_many(records, session=None): Crea múltiples registros
        update(filters, **data, session=None): Actualiza registros existentes
        delete(**filters, session=None): Elimina registros

    Parámetros de sesión:
        Todos los métodos aceptan un parámetro opcional 'session':
        - Si session=None: Se crea una sesión automática con commit
        - Si session=Session: Se usa la sesión proporcionada (para transacciones)
    
    Ejemplos de uso:
        ```python
        # Operaciones simples (sesión automática)
        crud = AgendaSyncDAO(session_manager)
        found = crud.find_by_id(1)
        
        # Operaciones transaccionales (sesión compartida)
        with session_manager.transaction() as session:
            record1 = crud.create(data="valor1", session=session)
            record2 = crud.create(data="valor2", session=session)
            # Ambos se crean en la misma transacción
        ```
    """
    
    # Constantes de validación para agregaciones
    OPERATION_TYPE_VALIDATORS = {
        'sum': ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT'],
        'mean': ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT'],
        'max': ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT', 'DATETIME', 'TIMESTAMP', 'DATE', 'TIME'],
        'min': ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT', 'DATETIME', 'TIMESTAMP', 'DATE', 'TIME'],
        'count': ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT', 'DATETIME', 'TIMESTAMP', 'DATE', 'TIME', 'VARCHAR', 'TEXT', 'CHAR', 'STRING', 'BOOLEAN', 'BOOL']
    }
    
    OPERATION_FUNCTIONS = {
        'sum': func.sum,
        'mean': func.avg,
        'max': func.max,
        'min': func.min,
        'count': func.count
    }
    
    def __init__(self, session_manager: SyncSessionManager):
        """
        Inicializa el SyncDAO con un gestor de sesiones.
        
        Args:
            session_manager: Gestor de sesiones síncronas
        """
        self.session_manager = session_manager
        self._df_validator = AgendaDataFrameValidator()

    @error_handler
    def find(
        self,
        id: int,
        includes: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> Optional[AgendaRead]:
        """
        Busca un único registro por primary key con carga optimizada de relaciones.
        
        Args:
            id: Filtrar por id
            includes: Lista de relaciones a incluir  (formato: 'relation' o 'relation.nested')
            session: Sesión existente (opcional)
            
        Returns:
            Instancia del modelo o None si no se encuentra

        Examples:
            Incluir relación simple

            dao.find(id=1, includes=['author'])
            
            Incluir relaciones anidadas

            dao.find(id=1, includes=['author', 'author.posts'])
            
            Múltiples relaciones

            dao.find(id=1, includes=['author', 'comments', 'tags'])
        """
        logger.info(f"[public] 🔍 Buscando Agenda:")
        logger.info(f"[public]     id={id}")
        logger.info(f"[public]     includes={includes}")

        # Construir query base
        query = select(Agenda)
        
        query = query.where(Agenda.id == id)

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, Agenda, rls)

        # Aplicar opciones de carga optimizada
        if includes:
            loading_options = get_loading_options(Agenda, includes)
            if loading_options:
                query = query.options(*loading_options)

        # Ejecutar query
        def execute_query(session: Session) -> Optional[AgendaRead]:
            result = session.execute(query)
            instance = result.scalars().first()
            
            if instance:
                logger.info(f"[public] ✅ Agenda encontrado exitosamente")
                return AgendaRead.from_instance(
                    instance, 
                    includes=includes, 
                    max_depth=5
                )
            else:
                logger.info(f"[public] 📭 Agenda no encontrado")
                return None

        if session is not None:
            return execute_query(session)
        else:
            with self.session_manager.get_session() as session:
                return execute_query(session)
    
    @error_handler
    def find_many(
        self,
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        order_by: Optional[List[str]] = None,
        order: Literal["ASC", "DESC"] = "ASC",
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        includes: Optional[List[str]] = None,
        rls: Optional[Union[List[RLS], RLS]] = None,
        session: Optional[Session] = None
    ) -> List[AgendaRead]:
        """
        Busca múltiples registros, filtrados, con carga optimizada de relaciones.
        
        Args:
        - limit: Límite de registros a retornar
        - offset: Número de registros a saltar
        - order_by: Lista de nombres de columnas para ordenar los resultados
        - order: ASC/DESC (por defecto ASC). Solo se aplica si se especifica order_by.
        - nombre: Filtrar por nombre
        - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
        - correo: Filtrar por correo
        - in_correo: Filtrar por múltiples valores de correo (OR lógico)
        - telefono: Filtrar por telefono
        - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
        - includes: Lista de relaciones a incluir (formato: 'relation' o 'relation.nested')
        - session: Sesión existente (opcional)
            
        Returns:
            Lista de instancias del modelo

        Examples:
            Búsqueda simple con relaciones

            dao.find_many(limit=10, includes=['author'])
            
            Relaciones anidadas

            dao.find_many(
                ..., 
                includes=['author', 'author.profile', 'comments']
            )
            
            Ordenamiento ascendente por columnas

            dao.find_many(order_by=['created_at', 'name'], order='ASC')
            
            Ordenamiento descendente por columnas

            dao.find_many(order_by=['created_at', 'name'], order='DESC')
            
            Paginación

            # Obtener los primeros 10 registros
            dao.find_many(limit=10)
            
            # Obtener los últimos 5 registros ordenados por fecha
            dao.find_many(limit=5, order_by=['created_at'], order='DESC')
            
            # Paginación con offset
            dao.find_many(limit=10, offset=20)
        """
        logger.info(f"[public] 🔍 Buscando múltiples Agenda:")
        logger.info(f"[public]     limit={limit}")
        logger.info(f"[public]     offset={offset}")
        logger.info(f"[public]     order_by={order_by}")
        logger.info(f"[public]     order={order}")
        logger.info(f"[public]     includes={includes}")

        # Construir query base
        query = select(Agenda)
        
        # Filters
        filters = {}
        
        # Aplicar filtros de búsqueda
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        # Aplicar regla RLS (si existe)
        if rls is not None:
            query = RLSQueryApplicator.apply_rls(query, Agenda, rls)
        
        # Aplicar opciones de carga optimizada
        if includes:
            loading_options = get_loading_options(Agenda, includes)
            if loading_options:
                query = query.options(*loading_options)
        
        # Aplicar ordenamiento
        if order_by:
            for column_name in order_by:
                if hasattr(Agenda, column_name):
                    column = getattr(Agenda, column_name)
                    if order.upper() == "DESC":
                        query = query.order_by(column.desc())
                    elif order.upper() == "ASC":
                        query = query.order_by(column.asc())
                else:
                    logger.warning(f"[public] ⚠️ Columna '{column_name}' no existe en modelo Agenda, ignorando en order_by")

        # Aplicar límite (solo valores positivos)
        if limit is not None and limit > 0:
            query = query.limit(limit)

        # Aplicar paginación
        if offset is not None:
            query = query.offset(offset)

        # Ejecutar query
        def execute_query(session: Session) -> List[AgendaRead]:
            results = session.execute(query)
            instances = results.scalars().all()
            
            logger.info(f"[public] ✅ Encontrados {len(instances)} registros Agenda")

            return [
                AgendaRead.from_instance(
                    instance, 
                    includes=includes, 
                    max_depth=5
                ) 
                for instance in instances
            ]
        
        if session is not None:
            return execute_query(session)
        else:
            with self.session_manager.get_session() as session:
                return execute_query(session)

    def as_dataframe(
        self,
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        nombre: Optional[str] = None,
        correo: Optional[str] = None,
        telefono: Optional[str] = None,
    ) -> DataFrame:
        """
        Busca múltiples registros estableciendo filtros y devuelve el resultado como pandas DataFrame.
        
        Args:
            limit: Límite de registros a retornar (positivo para primeros n, negativo para últimos n - requiere order_by)
            offset: Número de registros a saltar
            nombre: Filtrar por nombre
            correo: Filtrar por correo
            telefono: Filtrar por telefono
            
        Returns:
            pandas.DataFrame con los registros encontrados
            
        Raises:
            ImportError: Si pandas no está instalado
            
        Example:
            ```python
            
            # Obtener todos los registros como DataFrame
            df = db_api.agenda.as_dataframe()
            
            # Con filtros y límites
            df = db_api.agenda.as_dataframe(
                limit=100,
                id="valor_filtro"
            )
            
            # Análisis de datos
            print(df.describe())
            print(df.head())
            
            # Exportar a CSV
            df.to_csv('agenda_data.csv', index=False)
            ```
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas no está instalado. Para usar find_as_dataframe(), instala pandas:\n"
                "pip install pandas\n"
                "o si usas poetry:\n"
                "poetry add pandas"
            )
        
        # Obtener los registros usando find_many
        records = self.find_many(
            limit=limit,
            offset=offset,
            nombre=nombre,
            correo=correo,
            telefono=telefono,
        )

        # Si no hay registros, devolver DataFrame vacío con las columnas del modelo
        if not records:
            return pd.DataFrame(columns=[
                'id',
                'nombre',
                'correo',
                'telefono'
            ])

        data = [record.to_dict() for record in records]
        
        # Crear DataFrame
        df = pd.DataFrame(data)
        
        # Optimizar tipos de datos si es posible
        return self._optimize_dataframe_dtypes(df)

    def _optimize_dataframe_dtypes(self, df: DataFrame) -> DataFrame:
        """
        Optimiza los tipos de datos del DataFrame basándose en las columnas del modelo.
        
        Args:
            df: DataFrame a optimizar
            
        Returns:
            DataFrame con tipos de datos optimizados
        """
        try:
            import pandas as pd
        except ImportError:
            # Si pandas no está disponible, devolver el DataFrame tal como está
            return df
        
        if df.empty:
            return df
        
        # Mapeo de tipos SQLAlchemy a tipos pandas optimizados
        type_mapping = {
            'id': 'int64',
            'nombre': 'string',
            'correo': 'string',
            'telefono': 'string'
        }
        
        # Aplicar conversiones de tipo de forma segura
        for column, target_type in type_mapping.items():
            if column in df.columns:
                try:
                    if target_type == 'int64':
                        # Manejar valores nulos en columnas enteras
                        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                    elif target_type == 'float64':
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    elif target_type == 'boolean':
                        df[column] = df[column].astype('boolean')
                    elif target_type == 'datetime64[ns]':
                        df[column] = pd.to_datetime(df[column], errors='coerce')
                    elif target_type == 'string':
                        df[column] = df[column].astype('string')
                    # 'object' se deja como está
                except Exception:
                    # Si falla la conversión, mantener el tipo original
                    continue
        
        return df

    def from_dataframe(
        self,
        df: DataFrame,
        validate_types: bool = False,
        ignore_extra_columns: bool = False,
        fill_missing_nullable: bool = True
    ) -> int:
        """
        Ingesta un DataFrame de pandas en la tabla correspondiente.
        
        Realiza validaciones de esquema y tipos de datos antes de la inserción,
        y permite diferentes modos de inserción (create o upsert).
        
        Args:
            df: DataFrame de pandas con los datos a insertar
            validate_types (False): Si True, valida tipos de datos del DataFrame
            ignore_extra_columns (False): Si True, ignora columnas extra del DataFrame
            fill_missing_nullable (True): Si True, llena con None las columnas nullable faltantes
            
        Returns:
            Número de registros creados o actualizados
            
        Raises:
            ImportError: Si pandas no está instalado
            ValueError: Si el DataFrame no cumple con el esquema requerido
            TypeError: Si los tipos de datos no son compatibles
            
        Example:
            ```python
            import pandas as pd
            
            crud = AgendaSyncDAO(session_manager)
            
            # Crear DataFrame
            df = pd.DataFrame({
                'id': [1, 2, 3],
                'nombre': ['valor1', 'valor2', 'valor3'],
                'correo': ['valor1', 'valor2', 'valor3'],
                'telefono': ['valor1', 'valor2', 'valor3']
            })
            
            # Inserción simple
            records = crud.from_df(df)
            
            # Upsert con validaciones relajadas
            records = crud.from_df(
                df, 
                mode='upsert',
                ignore_extra_columns=True
            )
            ```
        """
        
        if df.empty:
            return []

        
        # Realizar validaciones del esquema
        self._df_validator.validate_dataframe_schema(df, ignore_extra_columns, fill_missing_nullable)
        
        # Validar tipos de datos si se solicita
        if validate_types:
            self._df_validator.validate_dataframe_types(df)
        
        # Preparar DataFrame para inserción
        cleaned_df = self._df_validator.prepare_dataframe_for_insertion(df, ignore_extra_columns, fill_missing_nullable)
        
        # Convertir DataFrame a lista de diccionarios
        records_data = cleaned_df.to_dict('records')
        
        # Limpiar valores NaN/None problemáticos
        records_data = self._df_validator.clean_records_data(records_data)
        
        # Ejecutar inserción según el modo
        return self.create_many([AgendaCreate.from_dict(record) for record in records_data])

    @error_handler
    def create(
        self, 
        agenda: AgendaCreate,
        session: Optional[Session] = None
    ) -> AgendaRead:
        """
        Crea un nuevo registro.
        
        Args:
            agenda: Datos del agenda a crear
            session: Sesión existente (opcional)
            
        Returns:
            Instancia del modelo creado
        """
        logger.info(f"[public] 🆕 Creando nuevo Agenda")
        instance = agenda.to_instance()

        if session is not None:
            session.add(instance)
            session.flush()  # Asegura que se genere el ID si es autoincrement
            included = load_relationships_from_dto(session, instance, agenda)
            data = AgendaRead.from_created_instance(instance, included)
        else:
            with self.session_manager.get_session() as session:
                session.add(instance)
                session.flush()
                included = load_relationships_from_dto(session, instance, agenda)
                data = AgendaRead.from_created_instance(instance, included)

        logger.info(f"[public] ✅ Agenda creado exitosamente con id={getattr(data, 'id', 'N/A')}")
        return data
    
    @error_handler
    def create_many(self, records: List[AgendaCreate], session: Optional[Session] = None) -> int:
        """
        Crea múltiples registros en la tabla agenda.
        
        Args:
            records: Lista de AgendaCreate con los datos de los registros
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros creados

        """
        logger.info(f"[public] 🔢 Creando {len(records)} registros Agenda")

        instances = []
        for record in records:
            instances.append(record.to_instance())
        
        if session is not None:
            session.add_all(instances)
            session.flush()  # Asegura que se generen los IDs si son autoincrement
        else:
            with self.session_manager.get_session() as session:
                session.add_all(instances)
                session.flush()  # Asegura que se generen los IDs si son autoincrement

        logger.info(f"[public] ✅ {len(instances)} registros Agenda creados exitosamente")

        return len(instances)
    
    @error_handler
    def update(
        self, 
        id: int,
        updated_values: AgendaUpdateValues,
        session: Optional[Session] = None
    ) -> int:
        """
        Actualiza registros que coincidan con los filtros.
        
        Args:
            id: Identificador del registro
            updated_values: Datos a actualizar
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros actualizados
        """

        update_data = updated_values.to_dict()

        if not update_data:  # Solo actualizar si hay datos
            return 0

        logger.info(f"[public] 🔄 Actualizando Agenda:")
        logger.info(f"[public]     id={id}")
        logger.info(f"[public]     valores={updated_values.to_dict()}")

        query = select(Agenda)

        query = query.where(Agenda.id == id)
        
        if session is not None:
            result = session.execute(query)
            record = result.scalar_one_or_none()
            if record is None:
                return 0
            for key, value in update_data.items():
                setattr(record, key, value)

            session.flush()  # Aplicar cambios a la base de datos  
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)
                record = result.scalar_one_or_none()
                if record is None:
                    return 0
                for key, value in update_data.items():
                    setattr(record, key, value)

                session.flush()  # Aplicar cambios a la base de datos
        
        logger.info(f"[public] ✅ 1 registros Agenda actualizados exitosamente")

        return 1
    
    @error_handler
    def update_many(
        self,
        payload: AgendaUpdate, 
        session: Optional[Session] = None
    ) -> int:
        """
        Actualiza múltiples registros basándose en campos de coincidencia.
        
        Args:
            payload: Datos de actualización y filtros
            session: Sesión existente (opcional)
            
        Returns:
            Número total de registros actualizados
        """
        logger.info(f"[public] 🔄 Actualizando múltiples Agenda con filtros: {payload.filter.to_dict()}, valores: {payload.values.to_dict()}")

        filters = payload.filter.to_dict()
        values = payload.values.to_dict()
        
        if not filters and not values:  # Solo actualizar si hay filtros y valores
            return 0

        query = update(Agenda)

        for key, value in filters.items():
            query = query.where(getattr(Agenda, key) == value)
        
        query = query.values(**values)
                
        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)
        
        logger.info(f"[public] ✅ {result.rowcount} registros Agenda actualizados masivamente exitosamente")

        return result.rowcount
    
    @error_handler
    def delete(
        self, 
        id: int,
        session: Optional[Session] = None
    ) -> int:
        """
        Elimina un registro atentiendo a su primary key.
        
        Args:
            id: Filtrar por id para eliminar
            session: Sesión existente (opcional)
            
        Returns:
            Número de registros eliminados
        """
        logger.info(f"[public] 🗑️ Eliminando Agenda:")
        logger.info(f"[public]    id={id}")

        query = delete(Agenda)
        
        query = query.where(Agenda.id == id)

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        logger.info(f"[public] ✅ {result.rowcount} registros Agenda eliminados exitosamente")

        return result.rowcount
    
    @error_handler
    def delete_many(self, filters_list: List[Dict[str, Any]] = [], session: Optional[Session] = None) -> int:
        """
        Elimina múltiples registros basándose en una lista de filtros.
        
        Args:
            filters_list: Lista de diccionarios con filtros para cada eliminación
            
        Returns:
            Número total de registros eliminados
        """
        logger.info(f"[public] 🗑️  Eliminando múltiples Agenda con {len(filters_list)} filtros")

        def execute_query(session: Session) -> int:
            query = delete(Agenda)
            for filters in filters_list:
                for key, value in filters.items():
                    if hasattr(Agenda, key):
                        query = query.where(getattr(Agenda, key) == value)
                
            result = session.execute(query)
            return result.rowcount
        
        if session is not None:
            total_deleted = execute_query(session)
        else:
            with self.session_manager.get_session() as session:
                total_deleted = execute_query(session)
        
        logger.info(f"[public] ✅ {total_deleted} registros Agenda eliminados masivamente exitosamente")

        return total_deleted
    
    @error_handler
    def count(
        self,
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> int:
        """
        Cuenta registros que coincidan con los filtros.
        
        Args:
        - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
        - session: Sesión existente (opcional)
            
        Returns:
            Número de registros que coinciden con los filtros
        """
        logger.info(f"[public] 🔢 Contando registros Agenda con filtros aplicados")
        
        query = select(func.count()).select_from(Agenda)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query).scalar()
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query).scalar()

        count_result = result.scalar() or 0
        logger.info(f"[public] ✅ Conteo Agenda completado: {count_result} registros")
        return count_result

    @error_handler
    def sum(
        self,
        agg_fields: List[str],
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Suma los valores de campos específicos que coincidan con los filtros.
        
        Args:
            - agg_fields: Lista de nombres de campos a sumar
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            - session: Sesión existente (opcional)
            
        Returns:
            AggregationResult con información detallada de la operación:
            - success: True si al menos un campo fue procesado
            - data: Diccionario con las sumas {"sum_<field>": value}
            - processed_fields: Lista de campos procesados exitosamente
            - warnings: Lista de advertencias (campos no numéricos)
            - errors: Lista de errores (campos inexistentes)
            - metadata: Información adicional sobre la operación
        """
        logger.info(f"[public] 🧮 Sumando campos {agg_fields} de registros Agenda con filtros aplicados")
        
        warnings = []
        errors = []
        valid_fields = []
        
        if not agg_fields:
            logger.warning(f"[public] ⚠️ No se proporcionaron campos para sumar")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=[],
                errors=["No se proporcionaron campos para sumar"],
                metadata={"total_requested_fields": 0}
            )
        
        # Validar que los campos existen en el modelo y son de tipo válido
        for field in agg_fields:
            if hasattr(Agenda, field):
                column = getattr(Agenda, field)
                column_type = str(column.type).upper()
                # Usar validadores genéricos
                if any(valid_type in column_type for valid_type in self.OPERATION_TYPE_VALIDATORS['sum']):
                    valid_fields.append(field)
                else:
                    warning_msg = f"Campo '{field}' de tipo '{column_type}' no es válido para suma"
                    warnings.append(warning_msg)
                    logger.warning(f"[public] ⚠️ {warning_msg}")
            else:
                error_msg = f"Campo '{field}' no existe en modelo Agenda"
                errors.append(error_msg)
                logger.warning(f"[public] ⚠️ {error_msg}")
        
        if not valid_fields:
            logger.warning(f"[public] ⚠️ No hay campos válidos para sumar")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0
                }
            )
        
        # Construir las expresiones de suma
        sum_expressions = []
        for field in valid_fields:
            column = getattr(Agenda, field)
            sum_expressions.append(func.sum(column).label(f"sum_{field}"))
        
        query = select(*sum_expressions)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        # Obtener el resultado y construir el diccionario
        row = result.first()
        sum_result = {}
        
        if row:
            for field in valid_fields:
                sum_key = f"sum_{field}"
                sum_value = getattr(row, sum_key)
                sum_result[sum_key] = float(sum_value) if sum_value is not None else None
        else:
            # Si no hay resultados, devolver None para todos los campos
            for field in valid_fields:
                sum_result[f"sum_{field}"] = None
        
        logger.info(f"[public] ✅ Suma Agenda completada: {sum_result}")
        
        return AggregationResult(
            success=True,
            data=sum_result,
            processed_fields=valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(valid_fields),
                "operation": "sum"
            }
        )
    
    @error_handler
    def mean(
        self,
        agg_fields: List[str],
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Calcula la media de los valores de campos específicos que coincidan con los filtros.
        
        Args:
            - agg_fields: Lista de nombres de campos para calcular la media
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            - session: Sesión existente (opcional)
            
        Returns:
            AggregationResult con información detallada de la operación:
            - success: True si al menos un campo fue procesado
            - data: Diccionario con las medias {"mean_<field>": value}
            - processed_fields: Lista de campos procesados exitosamente
            - warnings: Lista de advertencias (campos no numéricos)
            - errors: Lista de errores (campos inexistentes)
            - metadata: Información adicional sobre la operación
        """
        logger.info(f"[public] 📊 Calculando media de campos {agg_fields} de registros Agenda con filtros aplicados")
        
        warnings = []
        errors = []
        valid_fields = []
        
        if not agg_fields:
            logger.warning(f"[public] ⚠️ No se proporcionaron campos para calcular la media")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=[],
                errors=["No se proporcionaron campos para calcular la media"],
                metadata={"total_requested_fields": 0}
            )
        
        # Validar que los campos existen en el modelo y son de tipo válido
        for field in agg_fields:
            if hasattr(Agenda, field):
                column = getattr(Agenda, field)
                column_type = str(column.type).upper()
                # Usar validadores genéricos
                if any(valid_type in column_type for valid_type in self.OPERATION_TYPE_VALIDATORS['mean']):
                    valid_fields.append(field)
                else:
                    warning_msg = f"Campo '{field}' de tipo '{column_type}' no es válido para media"
                    warnings.append(warning_msg)
                    logger.warning(f"[public] ⚠️ {warning_msg}")
            else:
                error_msg = f"Campo '{field}' no existe en modelo Agenda"
                errors.append(error_msg)
                logger.warning(f"[public] ⚠️ {error_msg}")
        
        if not valid_fields:
            logger.warning(f"[public] ⚠️ No hay campos válidos para calcular la media")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0
                }
            )
        
        # Construir las expresiones de media
        mean_expressions = []
        for field in valid_fields:
            column = getattr(Agenda, field)
            mean_expressions.append(func.avg(column).label(f"mean_{field}"))
        
        query = select(*mean_expressions)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        # Obtener el resultado y construir el diccionario
        row = result.first()
        mean_result = {}
        
        if row:
            for field in valid_fields:
                mean_key = f"mean_{field}"
                mean_value = getattr(row, mean_key)
                mean_result[mean_key] = float(mean_value) if mean_value is not None else None
        else:
            # Si no hay resultados, devolver None para todos los campos
            for field in valid_fields:
                mean_result[f"mean_{field}"] = None
        
        logger.info(f"[public] ✅ Media Agenda completada: {mean_result}")
        
        return AggregationResult(
            success=True,
            data=mean_result,
            processed_fields=valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(valid_fields),
                "operation": "mean"
            }
        )
    
    @error_handler
    def max(
        self,
        agg_fields: List[str],
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Encuentra el valor máximo de campos específicos que coincidan con los filtros.
        
        Args:
            - agg_fields: Lista de nombres de campos para encontrar el máximo
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            - session: Sesión existente (opcional)
            
        Returns:
            AggregationResult con información detallada de la operación:
            - success: True si al menos un campo fue procesado
            - data: Diccionario con los máximos {"max_<field>": value}
            - processed_fields: Lista de campos procesados exitosamente
            - warnings: Lista de advertencias (campos no válidos)
            - errors: Lista de errores (campos inexistentes)
            - metadata: Información adicional sobre la operación
        """
        logger.info(f"[public] 🔺 Calculando máximo de campos {agg_fields} de registros Agenda con filtros aplicados")
        
        warnings = []
        errors = []
        valid_fields = []
        field_types = {}  # Trackear el tipo de cada campo para parsear el resultado
        
        if not agg_fields:
            logger.warning(f"[public] ⚠️ No se proporcionaron campos para calcular el máximo")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=[],
                errors=["No se proporcionaron campos para calcular el máximo"],
                metadata={"total_requested_fields": 0}
            )
        
        # Validar que los campos existen en el modelo y son de tipo válido
        for field in agg_fields:
            if hasattr(Agenda, field):
                column = getattr(Agenda, field)
                column_type = str(column.type).upper()
                # Usar validadores genéricos
                if any(valid_type in column_type for valid_type in self.OPERATION_TYPE_VALIDATORS['max']):
                    # Determinar el tipo del campo
                    if any(num_type in column_type for num_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT']):
                        field_types[field] = 'numeric'
                    elif any(date_type in column_type for date_type in ['DATETIME', 'TIMESTAMP', 'DATE', 'TIME']):
                        field_types[field] = 'datetime'
                    valid_fields.append(field)
                else:
                    warning_msg = f"Campo '{field}' de tipo '{column_type}' no es válido para máximo"
                    warnings.append(warning_msg)
                    logger.warning(f"[public] ⚠️ {warning_msg}")
            else:
                error_msg = f"Campo '{field}' no existe en modelo Agenda"
                errors.append(error_msg)
                logger.warning(f"[public] ⚠️ {error_msg}")
        
        if not valid_fields:
            logger.warning(f"[public] ⚠️ No hay campos válidos para calcular el máximo")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0
                }
            )
        
        # Construir las expresiones de máximo
        max_expressions = []
        for field in valid_fields:
            column = getattr(Agenda, field)
            max_expressions.append(func.max(column).label(f"max_{field}"))
        
        query = select(*max_expressions)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        # Obtener el resultado y construir el diccionario
        row = result.first()
        max_result = {}
        
        if row:
            for field in valid_fields:
                max_key = f"max_{field}"
                max_value = getattr(row, max_key)
                if max_value is not None:
                    # Parsear según el tipo de campo
                    if field_types[field] == 'numeric':
                        max_result[max_key] = float(max_value)
                    elif field_types[field] == 'datetime':
                        max_result[max_key] = max_value.isoformat() if hasattr(max_value, 'isoformat') else str(max_value)
                else:
                    max_result[max_key] = None
        else:
            # Si no hay resultados, devolver None para todos los campos
            for field in valid_fields:
                max_result[f"max_{field}"] = None
        
        logger.info(f"[public] ✅ Máximo Agenda completado: {max_result}")
        
        return AggregationResult(
            success=True,
            data=max_result,
            processed_fields=valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(valid_fields),
                "field_types": field_types,
                "operation": "max"
            }
        )
    
    @error_handler
    def min(
        self,
        agg_fields: List[str],
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Encuentra el valor mínimo de campos específicos que coincidan con los filtros.
        
        Args:
            - agg_fields: Lista de nombres de campos para encontrar el mínimo
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            - session: Sesión existente (opcional)
            
        Returns:
            AggregationResult con información detallada de la operación:
            - success: True si al menos un campo fue procesado
            - data: Diccionario con los mínimos {"min_<field>": value}
            - processed_fields: Lista de campos procesados exitosamente
            - warnings: Lista de advertencias (campos no válidos)
            - errors: Lista de errores (campos inexistentes)
            - metadata: Información adicional sobre la operación
        """
        logger.info(f"[public] 🔻 Calculando mínimo de campos {agg_fields} de registros Agenda con filtros aplicados")
        
        warnings = []
        errors = []
        valid_fields = []
        field_types = {}  # Trackear el tipo de cada campo para parsear el resultado
        
        if not agg_fields:
            logger.warning(f"[public] ⚠️ No se proporcionaron campos para calcular el mínimo")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=[],
                errors=["No se proporcionaron campos para calcular el mínimo"],
                metadata={"total_requested_fields": 0}
            )
        
        # Validar que los campos existen en el modelo y son de tipo válido
        for field in agg_fields:
            if hasattr(Agenda, field):
                column = getattr(Agenda, field)
                column_type = str(column.type).upper()
                # Usar validadores genéricos
                if any(valid_type in column_type for valid_type in self.OPERATION_TYPE_VALIDATORS['min']):
                    # Determinar el tipo del campo
                    if any(num_type in column_type for num_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT']):
                        field_types[field] = 'numeric'
                    elif any(date_type in column_type for date_type in ['DATETIME', 'TIMESTAMP', 'DATE', 'TIME']):
                        field_types[field] = 'datetime'
                    valid_fields.append(field)
                else:
                    warning_msg = f"Campo '{field}' de tipo '{column_type}' no es válido para mínimo"
                    warnings.append(warning_msg)
                    logger.warning(f"[public] ⚠️ {warning_msg}")
                    logger.warning(f"[public] ⚠️ {warning_msg}")
            else:
                error_msg = f"Campo '{field}' no existe en modelo Agenda"
                errors.append(error_msg)
                logger.warning(f"[public] ⚠️ {error_msg}")
        
        if not valid_fields:
            logger.warning(f"[public] ⚠️ No hay campos válidos para calcular el mínimo")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={
                    "total_requested_fields": len(agg_fields),
                    "valid_fields_count": 0
                }
            )
        
        # Construir las expresiones de mínimo
        min_expressions = []
        for field in valid_fields:
            column = getattr(Agenda, field)
            min_expressions.append(func.min(column).label(f"min_{field}"))
        
        query = select(*min_expressions)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        # Obtener el resultado y construir el diccionario
        row = result.first()
        min_result = {}
        
        if row:
            for field in valid_fields:
                min_key = f"min_{field}"
                min_value = getattr(row, min_key)
                if min_value is not None:
                    # Parsear según el tipo de campo
                    if field_types[field] == 'numeric':
                        min_result[min_key] = float(min_value)
                    elif field_types[field] == 'datetime':
                        min_result[min_key] = min_value.isoformat() if hasattr(min_value, 'isoformat') else str(min_value)
                else:
                    min_result[min_key] = None
        else:
            # Si no hay resultados, devolver None para todos los campos
            for field in valid_fields:
                min_result[f"min_{field}"] = None
        
        logger.info(f"[public] ✅ Mínimo Agenda completado: {min_result}")
        
        return AggregationResult(
            success=True,
            data=min_result,
            processed_fields=valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_requested_fields": len(agg_fields),
                "valid_fields_count": len(valid_fields),
                "field_types": field_types,
                "operation": "min"
            }
        )
    
    @error_handler
    def agg(
        self,
        aggregations: Dict[str, Union[List[str], List[Dict[str, Any]]]],
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> AggregationResult:
        """
        Realiza múltiples operaciones de agregación en una sola consulta.
        
        Args:
            - aggregations: Diccionario con operaciones y campos/expresiones a agregar.
                           Formato:
                           {
                               "sum": ["field1", "field2/field3", {"expr": "revenue-cost", "as": "profit"}],
                               "mean": ["field4", "(field5+field6)/2"],
                               "max": ["created_at"],
                               "min": ["updated_at"],
                               "count": ["id", "status"]
                           }
                           
                           Cada campo puede ser:
                           - str: Nombre de campo simple o expresión aritmética
                           - dict: Objeto con 'expr' (expresión) y opcionalmente 'as' (alias)
                           
                           Operaciones soportadas:
                           - sum: Suma de valores numéricos
                           - mean: Promedio de valores numéricos
                           - max: Valor máximo (numérico o fechas)
                           - min: Valor mínimo (numérico o fechas)
                           - count: Conteo de registros (cualquier tipo de campo)
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            - session: Sesión existente (opcional)
            
        Returns:
            AggregationResult con información detallada de todas las operaciones:
            - success: True si al menos un campo fue procesado
            - data: Diccionario con todos los resultados {"operation_field": value} o {"operation_alias": value}
            - processed_fields: Lista de todos los campos/expresiones procesados exitosamente
            - warnings: Lista de advertencias (campos no válidos para su operación)
            - errors: Lista de errores (operaciones no soportadas, campos inexistentes, errores en expresiones)
            - metadata: Información detallada por operación
            
        Examples:
            ```python
            # Expresiones simples en strings
            result = dao.agg(
                aggregations={
                    "sum": ["price/quantity", "total*tax"],
                    "mean": ["(revenue-cost)/items"]
                },
                category="electronics"
            )
            print(result.data["sum_price_quantity"])
            
            # Con aliases personalizados
            result = dao.agg(
                aggregations={
                    "sum": [
                        {"expr": "revenue-cost", "as": "profit"},
                        {"expr": "price*quantity", "as": "total_value"}
                    ]
                },
                category="electronics"
            )
            print(result.data["sum_profit"])
            
            # Mixto: campos simples y expresiones
            result = dao.agg(
                aggregations={
                    "sum": ["price", "total"],
                    "mean": ["quantity"],
                    "max": ["created_at"],
                    "min": ["updated_at"],
                    "count": ["id"]
                }
            )
            print(result.data["sum_price"])
            print(result.data["mean_quantity"])
            print(result.data["count_id"])
            print(result.metadata["operations_summary"])
            ```
        """
        logger.info(f"[public] 🎯 Realizando agregaciones múltiples en Agenda: {list(aggregations.keys())}")
        
        warnings = []
        errors = []
        all_valid_fields = []
        operations_metadata = {}
        
        if not aggregations:
            logger.warning(f"[public] ⚠️ No se proporcionaron operaciones de agregación")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=[],
                errors=["No se proporcionaron operaciones de agregación"],
                metadata={"total_operations": 0}
            )
        
        # Validar y construir expresiones de agregación
        agg_expressions = []
        
        for operation, fields in aggregations.items():
            # Validar que la operación es soportada
            if operation not in self.OPERATION_TYPE_VALIDATORS:
                error_msg = f"Operación '{operation}' no soportada. Operaciones válidas: {list(self.OPERATION_TYPE_VALIDATORS.keys())}"
                errors.append(error_msg)
                logger.warning(f"[public] ⚠️ {error_msg}")
                continue
            
            if not fields:
                warning_msg = f"No se proporcionaron campos para la operación '{operation}'"
                warnings.append(warning_msg)
                logger.warning(f"[public] ⚠️ {warning_msg}")
                continue
            
            # Validar campos para esta operación
            valid_fields_for_operation = []
            field_types_for_operation = {}
            field_label_mapping = {}  # Mapeo de field_key -> label_name
            
            for field in fields:
                try:
                    # Extraer expresión y alias
                    if isinstance(field, dict):
                        expression = field.get('expr', field.get('expression', ''))
                        alias = field.get('as', field.get('alias'))
                        if not expression:
                            error_msg = f"Diccionario de campo sin 'expr' o 'expression': {field}"
                            errors.append(error_msg)
                            logger.warning(f"[public] ⚠️ {error_msg}")
                            continue
                    else:
                        expression = str(field)
                        alias = None
                    
                    # Detectar si es una expresión aritmética
                    is_expression = any(op in expression for op in ['+', '-', '*', '/', '%', '(', ')'])
                    
                    if is_expression:
                        # Parsear expresión usando ExpressionParser
                        try:
                            column_expr = ExpressionParser.parse(expression, Agenda)
                            
                            # Generar label y field_key
                            if alias:
                                field_key = alias
                                label_name = f"{operation}_{alias}"
                            else:
                                clean_expr = ExpressionParser.get_field_name(expression)
                                field_key = clean_expr
                                label_name = f"{operation}_{clean_expr}"
                            
                            # Agregar a campos válidos
                            valid_fields_for_operation.append(field_key)
                            all_valid_fields.append(field_key)
                            field_label_mapping[field_key] = label_name
                            
                            # Construir expresión de agregación
                            sql_func = self.OPERATION_FUNCTIONS[operation]
                            agg_expressions.append(sql_func(column_expr).label(label_name))
                            
                            # Las expresiones siempre son numéricas
                            if operation in ['max', 'min']:
                                field_types_for_operation[field_key] = 'numeric'
                            
                        except ValueError as e:
                            error_msg = f"Error al parsear expresión '{expression}': {str(e)}"
                            errors.append(error_msg)
                            logger.warning(f"[public] ⚠️ {error_msg}")
                    
                    else:
                        # Campo simple (lógica actual)
                        if hasattr(Agenda, expression):
                            column = getattr(Agenda, expression)
                            column_type = str(column.type).upper()
                            
                            # Validar tipo usando validadores genéricos
                            if any(valid_type in column_type for valid_type in self.OPERATION_TYPE_VALIDATORS[operation]):
                                # Generar label y field_key
                                if alias:
                                    field_key = alias
                                    label_name = f"{operation}_{alias}"
                                else:
                                    field_key = expression
                                    label_name = f"{operation}_{expression}"
                                
                                valid_fields_for_operation.append(field_key)
                                all_valid_fields.append(field_key)
                                field_label_mapping[field_key] = label_name
                                
                                # Determinar tipo de campo para max/min
                                if operation in ['max', 'min']:
                                    if any(num_type in column_type for num_type in ['INTEGER', 'FLOAT', 'NUMERIC', 'DECIMAL', 'DOUBLE', 'REAL', 'BIGINT', 'SMALLINT', 'TINYINT']):
                                        field_types_for_operation[field_key] = 'numeric'
                                    elif any(date_type in column_type for date_type in ['DATETIME', 'TIMESTAMP', 'DATE', 'TIME']):
                                        field_types_for_operation[field_key] = 'datetime'
                                
                                # Construir expresión SQL
                                sql_func = self.OPERATION_FUNCTIONS[operation]
                                agg_expressions.append(sql_func(column).label(label_name))
                            else:
                                warning_msg = f"Campo '{expression}' de tipo '{column_type}' no es válido para operación '{operation}'"
                                warnings.append(warning_msg)
                                logger.warning(f"[public] ⚠️ {warning_msg}")
                        else:
                            error_msg = f"Campo '{expression}' no existe en modelo Agenda"
                            errors.append(error_msg)
                            logger.warning(f"[public] ⚠️ {error_msg}")
                
                except Exception as e:
                    error_msg = f"Error inesperado procesando campo '{field}': {str(e)}"
                    errors.append(error_msg)
                    logger.warning(f"[public] ⚠️ {error_msg}")
            
            # Guardar metadata de esta operación
            if valid_fields_for_operation:
                operations_metadata[operation] = {
                    "requested_fields": [f if isinstance(f, str) else f.get('expr', str(f)) for f in fields],
                    "valid_fields": valid_fields_for_operation,
                    "field_label_mapping": field_label_mapping,
                    "valid_count": len(valid_fields_for_operation),
                    "invalid_count": len(fields) - len(valid_fields_for_operation)
                }
                
                if operation in ['max', 'min'] and field_types_for_operation:
                    operations_metadata[operation]["field_types"] = field_types_for_operation
        
        # Si no hay expresiones válidas, retornar error
        if not agg_expressions:
            logger.warning(f"[public] ⚠️ No hay operaciones válidas para ejecutar")
            return AggregationResult(
                success=False,
                data={},
                processed_fields=[],
                warnings=warnings,
                errors=errors,
                metadata={
                    "total_operations": len(aggregations),
                    "valid_operations": 0,
                    "operations_summary": operations_metadata
                }
            )
        
        # Construir query con todas las agregaciones
        query = select(*agg_expressions)
        
        # Filters
        filters = {}
        
        if nombre is not None:
            filters['nombre'] = nombre
            if isinstance(nombre, str) and '%' in nombre:
                query = query.where(Agenda.nombre.ilike(nombre))
            else:
                query = query.where(Agenda.nombre == nombre)
        if in_nombre is not None and len(in_nombre) > 0:
            filters['in_nombre'] = in_nombre
            query = query.where(Agenda.nombre.in_(in_nombre))
        if correo is not None:
            filters['correo'] = correo
            if isinstance(correo, str) and '%' in correo:
                query = query.where(Agenda.correo.ilike(correo))
            else:
                query = query.where(Agenda.correo == correo)
        if in_correo is not None and len(in_correo) > 0:
            filters['in_correo'] = in_correo
            query = query.where(Agenda.correo.in_(in_correo))
        if telefono is not None:
            filters['telefono'] = telefono
            if isinstance(telefono, str) and '%' in telefono:
                query = query.where(Agenda.telefono.ilike(telefono))
            else:
                query = query.where(Agenda.telefono == telefono)
        if in_telefono is not None and len(in_telefono) > 0:
            filters['in_telefono'] = in_telefono
            query = query.where(Agenda.telefono.in_(in_telefono))
        
        # Log de parámetros aplicados
        if filters:
            logger.info(f"[public]     filters={filters}")

        if session is not None:
            result = session.execute(query)
        else:
            with self.session_manager.get_session() as session:
                result = session.execute(query)

        # Obtener el resultado y construir el diccionario
        row = result.first()
        agg_result = {}
        
        if row:
            for operation, metadata in operations_metadata.items():
                field_label_mapping = metadata.get("field_label_mapping", {})
                for field in metadata["valid_fields"]:
                    # Usar el label real que se generó, no el nombre del campo
                    label_name = field_label_mapping.get(field, f"{operation}_{field}")
                    result_value = getattr(row, label_name)
                    
                    # La clave en el resultado sigue siendo operation_field para consistencia
                    result_key = f"{operation}_{field}"
                    
                    if result_value is not None:
                        # Parsear según el tipo de campo y operación
                        if operation == 'count':
                            agg_result[result_key] = int(result_value)
                        elif operation in ['max', 'min'] and 'field_types' in metadata:
                            if metadata['field_types'].get(field) == 'datetime':
                                agg_result[result_key] = result_value.isoformat() if hasattr(result_value, 'isoformat') else str(result_value)
                            else:
                                agg_result[result_key] = float(result_value)
                        elif operation in ['sum', 'mean']:
                            agg_result[result_key] = float(result_value)
                        else:
                            agg_result[result_key] = result_value
                    else:
                        agg_result[result_key] = None if operation != 'count' else 0
        else:
            # Si no hay resultados, devolver None para todos los campos (0 para count)
            for operation, metadata in operations_metadata.items():
                for field in metadata["valid_fields"]:
                    result_key = f"{operation}_{field}"
                    agg_result[result_key] = 0 if operation == 'count' else None
        
        logger.info(f"[public] ✅ Agregaciones múltiples Agenda completadas: {len(agg_expressions)} expresiones procesadas")
        
        return AggregationResult(
            success=True,
            data=agg_result,
            processed_fields=all_valid_fields,
            warnings=warnings,
            errors=errors,
            metadata={
                "total_operations": len(aggregations),
                "valid_operations": len(operations_metadata),
                "total_expressions": len(agg_expressions),
                "operations_summary": operations_metadata
            }
        )
    
    @error_handler
    def exists(
        self,
        nombre: Optional[str] = None,
        in_nombre: Optional[List[str]] = None,
        correo: Optional[str] = None,
        in_correo: Optional[List[str]] = None,
        telefono: Optional[str] = None,
        in_telefono: Optional[List[str]] = None,
        session: Optional[Session] = None
    ) -> bool:
        """
        Verifica si existe al menos un registro que coincida con los filtros.
        
        Args:
            - nombre: Filtrar por nombre
            - in_nombre: Filtrar por múltiples valores de nombre (OR lógico)
            - correo: Filtrar por correo
            - in_correo: Filtrar por múltiples valores de correo (OR lógico)
            - telefono: Filtrar por telefono
            - in_telefono: Filtrar por múltiples valores de telefono (OR lógico)
            session: Sesión existente (opcional)
            
        Returns:
            True si existe al menos un registro, False en caso contrario
        """
        logger.info(f"[public] ❓ Verificando existencia de registros Agenda")
        records = self.count(
            nombre=nombre,
            in_nombre=in_nombre,
            correo=correo,
            in_correo=in_correo,
            telefono=telefono,
            in_telefono=in_telefono,
            session=session
        )
        exists_result = records > 0
        logger.info(f"[public] ✅ Verificación Agenda completada: {'existe' if exists_result else 'no existe'}")
        return exists_result
    
