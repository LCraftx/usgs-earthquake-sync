# USGS Earthquake Sync

Mini proyecto de Ingeniería de Datos que implementa un pipeline ETL para extraer, transformar y almacenar registros de terremotos desde la API pública de USGS utilizando Python y DuckDB.

## Tecnologías
- Python
- Requests
- DuckDB
- API REST de USGS

## Funcionalidades
- Extracción de terremotos de los últimos 7 días (magnitud ≥ 4.5).
- Transformación de datos JSON a registros estructurados.
- Almacenamiento persistente en DuckDB.
- Inserción de registros nuevos y actualización de los modificados.
- Prevención de duplicados mediante clave primaria.
- Resumen de registros insertados, actualizados y sin cambios.

## Instalación y ejecución

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Ejecutar el pipeline:

```bash
python main.py
```

La base de datos `terremotos.duckdb` se crea automáticamente.

## Fuente de datos
[USGS Earthquake API](https://earthquake.usgs.gov/fdsnws/event/1/)

## Estado
**Versión 1:** ETL funcional con sincronización por ID. Pendiente: carga incremental mediante `updatedafter` y optimización con `MERGE`.