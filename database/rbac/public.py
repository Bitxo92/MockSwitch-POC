from schemas.public import *
from tai_sql.rbac import app, screen

my_app = app(id='my_app')

# Definir pantallas y permisos aquí
# Ejemplo:
# my_screen = screen(
#     id='my_screen',
#     dependencies=[
#         AllTables.READ,
#         Post.ADMIN
#     ]
# )

# my_app.add_screen(my_screen)

# print(my_screen.dependencies)