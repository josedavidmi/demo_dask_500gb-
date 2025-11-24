import os
import numpy as np
import pandas as pd

# Parámetros de la demo
N_FILAS = 2_000_000       # cambia a 5M si el equipo aguanta
CHUNK_SIZE = 200_000      # filas por bloque de escritura
RUTA_SALIDA = "data/ventas_logs.csv"

def main():
    os.makedirs(os.path.dirname(RUTA_SALIDA), exist_ok=True)

    # Si existe, lo borramos para generar desde cero
    if os.path.exists(RUTA_SALIDA):
        os.remove(RUTA_SALIDA)

    num_chunks = N_FILAS // CHUNK_SIZE

    rng = np.random.default_rng(seed=42)

    for i in range(num_chunks):
        # Simulamos un pequeño log de ventas
        df = pd.DataFrame({
            "id_venta": np.arange(i*CHUNK_SIZE, (i+1)*CHUNK_SIZE),
            "usuario_id": rng.integers(1, 100_000, size=CHUNK_SIZE),
            "importe": rng.normal(loc=50, scale=20, size=CHUNK_SIZE).round(2),
            "pais": rng.choice(["ES", "DE", "FR", "IT"], size=CHUNK_SIZE),
        })

        # Escritura incremental en CSV
        modo = "w" if i == 0 else "a"
        header = i == 0
        df.to_csv(RUTA_SALIDA, mode=modo, header=header, index=False)

        print(f"Chunk {i+1}/{num_chunks} escrito")

    print(f"Fichero generado en: {RUTA_SALIDA}")

if __name__ == "__main__":
    main()

