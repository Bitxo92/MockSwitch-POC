# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente
from __future__ import annotations
from typing import (
    List,
    Optional,
    Dict,
    Literal,
    Any,
    Union,
    TYPE_CHECKING
)
from database.public.models import *
from pydantic import (
    Field,
    ConfigDict
)

from tai_alphi import Alphi

from .utils import (
    should_include_relation,
    get_nested_includes,
    PrettyModel
)

if TYPE_CHECKING:
    from pandas import DataFrame, Series  # type: ignore[import-untyped]
# Logger
logger = Alphi.get_logger_by_name("tai-sql")

# General Enum class
class EnumModel:

    def __init__(self, name: str, values: List[str]):
        self.name = name
        self.values = values
    
    def find_many(self) -> List[str]:
        """
        Devuelve una lista de los valores del Enum.
        
        Returns:
            List[str]: Lista de valores del Enum
        """
        logger.info(f"Obteniendo valores del Enum '{self.name}' - {len(self.values)} valores disponibles")
        return self.values


class AggregationResult(PrettyModel):
    """
    Resultado estructurado para operaciones de agregación.
    
    Proporciona información detallada sobre el resultado de operaciones
    como sum, mean, max, min, incluyendo metadatos de validación y errores.
    
    Attributes:
        success: Indica si la operación fue exitosa (al menos un campo válido procesado)
        data: Diccionario con los resultados de la agregación
        processed_fields: Lista de campos que se procesaron exitosamente
        warnings: Lista de advertencias sobre campos que se ignoraron
        errors: Lista de errores encontrados durante la validación
        metadata: Información adicional sobre la operación
    
    Examples:
        ```python
        # Operación exitosa
        result = AggregationResult(
            success=True,
            data={"sum_price": 150.50, "sum_quantity": 25},
            processed_fields=["price", "quantity"],
            warnings=[],
            errors=[],
            metadata={"total_requested_fields": 2, "execution_time_ms": 45}
        )
        
        # Operación con advertencias
        result = AggregationResult(
            success=True,
            data={"sum_price": 150.50},
            processed_fields=["price"],
            warnings=["Campo 'description' de tipo 'TEXT' no es numérico"],
            errors=[],
            metadata={"total_requested_fields": 2, "execution_time_ms": 32}
        )
        
        # Operación con errores
        result = AggregationResult(
            success=False,
            data={},
            processed_fields=[],
            warnings=[],
            errors=["Campo 'nonexistent_field' no existe en el modelo"],
            metadata={"total_requested_fields": 1, "execution_time_ms": 12}
        )
        ```
    """
    
    success: bool = Field(
        description="Indica si la operación fue exitosa (al menos un campo válido procesado)"
    )
    
    data: Dict[str, Optional[Union[int, float, str]]] = Field(
        description="Diccionario con los resultados de la agregación. Las claves siguen el patrón '<operacion>_<campo>'"
    )
    
    processed_fields: List[str] = Field(
        description="Lista de campos que se procesaron exitosamente en la agregación"
    )
    
    warnings: List[str] = Field(
        default_factory=list,
        description="Lista de advertencias sobre campos que se ignoraron (ej: tipos no numéricos)"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="Lista de errores encontrados durante la validación (ej: campos inexistentes)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Información adicional sobre la operación (ej: tiempo de ejecución, estadísticas)"
    )
    
    def has_warnings(self) -> bool:
        """Retorna True si hay advertencias."""
        return len(self.warnings) > 0
    
    def has_errors(self) -> bool:
        """Retorna True si hay errores."""
        return len(self.errors) > 0
    
    def get_summary(self) -> str:
        """
        Retorna un resumen legible de la operación.
        
        Returns:
            str: Resumen de la operación de agregación
        """
        if not self.success:
            return f"Operación fallida: {len(self.errors)} errores encontrados"
        
        summary_parts = [f"Operación exitosa: {len(self.processed_fields)} campos procesados"]
        
        if self.has_warnings():
            summary_parts.append(f"{len(self.warnings)} advertencias")
            
        if self.has_errors():
            summary_parts.append(f"{len(self.errors)} errores no críticos")
        
        return ", ".join(summary_parts)
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "arbitrary_types_allowed": True,
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "data": {"sum_price": 150.50, "sum_quantity": 25},
                    "processed_fields": ["price", "quantity"],
                    "warnings": [],
                    "errors": [],
                    "metadata": {"total_requested_fields": 2, "execution_time_ms": 45}
                },
                {
                    "success": True,
                    "data": {"mean_score": 8.5},
                    "processed_fields": ["score"],
                    "warnings": ["Campo 'name' de tipo 'VARCHAR' no es numérico"],
                    "errors": [],
                    "metadata": {"total_requested_fields": 2, "execution_time_ms": 32}
                },
                {
                    "success": False,
                    "data": {},
                    "processed_fields": [],
                    "warnings": [],
                    "errors": ["Campo 'invalid_field' no existe en el modelo"],
                    "metadata": {"total_requested_fields": 1, "execution_time_ms": 12}
                }
            ]
        }
    }


class AgendaRead(PrettyModel):
    """
    Data Transfer Object de lectura para Agenda.
    
    Tabla que almacena información de los usuarios del sistema
    
    Este modelo se utiliza como respuesta en endpoints de la API que devuelven
    información de usuario existentes en la base de datos.
    
    Campos de la tabla:
        - id (int): Campo id de la tabla usuario
        - nombre (str): Nombre del usuario
        - correo (str): Correo electrónico del usuario
        - telefono (str): Número de teléfono del usuario
    
    
    Rendimiento:
        - Sin includes: Consulta rápida, solo tabla Agenda
        - Máxima profundidad de anidación: 5 niveles
    """

    id: int = Field(
        description="Campo id de la tabla usuario",
    )

    nombre: str = Field(
        description="Nombre del usuario",
    )

    correo: str = Field(
        description="Correo electrónico del usuario",
    )

    telefono: str = Field(
        description="Número de teléfono del usuario",
    )


    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=True,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    @classmethod
    def from_instance(
        cls,
        instance: Agenda,
        includes: Optional[List[str]] = None,
        max_depth: int = 5
    ) -> AgendaRead:
        """
        Crea un DTO desde una instancia del modelo SQLAlchemy con carga optimizada de relaciones.
        
        Args:
            instance: Instancia del modelo Agenda
            includes: Lista de relaciones a incluir (formato: 'relation' o 'relation.nested_relation')
            max_depth: Profundidad máxima de anidación para evitar recursión infinita
            
        Returns:
            AgendaRead: Instancia del DTO
        """

        # Construir DTO base
        dto_data = {
            'id': instance.id,
            'nombre': instance.nombre,
            'correo': instance.correo,
            'telefono': instance.telefono,
        }

        return cls(**dto_data)

    @classmethod
    def from_created_instance(cls, instance: Agenda, included: set[str], excluded: str=None) -> AgendaRead:
        """
        Crea un DTO desde una instancia del modelo SQLAlchemy
        
        Args:
            instance: Instancia del modelo Agenda
            included: Set de nombres de relaciones que fueron cargadas con session.refresh()
            excluded: Nombre de relación a excluir para evitar recursión infinita
            
        Returns:
            AgendaRead: Instancia del DTO
        """

        # Construir DTO base
        dto_data = {
            'id': instance.id,
            'nombre': instance.nombre,
            'correo': instance.correo,
            'telefono': instance.telefono,
        }

        return cls(**dto_data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgendaRead:
        """
        Crea un DTO desde un diccionario
        
        Args:
            data: Diccionario con los datos del DTO
            
        Returns:
            AgendaRead: Instancia del DTO
        """
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class AgendaCreate(PrettyModel):
    """Data Transfer Object de escritura para Agenda. Define objetos para ser creados en la base de datos."""
    nombre: str
    correo: str
    telefono: str


    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=True,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    def to_instance(self) -> Agenda:
        """
        Crea una instancia del modelo SQLAlchemy desde el DTO
        
        Returns:
            Agenda: Instancia del modelo SQLAlchemy
        """

        model = Agenda(
            nombre=self.nombre,
            correo=self.correo,
            telefono=self.telefono,
        )
        
        # Evaluación lazy de relaciones costosas

        return model
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AgendaCreate:
        """
        Crea un DTO desde un diccionario
        
        Args:
            data: Diccionario con los datos del DTO
            
        Returns:
            AgendaCreate: Instancia del DTO
        """
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class AgendaFilter(PrettyModel):
    """Data Transfer Object de actualización para Agenda.
    Define los filtros que sirven para buscar registros en la DB."""
    nombre: str = None
    correo: str = None
    telefono: str = None

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=True,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class AgendaUpdateValues(PrettyModel):
    """Data Transfer Object de actualización para Agenda.
    Define los valores que se modificarán en los registros correspondientes."""
    nombre: str = None
    correo: str = None
    telefono: str = None

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=True,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )
    
    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class AgendaUpdate(PrettyModel):
    """Data Transfer Object de actualización para Agenda."""
    filter: AgendaFilter
    values: AgendaUpdateValues

    model_config = ConfigDict(
        # Performance optimizations
        arbitrary_types_allowed=False,  # Más rápido al validar tipos estrictos
        use_enum_values=True,
        validate_assignment=True,  # Valida en cada asignación
        frozen=False,  # Si True, hace el objeto inmutable
        str_strip_whitespace=False,  # No procesa strings automáticamente
        validate_default=False,  # No valida valores por defecto
        extra="forbid",  # Más rápido que "allow" o "ignore"
        # Configuraciones adicionales de v2
        populate_by_name=True,  # Permite usar alias y nombres originales
        use_attribute_docstrings=True,  # Usa docstrings como descripciones
        validate_call=True,  # Valida llamadas a métodos
    )

class AgendaDataFrameValidator:
    """ Validador de DataFrame para el modelo Agenda """

    def validate_dataframe_schema(
        self, 
        df: DataFrame, 
        ignore_extra_columns: bool, 
        fill_missing_nullable: bool
    ) -> None:
        """
        Valida que el esquema del DataFrame sea compatible con el modelo.
        
        Args:
            df: DataFrame a validar
            ignore_extra_columns: Si ignorar columnas extra
            fill_missing_nullable: Si llenar columnas nullable faltantes
            
        Raises:
            ValueError: Si el esquema no es compatible
        """
        # Definir columnas del modelo
        model_columns = {
            'id': {
                'type': 'int',
                'nullable': False,
                'primary_key': True,
                'autoincrement': True
            },
            'nombre': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False
            },
            'correo': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False
            },
            'telefono': {
                'type': 'str',
                'nullable': False,
                'primary_key': False,
                'autoincrement': False
            }
        }
        
        df_columns = set(df.columns)
        required_columns = set(model_columns.keys())
        
        # Verificar columnas extra
        extra_columns = df_columns - required_columns
        if extra_columns and not ignore_extra_columns:
            raise ValueError(
                f"DataFrame contiene columnas no definidas en el modelo: {list(extra_columns)}\n"
                f"Usa ignore_extra_columns=True para ignorarlas o elimínalas del DataFrame"
            )
        
        # Verificar columnas faltantes
        missing_columns = required_columns - df_columns
        
        # Filtrar columnas que pueden faltar
        critical_missing = []
        for col in missing_columns:
            col_info = model_columns[col]
            # Las columnas críticas son las que no son nullable, no son auto-increment y no son PK auto
            if (not col_info['nullable'] and 
                not col_info['autoincrement'] and 
                not (col_info['primary_key'] and col_info['autoincrement'])):
                critical_missing.append(col)
        
        if critical_missing:
            raise ValueError(
                f"DataFrame falta columnas requeridas (NOT NULL): {critical_missing}\n"
                f"Estas columnas son obligatorias y deben estar presentes en el DataFrame"
            )
        
        # Advertir sobre columnas nullable faltantes
        nullable_missing = [col for col in missing_columns if col not in critical_missing]
        if nullable_missing and not fill_missing_nullable:
            import warnings
            warnings.warn(
                f"DataFrame falta columnas nullable: {nullable_missing}\n"
                f"Usa fill_missing_nullable=True para llenarlas automáticamente con None"
            )
    
    def validate_dataframe_types(self, df: "DataFrame") -> None:
        """
        Valida que los tipos de datos del DataFrame sean compatibles.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            TypeError: Si los tipos no son compatibles
        """
        
        # Mapeo de tipos SQLAlchemy a tipos pandas compatibles
        type_compatibility = {
            'id': {
                'sqlalchemy_type': 'int',
                'compatible_pandas_types': [
                    'int64', 'Int64', 'int32', 'Int32', 'int16', 'Int16', 'int8', 'Int8', 'object'
                ]
            },
            'nombre': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'correo': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            },
            'telefono': {
                'sqlalchemy_type': 'str',
                'compatible_pandas_types': [
                    'object', 'string', 'category'
                ]
            }
        }
        
        type_errors = []
        
        for column in df.columns:
            if column in type_compatibility:
                df_dtype = str(df[column].dtype)
                compatible_types = type_compatibility[column]['compatible_pandas_types']
                sqlalchemy_type = type_compatibility[column]['sqlalchemy_type']
                
                if df_dtype not in compatible_types:
                    # Verificar si puede ser convertido
                    if self.can_convert_type(df[column], sqlalchemy_type):
                        continue
                    
                    type_errors.append(
                        f"Columna '{column}': tipo '{df_dtype}' no compatible con '{sqlalchemy_type}'. "
                        f"Tipos aceptados: {compatible_types}"
                    )
        
        if type_errors:
            raise TypeError(
                "Errores de tipo de datos encontrados:\n" + 
                "\n".join(f"  - {error}" for error in type_errors) +
                "\n\nConsidera convertir los tipos antes de la inserción."
            )
    
    def can_convert_type(self, series: "Series", target_sqlalchemy_type: str) -> bool:
        """
        Verifica si una serie puede ser convertida al tipo SQLAlchemy objetivo.
        
        Args:
            series: Serie de pandas a verificar
            target_sqlalchemy_type: Tipo SQLAlchemy objetivo
            
        Returns:
            bool: True si puede ser convertida
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas no está instalado. Para usar from_df(), instala pandas:\n"
                "pip install pandas\n"
                "o si usas poetry:\n"
                "poetry add pandas"
            )
        
        try:
            # Probar conversión en una muestra pequeña
            sample = series.dropna().head(10)
            if sample.empty:
                return True
            
            if 'int' in target_sqlalchemy_type:
                pd.to_numeric(sample, errors='raise')
            elif 'float' in target_sqlalchemy_type or 'Numeric' in target_sqlalchemy_type:
                pd.to_numeric(sample, errors='raise')
            elif 'bool' in target_sqlalchemy_type:
                # Verificar valores booleanos válidos
                valid_bool_values = {True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False'}
                if not all(val in valid_bool_values for val in sample.unique()):
                    return False
            elif 'datetime' in target_sqlalchemy_type or 'date' in target_sqlalchemy_type:
                pd.to_datetime(sample, errors='raise')
            
            return True
        except:
            return False
    
    def prepare_dataframe_for_insertion(
        self, 
        df: "DataFrame", 
        ignore_extra_columns: bool, 
        fill_missing_nullable: bool
    ) -> "DataFrame":
        """
        Prepara el DataFrame para inserción en la base de datos.
        
        Args:
            df: DataFrame original
            ignore_extra_columns: Si ignorar columnas extra
            fill_missing_nullable: Si llenar columnas faltantes nullable
            
        Returns:
            DataFrame preparado para inserción
        """
        try:
            import pandas as pd
            import numpy as np
        except ImportError:
            return df
        
        # Crear copia para no modificar el original
        cleaned_df = df.copy()
        
        # Definir columnas del modelo
        model_columns = {
            'id': {
                'nullable': False,
                'autoincrement': True
            },
            'nombre': {
                'nullable': False,
                'autoincrement': False
            },
            'correo': {
                'nullable': False,
                'autoincrement': False
            },
            'telefono': {
                'nullable': False,
                'autoincrement': False
            }
        }
        
        # Eliminar columnas extra si se solicita
        if ignore_extra_columns:
            extra_columns = set(cleaned_df.columns) - set(model_columns.keys())
            if extra_columns:
                cleaned_df = cleaned_df.drop(columns=list(extra_columns))
        
        # Agregar columnas nullable faltantes si se solicita
        if fill_missing_nullable:
            for col_name, col_info in model_columns.items():
                if (col_name not in cleaned_df.columns and 
                    col_info['nullable'] and 
                    not col_info['autoincrement']):
                    cleaned_df[col_name] = None
        
        # Eliminar columnas autoincrement (la BD las manejará)
        autoincrement_columns = [
            col for col, info in model_columns.items() 
            if info['autoincrement'] and col in cleaned_df.columns
        ]
        if autoincrement_columns:
            cleaned_df = cleaned_df.drop(columns=autoincrement_columns)
        
        # Reordenar columnas según el modelo (las que existan)
        model_column_order = [col for col in model_columns.keys() if col in cleaned_df.columns]
        cleaned_df = cleaned_df[model_column_order]
        
        return cleaned_df
    
    def clean_records_data(self, records_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Limpia los datos de registros para inserción en BD.
        
        Args:
            records_data: Lista de diccionarios con datos de registros
            
        Returns:
            Lista de diccionarios limpiados
        """
        try:
            import pandas as pd
        except ImportError:
            return records_data
        
        cleaned_records = []
        
        for record in records_data:
            cleaned_record = {}
            for key, value in record.items():
                # Manejar valores NaN y NaT de pandas
                if pd.isna(value):
                    cleaned_record[key] = None
                # Manejar tipos numpy
                elif hasattr(value, 'item'):  # numpy scalars
                    cleaned_record[key] = value.item()
                else:
                    cleaned_record[key] = value
            
            cleaned_records.append(cleaned_record)
        
        return cleaned_records

        
