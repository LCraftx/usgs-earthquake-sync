import requests
import duckdb
from datetime import datetime, timedelta, timezone

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

inicio = datetime.now(timezone.utc) - timedelta(days=7)

params = {
    "format": "geojson",
    "starttime": inicio.isoformat(),
    "minmagnitude": 4.5
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

datos = response.json()

#print("Total recibido:", len(datos["features"]))

def transformar_terremoto(evento):
    id_t = evento["id"]
    fecha = datetime.fromtimestamp(evento["properties"]["time"] / 1000, tz=timezone.utc)
    magnitud = evento["properties"]["mag"]
    profundidad = evento["geometry"]["coordinates"][2]
    lugar = evento["properties"]["place"]
    ultima_actualizacion = datetime.fromtimestamp(evento["properties"]["updated"] / 1000, tz=timezone.utc)

    return {
        "id": id_t,
        "fecha": fecha,
        "magnitud": magnitud,
        "profundidad": profundidad,
        "lugar": lugar,
        "ultima_actualizacion": ultima_actualizacion
    }

terremotos = []

for evento in datos["features"]:# [:3]: #Obtiene como máximo los primeros 3 terremotos
    terremotos.append(transformar_terremoto(evento))

print(terremotos)

#-----------------------------------------

con = duckdb.connect("terremotos.duckdb")

con.execute("""
CREATE TABLE IF NOT EXISTS terremotos (
    id VARCHAR PRIMARY KEY,
    fecha TIMESTAMPTZ,
    magnitud DOUBLE,
    profundidad DOUBLE,
    lugar VARCHAR,
    ultima_actualizacion TIMESTAMPTZ
);
""")

#con.sql("DESCRIBE terremotos").show()
insertados = 0
actualizados = 0
sin_cambios = 0
#---------------------------------------------
for terremoto in terremotos:

    resultado = con.execute(
        "SELECT id, ultima_actualizacion FROM terremotos WHERE id = ?",
        [terremoto["id"]]
    ).fetchone()

    con.complete()

    if resultado is None:
        con.execute(
            """INSERT INTO terremotos (id, fecha, magnitud, profundidad, lugar, ultima_actualizacion)
            VALUES (?, ?, ?, ?, ?, ?)""",
            [terremoto["id"], 
            terremoto["fecha"], 
            terremoto["magnitud"], 
            terremoto["profundidad"], 
            terremoto["lugar"], 
            terremoto["ultima_actualizacion"]]
        )
        insertados += 1
    else:
        if (resultado[1] < terremoto["ultima_actualizacion"]):
            con.execute(
                """
                UPDATE terremotos
                SET fecha = ?,
                    magnitud = ?,
                    profundidad = ?,
                    lugar = ?,
                    ultima_actualizacion = ?
                WHERE id = ?
                """,
                [terremoto["fecha"], 
                terremoto["magnitud"],
                terremoto["profundidad"],
                terremoto["lugar"],
                terremoto["ultima_actualizacion"],
                terremoto["id"]
                ]
            )
            actualizados += 1
        else:
            sin_cambios += 1
            print("Sin cambios")


Total = con.execute(
        "SELECT COUNT(*) FROM terremotos"
    ).fetchone()

con.complete()

print(f"Insertados: {insertados}, Actualizados: {actualizados}, Sin cambios: {sin_cambios}", f"Total en la base de datos: {Total[0]}")

con.close()