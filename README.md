# Proyecto Bobeda - Sistema de Análisis de Libros

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Django](https://img.shields.io/badge/Django-4.2-brightgreen)
![Pandas](https://img.shields.io/badge/Pandas-1.5%2B-orange)
![Seaborn](https://img.shields.io/badge/Seaborn-0.12%2B-yellow)

Sistema para análisis y recomendación de libros con integración a base de datos PostgreSQL y generación de reportes automatizados.

## Características Principales

- **Análisis de Géneros**: Identifica el género más valorado y promedios por categoría
- **Sistema de Recomendaciones**: Top 3 libros global y por género específico
- **Reportes Automatizados**:
  - 📊 PDF profesional con gráficos y tablas
  - 📝 Excel estructurado con múltiples hojas
- **API RESTful**: Integración con Django REST Framework
- **Autenticación JWT**: Seguridad con tokens de acceso

## Tecnologías Utilizadas

| Tecnología       | Uso                          |
|------------------|------------------------------|
| Python 3.11      | Lógica principal del sistema |
| Django + DRF     | Backend API                  |
| PostgreSQL       | Base de datos principal      |
| Pandas           | Análisis de datos            |
| Matplotlib/Seaborn | Visualizaciones            |
| ReportLab        | Generación de PDFs           |
| OpenPyXL         | Generación de Excel          |

## Instalación

1. **Clonar repositorio**:
  
   git clone https://github.com/tu-usuario/bobeda.git

   cd bobeda

3. **Configurar entorno virtual**:

    python -m venv venv
   
    venv\Scripts\activate    # Windows

4. **Instalar dependencias**:

    pip install -r requirements.txt

5. **Configurar base de datos**:

   1. Exportar BD desde pgAdmin (Para administradores)
        Abre pgAdmin y haz clic derecho en tu BD

        Selecciona Backup...

        Guarda como BOBEDA/database/bobeda:_db_backup.sql

    2. Restaurar BD (Para nuevos desarrolladores)

    # Crear base de datos
        createdb -U postgres bobeda_dev

    # Restaurar backup
        psql -U postgres -d bobeda_dev < database/bobeda_backup.sql

    3. Configurar variables de entorno
        Crea un archivo .env en la raíz del proyecto:


    # PostgreSQL
        DB_NAME=bobeda_db
        DB_USER=postgres
        DB_PASSWORD=tu_contraseña
        DB_HOST=localhost
        DB_PORT=5432

    # Django
        SECRET_KEY=tu-secret-key-unica
        DEBUG=True

    # Aplicar migraciones
        python manage.py migrate

6. **Iniciar servidor**
python manage.py runserver
Accede al sistema en: http://localhost:8000

**Comandos Útilies**
    # Crear superusuario
python manage.py createsuperuser
    # Crear reporte
python analisis_libros.py

**Como usar el generador de reportes**
 * Crear reporte
    python analisis_libros.py
    
* Seleccionar opciones del menú:

    Opción 1: Análisis completo de todos los libros

    Opción 2: Análisis específico por género

    Opción 3: Salir

* Resultados generados:

    Reporte en consola con los análisis

    PDF profesional en la carpeta reportes/

    Gráficos y tablas listos para presentación

**Estructura general**

BOBEDA/

├── accounts/

│   ├── __pycache__/

│   ├── migrations/

│   ├── __init__.py

│   ├── admin.py

│   ├── apps.py

│   ├── models.py

│   ├── serializers.py

│   ├── tests.py

│   ├── urls.py

│   └── views.py

├── bobeda/

│   ├── __pycache__/

│   ├── __init__.py

│   ├── asgi.py

│   ├── settings.py

│   ├── urls.py

│   └── wsgi.py

├── libros/

│   ├── __pycache__/

│   ├── migrations/

│   ├── __init__.py


│   ├── admin.py

│   ├── apps.py

│   ├── models.py

│   ├── serializers.py

│   ├── tests.py

│   ├── urls.py

│   └── views.py

├── reporters/ (vacío)

├── venv/

├── analisis_libros.py

├── LICENSE

├── manage.py

├── READML.md

└── requirements.txt

## Licencia  
Bobeda se distribuye bajo una licencia de uso **exclusivamente educativo y no comercial**.  
Consulta el archivo [LICENSE.md] para más detalles.  

**Creado por Nathaly Sabrina Coronel Benítez**  
