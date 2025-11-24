import os

import dask.dataframe as dd


# --------- CONFIGURACIÓN BÁSICA ---------

# Fichero que hemos generado antes
RUTA_ENTRADA = "data/ventas_logs.csv"

# Carpeta que hará de "bucket" de salida
RUTA_BUCKET_SALIDA = "output"           # piensa en "s3://mi-bucket/..." en producción
FICHERO_SALIDA_PARQUET = os.path.join(RUTA_BUCKET_SALIDA, "ventas_normalizadas.parquet")
FICHERO_STATS_SALIDA = os.path.join(RUTA_BUCKET_SALIDA, "stats_importe.csv")

# Tamaño lógico de partición (no exacto, pero orientativo)
BLOCKSIZE = "64MB"  # para la demo; en un caso real podría ser "256MB" o más


def main():
    os.makedirs(RUTA_BUCKET_SALIDA, exist_ok=True)

    # 1. Cargar el CSV con Dask en particiones
    print("Leyendo CSV con Dask...")
    df = dd.read_csv(
        RUTA_ENTRADA,
        blocksize=BLOCKSIZE,    # como si partiéramos el archivo en bloques
        assume_missing=True     # por si hay nulos
    )

    print(df.head())  # muestra unas pocas filas de ejemplo

    # 2. Cálculo de media y desviación típica (lazy hasta que hagamos compute())
    media = df["importe"].mean()
    std = df["importe"].std()

    print("Calculando media y desviación (compute)...")
    media_val = media.compute()
    std_val = std.compute()

    print(f"Media importe: {media_val:.4f}")
    print(f"Desviación importe: {std_val:.4f}")

    # Guardamos estas estadísticas como un CSV pequeño en el "bucket"
    import pandas as pd
    stats_df = pd.DataFrame([{
        "media_importe": media_val,
        "std_importe": std_val
    }])
    stats_df.to_csv(FICHERO_STATS_SALIDA, index=False)
    print(f"Estadísticas guardadas en: {FICHERO_STATS_SALIDA}")

    # 3. Normalización de la columna "importe"
    #    z = (x - media) / std
    print("Creando columna normalizada con Dask...")

    df_norm = df.assign(
        importe_norm=(df["importe"] - media_val) / std_val
    )

    # Ojo: todavía es lazy; aquí todavía no se ha procesado el fichero completo
    # 4. Escribir el resultado normalizado en Parquet (formato columnar)
    print("Escribiendo datos normalizados a Parquet (compute implícito)...")
    df_norm.to_parquet(
        FICHERO_SALIDA_PARQUET,
        engine="pyarrow",
        write_index=False
    )

    print(f"Fichero Parquet escrito en: {FICHERO_SALIDA_PARQUET}")

    # 5. Lectura de vuelta para verificar (opcional)
    print("Leyendo de nuevo el Parquet para verificar...")
    df_ver = dd.read_parquet(FICHERO_SALIDA_PARQUET)
    print(df_ver.head())


if __name__ == "__main__":
    main()

