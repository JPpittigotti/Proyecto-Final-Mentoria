# SuperGestión — Sistema Inteligente de Gestión para Cadena de Supermercados

Proyecto Final · Equipo de Desarrollo de Software  
Plataforma web para la gestión operativa de una cadena de supermercados, desarrollada como parte del proceso de transformación digital de la empresa.

---

## Descripción

SuperGestión es un MVP (Minimum Viable Product) que permite a la gerencia y al personal operativo gestionar productos e inventario en tiempo real, con información centralizada proveniente de todas las sucursales.

**Stack tecnológico:**
- **Backend:** Python · Flask
- **Frontend:** HTML5 · CSS3 (embebido en templates)
- **Base de datos:** MongoDB Atlas
- **Control de versiones:** Git · GitHub

---

## Módulos disponibles

| Módulo | Descripción |
|---|---|
| Login | Autenticación de usuarios por rol |
| Dashboard | Panel de resumen con indicadores generales |
| Productos | Gestión completa del catálogo (crear, editar, eliminar) |
| Inventario | Consulta de stock por sucursal y nivel de alerta |

---

## Estructura del proyecto

```
PROYECTO-FINAL-MENTORIA/
│
├── Models/
│   ├── __init__.py        ← exporta las colecciones
│   └── modelos.py         ← conexión a MongoDB y acceso a colecciones
│
├── Routes/
│   ├── __init__.py        ← exporta register_routes
│   └── rutas.py           ← definición de todas las rutas de la app
│
├── Services/
│   ├── __init__.py        ← exporta las funciones de servicio
│   └── servicios.py       ← lógica de consultas a MongoDB
│
├── Utils/
│   ├── __init__.py        ← exporta utilidades
│   └── utilidades.py      ← decorador login_requerido y helpers
│
├── templates/             ← páginas HTML (Jinja2)
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── productos.html
│   ├── producto_form.html
│   └── inventario.html
│
├── .env                   ← variables de entorno (no se sube a GitHub)
├── .gitignore
├── app.py                 ← punto de entrada de la aplicación
├── Config.py              ← carga de variables de entorno
└── requirements.txt       ← dependencias del proyecto
```

---

## Requisitos previos

- Python 3.10 o superior
- Git
- Cuenta en MongoDB Atlas (o MongoDB instalado localmente)

---

## Instalación

**1. Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/proyecto-final-mentoria.git
cd proyecto-final-mentoria
```

**2. Crear y activar el entorno virtual**
```bash
python -m venv venv
venv\Scripts\activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Configurar el archivo `.env`**

Crear un archivo llamado `.env` en la raíz del proyecto (importante: el punto es parte del nombre). Debe contener:

```
MONGO_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/
MONGO_DB=""
SECRET_KEY=""
```

> Si no tienes acceso a Atlas, puedes usar MongoDB local:
> `MONGO_URI=mongodb://localhost:27017/`

**5. Correr la aplicación**
```bash
python app.py
```

Abrir en el navegador: **http://localhost:5000**

---

## Usuarios de prueba

| Usuario | Contraseña |
|---|---|
| admin | admin123 |
| gerente | gerente123 |