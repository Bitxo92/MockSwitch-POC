# Este archivo ha sido generado automáticamente por tai-sql
# No modifiques este archivo directamente
from __future__ import annotations
from typing import (
    List,
    Optional,
    Dict,
    Union,
    Any
)
from api.database.public.models import *
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
            AgendaCreate: Instancia del DTO
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
    def from_instance(cls, instance: Agenda) -> AgendaCreate:
        """
        Crea un DTO desde una instancia del modelo SQLAlchemy
        
        Args:
            instance: Instancia del modelo Agenda
            
        Returns:
            AgendaCreate: Instancia del DTO
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


