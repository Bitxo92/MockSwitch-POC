# -*- coding: utf-8 -*-
"""
Fuente principal para la definición de esquemas y generación de modelos CRUD.
Usa el contenido de tai_sql para definir tablas, relaciones, vistas y generar automáticamente modelos y CRUDs.
Usa tai_sql.generators para generar modelos y CRUDs basados en las tablas definidas.
Ejecuta por consola tai_sql generate para generar los recursos definidos en este esquema.
"""
from __future__ import annotations
from tai_sql import *
from tai_sql.generators import *


# Configurar el datasource
datasource(
    provider=env('MAIN_DATABASE_URL'), # Además de env, también puedes usar (para testing) connection_string y params
    schema='public', # Esquema del datasource
)

# Configurar los generadores
generate(
    ModelsGenerator(
        output_dir='database/database' # Directorio donde se generarán los modelos
    ),
    CRUDGenerator(
        output_dir='database/database', # Directorio donde se generarán los CRUDs
        mode='sync' # Modo de generación: 'sync' para síncrono, 'async' para asíncrono, 'both' para ambos
    ),
    ERDiagramGenerator(
        output_dir='database/diagrams', # Directorio donde se generarán los diagramas
    )
)

# Definición de tablas y relaciones

# Ejemplo de definición de tablas y relaciones. Eliminar estos modelos y definir los tuyos propios.
class Agenda(Table):
    """Tabla que almacena información de los usuarios del sistema"""
    __tablename__ = "agenda"

    id: int = column(primary_key=True, autoincrement=True)
    name: str = column(description='Nombre del usuario')
    email: str = column(description='Correo electrónico del usuario')
    phone: str = column(description='Número de teléfono del usuario')



