import pandas as pd
from io import BytesIO
import os

def test_template():
    data = {
        "Sitio": ["Rancho_Ejemplo"],
        "Muestra": [1],
        "Especie": ["Paspalum notatum"],
        "Abundancia": [15]
    }
    df = pd.DataFrame(data)
    
    # Pruebo el método actual
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    
    content = buffer.getvalue()
    
    with open("test_output.xlsx", "wb") as f:
        f.write(content)
    
    print(f"Archivo de prueba generado. Tamaño: {len(content)} bytes")
    # Intentar leerlo de vuelta
    try:
        df_read = pd.read_excel("test_output.xlsx")
        print("Lectura exitosa!")
        print(df_read)
    except Exception as e:
        print(f"Error al leer el archivo!: {e}")

if __name__ == "__main__":
    test_template()
