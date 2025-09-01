![image](https://github.com/user-attachments/assets/8424e792-07b9-4045-a541-9abd711381a6)


<h1>Creando una app para dar seguimiento vender carro y partes!</h1>



# Sam

Aplicación Django para dar seguimiento a la venta de autos y partes

## Descripción
"Sam" es una plataforma desarrollada en Django que permite registrar, gestionar y hacer seguimiento de ventas de automóviles y sus partes. Provee paneles de administración y vistas públicas para facilitar procesos de venta y control de inventario.

## Características
- Gestión de autos: creación, edición, eliminación, detalle.
- Gestión de partes: asociadas a modelos específicos, con control de stock.
- Procesamiento de ventas: registrar transacciones, generar recibos y reportes.
- Dashboard administrativo: vistas intuitivas para visualizar inventario y estadísticas de ventas.
- Posible integración con pasarelas de pago (basado en módulos como `d_payments`).
- Frontend responsivo utilizando CSS, SCSS y JavaScript (según lo presente en el repositorio).

## Tecnologías utilizadas
- **Back-end**: Django (⚙ Python)
- **Front-end**: HTML, CSS, SCSS, JavaScript
- **Estructura**: carpetas como `core`, `d_account`, `d_payments`, `d_store`, `templates`, `static`, `sass`
- **Dependencias**: encontradas en `requirements.txt`; el archivo `package.json` y `package-lock.json` apuntan a herramientas del frontend.
- **Despliegue**: posible configuración con Railway (`railway.json`).

## Instalación y configuración
1. Clonar el repositorio:
   ```bash
   git clone https://github.com/lorf543/Sam.git
   cd Sam



   python -m venv env
source env/bin/activate  # en Windows: env\Scripts\activate
pip install -r requirements.txt


python manage.py migrate

npm install


python manage.py runserver

