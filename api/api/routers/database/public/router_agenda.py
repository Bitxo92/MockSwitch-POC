from fastapi import APIRouter, Depends, Query, Path, Body
from api.database.public.crud.asyn import *
from api.resources import (
    APIResponse, APIError, PaginatedResponse, RecordNotFoundException,
    ValidationException, ErrorCode
)
from typing import Optional, List, Literal, Union, Dict, Any
from tai_alphi import Alphi


logger = Alphi.get_logger_by_name("tai-api")

agenda_router = APIRouter(
    prefix="/agenda",
    tags=["Agenda"]
)

@agenda_router.get("",
    response_model=APIResponse[List[AgendaRead]],
    response_description="Lista de registros de agenda obtenido exitosamente",
    operation_id="agenda_find_many",
    summary="Busca varios registros en la tabla agenda",
    responses={
        200: {
            "description": "Lista de registros de agenda obtenido exitosamente",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/APIResponse_List_AgendaRead__"
                    }
                }
            },
            "links": {
                "self": {
                    "operationId": "agenda_find_many",
                    "description": "Enlace a la consulta actual con los mismos filtros",
                    "parameters": {
                        "nombre": "$request.query.nombre",
                        "correo": "$request.query.correo",
                        "telefono": "$request.query.telefono",
                        "limit": "$request.query.limit",
                        "offset": "$request.query.offset",
                        "order_by": "$request.query.order_by",
                        "order": "$request.query.order",
                        "includes": "$request.query.includes"
                    }
                },
                "item": {
                    "operationId": "agenda_find",
                    "description": "Enlace para acceder a un elemento específico",
                    "parameters": {
                        "id": "$response.body#/data/**/id",
                        "includes": "$request.query.includes"
                    }
                },
                "create": {
                    "operationId": "agenda_create",
                    "description": "Enlace para crear un nuevo Agenda"
                },
                "count": {
                    "operationId": "agenda_count",
                    "description": "Enlace para obtener el conteo total con los mismos filtros",
                    "parameters": {
                        "nombre": "$request.query.nombre",
                        "correo": "$request.query.correo",
                        "telefono": "$request.query.telefono",
                    }
                }}
        },
        422: {
            "description": "Error de validación en parámetros",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El límite no puede ser negativo",
                                "field": "limit",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_find_many(
    limit: Optional[int] = Query(None, description="Número de registros a retornar.", gt=0),
    order_by: List[str] = Query(None, description="Lista de nombres de columnas para ordenar los resultados. Si no existen serán omitidas."),
    order: Optional[Literal["ASC", "DESC"]] = Query("ASC", description="Dirección de ordenamiento: 'ASC' para ascendente (por defecto), 'DESC' para descendente. Solo aplica si order_by está definido", regex="^(ASC|DESC)$"),
    offset: Optional[int] = Query(None, description="Número de registros a omitir desde el inicio. Útil para paginación. Debe ser un valor no negativo", ge=0),
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[List[AgendaRead]]:
    """
    ## Resumen
    Obtiene una lista de `agendas` con filtros opcionales y soporte para paginación.
    
    Este endpoint permite realizar búsquedas flexibles aplicando filtros opcionales
    por cualquiera de los campos disponibles, con soporte completo para paginación
    mediante los parámetros limit y offset.

    ## Resultado
    En `APIResponse.data`, retorna un listado de objetos donde cada uno representa un registro de la tabla `agenda` que incluye todos sus atributos

    ## Datos
    Para cada registro en `data` se incluye:
    - **id** (int): Campo id de la tabla agenda
    - **nombre** (str): Nombre del usuario
    - **correo** (str): Correo electrónico del usuario
    - **telefono** (str): Número de teléfono del usuario
    
    ## Parámetros de Filtrado
    
    Todos los parámetros de filtrado son opcionales y se pueden combinar:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    ## Parámetros de Paginación
    
    - **limit**: Número máximo de registros a retornar. Solo admite valores positivos. Si no se especifica, retorna todos los registros que coincidan con los filtros.
    - **order_by**: Lista de nombres de columnas para ordenar los resultados.⚠️ **IMPORTANTE**: los nombres de columnas deben existir, si no serán omitidas.
    - **order**: Dirección de ordenamiento: 'ASC' para ascendente (por defecto), 'DESC' para descendente. Solo aplica si order_by está definido.
    - **offset**: Número de registros a omitir desde el inicio. Solo admite valores positivos. Si no se especifica, inicia desde el primer registro.
    
    ## Consulta combinada (recomendado para pocos registros)
    ⚠️ **IMPORTANTE**: Usa siempre el parámetro `includes` para cargar relaciones en una sola consulta y evitar múltiples llamadas al API.
    
    ⚠️ **WARNING**: Si la relación incluida tiene muchos registros relacionados, la respuesta puede ser muy grande y lenta. Mejor consultar su endpoint directamente con filtros.
    
    El parametro `includes` permite cargar relaciones asociadas a los registros.
    """

    result = await api.agenda.find_many(
        limit=limit,
        offset=offset,
        order_by=order_by,
        order=order,
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
        includes=includes,
        
    )
    
    # Obtener el total para metadatos de paginación si es necesario
    total = None
    if limit is not None or offset is not None:
        try:
            total = await api.agenda.count(
                nombre=nombre,
                in_nombre=in_nombre,
                correo=correo,
                in_correo=in_correo,
                telefono=telefono,
                in_telefono=in_telefono,
            )
        except Exception as e:
            logger.warning(f"No se pudo obtener el total de registros: {str(e)}")
    
    return PaginatedResponse.success_paginated(
        data=result,
        total=total,
        limit=limit,
        offset=offset,
        message=f"Agendas obtenidos exitosamente"
    )

@agenda_router.get("/count", 
    response_model=APIResponse[int],
    response_description="Número de registros de agenda según los filtros aplicados",
    operation_id="agenda_count",
    summary="Cuenta registros en la tabla agenda",
    responses={
        200: {
            "description": "Conteo realizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 42,
                        "message": "Conteo realizado exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_count(
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[int]:
    """
    Cuenta el número de Agendas que coinciden con los filtros.
    """
    result = await api.agenda.count(
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    return APIResponse.success(
        data=result,
        message="Conteo realizado exitosamente"
    )

@agenda_router.get("/exists", 
    response_model=APIResponse[bool],
    operation_id="agenda_exists",
    summary="Verifica existencia en la tabla agenda",
    responses={
        200: {
            "description": "Verificación realizada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": True,
                        "message": "Verificación realizada exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_exists(
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[bool]:
    """
    Verifica si existe al menos un agenda que coincida con los filtros.
    """
    result = await api.agenda.exists(
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    return APIResponse.success(
        data=result,
        message="Verificación realizada exitosamente"
    )

@agenda_router.get("/{field}/sum",
    response_model=APIResponse[Union[int, float]],
    operation_id="agenda_sum_field",
    summary="Suma un campo numérico específico en la tabla agenda",
    responses={
        200: {
            "description": "Suma calculada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 12500.75,
                        "message": "Suma de 'campo' calculada exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Campo inválido o no numérico",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El campo especificado no es válido para suma",
                                "field": "field",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_sum_field(
    field: str = Path(..., description="Nombre del campo numérico a sumar"),
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[Union[int, float]]:
    """
    ## Resumen
    Calcula la suma de un campo numérico específico que coincida con los filtros.
    
    Este endpoint permite sumar los valores de un campo numérico en todos los registros
    que cumplan con los criterios de filtrado especificados.

    ## Parámetros
    
    - **field** (path): Nombre del campo numérico a sumar. Debe ser un campo de tipo numérico (int, float, decimal, etc.)
    
    ## Filtros Opcionales
    
    Todos los filtros de búsqueda estándar están disponibles:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    ## Resultado
    
    Retorna directamente el valor de la suma en `data`. Si no hay registros que coincidan, retorna `null`.
    
    ## Ejemplos
    
    ```
    # Sumar campo sin filtros
    GET /agenda/edad/sum
    
    # Sumar campo con filtros
    GET /agenda/salario/sum?nombre=Juan
    ```
    """
    result = await api.agenda.sum(
        agg_fields=[field],
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    # Verificar si la operación fue exitosa
    if not result.success:
        # Construir mensaje de error completo con todos los errores y warnings
        error_parts = []
        if result.errors:
            error_parts.extend(result.errors)
        if result.warnings:
            error_parts.extend(result.warnings)
        
        error_message = " | ".join(error_parts) if error_parts else "No se pudo calcular la suma"
        raise ValidationException(error_message, field)
    
    # Extraer el valor directo del diccionario retornado por el DAO
    sum_key = f"sum_{field}"
    value = result.data.get(sum_key) if result.data else None
    
    return APIResponse.success(
        data=value,
        message=f"Suma de '{field}' calculada exitosamente",
        meta={"warnings": result.warnings} if result.warnings else None
    )

@agenda_router.get("/{field}/mean",
    response_model=APIResponse[float],
    operation_id="agenda_mean_field",
    summary="Calcula la media de un campo numérico específico en la tabla agenda",
    responses={
        200: {
            "description": "Media calculada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 32.45,
                        "message": "Media de 'campo' calculada exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Campo inválido o no numérico",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El campo especificado no es válido para media",
                                "field": "field",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_mean_field(
    field: str = Path(..., description="Nombre del campo numérico para calcular la media"),
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[float]:
    """
    ## Resumen
    Calcula la media (promedio) de un campo numérico específico que coincida con los filtros.
    
    Este endpoint permite calcular el promedio de los valores de un campo numérico en todos
    los registros que cumplan con los criterios de filtrado especificados.

    ## Parámetros
    
    - **field** (path): Nombre del campo numérico para calcular la media. Debe ser un campo de tipo numérico (int, float, decimal, etc.)
    
    ## Filtros Opcionales
    
    Todos los filtros de búsqueda estándar están disponibles:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    ## Resultado
    
    Retorna directamente el valor de la media en `data`. Si no hay registros que coincidan, retorna `null`.
    
    ## Ejemplos
    
    ```
    # Calcular media de campo sin filtros
    GET /agenda/edad/mean
    
    # Calcular media de campo con filtros
    GET /agenda/salario/mean?departamento=ventas
    ```
    """
    result = await api.agenda.mean(
        agg_fields=[field],
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    # Verificar si la operación fue exitosa
    if not result.success:
        # Construir mensaje de error completo con todos los errores y warnings
        error_parts = []
        if result.errors:
            error_parts.extend(result.errors)
        if result.warnings:
            error_parts.extend(result.warnings)
        
        error_message = " | ".join(error_parts) if error_parts else "No se pudo calcular la media"
        raise ValidationException(error_message, field)
    
    # Extraer el valor directo del diccionario retornado por el DAO
    mean_key = f"mean_{field}"
    value = result.data.get(mean_key) if result.data else None
    
    return APIResponse.success(
        data=value,
        message=f"Media de '{field}' calculada exitosamente",
        meta={"warnings": result.warnings} if result.warnings else None
    )

@agenda_router.get("/{field}/max",
    response_model=APIResponse[Optional[Union[int, float, str]]],
    operation_id="agenda_max_field",
    summary="Encuentra el valor máximo de un campo específico en la tabla agenda",
    responses={
        200: {
            "description": "Valor máximo encontrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 99999.99,
                        "message": "Máximo de 'campo' encontrado exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Campo inválido",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El campo especificado no es válido para máximo",
                                "field": "field",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_max_field(
    field: str = Path(..., description="Nombre del campo para encontrar el valor máximo"),
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[Optional[Union[int, float, str]]]:
    """
    ## Resumen
    Encuentra el valor máximo de un campo específico que coincida con los filtros.
    
    Este endpoint permite encontrar el valor máximo de un campo numérico o de fecha/hora
    en todos los registros que cumplan con los criterios de filtrado especificados.

    ## Parámetros
    
    - **field** (path): Nombre del campo para encontrar el máximo. Puede ser numérico (int, float, decimal) o temporal (date, datetime, timestamp)
    
    ## Filtros Opcionales
    
    Todos los filtros de búsqueda estándar están disponibles:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    ## Resultado
    
    Retorna directamente el valor máximo en `data`. Si no hay registros que coincidan, retorna `null`.
    Para campos de fecha/hora, el valor se retorna en formato ISO 8601.
    
    ## Ejemplos
    
    ```
    # Encontrar valor máximo sin filtros
    GET /agenda/salario/max
    
    # Encontrar fecha más reciente con filtros
    GET /agenda/fecha_creacion/max?activo=true
    ```
    """
    result = await api.agenda.max(
        agg_fields=[field],
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    # Verificar si la operación fue exitosa
    if not result.success:
        # Construir mensaje de error completo con todos los errores y warnings
        error_parts = []
        if result.errors:
            error_parts.extend(result.errors)
        if result.warnings:
            error_parts.extend(result.warnings)
        
        error_message = " | ".join(error_parts) if error_parts else "No se pudo encontrar el máximo"
        raise ValidationException(error_message, field)
    
    # Extraer el valor directo del diccionario retornado por el DAO
    max_key = f"max_{field}"
    value = result.data.get(max_key) if result.data else None
    
    return APIResponse.success(
        data=value,
        message=f"Máximo de '{field}' encontrado exitosamente",
        meta={"warnings": result.warnings} if result.warnings else None
    )

@agenda_router.get("/{field}/min",
    response_model=APIResponse[Optional[Union[int, float, str]]],
    operation_id="agenda_min_field",
    summary="Encuentra el valor mínimo de un campo específico en la tabla agenda",
    responses={
        200: {
            "description": "Valor mínimo encontrado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 100.00,
                        "message": "Mínimo de 'campo' encontrado exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Campo inválido",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El campo especificado no es válido para mínimo",
                                "field": "field",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_min_field(
    field: str = Path(..., description="Nombre del campo para encontrar el valor mínimo"),
    nombre: Optional[str] = Query(None, description='Filtrar por nombre. Utiliza "%nombre%" para hacer consultas ILIKE. Nombre del usuario', min_length=1, max_length=255),
    in_nombre: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna nombre. Nombre del usuario'),
    correo: Optional[str] = Query(None, description='Filtrar por correo. Utiliza "%correo%" para hacer consultas ILIKE. Correo electrónico del usuario', min_length=1, max_length=255),
    in_correo: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna correo. Correo electrónico del usuario'),
    telefono: Optional[str] = Query(None, description='Filtrar por telefono. Utiliza "%telefono%" para hacer consultas ILIKE. Número de teléfono del usuario', min_length=1, max_length=255),
    in_telefono: Optional[List[str]] = Query(None, description='Filtrar por varios valores de la columna telefono. Número de teléfono del usuario'),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[Optional[Union[int, float, str]]]:
    """
    ## Resumen
    Encuentra el valor mínimo de un campo específico que coincida con los filtros.
    
    Este endpoint permite encontrar el valor mínimo de un campo numérico o de fecha/hora
    en todos los registros que cumplan con los criterios de filtrado especificados.

    ## Parámetros
    
    - **field** (path): Nombre del campo para encontrar el mínimo. Puede ser numérico (int, float, decimal) o temporal (date, datetime, timestamp)
    
    ## Filtros Opcionales
    
    Todos los filtros de búsqueda estándar están disponibles:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    ## Resultado
    
    Retorna directamente el valor mínimo en `data`. Si no hay registros que coincidan, retorna `null`.
    Para campos de fecha/hora, el valor se retorna en formato ISO 8601.
    
    ## Ejemplos
    
    ```
    # Encontrar valor mínimo sin filtros
    GET /agenda/edad/min
    
    # Encontrar fecha más antigua con filtros
    GET /agenda/fecha_registro/min?ciudad=Madrid
    ```
    """
    result = await api.agenda.min(
        agg_fields=[field],
        nombre=nombre,
        in_nombre=in_nombre,
        correo=correo,
        in_correo=in_correo,
        telefono=telefono,
        in_telefono=in_telefono,
    )
    
    # Verificar si la operación fue exitosa
    if not result.success:
        # Construir mensaje de error completo con todos los errores y warnings
        error_parts = []
        if result.errors:
            error_parts.extend(result.errors)
        if result.warnings:
            error_parts.extend(result.warnings)
        
        error_message = " | ".join(error_parts) if error_parts else "No se pudo encontrar el mínimo"
        raise ValidationException(error_message, field)
    
    # Extraer el valor directo del diccionario retornado por el DAO
    min_key = f"min_{field}"
    value = result.data.get(min_key) if result.data else None
    
    return APIResponse.success(
        data=value,
        message=f"Mínimo de '{field}' encontrado exitosamente",
        meta={"warnings": result.warnings} if result.warnings else None
    )

@agenda_router.post("/agg",
    response_model=APIResponse[Dict[str, Optional[Union[int, float, str]]]],
    operation_id="agenda_aggregate",
    summary="Realiza múltiples agregaciones en la tabla agenda",
    responses={
        200: {
            "description": "Agregaciones calculadas exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
                            "sum_edad": 450,
                            "sum_salario": 150000.50,
                            "mean_edad": 30.5,
                            "max_fecha_nacimiento": "2000-01-15T00:00:00",
                            "min_fecha_nacimiento": "1970-05-20T00:00:00"
                        },
                        "message": "Agregaciones calculadas exitosamente",
                        "meta": {
                            "total_operations": 4,
                            "valid_operations": 4,
                            "total_expressions": 5,
                            "warnings": []
                        }
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en operaciones o filtros",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "Operación 'median' no soportada. Operaciones válidas: ['sum', 'mean', 'max', 'min']",
                                "field": "operations",
                                "details": None
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "INTERNAL_SERVER_ERROR",
                                "message": "Ha ocurrido un error inesperado",
                                "field": None,
                                "details": None
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def agenda_aggregate(
    payload: Dict[str, Any] = Body(..., 
        example={
            "operations": {
                "sum": [
                    "precio",
                    "precio*cantidad",
                    {"expr": "ingreso-coste", "as": "ganancia"}
                ],
                "mean": ["cantidad"],
                "max": ["fecha_creacion"],
                "min": ["fecha_creacion"]
            },
            "filters": {
                "activo": True,
                "email": "%@gmail.com"
            }
        }
    ),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[Dict[str, Optional[Union[int, float, str]]]]:
    """
    ## Resumen
    Realiza múltiples operaciones de agregación en una sola consulta sobre la tabla agenda.
    
    Este endpoint permite combinar diferentes operaciones de agregación (sum, mean, max, min, count) 
    sobre múltiples campos en una única petición, con soporte completo para:
    - **Campos simples**: Agregaciones directas sobre columnas de la tabla
    - **Expresiones aritméticas**: Cálculos antes de agregar (e.g., `precio*cantidad`)
    - **Aliases personalizados**: Nombres descriptivos para los resultados
    - **Filtros avanzados**: Combinación de múltiples criterios de búsqueda

    ## Cuerpo de la Petición
    
    El body debe incluir:
    
    ### operations (requerido)
    Diccionario donde cada clave es una operación y el valor es una lista de campos o expresiones.
    
    Cada elemento de la lista puede ser:
    
    #### 1. Campo simple (string)
    ```json
    "sum": ["precio", "cantidad"]
    ```
    
    #### 2. Expresión aritmética (string)
    Operadores soportados: `+`, `-`, `*`, `/`, `%`, `(`, `)`
    ```json
    "sum": ["precio*cantidad", "(ingreso-costo)/cantidad"]
    ```
    
    #### 3. Expresión con alias personalizado (objeto)
    ```json
    "sum": [
        {"expr": "ingreso-costo", "as": "ganancia"},
        {"expr": "precio*cantidad", "as": "valor_total"}
    ]
    ```
    
    #### Operaciones disponibles:
    - **sum**: Suma de valores numéricos (campos o expresiones)
    - **mean**: Promedio de valores numéricos (campos o expresiones)
    - **max**: Valor máximo (numérico o fechas, solo campos simples)
    - **min**: Valor mínimo (numérico o fechas, solo campos simples)
    - **count**: Conteo de registros (cualquier campo)
    
    ⚠️ **IMPORTANTE**: Las expresiones aritméticas solo están disponibles para operaciones numéricas (sum, mean). 
    Para max/min de fechas, use campos simples.
    
    ### filters (opcional)
    Diccionario con filtros a aplicar. Las claves deben ser nombres de campos válidos:
    - **nombre**: Filtrar por nombre. Utilizar "%nombre%" para hacer consultas ILIKE.
    - **in_nombre**: Filtrar por varios valores de la columna nombre
    - **correo**: Filtrar por correo. Utilizar "%correo%" para hacer consultas ILIKE.
    - **in_correo**: Filtrar por varios valores de la columna correo
    - **telefono**: Filtrar por telefono. Utilizar "%telefono%" para hacer consultas ILIKE.
    - **in_telefono**: Filtrar por varios valores de la columna telefono

    
    Los filtros con prefijo `in_` permiten buscar múltiples valores (OR lógico).
    Los filtros `min_` y `max_` permiten rangos para campos numéricos o de fecha.
    Los filtros de texto soportan LIKE con el carácter `%`.
    
    ## Resultado
    
    Retorna un diccionario en `data` donde cada clave tiene el formato:
    - `{operación}_{campo}`: Para campos simples (e.g., `sum_precio`)
    - `{operación}_{alias}`: Para expresiones con alias (e.g., `sum_ganancia`)
    - `{operación}_{expresión_sanitizada}`: Para expresiones sin alias (e.g., `sum_precio_cantidad`)
    
    Valores retornados:
    - **sum**: Suma total (float o int)
    - **mean**: Media aritmética (float)
    - **max/min**: Valor máximo/mínimo (numeric → float, datetime → ISO 8601 string)
    - **count**: Cantidad de registros (int, nunca null, mínimo 0)
    
    El campo `meta` incluye:
    - **total_operations**: Número total de operaciones solicitadas
    - **valid_operations**: Número de operaciones procesadas exitosamente
    - **total_expressions**: Número total de expresiones SQL generadas
    - **warnings**: Lista de advertencias (campos no válidos, tipos incompatibles)
    - **operations_summary**: Detalle de cada operación con fields y labels
    
    ## Seguridad y Validaciones
    
    ✅ **Validaciones automáticas**:
    - Los campos deben existir en el modelo Agenda
    - Los campos numéricos son válidos para: sum, mean, max, min, count
    - Los campos de fecha son válidos para: max, min, count
    - Expresiones aritméticas solo permiten campos numéricos
    - Longitud máxima de expresiones: 200 caracteres
    - Máximo de tokens por expresión: 50
    - Profundidad máxima de paréntesis: 5 niveles
    
    ⚠️ **Comportamiento con campos inválidos**:
    - Si un campo no existe → se genera un error y se omite
    - Si un campo no es válido para su operación → se genera un warning y se omite
    - Si NO hay campos válidos → el endpoint retorna un error 422
    - Si hay AL MENOS un campo válido → el endpoint retorna éxito con warnings
    
    ## Ejemplos
    
    ### Ejemplo 1: Campos simples
    ```json
    POST /agenda/agg
    {
      "operations": {
        "sum": ["precio", "cantidad"],
        "mean": ["precio"],
        "count": ["id"]
      }
    }
    ```
    **Respuesta:**
    ```json
    {
      "status": "success",
      "data": {
        "sum_precio": 15000.50,
        "sum_cantidad": 450,
        "mean_precio": 125.42,
        "count_id": 120
      },
      "meta": {
        "total_operations": 3,
        "valid_operations": 3,
        "total_expressions": 4,
        "warnings": []
      }
    }
    ```
    
    ### Ejemplo 2: Expresiones aritméticas sin alias
    ```json
    POST /agenda/agg
    {
      "operations": {
        "sum": ["precio*cantidad", "total-descuento"],
        "mean": ["(ingreso-costo)/cantidad"]
      }
    }
    ```
    **Respuesta:**
    ```json
    {
      "status": "success",
      "data": {
        "sum_precio_cantidad": 125000.00,
        "sum_total_descuento": 98500.50,
        "mean_ingreso_costo_cantidad": 45.30
      }
    }
    ```
    
    ### Ejemplo 3: Expresiones con aliases personalizados
    ```json
    POST /agenda/agg
    {
      "operations": {
        "sum": [
          {"expr": "ingreso-costo", "as": "ganancia"},
          {"expr": "precio*cantidad", "as": "valor_total"}
        ],
        "mean": [
          {"expr": "(ingreso-costo)/cantidad", "as": "margen_unitario"}
        ]
      },
      "filters": {
        "in_categoria": ["electronica", "hogar"],
        "min_fecha": "2024-01-01T00:00:00"
      }
    }
    ```
    **Respuesta:**
    ```json
    {
      "status": "success",
      "data": {
        "sum_ganancia": 45000.00,
        "sum_valor_total": 125000.00,
        "mean_margen_unitario": 12.50
      },
      "meta": {
        "total_operations": 2,
        "valid_operations": 2,
        "total_expressions": 3,
        "warnings": [],
        "operations_summary": {
          "sum": {
            "requested_fields": ["ingreso-costo", "precio*cantidad"],
            "valid_fields": ["ganancia", "valor_total"],
            "valid_count": 2
          },
          "mean": {
            "requested_fields": ["(ingreso-costo)/cantidad"],
            "valid_fields": ["margen_unitario"],
            "valid_count": 1
          }
        }
      }
    }
    ```
    
    ### Ejemplo 4: Combinación de campos simples, expresiones y filtros
    ```json
    POST /agenda/agg
    {
      "operations": {
        "sum": [
          "precio",
          "cantidad",
          {"expr": "precio*cantidad", "as": "total_ventas"}
        ],
        "mean": ["precio"],
        "max": ["fecha_creacion"],
        "min": ["fecha_creacion"],
        "count": ["id"]
      },
      "filters": {
        "activo": true,
        "in_estado": ["completado", "enviado"],
        "email": "%@empresa.com",
        "min_fecha": "2024-01-01T00:00:00",
        "max_fecha": "2024-12-31T23:59:59"
      }
    }
    ```
    **Respuesta:**
    ```json
    {
      "status": "success",
      "data": {
        "sum_precio": 15000.50,
        "sum_cantidad": 450,
        "sum_total_ventas": 125000.00,
        "mean_precio": 125.42,
        "max_fecha_creacion": "2024-12-31T15:30:00",
        "min_fecha_creacion": "2024-01-05T08:15:00",
        "count_id": 120
      },
      "meta": {
        "total_operations": 5,
        "valid_operations": 5,
        "total_expressions": 7,
        "warnings": []
      }
    }
    ```
    
    ### Ejemplo 5: Manejo de campos inválidos
    ```json
    POST /agenda/agg
    {
      "operations": {
        "sum": ["precio", "nombre", "cantidad"],
        "mean": ["descripcion", "precio"]
      }
    }
    ```
    **Respuesta:**
    ```json
    {
      "status": "success",
      "data": {
        "sum_precio": 15000.50,
        "sum_cantidad": 450,
        "mean_precio": 125.42
      },
      "meta": {
        "total_operations": 2,
        "valid_operations": 2,
        "total_expressions": 3,
        "warnings": [
          "Campo 'nombre' de tipo 'VARCHAR' no es válido para operación 'sum'",
          "Campo 'descripcion' de tipo 'TEXT' no es válido para operación 'mean'"
        ]
      }
    }
    ```
    """
    # Validar estructura del payload
    if not isinstance(payload, dict):
        raise ValidationException("El cuerpo de la petición debe ser un objeto JSON", "payload")
    
    operations = payload.get("operations", {})
    filters = payload.get("filters", {})
    
    # Validar que se proporcionaron operaciones
    if not operations:
        raise ValidationException("Se requiere al menos una operación en 'operations'", "operations")
    
    if not isinstance(operations, dict):
        raise ValidationException("'operations' debe ser un objeto con operaciones como claves", "operations")
    
    if not isinstance(filters, dict):
        filters = {}
    
    # Extraer los filtros y mapearlos a los parámetros del método agg()
    filter_params = {}
    # Filtro: id (tipo: int)
    if "id" in filters:
        filter_params["id"] = filters["id"]
    if "in_id" in filters:
        filter_params["in_id"] = filters["in_id"]
    # Filtro: nombre (tipo: str)
    if "nombre" in filters:
        filter_params["nombre"] = filters["nombre"]
    if "in_nombre" in filters:
        filter_params["in_nombre"] = filters["in_nombre"]
    # Filtro: correo (tipo: str)
    if "correo" in filters:
        filter_params["correo"] = filters["correo"]
    if "in_correo" in filters:
        filter_params["in_correo"] = filters["in_correo"]
    # Filtro: telefono (tipo: str)
    if "telefono" in filters:
        filter_params["telefono"] = filters["telefono"]
    if "in_telefono" in filters:
        filter_params["in_telefono"] = filters["in_telefono"]

    
    # Llamar al método agg() del DAO
    result = await api.agenda.agg(
        aggregations=operations,
        **filter_params
    )
    
    # Verificar si la operación fue exitosa
    if not result.success:
        # Si hay errores, lanzar excepción
        error_parts = []
        if result.errors:
            error_parts.extend(result.errors)
        if result.warnings:
            error_parts.extend(result.warnings)
        
        error_message = " | ".join(error_parts) if error_parts else "No se pudieron procesar las agregaciones"
        raise ValidationException(error_message, "operations")
    
    # Preparar metadata extendida
    meta = {
        "total_operations": result.metadata.get("total_operations", 0),
        "valid_operations": result.metadata.get("valid_operations", 0),
        "total_expressions": result.metadata.get("total_expressions", 0),
        "warnings": result.warnings,
        "operations_summary": result.metadata.get("operations_summary", {})
    }
    
    return APIResponse.success(
        data=result.data,
        message="Agregaciones calculadas exitosamente",
        meta=meta
    )



@agenda_router.get("/{id:int}", 
    response_model=APIResponse[AgendaRead],
    response_description="Registro único de agenda obtenido exitosamente",
    operation_id="agenda_find",
    summary="Busca un registro en la tabla agenda",
    responses={
        200: {
            "description": "Registro único de agenda obtenido exitosamente",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/APIResponse_AgendaRead_"
                    }
                }
            },
            "links": {
                "self": {
                    "operationId": "agenda_find",
                    "description": "Enlace al recurso actual",
                    "parameters": {
                        "id": "$response.body#/data/id",
                        "includes": "$request.query.includes"
                    }
                },
                "collection": {
                    "operationId": "agenda_find_many",
                    "description": "Enlace a la colección de Agendas"
                },
                "edit": {
                    "operationId": "agenda_update",
                    "description": "Enlace para actualizar este Agenda",
                    "parameters": {
                        "id": "$response.body#/data/id",
                    }
                },
                "delete": {
                    "operationId": "agenda_delete",
                    "description": "Enlace para eliminar este Agenda",
                    "parameters": {
                        "id": "$response.body#/data/id",
                    }
                }}
        },
        422: {
            "description": "Error de validación en parámetros",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "id debe ser mayor a 0",
                                "field": "id",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        404: {
            "description": "Agenda no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Agenda no encontrado",
                        "errors": [
                            {
                                "code": "RECORD_NOT_FOUND",
                                "message": "Agenda no encontrado",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_find(
    id: int = Path(..., description="Campo id de la tabla agenda", gt=0),
    includes: List[str] = Query(None, description="Lista de relaciones a incluir en la respuesta para obtener datos relacionados. Especifica los nombres de las relaciones que deseas expandir"),

    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[AgendaRead]:
    """
    ## Resumen
    Obtiene un Agenda específico por su clave primaria.
    
    Este endpoint permite recuperar un registro individual de Agenda
    utilizando su identificador único (clave primaria). Opcionalmente puede
    incluir datos de relaciones asociadas.

    ## Resultado
    Si la consulta es exitosa, en `APIResponse.data`, retorna un objeto que representa un registro de la tabla `agenda` que incluye todos sus atributos

    Si no se encuentra el registro, devuelve un error 404 `RECORD_NOT_FOUND`.

    ## Datos
    Para cada registro en `data` se incluye:
    - **id** (int): Campo id de la tabla agenda
    - **nombre** (str): Nombre del usuario
    - **correo** (str): Correo electrónico del usuario
    - **telefono** (str): Número de teléfono del usuario
    
    ## Parámetros de Identificación
    
    - **id**: id del Agenda a buscar (tipo: int)
    
    ## Consulta combinada (RECOMENDADO)
    ⚠️ **IMPORTANTE**: Usa siempre el parámetro `includes` para cargar relaciones en una sola consulta y evitar múltiples llamadas al API.
    
    El parametro `includes` permite cargar relaciones asociadas a los registros.
    """
    # Validaciones básicas de entrada
    if id <= 0:
        raise ValidationException("id debe ser mayor a 0", "id")

    
    result = await api.agenda.find(
        id=id,
        includes=includes,

    )
    
    if result is None:
        raise RecordNotFoundException("Agenda")
        
    return APIResponse.success(
        data=result,
        message="Agenda obtenido exitosamente"
    )

@agenda_router.post("",
    response_model=APIResponse[AgendaRead],
    status_code=201,
    operation_id="agenda_create",
    summary="Crea un registro en la tabla agenda",
    responses={
        422: {
            "description": "Error de validación en los datos de entrada",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "El campo es requerido",
                                "field": "nombre",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        409: {
            "description": "Registro duplicado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "El registro ya existe",
                        "errors": [
                            {
                                "code": "DUPLICATE_RECORD",
                                "message": "El registro ya existe",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Violación de clave foránea",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Violación de clave foránea",
                        "errors": [
                            {
                                "code": "FOREIGN_KEY_VIOLATION",
                                "message": "La referencia especificada no existe",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_create(
    agenda: AgendaCreate,
    
    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[AgendaRead]:
    """
    Crea un nuevo Agenda.
    """
    result = await api.agenda.create(agenda)
    
    return APIResponse.success(
        data=result,
        message="Agenda creado exitosamente"
    )

@agenda_router.patch("/{id:int}", 
    response_model=APIResponse[int],
    operation_id="agenda_update",
    summary="Actualiza un registro en la tabla agenda",
    responses={
        200: {
            "description": "Agenda actualizado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 1,
                        "message": "Agenda actualizado exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en parámetros o datos",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "id debe ser mayor a 0",
                                "field": "id",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        404: {
            "description": "Agenda no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Agenda no encontrado",
                        "errors": [
                            {
                                "code": "RECORD_NOT_FOUND",
                                "message": "Agenda no encontrado",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Violación de clave foránea",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Violación de clave foránea",
                        "errors": [
                            {
                                "code": "FOREIGN_KEY_VIOLATION",
                                "message": "La referencia especificada no existe",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_update(
    id: int = Path(..., description="Campo id de la tabla agenda", gt=0),
    values: AgendaUpdateValues = Body(...),
    
    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[int]:
    """
    Actualiza un Agenda específico.
    """
    # Validaciones básicas de entrada
    if id <= 0:
        raise ValidationException("id debe ser mayor a 0", "id")
    
    # Verificar que el registro existe antes de actualizar
    existing = await api.agenda.find(
        id=id,
    )
    
    if existing is None:
        raise RecordNotFoundException("Agenda")
    
    result = await api.agenda.update(
        id=id,
        updated_values=values
    )
    
    if result == 0:
        raise RecordNotFoundException("Agenda")
        
    return APIResponse.success(
        data=result,
        message="Agenda actualizado exitosamente"
    )

@agenda_router.patch("", 
    response_model=APIResponse[int],
    operation_id="agenda_update_many",
    summary="Actualiza múltiples registros en la tabla agenda",
    responses={
        200: {
            "description": "Agendas actualizados exitosamente",
            "content": {
                "application/json": {
                    "examples": {
                        "records_updated": {
                            "summary": "Registros actualizados",
                            "value": {
                                "status": "success",
                                "data": 5,
                                "message": "5 Agendas actualizados exitosamente",
                                "errors": None,
                                "meta": None
                            }
                        },
                        "no_records_found": {
                            "summary": "No se encontraron registros",
                            "value": {
                                "status": "success",
                                "data": 0,
                                "message": "No se encontraron registros que coincidan con los criterios",
                                "errors": None,
                                "meta": None
                            }
                        }
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en los datos",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "Los criterios de búsqueda son requeridos",
                                "field": "filters",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_update_many(
    payload: AgendaUpdate,
    
    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[int]:
    """
    Actualiza múltiples Agendas.
    """
    result = await api.agenda.update_many(payload)
    
    message = f"{result} Agendas actualizados exitosamente" if result > 0 else "No se encontraron registros que coincidan con los criterios"
    
    return APIResponse.success(
        data=result,
        message=message
    )

@agenda_router.delete("/{id:int}", 
    response_model=APIResponse[int],
    operation_id="agenda_delete",
    summary="Elimina un registro en la tabla agenda",
    responses={
        200: {
            "description": "Agenda eliminado exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": 1,
                        "message": "Agenda eliminado exitosamente",
                        "errors": None,
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Error de validación en parámetros",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error de validación",
                        "errors": [
                            {
                                "code": "VALIDATION_ERROR",
                                "message": "id debe ser mayor a 0",
                                "field": "id",
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        404: {
            "description": "Agenda no encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Agenda no encontrado",
                        "errors": [
                            {
                                "code": "RECORD_NOT_FOUND",
                                "message": "Agenda no encontrado",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        422: {
            "description": "Violación de clave foránea",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Violación de clave foránea",
                        "errors": [
                            {
                                "code": "FOREIGN_KEY_VIOLATION",
                                "message": "No se puede eliminar el registro porque está siendo referenciado",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        },
        500: {
            "description": "Error interno del servidor",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "data": None,
                        "message": "Error interno del servidor",
                        "errors": [
                            {
                                "code": "DATABASE_ERROR",
                                "message": "Error en la base de datos",
                                "field": None,
                                "details": None
                            }
                        ],
                        "meta": None
                    }
                }
            }
        }
    }
)
async def agenda_delete(
    id: int = Path(..., description="Campo id de la tabla agenda", gt=0),
    
    api: PublicAsyncDBAPI = Depends(PublicAsyncDBAPI)
) -> APIResponse[int]:
    """
    Elimina un Agenda por su primary key.
    """
    # Validaciones básicas de entrada
    if id <= 0:
        raise ValidationException("id debe ser mayor a 0", "id")
    
    # Verificar que el registro existe antes de eliminar
    existing = await api.agenda.find(
        id=id,
    )
    
    if existing is None:
        raise RecordNotFoundException("Agenda")
    
    result = await api.agenda.delete(
        id=id,
    )
    
    if result == 0:
        raise RecordNotFoundException("Agenda")
        
    return APIResponse.success(
        data=result,
        message="Agenda eliminado exitosamente"
    )
