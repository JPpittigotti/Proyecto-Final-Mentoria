from Models import productos, inventario, sucursales, tickets

def get_total_productos():
    return productos.count_documents({})

def get_total_sucursales():
    return sucursales.count_documents({})

def get_total_tickets():
    return tickets.count_documents({})

def get_alertas_inventario():
    return inventario.count_documents(
        {"nivel_alerta": {"$in": ["Alerta", "Critico", "Quiebre"]}}
    )

def get_productos(busqueda="", categoria=""):
    filtro = {}
    if busqueda:
        filtro["nombre"] = {"$regex": busqueda, "$options": "i"}
    if categoria:
        filtro["categoria"] = categoria
    return list(productos.find(filtro).sort("sku", 1))

def get_categorias():
    return productos.distinct("categoria")

def get_inventario(sucursal_sel="", alerta_sel=""):
    pipeline = [
        {"$sort": {"fecha": -1}},
        {"$group": {
            "_id": {"sucursal_id": "$sucursal_id", "sku": "$sku"},
            "doc": {"$first": "$$ROOT"}
        }},
        {"$replaceRoot": {"newRoot": "$doc"}}
    ]
    if sucursal_sel:
        pipeline.insert(0, {"$match": {"sucursal_id": sucursal_sel}})
    if alerta_sel:
        pipeline.insert(0, {"$match": {"nivel_alerta": alerta_sel}})
    return list(inventario.aggregate(pipeline))