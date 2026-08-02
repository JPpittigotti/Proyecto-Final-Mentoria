from pymongo import MongoClient
from Config import MONGO_URI, MONGO_DB

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

# Acceso directo a cada colección
productos        = db["productos"]
inventario       = db["inventario_diario"]
sucursales       = db["sucursales"]
clientes         = db["clientes"]
tickets          = db["tickets"]