from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv("SECRET_KEY")

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]


# ── Usuario de prueba (para el MVP) 
USUARIOS = {
    "admin": "admin123",
    "gerente": "gerente123"
}


# -------------------------
# LOGIN
# -------------------------


@app.route("/", methods=["GET", "POST"])
def login():
    if "usuario" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave   = request.form.get("clave", "").strip()

        if usuario in USUARIOS and USUARIOS[usuario] == clave:
            session["usuario"] = usuario
            return redirect(url_for("dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# -------------------------
# DASHBOARD (página de inicio tras login)
# -------------------------

@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    total_productos   = db.productos.count_documents({})
    total_sucursales  = db.sucursales.count_documents({})
    total_tickets     = db.tickets.count_documents({})
    alertas_inventario = db.inventario_diario.count_documents(
        {"nivel_alerta": {"$in": ["Alerta", "Critico", "Quiebre"]}}
    )

    return render_template("dashboard.html",
        total_productos=total_productos,
        total_sucursales=total_sucursales,
        total_tickets=total_tickets,
        alertas_inventario=alertas_inventario,
        usuario=session["usuario"]
    )

# -------------------------
# PRODUCTOS
# -------------------------


@app.route("/productos")
def productos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    busqueda  = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()

    filtro = {}
    if busqueda:
        filtro["nombre"] = {"$regex": busqueda, "$options": "i"}
    if categoria:
        filtro["categoria"] = categoria

    lista      = list(db.productos.find(filtro).sort("sku", 1))
    categorias = db.productos.distinct("categoria")

    return render_template("productos.html",
        productos=lista,
        categorias=categorias,
        busqueda=busqueda,
        categoria_sel=categoria,
        usuario=session["usuario"]
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
def producto_nuevo():
    if "usuario" not in session:
        return redirect(url_for("login"))

    categorias = ["Abarrotes", "Lácteos", "Carnes", "Frutas y Verduras",
                  "Panadería", "Bebidas", "Limpieza", "Cuidado Personal"]

    if request.method == "POST":
        sku = request.form.get("sku", "").strip().upper()

        # Verificar que el SKU no exista ya
        if db.productos.find_one({"sku": sku}):
            flash(f"El SKU {sku} ya existe.", "error")
            return render_template("producto_form.html", categorias=categorias,
                                   usuario=session["usuario"], producto=None)

        nuevo = {
            "sku":            sku,
            "nombre":         request.form.get("nombre", "").strip(),
            "categoria":      request.form.get("categoria", "").strip(),
            "perecedero":     request.form.get("perecedero") == "on",
            "precio_lista":   float(request.form.get("precio_lista", 0)),
            "costo_unitario": float(request.form.get("costo_unitario", 0)),
            "stock_minimo":   int(request.form.get("stock_minimo", 0)),
            "punto_reorden":  int(request.form.get("punto_reorden", 0)),
        }

        db.productos.insert_one(nuevo)
        flash(f"Producto {sku} creado correctamente.", "ok")
        return redirect(url_for("productos"))

    return render_template("producto_form.html", categorias=categorias,
                           usuario=session["usuario"], producto=None)


@app.route("/productos/editar/<sku>", methods=["GET", "POST"])
def producto_editar(sku):
    if "usuario" not in session:
        return redirect(url_for("login"))

    producto   = db.productos.find_one({"sku": sku})
    categorias = ["Abarrotes", "Lácteos", "Carnes", "Frutas y Verduras",
                  "Panadería", "Bebidas", "Limpieza", "Cuidado Personal"]

    if not producto:
        flash("Producto no encontrado.", "error")
        return redirect(url_for("productos"))

    if request.method == "POST":
        cambios = {
            "nombre":         request.form.get("nombre", "").strip(),
            "categoria":      request.form.get("categoria", "").strip(),
            "perecedero":     request.form.get("perecedero") == "on",
            "precio_lista":   float(request.form.get("precio_lista", 0)),
            "costo_unitario": float(request.form.get("costo_unitario", 0)),
            "stock_minimo":   int(request.form.get("stock_minimo", 0)),
            "punto_reorden":  int(request.form.get("punto_reorden", 0)),
        }
        db.productos.update_one({"sku": sku}, {"$set": cambios})
        flash(f"Producto {sku} actualizado.", "ok")
        return redirect(url_for("productos"))

    return render_template("producto_form.html", categorias=categorias,
                           usuario=session["usuario"], producto=producto)


@app.route("/productos/eliminar/<sku>", methods=["POST"])
def producto_eliminar(sku):
    if "usuario" not in session:
        return redirect(url_for("login"))
    db.productos.delete_one({"sku": sku})
    flash(f"Producto {sku} eliminado.", "ok")
    return redirect(url_for("productos"))

# -------------------------
# INVENTARIO
# -------------------------

@app.route("/inventario")
def inventario():
    if "usuario" not in session:
        return redirect(url_for("login"))

    sucursal_sel = request.args.get("sucursal", "").strip()
    alerta_sel   = request.args.get("alerta", "").strip()

    # Tomar el registro más reciente por producto + sucursal
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

    registros  = list(db.inventario_diario.aggregate(pipeline))
    sucursales = db.sucursales.distinct("sucursal_id")
    niveles    = ["Normal", "Alerta", "Critico", "Quiebre"]

    # Enriquecer con nombre de producto
    skus = {p["sku"]: p["nombre"] for p in db.productos.find({}, {"sku":1,"nombre":1})}
    for r in registros:
        r["nombre_producto"] = skus.get(r.get("sku"), r.get("sku", "—"))

        if isinstance(r.get("fecha"), str):
            try:
                from datetime import datetime
                r["fecha"] = datetime.strptime(r["fecha"], "%Y-%m-%d")
            except:
                r["fecha"] = None

    return render_template("inventario.html",
        registros=registros,
        sucursales=sucursales,
        niveles=niveles,
        sucursal_sel=sucursal_sel,
        alerta_sel=alerta_sel,
        usuario=session["usuario"]
    )


# -------------------------

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
