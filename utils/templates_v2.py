import pandas as pd
from io import BytesIO

# =============================================================================
# ECOMETRICS - Generador de Plantillas de Datos
# =============================================================================
# NOTA TÉCNICA: NO usar @st.cache_data en ninguna función de este módulo.
# El caché de Streamlit causa que st.download_button genere archivos con
# nombres UUID (ej: 514fa453-f8fa-477c-...) en lugar del nombre especificado
# en file_name. Esto ocurre porque:
#   1. openpyxl incluye timestamps en la metadata del Excel
#   2. Cada rerun genera bytes DIFERENTES aunque los datos sean iguales
#   3. Streamlit no puede vincular el clic del botón con los bytes originales
# NOTA TÉCNICA: Se generan bytes nuevos en cada rerun para evitar
# que Streamlit pierda la referencia interna (Missing file) y envíe
# nombres de archivo UUID (ej: 514fa453-f8fa-477c-...) en st.download_button.
# =============================================================================


def create_pastos_template():
    """Plantilla para el módulo de Pastizales (Incidencia y Abundancia)."""
    data = {
        "Sitio": ["Parcela_01", "Parcela_01", "Parcela_02"],
        "Muestra": [1, 2, 1],
        "Especie": ["Paspalum notatum", "Cynodon dactylon", "Festuca arundinacea"],
        "Abundancia": [15, 8, 22],
        "Cobertura_%": [45, 20, 60],
        "Frecuencia": [1, 1, 1],
        "Observaciones": ["Zona norte", "Zona centro", "Ladera sur"]
    }
    return pd.DataFrame(data)


def create_forestry_template():
    """Plantilla para el módulo de Silvicultura (Inventario Forestal Real)."""
    data = {
        "Sitio": ["S1", "S1", "S2"],
        "Tamaño_Sitio_m2": [400, 400, 400],
        "Arbol_ID": [1, 2, 1],
        "Especie": ["Pinus durangensis", "Quercus sideroxyla", "Pinus arizonica"],
        "DAP_cm": [35.2, 28.5, 42.1],
        "Altura_m": [18.5, 12.0, 22.3],
        "Alt_Fuste_m": [12.0, 8.5, 15.2],
        "D_Copa_m": [4.5, 3.2, 5.1],
        "X": [254300, 254305, 254410],
        "Y": [2876100, 2876105, 2876200]
    }
    return pd.DataFrame(data)


def create_stats_wide_template():
    """Plantilla para Bioestadística Pro (Formato Ancho - v2)."""
    data = {
        "Sitio": ["Muestra_01", "Muestra_02", "Muestra_03", "Muestra_04"],
        "Nitrogeno_suelo": [1.2, 0.8, 1.5, 1.1],
        "Pendiente_grados": [15, 22, 10, 18],
        "Materia_Organica": [4.2, 3.8, 5.1, 4.5],
        "pH_suelo": [6.5, 6.2, 6.8, 6.4]
    }
    return pd.DataFrame(data)





def create_dca_template():
    """Diseño Completamente al Azar (Formato Ancho: Columnas = Tratamientos)."""
    return pd.DataFrame({
        "Repeticion": [1, 2, 3, 4],
        "Testigo": [10, 9, 11, 10],
        "Fert_A": [12, 13, 14, 12],
        "Fert_B": [11, 12, 13, 11]
    })


def create_dbca_template():
    """Diseño en Bloques (Formato Ancho: Columnas = Tratamientos, Filas = Bloques)."""
    return pd.DataFrame({
        "Bloque": ["Bloque_I", "Bloque_II", "Bloque_III"],
        "T1": [25, 26, 24],
        "T2": [30, 31, 29],
        "T3": [28, 29, 27]
    })


def create_latino_template():
    """Diseño en Cuadro Latino."""
    return pd.DataFrame({
        "Fila": [1, 1, 1, 2, 2, 2, 3, 3, 3],
        "Columna": [1, 2, 3, 1, 2, 3, 1, 2, 3],
        "Tratamiento": ["A", "B", "C", "B", "C", "A", "C", "A", "B"],
        "Respuesta": [50, 55, 60, 52, 58, 51, 62, 53, 59]
    })


def create_regression_template():
    """Regresión Lineal y Logística."""
    return pd.DataFrame({
        "Variable_Y": [10, 15, 20, 25, 30, 35, 40],
        "Factor_X1": [1, 2, 3, 4, 5, 6, 7],
        "Factor_X2": [0.5, 0.8, 1.2, 1.5, 2.0, 2.3, 2.8],
        "Presencia_Binaria": [0, 0, 1, 1, 1, 1, 1]
    })


def create_growth_template():
    """Modelos de Crecimiento."""
    return pd.DataFrame({
        "Edad_t": [10, 20, 30, 40, 50, 60, 70],
        "Volumen_V": [5, 25, 60, 110, 150, 180, 200]
    })


def create_advanced_community_template():
    """Matriz de Comunidad (NMDS/PERMANOVA)."""
    return pd.DataFrame({
        "Sitio": ["Bosque_A", "Bosque_A", "Bosque_B", "Bosque_B"],
        "Especie": ["Pinus", "Quercus", "Pinus", "Quercus"],
        "Abundancia": [50, 10, 5, 40]
    })


def get_template_download_link(df, filename):
    """Genera bytes de Excel frescos para st.download_button.
    
    Se genera de nuevo en cada rerun de Streamlit. Evitar cualquier
    tipo de caché aquí (ni @st.cache_data ni cachés Python)
    previene que Streamlit pierda la referencia interna y retorne UUIDs.
    """
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos')
    return buffer.getvalue()

def render_download_button(df, filename, label="⬇️ Descargar Plantilla"):
    """Wrapper nativo de st.download_button con mitigación del bug de UUIDs."""
    import streamlit as st
    
    st.download_button(
        label=label,
        data=get_template_download_link(df, filename),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key=f"dl_{filename}"
    )
