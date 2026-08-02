from flask import render_template, request, redirect, url_for, session, flash
from Utils import login_requerido
from Services import (get_total_productos, get_total_sucursales,
                      get_total_tickets, get_alertas_inventario,
                      get_productos, get_categorias, get_inventario)
from Models import productos, inventario, sucursales

USUARIOS = {
    "admin": "admin123",
    "gerente": "gerente123"
}

CATEGORIAS = ["Abarrotes", "Lácteos", "Carnes", "Frutas y Verduras",
              "Panadería", "Bebidas", "Limpieza", "Cuidado Personal"]

def register_routes(app):

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
            flash("Usuario o contraseña incorrectos.", "error")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_requerido
    def dashboard():
        return render_template("dashboard.html",
            total_productos=get_total_productos(),
            total_sucursales=get_total_sucursales(),
            total_tickets=get_total_tickets(),
            alertas_inventario=get_alertas_inventario(),
            usuario=session["usuario"]
        )

    @app.route("/productos")
    @login_requerido
    def lista_productos():
        busqueda  = request.args.get("q", "").strip()
        categoria = request.args.get("categoria", "").strip()
        return render_template("productos.html",
            productos=get_productos(busqueda, categoria),
            categorias=get_categorias(),
            busqueda=busqueda,
            categoria_sel=categoria,
            usuario=session["usuario"]
        )

    @app.route("/productos/nuevo", methods=["GET", "POST"])
    @login_requerido
    def producto_nuevo():
        if request.method == "POST":
            sku = request.form.get("sku", "").strip().upper()
            if productos.find_one({"sku": sku}):
                flash(f"El SKU {sku} ya existe.", "error")
                return render_template("producto_form.html",
                    categorias=CATEGORIAS, usuario=session["usuario"], producto=None)
            productos.insert_one({
                "sku":            sku,
                "nombre":         request.form.get("nombre", "").strip(),
                "categoria":      request.form.get("categoria", "").strip(),
                "perecedero":     request.form.get("perecedero") == "on",
                "precio_lista":   float(request.form.get("precio_lista", 0)),
                "costo_unitario": float(request.form.get("costo_unitario", 0)),
                "stock_minimo":   int(request.form.get("stock_minimo", 0)),
                "punto_reorden":  int(request.form.get("punto_reorden", 0)),
            })
            flash(f"Producto {sku} creado.", "ok")
            return redirect(url_for("lista_productos"))
        return render_template("producto_form.html",
            categorias=CATEGORIAS, usuario=session["usuario"], producto=None)

    @app.route("/productos/editar/<sku>", methods=["GET", "POST"])
    @login_requerido
    def producto_editar(sku):
        producto = productos.find_one({"sku": sku})
        if not producto:
            flash("Producto no encontrado.", "error")
            return redirect(url_for("lista_productos"))
        if request.method == "POST":
            productos.update_one({"sku": sku}, {"$set": {
                "nombre":         request.form.get("nombre", "").strip(),
                "categoria":      request.form.get("categoria", "").strip(),
                "perecedero":     request.form.get("perecedero") == "on",
                "precio_lista":   float(request.form.get("precio_lista", 0)),
                "costo_unitario": float(request.form.get("costo_unitario", 0)),
                "stock_minimo":   int(request.form.get("stock_minimo", 0)),
                "punto_reorden":  int(request.form.get("punto_reorden", 0)),
            }})
            flash(f"Producto {sku} actualizado.", "ok")
            return redirect(url_for("lista_productos"))
        return render_template("producto_form.html",
            categorias=CATEGORIAS, usuario=session["usuario"], producto=producto)

    @app.route("/productos/eliminar/<sku>", methods=["POST"])
    @login_requerido
    def producto_eliminar(sku):
        productos.delete_one({"sku": sku})
        flash(f"Producto {sku} eliminado.", "ok")
        return redirect(url_for("lista_productos"))

    @app.route("/inventario")
    @login_requerido
    def inventario_lista():
        sucursal_sel = request.args.get("sucursal", "").strip()
        alerta_sel   = request.args.get("alerta", "").strip()
        registros    = get_inventario(sucursal_sel, alerta_sel)
        skus = {p["sku"]: p["nombre"] for p in productos.find({}, {"sku":1,"nombre":1})}
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
            sucursales=sucursales.distinct("sucursal_id"),
            niveles=["Normal", "Alerta", "Critico", "Quiebre"],
            sucursal_sel=sucursal_sel,
            alerta_sel=alerta_sel,
            usuario=session["usuario"]
        )