"""
# utils.py
# Módulo de utilidades para manejo de errores en DAOs síncronos
# Contiene decoradores para manejo de errores, carga de relaciones y opciones de carga optimizadas
"""
import re
import functools
from pydantic import BaseModel
from typing import (
    Any,
    List,
    Union,
    Dict,
    Optional
)
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    class_mapper,
    selectinload,
    joinedload,
    RelationshipProperty,
    DeclarativeMeta
)
from sqlalchemy.sql.elements import ColumnElement
from tai_alphi import Alphi

from api.database.public.models import *

# Logger
logger = Alphi.get_logger_by_name("tai-sql")

class PrettyModel(BaseModel):
    def __str__(self):
        try:
            from rich.console import Console
            from rich.syntax import Syntax
            console = Console()
            json_str = self.model_dump_json(indent=2)
            syntax = Syntax(json_str, "json", theme="ansi_dark", line_numbers=False)
            with console.capture() as capture:
                console.print(syntax)
            return capture.get()
        except ImportError:
            # Fallback si rich no está disponible
            return self.model_dump_json(indent=2)
        except Exception as e:
            return str(e)

def error_handler(func):
    """
    Decorador para manejo de errores consistente en métodos DAO.
    Siempre debe usarse sin paréntesis: @error_handler
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        operation_verbs = {
            "create": "crear",
            "create_many": "crear",
            "find": "buscar",
            "find_many": "buscar",
            "update": "actualizar",
            "update_many": "actualizar",
            "delete": "eliminar",
            "delete_many": "eliminar",
            "count": "contar",
            "exists": "verificar existencia de"
        }

        operation_type = func.__name__
        class_name: str = self.__class__.__name__
        model_name = class_name.removesuffix("AsyncDAO") if class_name.endswith("AsyncDAO") else "Modelo"

        try:
            return func(self, *args, **kwargs)

        except exc.NoResultFound:
            logger.warning(f"[public] ⚠️ Registro no encontrado en {operation_type}: {model_name}")
            raise

        except exc.IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            logger.error(f"[public] ❌ Error de integridad en {operation_type}: {error_msg}")

            if "UNIQUE constraint failed" in error_msg or "duplicate key" in error_msg.lower():
                logger.error(f"[public] ❌ Ya existe un {model_name} con esos datos")
                raise 
            elif "FOREIGN KEY constraint failed" in error_msg or "foreign key" in error_msg.lower():
                if operation_type == "delete":
                    logger.error(f"[public] ❌ No se puede eliminar el {model_name} porque está siendo referenciado por otros registros")
                    raise 
                else:
                    logger.error(f"[public] ❌ Error de referencia en los datos del {model_name}")
                    raise
            else:
                logger.error(f"[public] ❌ Error de integridad al {operation_verbs.get(operation_type, 'procesar')} {model_name}")
                raise 

        except exc.SQLAlchemyError as e:
            logger.error(f"[public] ❌ SQLAlchemy error en {operation_type}: {str(e)}")
            logger.error(f"[public] ❌ Error en la base de datos al {operation_verbs.get(operation_type, 'procesar')} {model_name}")
            raise

        except Exception as e:
            error_msg = str(e)
            logger.error(f"[public] ❌ Error inesperado en {operation_type}: {error_msg}")
            logger.error(f"[public] ❌ Error inesperado al {operation_verbs.get(operation_type, 'procesar')} {model_name}")
            raise 

    return wrapper

def should_include_relation(relation_name: str, includes: List[str]) -> bool:
    """
    Determina si una relación debe ser incluida basándose en la lista de includes.
    
    Args:
        relation_name: Nombre de la relación a verificar
        includes: Lista de relaciones a incluir
        
    Returns:
        bool: True si la relación debe incluirse
    """
    return any(
        include == relation_name or include.startswith(f"{relation_name}.")
        for include in includes
    )

def get_nested_includes(relation_name: str, includes: List[str]) -> List[str]:
    """
    Extrae las relaciones anidadas para una relación específica.
    
    Args:
        relation_name: Nombre de la relación padre
        includes: Lista completa de includes
        
    Returns:
        List[str]: Lista de includes anidados para la relación
        
    Example:
        includes = ['author', 'author.posts', 'author.posts.comments']
        get_nested_includes('author', includes) -> ['posts', 'posts.comments']
    """
    nested = []
    prefix = f"{relation_name}."
    
    for include in includes:
        if include.startswith(prefix):
            # Remover el prefijo y añadir a nested
            nested_path = include[len(prefix):]
            nested.append(nested_path)
    
    return nested

def get_loading_options(model_class, includes: Optional[List[str]] = None) -> List[Any]:
    """
    Genera las opciones de carga optimizadas para SQLAlchemy basándose en los includes.
    
    Args:
        model_class: Clase del modelo SQLAlchemy base
        includes: Lista de relaciones a incluir
        
    Returns:
        List[Any]: Lista de opciones de carga (joinedload/selectinload)
    """
    if not includes:
        return []
    
    options = []
    processed_relations = set()
    
    for include_path in includes:
        
        # Evitar duplicados
        if include_path in processed_relations:
            continue

        # Procesar cada nivel del path (ej: 'author.posts.comments')
        path_parts = include_path.split('.')
        current_model = model_class
        current_option = None
        
        for i, part in enumerate(path_parts):
            # Verificar que la relación existe en el modelo actual
            if not hasattr(current_model, part):
                break
                
            relation: RelationshipProperty = getattr(current_model, part)
            
            if i == 0:
                # Primera relación desde el modelo principal
                # Determinar estrategia basándose en el tipo de relación
                if hasattr(relation, 'direction'):
                    # Para relaciones 1:N usar selectinload, para N:1 usar joinedload
                    if relation.direction.name in ['ONETOMANY', 'MANYTOMANY']:
                        current_option = selectinload(relation)
                    else:  # MANYTOONE, ONETOONE
                        current_option = joinedload(relation)
                else:
                    # Fallback a selectinload si no se puede determinar
                    current_option = selectinload(relation)
                
                # Actualizar el modelo actual para relaciones anidadas
                if hasattr(relation, 'mapper'):
                    current_model = relation.mapper.class_
            else:
                # Relaciones anidadas
                if current_option is not None and hasattr(current_model, part):
                    nested_relation: RelationshipProperty = getattr(current_model, part)
                    
                    # Determinar estrategia para relación anidada
                    if hasattr(nested_relation, 'direction'):
                        if nested_relation.direction.name in ['ONETOMANY', 'MANYTOMANY']:
                            current_option = current_option.selectinload(nested_relation)
                        else:
                            current_option = current_option.joinedload(nested_relation)
                    else:
                        current_option = current_option.selectinload(nested_relation)
                    
                    # Actualizar el modelo actual
                    if hasattr(nested_relation, 'mapper'):
                        current_model = nested_relation.mapper.class_
        
        # Añadir la opción completa
        if current_option is not None:
            options.append(current_option)
            processed_relations.add(include_path)
    
    return options

async def load_relationships_from_dto(session: AsyncSession, instance: Any, dto: BaseModel, included: Optional[set[str]] = None) -> set[str]:
    """
    Refresca recursivamente las relaciones en la instancia que están definidas en el DTO.

    - Solo considera relaciones de SQLAlchemy.
    - Recorre las relaciones anidadas si el DTO las define.

    Args:
        session: Sesión SQLAlchemy asíncrona.
        instance: Objeto ORM ya añadido a la sesión y flush().
        dto: DTO que representa los datos creados.
    
    Returns:
        List[str]: Lista de nombres de relaciones que se han refrescado.
    """
    if included is None:
        included = set()

    model = type(instance)
    mapper = class_mapper(model)

    for attr in mapper.relationships:
        relation_name = attr.key
        if not hasattr(dto, relation_name):
            continue

        subdto = getattr(dto, relation_name)
        if subdto is None:
            continue  # esta relación no se quiere incluir

        # Refrescar la relación
        await session.refresh(instance, attribute_names=[relation_name])
        included.add(relation_name)
        subinstance = getattr(instance, relation_name, None)

        if subinstance is not None:
            if isinstance(subdto, list):
                for i, child_dto in enumerate(subdto):
                    if i < len(subinstance):  # por si la relación está incompleta
                        await load_relationships_from_dto(session, subinstance[i], child_dto, included)
            elif isinstance(subdto, BaseModel):
                await load_relationships_from_dto(session, subinstance, subdto, included)

    return included


class ExpressionParser:
    """
    Parser seguro para expresiones aritméticas en agregaciones SQLAlchemy.
    
    Soporta operaciones aritméticas básicas sobre columnas de modelos SQLAlchemy
    con validación estricta de seguridad.
    
    Examples:
        >>> # Expresión simple
        >>> expr = ExpressionParser.parse("field1/field2", MyModel)
        >>> 
        >>> # Expresión compleja
        >>> expr = ExpressionParser.parse("(revenue-cost)/quantity", MyModel)
        >>> 
        >>> # Con constantes
        >>> expr = ExpressionParser.parse("price*1.21", MyModel)
    """
    
    # Límites de seguridad
    MAX_EXPRESSION_LENGTH = 200
    MAX_TOKENS = 50
    MAX_NESTED_PARENS = 5
    
    # Operadores permitidos y sus funciones
    OPERATORS = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '%': lambda a, b: a % b,
    }
    
    # Precedencia de operadores (mayor número = mayor precedencia)
    PRECEDENCE = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '%': 2,
    }
    
    # Pattern para tokenizar: campos, números, operadores, paréntesis
    TOKEN_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*|\d+\.?\d*|[+\-*/%()])')
    
    @classmethod
    def parse(cls, expression: str, model: DeclarativeMeta) -> ColumnElement:
        """
        Parsea una expresión aritmética y la convierte en una expresión SQLAlchemy.
        
        Args:
            expression: String con la expresión aritmética (ej: "field1/field2")
            model: Modelo SQLAlchemy (clase que hereda de DeclarativeBase)
            
        Returns:
            Expresión SQLAlchemy compilada lista para usar en queries
            
        Raises:
            ValueError: Si la expresión es inválida, insegura o contiene campos inexistentes
            
        Examples:
            >>> from sqlalchemy import select, func
            >>> expr = ExpressionParser.parse("price/quantity", Product)
            >>> query = select(func.avg(expr))
        """
        # Validaciones de seguridad
        cls._validate_safety(expression)
        
        # Tokenizar
        tokens = cls._tokenize(expression)
        
        # Validar tokens
        cls._validate_tokens(tokens, model)
        
        # Convertir a notación postfija (RPN) usando Shunting Yard
        postfix = cls._to_postfix(tokens)
        
        # Evaluar y construir expresión SQLAlchemy
        return cls._evaluate_postfix(postfix, model)
    
    @classmethod
    def _validate_safety(cls, expression: str) -> None:
        """
        Valida que la expresión cumple con los límites de seguridad.
        
        Args:
            expression: La expresión a validar
            
        Raises:
            ValueError: Si la expresión excede los límites de seguridad
        """
        if not expression or not expression.strip():
            raise ValueError("La expresión no puede estar vacía")
        
        if len(expression) > cls.MAX_EXPRESSION_LENGTH:
            raise ValueError(
                f"Expresión demasiado larga. Máximo {cls.MAX_EXPRESSION_LENGTH} caracteres"
            )
        
        # Contar profundidad de paréntesis anidados
        depth = 0
        max_depth = 0
        for char in expression:
            if char == '(':
                depth += 1
                max_depth = max(max_depth, depth)
            elif char == ')':
                depth -= 1
                if depth < 0:
                    raise ValueError("Paréntesis desbalanceados: más ')' que '('")
        
        if depth != 0:
            raise ValueError("Paréntesis desbalanceados: más '(' que ')'")
        
        if max_depth > cls.MAX_NESTED_PARENS:
            raise ValueError(
                f"Demasiados paréntesis anidados. Máximo {cls.MAX_NESTED_PARENS} niveles"
            )
    
    @classmethod
    def _tokenize(cls, expression: str) -> List[str]:
        """
        Divide la expresión en tokens individuales.
        
        Args:
            expression: La expresión a tokenizar
            
        Returns:
            Lista de tokens (campos, números, operadores, paréntesis)
            
        Raises:
            ValueError: Si la expresión contiene caracteres inválidos
        """
        # Eliminar espacios en blanco
        expression = expression.strip().replace(' ', '')
        
        # Tokenizar usando regex
        tokens = cls.TOKEN_PATTERN.findall(expression)
        
        if len(tokens) > cls.MAX_TOKENS:
            raise ValueError(
                f"Demasiados tokens. Máximo {cls.MAX_TOKENS} tokens"
            )
        
        # Verificar que se parseó toda la expresión
        reconstructed = ''.join(tokens)
        if reconstructed != expression:
            invalid_chars = set(expression) - set(reconstructed)
            raise ValueError(
                f"Expresión contiene caracteres inválidos: {', '.join(repr(c) for c in invalid_chars)}"
            )
        
        return tokens
    
    @classmethod
    def _validate_tokens(cls, tokens: List[str], model: DeclarativeMeta) -> None:
        """
        Valida que todos los tokens sean seguros y válidos.
        
        Args:
            tokens: Lista de tokens a validar
            model: Modelo SQLAlchemy para validar nombres de campos
            
        Raises:
            ValueError: Si algún token es inválido o inseguro
        """
        if not tokens:
            raise ValueError("No se encontraron tokens en la expresión")
        
        for token in tokens:
            # Permitir paréntesis
            if token in '()':
                continue
            
            # Permitir operadores
            if token in cls.OPERATORS:
                continue
            
            # Permitir números (enteros o decimales)
            if re.match(r'^\d+\.?\d*$', token):
                continue
            
            # Debe ser un campo válido del modelo
            if not hasattr(model, token):
                raise ValueError(
                    f"Campo '{token}' no existe en el modelo {model.__name__}"
                )
            
            # Verificar que es una columna (no una relación u otro atributo)
            attr = getattr(model, token)
            if not hasattr(attr, 'type'):
                raise ValueError(
                    f"'{token}' no es una columna válida en {model.__name__}"
                )
    
    @classmethod
    def _to_postfix(cls, tokens: List[str]) -> List[str]:
        """
        Convierte tokens en notación infija a notación postfija usando el algoritmo Shunting Yard.
        
        Args:
            tokens: Lista de tokens en notación infija
            
        Returns:
            Lista de tokens en notación postfija (RPN)
            
        Raises:
            ValueError: Si hay errores de sintaxis en la expresión
        """
        output = []
        operator_stack = []
        
        for token in tokens:
            # Número o campo: añadir directamente a output
            if token not in '()' and token not in cls.OPERATORS:
                output.append(token)
            
            # Operador: aplicar reglas de precedencia
            elif token in cls.OPERATORS:
                while (operator_stack and 
                       operator_stack[-1] != '(' and 
                       operator_stack[-1] in cls.PRECEDENCE and
                       cls.PRECEDENCE[operator_stack[-1]] >= cls.PRECEDENCE[token]):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            
            # Paréntesis izquierdo: push al stack
            elif token == '(':
                operator_stack.append(token)
            
            # Paréntesis derecho: pop hasta encontrar '('
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Paréntesis desbalanceados")
                operator_stack.pop()  # Remover '('
        
        # Vaciar el stack de operadores
        while operator_stack:
            if operator_stack[-1] in '()':
                raise ValueError("Paréntesis desbalanceados")
            output.append(operator_stack.pop())
        
        return output
    
    @classmethod
    def _evaluate_postfix(cls, postfix: List[str], model: DeclarativeMeta) -> ColumnElement:
        """
        Evalúa la expresión en notación postfija y construye la expresión SQLAlchemy.
        
        Args:
            postfix: Lista de tokens en notación postfija
            model: Modelo SQLAlchemy
            
        Returns:
            Expresión SQLAlchemy compilada
            
        Raises:
            ValueError: Si la expresión es sintácticamente incorrecta
        """
        stack = []
        
        for token in postfix:
            # Operador: pop dos operandos, aplicar operación, push resultado
            if token in cls.OPERATORS:
                if len(stack) < 2:
                    raise ValueError(
                        "Expresión inválida: operador sin suficientes operandos"
                    )
                
                right = stack.pop()
                left = stack.pop()
                
                # Aplicar operación SQLAlchemy
                result = cls.OPERATORS[token](left, right)
                stack.append(result)
            
            # Número literal
            elif re.match(r'^\d+\.?\d*$', token):
                value = float(token) if '.' in token else int(token)
                stack.append(value)
            
            # Campo del modelo
            else:
                column = getattr(model, token)
                stack.append(column)
        
        # Debe quedar exactamente un elemento en el stack
        if len(stack) != 1:
            raise ValueError(
                "Expresión inválida: " + 
                ("demasiados operandos" if len(stack) > 1 else "sin operandos")
            )
        
        return stack[0]
    
    @classmethod
    def get_field_name(cls, expression: str) -> str:
        """
        Genera un nombre de campo limpio para usar como label en la agregación.
        
        Args:
            expression: La expresión original
            
        Returns:
            Nombre limpio para usar como label (ej: "field1_field2" para "field1/field2")
            
        Examples:
            >>> ExpressionParser.get_field_name("field1/field2")
            'field1_field2'
            >>> ExpressionParser.get_field_name("(revenue-cost)/quantity")
            '_revenue_cost__quantity'
        """
        # Reemplazar operadores y paréntesis con guiones bajos
        clean = re.sub(r'[^a-zA-Z0-9_]', '_', expression)
        # Eliminar guiones bajos consecutivos
        clean = re.sub(r'_+', '_', clean)
        # Eliminar guiones bajos al inicio/final
        clean = clean.strip('_')
        return clean if clean else 'expr'


sqlalchemy_table_mapper = {
    "usuario": Agenda,
}
