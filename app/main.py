import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# --- AJUSTE DE PATH PARA MODULOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from modules.forestry_engine import ForestryEngine
from modules.bio_engine import BiodiversityEngine
from modules.stats_pro_v2 import StatsProEngine, ExperimentalEngine, AdvancedStatsEngine
from modules import interpretation_v3 as nlg
from utils import templates_v2 as templates
import modules.forestry_engine as forestry_engine
import modules.bio_engine as bio_engine
import modules.stats_pro_v2 as stats_pro
import modules.interpretation_v3 as nlg_module
# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="ECOMETRICS | Suite Bioestadística para Monitoreo Ecológico",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILO VISUAL PREMIUM "NATURE" ---
st.markdown("""
<style>
    /* Tipografía y Colores Base */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Outfit:wght@300;600&display=swap');
    
    .main {
        background-color: #f0f4f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Encabezados */
    h1, h2, h3 {
        color: #1b5e20;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e6e0;
    }
    
    /* Botones Premium */
    .stButton>button {
        background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.3);
        background: linear-gradient(135deg, #388e3c 0%, #2e7d32 100%);
    }
    
    /* Tarjetas (Cards) */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #2e7d32;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    
    /* Footer Premium (Estilo CHANNEL) */
    .footer {
        background-color: #ffffff;
        padding: 4rem 2rem;
        margin-top: 5rem;
        border-top: 1px solid #e0e6e0;
        font-family: 'Inter', sans-serif;
    }
    .footer-content {
        max-width: 1200px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1.5fr 1fr 1fr;
        gap: 3rem;
        text-align: left;
    }
    .footer-col h4 {
        color: #1b5e20;
        margin-bottom: 1.2rem;
        font-size: 1.1rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .footer-col p {
        color: #555;
        line-height: 1.6;
        font-size: 0.9rem;
    }
    .footer-links {
        list-style: none;
        padding: 0;
    }
    .footer-links li {
        margin-bottom: 0.8rem;
    }
    .footer-links a {
        color: #2e7d32;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.2s;
    }
    .footer-links a:hover {
        color: #1b5e20;
        text-decoration: underline;
    }
    .footer-bottom {
        text-align: center;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #f0f0f0;
        color: #888;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.image("https://img.icons8.com/flat-round/200/leaf.png", width=100)
    st.title("ECOMETRICS")
    st.markdown("*Inteligencia Ecológica y Monitoreo de Biodiversidad*")
    
    st.divider()
    
    menu = st.radio(
        "Navegación del Ecosistema",
        [
            "🏠 Dashboard Principal",
            "🌿 Evaluación de muestreo",
            "📊 Comparación (Hutcheson)",
            "🌲 Silvicultura e Inventarios",
            "🔬 Evaluación de variables",
            "🧪 Diseño Experimental",
            "📈 Modelos y Regresón",
            "🧩 PCA y NMDS",
            "📖 Acerca de ECOMETRICS",
            "⚠️ Aviso Legal"
        ]
    )
    
    st.divider()
    st.info("💡 **Dato Pro**: Utiliza las plantillas oficiales para asegurar que los factores de expansión y modelos biométricos se apliquen correctamente.")

# --- LOGICA DE PÁGINAS ---

# 1. DASHBOARD PRINCIPAL
if menu == "🏠 Dashboard Principal":
    st.title("🌿 Bienvenida a ECOMETRICS")
    st.write("Selecciona un módulo en la barra lateral para comenzar tus análisis bioestadísticos.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Precisión Estadística**\n\nImplementación rigurosa de iNEXT y modelos asintóticos.")
    with col2:
        st.success("🌲 **Gestión Forestal**\n\nAnálisis de inventarios de campo y proyecciones de crecimiento.")
    with col3:
        st.warning("🔬 **Bioestadística Pro**\n\nCorrelaciones, ordenación y análisis de comunidades.")

# 2. BIODIVERSIDAD Y CURVAS DE ACUMULACIÓN
elif menu == "🌿 Biodiversidad y Curvas":
    st.header("🌿 Biodiversidad y Curvas de Acumulación")
    
    with st.expander("ℹ️ Guía del Módulo: ¿Qué datos subir y qué obtendrás?", expanded=True):
        st.markdown("""
        ### 📊 ¿Para qué sirve esta sección?
        Este módulo automatiza el análisis de la **riqueza de especies** y la **completitud del muestreo**. Su objetivo es determinar si el esfuerzo de campo fue suficiente para representar la biodiversidad real del sitio.
        
        ### 📥 Datos de Entrada
        Puedes subir archivos en formato **Excel (.xlsx)** o **CSV**:
        *   **Formato Largo (Recomendado)**: Una tabla con columnas para `Sitio`, `Especie` y `Abundancia` (o incidencia).
        *   **Plantilla**: Utiliza la plantilla de ejemplo a la derecha para asegurar la compatibilidad.
        
        ### 📉 Resultados (Salida)
        1. **Curva iNEXT**: Visualiza la rarefacción (lo observado) y la extrapolación (lo que falta por encontrar).
        2. **Estimadores Asintóticos (Chao1)**: Cálculo de la riqueza máxima teórica.
        3. **Índices de Diversidad**: Shannon (H'), Simpson (D), Equitatividad (J') y más.
        4. **Prueba de Hutcheson**: Comparación técnica de la diversidad entre múltiples sitios.
        """)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("📂 Gestión de Datos")
        
        # Botón de Plantilla (JS Blob - bypass de bug Streamlit UUID filenames)
        pastos_template = templates.create_pastos_template()
        templates.render_download_button(pastos_template, "plantilla_pastos_ecometrics.xlsx", "⬇️ Descargar Plantilla de Ejemplo")
        
        uploaded_file = st.file_uploader("Sube tu archivo (Excel o CSV)", type=["xlsx", "csv"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.success("¡Datos cargados con éxito!")
                st.dataframe(df.head(), use_container_width=True)
                
                # Identificación de columnas (Busca Sitio, Especie, Abundancia)
                cols = df.columns.tolist()
                s_col = st.selectbox("Columna de Sitio/Parcela", cols, index=cols.index("Sitio") if "Sitio" in cols else 0)
                sp_col = st.selectbox("Columna de Especies", cols, index=cols.index("Especie") if "Especie" in cols else 0)
                ab_col = st.selectbox("Columna de Abundancia", cols, index=cols.index("Abundancia") if "Abundancia" in cols else 0)
                
                # AGRUPACIÓN DE DATOS (FIX)
                df_grouped = df.groupby(sp_col)[ab_col].sum().reset_index()
                abundances = df_grouped[ab_col].values
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
                abundances = None
        else:
            abundances = None
    
    with col1:
        st.subheader("📊 Visualización de Resultados")
        curve_type_mode = st.radio("Tipo de Análisis", ["Abundancia (Individuos)", "Incidencia (Sitios/Parcelas)"], horizontal=True)
        
        if abundances is not None:
            with st.spinner("Procesando modelos de rarefacción y extrapolación..."):
                if "Abundancia" in curve_type_mode:
                    curve_data = BiodiversityEngine.get_inext_curve(abundances, is_incidence=False)
                else:
                    # Preparar datos de incidencia [T, y1, y2, ...]
                    T = df[s_col].nunique()
                    y = df.groupby(sp_col)[s_col].nunique().values
                    incidence_data = [T] + y.tolist()
                    curve_data = BiodiversityEngine.get_inext_curve(incidence_data, is_incidence=True)
                
                fig = px.line(
                    curve_data, x="m", y="s", color="type",
                    title=f"Curva de Acumulación ({curve_type_mode})",
                    labels={"m": "Esfuerzo (Sitios)" if "Incidencia" in curve_type_mode else "Esfuerzo (Individuos)", "s": "Riqueza Estimada", "type": "Estado"},
                    color_discrete_map={"Rarefacción": "#2e7d32", "Extrapolación": "#fbc02d"}
                )
                fig.update_layout(template="simple_white", hovermode="x unified")
                st.plotly_chart(fig, use_container_width=True)
                
                # Resumen Métrico
                st.subheader("🧠 Interpretación Científica")
                s_obs = np.sum(abundances > 0)
                chao1 = BiodiversityEngine.chao1_estimator(abundances)
                coverage = (s_obs / chao1) * 100 if chao1 > 0 else 0
                
                # Calcular catálogo completo
                all_indices = BiodiversityEngine.calculate_all_indices(abundances)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("S. Observada", s_obs)
                m2.metric("Chao1 (Asintótico)", f"{chao1:.2f}")
                m3.metric("Cobertura", f"{coverage:.1f}%")
                
                with st.expander("🔬 Catálogo Completo de Índices", expanded=True):
                    i_col1, i_col2 = st.columns(2)
                    with i_col1:
                        st.write(f"**Shannon (H'):** {all_indices['Shannon_H']:.3f}")
                        st.write(f"**Simpson (D):** {all_indices['Simpson_D']:.3f}")
                        st.write(f"**Simpson Inv (1/D):** {all_indices['Simpson_Inv']:.3f}")
                        st.write(f"**Equitatividad (Pielou J'):** {all_indices['Pielou_J']:.3f}")
                    with i_col2:
                        st.write(f"**Margalef (Riqueza):** {all_indices['Margalef']:.3f}")
                        st.write(f"**Menhinick:** {all_indices['Menhinick']:.3f}")
                        st.write(f"**Brillouin:** {all_indices['Brillouin']:.3f}")
                        st.write(f"**Berger-Parker:** {all_indices['Berger_Parker']:.3f}")
                
                # Carga de Interpretación Detallada (NUEVO)
                detalled_report = nlg.interpret_inext_metrics(s_obs, chao1, coverage)
                
                with st.expander("📖 Ver Análisis Científico Detallado"):
                    with st.chat_message("assistant", avatar="🧠"):
                        st.write("### 🤖 Análisis de Diversidad iNEXT")
                        st.markdown(detalled_report)
                
                # --- NUEVO: BETA DIVERSIDAD ---
                st.divider()
                st.subheader("🌐 Beta Diversidad (Multisitio)")
                if uploaded_file and "Sitio" in df.columns:
                    comm_matrix = df.pivot_table(index=s_col, columns=sp_col, values=ab_col, fill_value=0)
                    if len(comm_matrix) > 1:
                        beta_res = BiodiversityEngine.calculate_beta_diversity(comm_matrix)
                        st.write(f"**Disimilitud Media (Bray-Curtis):** {beta_res['Media_Bray']:.3f}")
                        st.write(f"**Disimilitud Media (Sorensen):** {beta_res['Media_Sorensen']:.3f}")
                        
                        b_col1, b_col2 = st.columns(2)
                        with b_col1:
                            st.write("Matriz de Distancia (Bray-Curtis)")
                            st.dataframe(beta_res['Bray_Matrix'], use_container_width=True)
                        with b_col2:
                            fig_beta = px.imshow(beta_res['Bray_Matrix'], title="Heatmap de Disimilitud", color_continuous_scale="Viridis")
                            st.plotly_chart(fig_beta, use_container_width=True)
                    else:
                        st.info("Se requieren al menos 2 sitios para calcular Beta Diversidad.")
        else:
            st.info("Por favor, descarga la plantilla de la derecha o sube tus propios datos para iniciar el análisis.")
            st.image("https://img.icons8.com/stickers/200/line-chart.png", width=150)

# 2.5 COMPARACIÓN DE DIVERSIDAD (HUTCHESON)
elif menu == "📊 Comparación (Hutcheson)":
    st.header("🦉 Comparación de Diversidad (Hutcheson t-test)")
    st.markdown("""
    Esta prueba estadística permite determinar si la diversidad de Shannon ($H'$) entre comunidades es significativamente diferente, 
    considerando tanto el índice como el tamaño de la muestra y la riqueza observada.
    """)
    
    # Layout de carga de archivos y configuración dentro del área principal
    c_up, c_cfg = st.columns([2, 1])
    
    with c_up:
        with st.container(border=True):
            st.subheader("📂 Carga de Datos")
            h_file = st.file_uploader("Sube tu archivo para Hutcheson (Formato: Sitio, Especie, Abundancia)", type=["xlsx", "csv"], key="h_file_up")
    
    with c_cfg:
        with st.container(border=True):
            st.subheader("🔬 Configuración")
            st.info("💡 **Dato Pro**: La prueba de Hutcheson utiliza la aproximación clásica del índice de Shannon para comparar la diversidad entre comunidades.")
    
    st.divider()

    # Usar columnas más amplias para el contenido principal
    main_col, side_info = st.columns([1, 0.01]) # side_info ya no se usa tanto
    
    with main_col:
        if h_file:
            try:
                if h_file.name.endswith('.csv'): h_df = pd.read_csv(h_file)
                else: h_df = pd.read_excel(h_file)
                
                st.success("¡Datos cargados para comparación!")
                
                # Selectores de columnas
                h_cols = h_df.columns.tolist()
                h_s_col = st.selectbox("Columna de Sitio", h_cols, index=h_cols.index("Sitio") if "Sitio" in h_cols else 0, key="h_s")
                h_sp_col = st.selectbox("Columna de Especie", h_cols, index=h_cols.index("Especie") if "H_Especie" in h_cols else 0, key="h_sp")
                h_ab_col = st.selectbox("Columna de Abundancia", h_cols, index=h_cols.index("Abundancia") if "H_Abundancia" in h_cols else 0, key="h_ab")
            
                # Generar matriz
                h_comm_matrix = h_df.pivot_table(index=h_s_col, columns=h_sp_col, values=h_ab_col, fill_value=0)
                
                if len(h_comm_matrix) >= 2:
                    with st.spinner("Calculando comparaciones de Hutcheson..."):
                        sites = h_comm_matrix.index.tolist()
                        n_sites = len(sites)
                        
                        site_metrics = {}
                        for s in sites:
                            ab = h_comm_matrix.loc[s].values
                            site_metrics[s] = BiodiversityEngine.calculate_all_indices(ab)
                        
                        p_matrix = pd.DataFrame(index=sites, columns=sites, dtype=float)
                        significant_pairs = []
                        
                        for i in range(n_sites):
                            for j in range(i + 1, n_sites):
                                s1, s2 = sites[i], sites[j]
                                m1, m2 = site_metrics[s1], site_metrics[s2]

                                try:
                                    t, p, dfv = ExperimentalEngine.run_hutcheson_t_test(
                                        m1['Shannon_H'], m1['N_total'],
                                        m2['Shannon_H'], m2['N_total'],
                                        m1['S_obs'], m2['S_obs']
                                    )
                                    p_matrix.loc[s1, s2] = p
                                    p_matrix.loc[s2, s1] = p
                                    
                                    if p < 0.05:
                                        winner = s1 if m1['Shannon_H'] > m2['Shannon_H'] else s2
                                        significant_pairs.append({
                                            "Comparación": f"{s1} vs {s2}",
                                            "p-valor": f"{p:.4f}",
                                            "Sitio más Diverso": winner,
                                            "Diferencia H'": f"{abs(m1['Shannon_H'] - m2['Shannon_H']):.3f}",
                                            "Metodología": "Hutcheson (Expansión Taylor)"
                                        })
                                except:
                                    p_matrix.loc[s1, s2] = np.nan
                        
                        st.subheader("📊 Resultados de Comparación Multisitio")
                        fig_hutch = px.imshow(
                            p_matrix, 
                            title="Matriz de p-valores (Hutcheson T-Test)",
                            color_continuous_scale="RdYlGn_r",
                            range_color=[0, 0.1],
                            labels=dict(color="p-valor")
                        )
                        st.plotly_chart(fig_hutch, use_container_width=True)
                        
                        if significant_pairs:
                            st.success(f"✨ Se detectaron {len(significant_pairs)} pares con diferencias significativas.")
                            st.dataframe(pd.DataFrame(significant_pairs), use_container_width=True)
                        else:
                            st.info("No se encontraron diferencias significativas entre los sitios (p > 0.05).")
                else:
                    st.warning("Se necesitan al menos 2 sitios para comparar.")
                
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")
    
        else:
            st.divider()
            st.subheader("⌨️ Entrada Manual Multisitio")
            st.info("Indica el número de sitios y rellena sus valores de biodiversidad para compararlos entre sí.")
            
            num_m = st.number_input("Número de Sitios a Comparar", min_value=2, max_value=1000, value=2, step=1)
            
            # Crear DataFrame inicial para el editor
            cols_manual = ["Sitio", "Shannon_H", "N_total", "S_obs"]
            
            df_init_manual = pd.DataFrame({
                "Sitio": [f"Sitio {chr(65+i) if i < 26 else i+1}" for i in range(num_m)],
                "Shannon_H": [1.5] * num_m,
                "N_total": [100] * num_m,
                "S_obs": [10] * num_m
            })
            
            st.write("📝 **Editor de Datos (Manual)**")
            edited_df = st.data_editor(
                df_init_manual, 
                num_rows="dynamic", 
                use_container_width=True,
                column_config={
                    "Shannon_H": st.column_config.NumberColumn("Shannon H'", help="Índice de Shannon (H')", format="%.3f"),
                    "N_total": st.column_config.NumberColumn("Individuos (N)", help="Suma total de individuos"),
                    "S_obs": st.column_config.NumberColumn("Especies (S)", help="Riqueza observada de especies")
                }
            )
            
            if st.button("🚀 Ejecutar Comparación Shannon (Manual)"):
                try:
                    # Filtrar filas vacías o con errores si las hay
                    clean_df = edited_df.dropna()
                    n_m = len(clean_df)
                    
                    if n_m < 2:
                        st.warning("Se necesitan al menos 2 sitios con datos válidos.")
                    else:
                        with st.spinner("Procesando comparaciones masivas..."):
                            sites_m = clean_df["Sitio"].tolist()
                            p_matrix_m = pd.DataFrame(1.0, index=sites_m, columns=sites_m, dtype=float)
                            sig_pairs_m = []
                            
                            rows = clean_df.to_dict('records')
                            
                            for i in range(n_m):
                                for j in range(i + 1, n_m):
                                    s1, s2 = rows[i], rows[j]
                                    
                                    try:
                                        t, p, dfv = ExperimentalEngine.run_hutcheson_t_test(
                                            s1['Shannon_H'], s1['N_total'], 
                                            s2['Shannon_H'], s2['N_total'], 
                                            s1['S_obs'], s2['S_obs']
                                        )
                                        p_matrix_m.loc[s1['Sitio'], s2['Sitio']] = p
                                        p_matrix_m.loc[s2['Sitio'], s1['Sitio']] = p
                                        
                                        if p < 0.05:
                                            # Indicar el ganador
                                            winner = s1['Sitio'] if s1['Shannon_H'] > s2['Shannon_H'] else s2['Sitio']
                                            
                                            sig_pairs_m.append({
                                                "Comparación": f"{s1['Sitio']} vs {s2['Sitio']}",
                                                "p-valor": f"{p:.4f}",
                                                "Más Diverso": winner,
                                                "Dif H'": f"{abs(s1['Shannon_H'] - s2['Shannon_H']):.3f}",
                                                "Metodología": "Hutcheson Standard"
                                            })
                                    except:
                                        p_matrix_m.loc[s1['Sitio'], s2['Sitio']] = np.nan
                            
                            st.divider()
                            st.subheader("📊 Resultados de Comparación (Taylor Approximation)")
                            
                            fig_m = px.imshow(
                                p_matrix_m, 
                                title="📊 Matriz Probabilística de Similitud (p-valores)",
                                color_continuous_scale="RdYlGn_r",
                                range_color=[0, 0.05],
                                text_auto=".4f",
                                labels=dict(color="p-valor")
                            )
                            fig_m.update_traces(hovertemplate="Sitio: %{x}<br>vs Sitio: %{y}<br>p-valor: %{z:.4f}")
                            st.plotly_chart(fig_m, use_container_width=True)
                            
                            if sig_pairs_m:
                                st.success(f"✨ Diferencias significativas en {len(sig_pairs_m)} comparaciones.")
                                st.dataframe(pd.DataFrame(sig_pairs_m), use_container_width=True)
                            else:
                                st.info("🔍 **Resultado**: No hay diferencias significativas (p > 0.05) entre los sitios evaluados.")
                                if n_m == 2:
                                    pval_final = p_matrix_m.iloc[0,1]
                                    st.write("---")
                                    m_col1, m_col2 = st.columns(2)
                                    with m_col1:
                                        status_p = "Indistinguibles" if pval_final > 0.05 else "Diferentes"
                                        st.metric("p-valor (Hutcheson)", f"{pval_final:.4f}", help="Probabilidad de que la diferencia sea debida al azar.")
                                    with m_col2:
                                        if pval_final < 0.05:
                                            st.success(f"Diferencia Significativa: {status_p}")
                                        else:
                                            st.warning(f"Diferencia No Significativa: {status_p}")
                except Exception as ex:
                    st.error(f"Error en el cálculo: {ex}")

# 3. SILVICULTURA E INVENTARIOS
elif menu == "🌲 Silvicultura e Inventarios":
    st.header("🌲 Silvicultura e Inventarios Forestales")
    st.markdown("*Cálculo de existencia real, factores de expansión y modelos biométricos.*")
    
    # LAYOUT EXPANDIDO
    col_input, col_results = st.columns([1, 2.5])
    
    with col_input:
        st.subheader("📦 Gestión de Inventario")
        st.write("Configuración de DAP y Altura.")
        
        from utils import templates_v2 as templates
        forestry_template = templates.create_forestry_template()
        templates.render_download_button(forestry_template, "plantilla_forestal_ecometrics.xlsx", "📄 Plantilla de Inventario")
        
        f_file = st.file_uploader("Subir Inventarios", type=["xlsx", "csv"], key="f_up")
        f_df = None
        if f_file:
            try:
                if f_file.name.endswith('.csv'): 
                    f_df = pd.read_csv(f_file)
                else: 
                    xl = pd.ExcelFile(f_file)
                    sheets = xl.sheet_names
                    if len(sheets) > 1:
                        sel_sheet = st.selectbox("Seleccionar Hoja de Excel", sheets, help="El archivo tiene múltiples pestañas.")
                    else:
                        sel_sheet = sheets[0]
                    f_df = pd.read_excel(f_file, sheet_name=sel_sheet)
                
                # Selectors agrupados para ahorrar espacio vertical
                f_cols = f_df.columns.tolist()
                s_col = st.selectbox("Sitio/Parcela", f_cols, index=f_cols.index("Sitio") if "Sitio" in f_cols else 0)
                
                # Flexibilidad en el tamaño del sitio
                size_options = f_cols + ["Escribir Tamaño Manual"]
                size_col = st.selectbox("Tamaño (m2)", size_options, index=f_cols.index("Tamaño_Sitio_m2") if "Tamaño_Sitio_m2" in f_cols else 0)
                
                manual_size = None
                if size_col == "Escribir Tamaño Manual":
                    manual_size = st.number_input("Ingresar Área del Sitio (m2)", min_value=1.0, value=1000.0, step=10.0)
                
                dap_col = st.selectbox("DAP (cm)", f_cols, index=f_cols.index("DAP_cm") if "DAP_cm" in f_cols else 0)
                alt_col = st.selectbox("Altura (m)", f_cols, index=f_cols.index("Altura_m") if "Altura_m" in f_cols else 0)
                sp_col = st.selectbox("Especie", f_cols, index=f_cols.index("Especie") if "Especie" in f_cols else 0)
                
                run_forest = st.button("🚀 Ejecutar Análisis", key="run_forest", use_container_width=True)
            except Exception as e:
                st.error(f"Error al leer archivo: {e}")

    with col_results:
        # Usar session_state para mantener los resultados visibles tras el click
        if "f_results" not in st.session_state: st.session_state["f_results"] = None
        
        if f_df is not None:
            if run_forest or st.session_state["f_results"] is not None:
                try:
                    # Preparar tamaño si es manual
                    if size_col == "Escribir Tamaño Manual":
                        f_df["_t_manual"] = manual_size
                        target_size_col = "_t_manual"
                    else:
                        target_size_col = size_col

                    # Limpieza de columnas previas para evitar "Duplicate Columns"
                    clean_df = f_df.copy()
                    cols_to_drop = ['FE', 'G_ha', 'V_ha', 'B_ha_ton', 'C_ha_ton', 'CO2e_ha', 'Esbeltez', 'G_m2', 'V_m3']
                    clean_df = clean_df.drop(columns=[c for c in cols_to_drop if c in clean_df.columns])

                    # --- AUDITORÍA DE DATOS ---
                    with st.expander("🔍 Auditoría de Datos Detectados", expanded=True):
                        total_t = len(clean_df)
                        unique_s = clean_df[s_col].nunique()
                        avg_size = clean_df[target_size_col].mean()
                        
                        aud1, aud2, aud3 = st.columns(3)
                        aud1.metric("Árboles en Excel", total_t)
                        aud2.metric("Sitios/Parcelas", unique_s)
                        aud3.metric("Área Prom. (m2)", f"{avg_size:.1f}")
                        
                        if total_t > 5000:
                            st.warning("⚠️ El archivo tiene muchos registros. Verifica que no haya duplicados.")

                    # Selector de Rigor Científico y Crecimiento
                    use_scientific = st.toggle("Aplicar Modelos Vargas-Larreta/Cruz-Cobos", value=True, help="Si se desactiva, usará modelos genéricos internacionales.")
                    t_paso = st.slider("Tiempo de Paso (años)", 5, 20, 10, help="Vigencia del programa de manejo o intervalo de retorno.")
                    
                    # Ejecutar cálculos
                    results = ForestryEngine.expand_metrics(
                        clean_df, 
                        dap_col=dap_col, 
                        height_col=alt_col, 
                        species_col=sp_col, 
                        plot_area_col=target_size_col, 
                        use_scientific=use_scientific
                    )
                    
                    # 1. Agrupar por Sitio y sumar valores de árboles para obtener totales por parcela
                    site_summaries = results.groupby(s_col).agg({
                        'N_ha': 'sum',
                        'G_ha': 'sum',
                        'V_ha': 'sum',
                        'B_ha_ton': 'sum',
                        'C_ha_ton': 'sum'
                    })
                    
                    # 2. Obtener el promedio del Rodal
                    stand_avg = site_summaries.mean()
                    ica_val = ForestryEngine.calculate_annual_increment(stand_avg['V_ha'], t_paso)
                    
                    # --- CÁLCULOS ADICIONALES (REINEKE, COBERTURA, RATING) ---
                    dcq_val = ForestryEngine.calculate_dcq(stand_avg['G_ha'], stand_avg['N_ha'])
                    reineke_sdi = ForestryEngine.calculate_reineke_sdi(stand_avg['N_ha'], dcq_val)
                    canopy_cover = ForestryEngine.calculate_canopy_cover(results, avg_size, dap_col=dap_col)
                    stand_rating = ForestryEngine.calculate_stand_rating(reineke_sdi)

                    st.divider()
                    
                    # --- SISTEMA DE PESTAÑAS (TABS) ---
                    tab_bio, tab_ivi, tab_div, tab_growth = st.tabs([
                        "📊 Biometría", 
                        "💎 IVI", 
                        "🌿 Diversidad", 
                        "📈 Proyecciones"
                    ])

                    # TAB 1: BIOMETRÍA Y EXISTENCIAS
                    with tab_bio:
                        st.subheader("📊 Resultados de Existencias y Densidad")
                        
                        # Fila 1: Stock Principal
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Existencias (m³/ha)", f"{stand_avg['V_ha']:.2f}")
                        c2.metric("Área Basal (m²/ha)", f"{stand_avg['G_ha']:.2f}")
                        c3.metric("Num. Árboles (A/ha)", f"{stand_avg['N_ha']:.1f}")
                        
                        # Fila 2: Densidad y Cobertura (Reineke, CC)
                        c4, c5, c6 = st.columns(3)
                        c4.metric("Índice Reineke (IDRR)", f"{reineke_sdi:.1f}")
                        c5.metric("Cobertura Copa (%)", f"{canopy_cover:.1f}%")
                        c6.metric("ICA (m³/ha/año)", f"{ica_val:.2f}")
                        
                        # Fila 3: Carbono y Calificación
                        c7, c8 = st.columns([1, 2])
                        c7.metric("Carbonó (C/ha)", f"{stand_avg['C_ha_ton']:.2f} Ton")
                        with c8:
                            st.info(f"🏷️ **2.1.7 Calificación del Rodal:** {stand_rating}")
                        
                        with st.expander("🔍 Ver Detalle de Expansión por Árbol"):
                            results['CO2e_ha'] = results['C_ha_ton'] * 3.67
                            st.dataframe(results, use_container_width=True)
                        
                        # Interpretación Narrativa (NUEVO)
                        with st.chat_message("assistant", avatar="🧠"):
                            st.write(nlg.ForestryInterpretation.generate_biometry_summary(reineke_sdi, canopy_cover, stand_rating))

                    # TAB 2: IVI (CON SUMATORIA)
                    with tab_ivi:
                        st.subheader("💎 Índice de Valor de Importancia (IVI)")
                        ivi_df = ForestryEngine.calculate_ivi(results, species_col=sp_col, site_col=s_col, dap_col=dap_col)
                        
                        if not ivi_df.empty:
                            iv_col1, iv_col2 = st.columns([1.5, 1])
                            
                            with iv_col1:
                                ivi_plot = ivi_df.reset_index()
                                ivi_melted = ivi_plot.melt(id_vars=[sp_col], value_vars=['AR_pct', 'DR_pct', 'FR_pct'], var_name='Componente', value_name='Valor')
                                name_map = {'AR_pct': 'Abundancia Relat.', 'DR_pct': 'Dominancia Relat.', 'FR_pct': 'Frecuencia Relat.'}
                                ivi_melted['Componente'] = ivi_melted['Componente'].map(name_map)
                                
                                fig_ivi = px.bar(ivi_melted, x=sp_col, y='Valor', color='Componente', barmode='stack', title="Composición del IVI", color_discrete_sequence=["#2e7d32", "#1b5e20", "#fbc02d"])
                                st.plotly_chart(fig_ivi, use_container_width=True)
                                
                            with iv_col2:
                                # Añadir Fila de Sumatoria (Requisito del usuario)
                                ivi_table = ivi_df[['IVI', 'AR_pct', 'DR_pct', 'FR_pct']].copy()
                                totals = pd.Series({
                                    'IVI': ivi_table['IVI'].sum(),
                                    'AR_pct': ivi_table['AR_pct'].sum(),
                                    'DR_pct': ivi_table['DR_pct'].sum(),
                                    'FR_pct': ivi_table['FR_pct'].sum()
                                }, name='SUMATORIA TOTAL')
                                ivi_table = pd.concat([ivi_table, totals.to_frame().T])
                                
                                st.dataframe(ivi_table.style.format("{:.2f}").highlight_max(axis=0, color='#e8f5e9'), use_container_width=True)
                                st.caption("🛡️ Se verifica que el IVI total suma 300.00 (100% por cada componente relativo).")
                        
                        # Interpretación Narrativa (NUEVO)
                        with st.chat_message("assistant", avatar="🧠"):
                            st.write(nlg.ForestryInterpretation.generate_ivi_summary(ivi_df))

                    # TAB 3: BIODIVERSIDAD (CONSOLIDADO)
                    with tab_div:
                        st.subheader("🌿 Índices de Diversidad y Riqueza")
                        # Obtener abundancias por especie para el Rodal
                        ab_counts = results.groupby(sp_col).size().values
                        div_indices = BiodiversityEngine.calculate_all_indices(ab_counts)
                        
                        d1, d2, d3, d4 = st.columns(4)
                        d1.metric("Shannon (H')", f"{div_indices['Shannon_H']:.3f}")
                        d2.metric("Simpson (D)", f"{div_indices['Simpson_D']:.3f}")
                        d3.metric("Margalef", f"{div_indices['Margalef']:.3f}")
                        d4.metric("Menhinick", f"{div_indices['Menhinick']:.3f}")
                        
                        st.info("💡 Estos índices se calculan analizando la comunidad completa detectada en el inventario.")
                        
                        # Interpretación Narrativa (NUEVO)
                        with st.chat_message("assistant", avatar="🧠"):
                            st.write(nlg.ForestryInterpretation.generate_biodiversity_summary(div_indices))

                    # TAB 4: CRECIMIENTO Y MODELOS
                    with tab_growth:
                        st.subheader("📈 Modelos de Crecimiento y Forma")
                        px_c1, px_c2 = st.columns(2)
                        with px_c1:
                            st.write("**Índice de Sitio (GADA)**")
                            h_ref = st.number_input("Altura Dominante (m)", value=15.0, key="h_si_v2")
                            a_ref = st.number_input("Edad Actual", value=25, key="a_si_v2")
                            if st.button("Calcular SI", key="btn_si"):
                                si = ForestryEngine.calculate_site_index_gada(h_ref, a_ref)
                                st.success(f"Índice de Sitio: **{si:.2f} m**")
                        with px_c2:
                            st.write("**Modelo de Ahusamiento (Fang)**")
                            d_ref = st.number_input("DAP (cm)", value=30.0, key="d_ta_v2")
                            ht = st.number_input("Altura Total (m)", value=20.0, key="ht_ta_v2")
                            h_tar = st.slider("Altura interés (m)", 0.0, float(ht), 1.3, key="h_tar_v2")
                            d_at = ForestryEngine.run_fang_taper(d_ref, ht, h_tar)
                            st.info(f"Diámetro a {h_tar}m: **{d_at:.2f} cm**")

                    st.session_state["f_results"] = results
                    
                except Exception as e:
                    st.error(f"Error en el análisis científico: {e}")
                    
                except Exception as e:
                    st.error(f"Error en el análisis biométrico: {e}")
                    st.info("💡 Consejo: Asegúrate de que las columnas seleccionadas contienen valores numéricos válidos.")
        else:
            st.info("Carga un archivo a la izquierda para visualizar los resultados aquí.")
            st.image("https://img.icons8.com/stickers/200/natural-food.png", width=200)

# 4. BIOESTADÍSTICA PRO (Enabled)
elif menu == "🔬 Bioestadística Pro":
    st.header("🔬 Bioestadística Pro: Análisis Exploratorio")
    st.markdown("*Correlaciones, distribuciones y estadística descriptiva de variables ambientales.*")
    
    with st.expander("ℹ️ Guía de Inicio: Análisis Exploratorio", expanded=True):
        st.markdown("""
        ### 🧪 ¿Para qué sirve?
        Este es el **punto de partida** obligatorio para cualquier estudio científico. Permite entender cómo interactúan tus variables antes de realizar modelos complejos.
        
        ### 📥 ¿Qué datos necesito?
        Sube una **Matriz de Variables Numéricas** (Excel):
        - cada **fila** es una muestra o sitio.
        - cada **columna** es una variable técnica (Ej: pH, Humedad, Diámetro, Nitrógeno).
        
        ### 📊 ¿Qué obtendrás?
        1. **Mapa de Correlaciones**: Identifica qué variables "se mueven juntas".
        2. **Análisis de Distribución**: Detecta valores atípicos y normalidad.
        3. **Estadística Descriptiva**: Promedios, desviaciones y cuartiles automáticos.
        """)
        
        st.markdown("**Estructura sugerida:**")
        example_data = pd.DataFrame({
            'Sitio': ['Muestra_1', 'Muestra_2', 'Muestra_3'],
            'Variable_A': [10.5, 12.1, 11.2],
            'Variable_B': [0.5, 0.4, 0.6],
            'Variable_C': [100, 110, 105]
        })
        st.table(example_data)
        
        stats_template = templates.create_stats_wide_template()
        templates.render_download_button(stats_template, "plantilla_ambiental_ecometrics.xlsx", "⬇️ Descargar Plantilla Maestras (Matriz de Variables)")
    
    b_file = st.file_uploader("Subir Matriz de Variables", type=["xlsx"], key="b_up_pro")
    
    if b_file:
        try:
            b_df = pd.read_excel(b_file)
            st.success("¡Datos cargados!")
            
            num_df = b_df.select_dtypes(include=[np.number])
            
            if num_df.empty:
                st.warning("⚠️ No se detectaron columnas numéricas. Asegúrate de que las variables ambientales sean números.")
            else:
                tab_corr, tab_desc = st.tabs(["📉 1. Mapa de Correlaciones", "📊 2. Distribución y Descriptiva"])
                
                with tab_corr:
                    st.subheader("Interacción entre Variables")
                    corr_matrix = StatsProEngine.calculate_correlation(num_df)
                    
                    with st.container(border=True):
                        # Gráfico Premium
                        fig_corr = px.imshow(
                            corr_matrix, 
                            text_auto=".2f", 
                            color_continuous_scale='RdYlGn',
                            aspect="auto",
                            labels=dict(color="Coeficiente r"),
                            title="Matriz de Correlación de Pearson"
                        )
                        fig_corr.update_layout(
                            margin=dict(l=20, r=20, t=50, b=20),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(size=12)
                        )
                        st.plotly_chart(fig_corr, use_container_width=True)
                        
                        # Interpretación Estilo Asistente (Visible por Defecto)
                        with st.chat_message("assistant", avatar="🧠"):
                            st.write("### 🤖 Diagnóstico Estadístico: Interpretación")
                            st.markdown(nlg.ExperimentalInterpretation.generate_correlation_summary(corr_matrix))
                
                with tab_desc:
                    st.subheader("Análisis de Distribución y Normalidad")
                    
                    # Variable Selector
                    sel_var = st.selectbox("🎯 Análisis de Variable:", num_df.columns)
                    
                    # Metrics Row
                    stats = num_df[sel_var].describe()
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Media", f"{stats['mean']:.2f}")
                    c2.metric("Desv. Est.", f"{stats['std']:.2f}")
                    c3.metric("Mín", f"{stats['min']:.2f}")
                    c4.metric("Máx", f"{stats['max']:.2f}")
                    
                    with st.container(border=True):
                            from scipy import stats
                            data = num_df[sel_var].dropna()
                            
                            # Estadísticas Diagnósticas
                            mean_v = data.mean()
                            median_v = data.median()
                            std_v = data.std()
                            skew_v = data.skew()
                            kurt_v = data.kurtosis()
                            
                            # Gráfico Científico (ff.create_distplot)
                            import plotly.figure_factory as ff
                            try:
                                fig_hist = ff.create_distplot(
                                    [data.values], 
                                    [sel_var], 
                                    show_hist=True, 
                                    show_rug=False,
                                    colors=['#2e7d32'],
                                    bin_size=(data.max() - data.min())/15
                                )
                                
                                # ELIMINACIÓN TOTAL DE LEYENDA (None)
                                fig_hist.update_layout(showlegend=False)
                                fig_hist.for_each_trace(lambda t: t.update(showlegend=False))
                                
                                # Estilo Journal
                                fig_hist.update_layout(
                                    title=f"🔬 Perfil de Distribución: {sel_var}",
                                    template="plotly_white",
                                    xaxis_title=f"Valor de {sel_var}",
                                    yaxis_title="Densidad de Probabilidad (KDE)",
                                    margin=dict(l=20, r=20, t=60, b=20)
                                )
                                
                                # Marcar Media y Mediana con texto explicativo
                                fig_hist.add_vline(x=mean_v, line_dash="dash", line_color="red")
                                fig_hist.add_vline(x=median_v, line_dash="dot", line_color="blue")
                                
                                fig_hist.add_annotation(x=mean_v, y=0.1, text="Media", showarrow=True, arrowhead=1, ax=40, ay=-30, font=dict(color="red"))
                                fig_hist.add_annotation(x=median_v, y=0.05, text="Mediana", showarrow=True, arrowhead=1, ax=-40, ay=-30, font=dict(color="blue"))
                                
                                # Dashboard de Estadísticas en la gráfica
                                stats_text = (
                                    f"📊 <b>Muestras: {len(data)}</b><br>"
                                    f"μ: {mean_v:.2f}<br>"
                                    f"Mo: {median_v:.2f}<br>"
                                    f"σ: {std_v:.2f}<br>"
                                    f"Skew: {skew_v:.2f}<br>"
                                    f"Kurt: {kurt_v:.2f}"
                                )
                                fig_hist.add_annotation(
                                    xref="paper", yref="paper",
                                    x=0.98, y=0.98,
                                    text=stats_text,
                                    showarrow=False,
                                    bgcolor="rgba(255, 255, 255, 0.9)",
                                    bordercolor="silver",
                                    align="left"
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                            
                                # INTERPRETACIÓN CIENTÍFICA (v4 forces reload)
                                with st.chat_message("assistant", avatar="🧠"):
                                    st.write(f"### 🧪 Diagnóstico de {sel_var}")
                                    # Llamada directa al motor v4
                                    desc_text = nlg.ExperimentalInterpretation.generate_descriptive_summary(num_df, sel_var)
                                    if desc_text:
                                        st.markdown(desc_text)
                                    else:
                                        st.info("Generando reporte detallado... cambie de variable para refrescar.")
                                            
                            except Exception as chart_err:
                                st.error(f"Error en visualización avanzada: {chart_err}")
                                st.dataframe(data.describe())

        except Exception as e:
            st.error(f"❌ Error al procesar datos: {e}")
            st.exception(e) # Para debug
# 5. ANÁLISIS MULTIVARIADO
elif menu == "🧩 Análisis Multivariado":
    st.header("🧩 Análisis Multivariado de Ecosistemas")
    st.markdown("""
    Este módulo permite visualizar la **similitud o diferencia** entre comunidades biológicas.
    - **PCA (Análisis de Componentes Principales)**: Ideal para variables ambientales continuas (Nitrógeno, PH, etc.) con relaciones lineales.
    - **NMDS (Escalamiento No Métrico)**: El estándar en ecología para matrices de especies (Abundancia/Presencia) con distancias de Bray-Curtis.
    """)
    
    from modules.stats_pro_v2 import StatsProEngine, AdvancedStatsEngine
    
    with st.sidebar:
        st.subheader("📂 Plantilla")
        if st.checkbox("Usar Matriz de Comunidad (Largo)", value=True):
            stats_template = templates.create_advanced_community_template()
            file_name = "plantilla_comunidad_ecometrics.xlsx"
        else:
            stats_template = templates.create_stats_wide_template()
            file_name = "plantilla_ambiente_ecometrics.xlsx"
            
        templates.render_download_button(stats_template, file_name, "⬇️ Descargar Plantilla Maestras")
    
    b_file = st.file_uploader("Subir Matriz Ambiental o de Comunidad", type=["xlsx"], key="b_up")
    
    if b_file:
        try:
            b_df = pd.read_excel(b_file)
            st.dataframe(b_df.head(), use_container_width=True)
            
            # Si los datos están en formato largo, convertir a matriz
            if "Especie" in b_df.columns and "Sitio" in b_df.columns:
                comm_df = StatsProEngine.get_community_matrix(b_df, "Sitio", "Especie", "Abundancia")
                st.info(f"Matriz generada: {comm_df.shape[0]} sitios x {comm_df.shape[1]} especies.")
            else:
                comm_df = b_df.select_dtypes(include=[np.number])
            
            tab_pca, tab_nmds, tab_sim = st.tabs(["📉 PCA (Ambiente)", "🧩 NMDS (Comunidad)", "📏 Similitud/Distancia"])
            
            with tab_pca:
                if not comm_df.empty:
                    pca_df, variance = StatsProEngine.run_pca(comm_df)
                    
                    with st.container(border=True):
                        fig_pca = px.scatter(
                            pca_df, x='PC1', y='PC2', 
                            text=pca_df.index,
                            title="Ordenación PCA (Componentes Principales)",
                            color_discrete_sequence=['#1b5e20']
                        )
                        fig_pca.update_traces(textposition='top center', marker=dict(size=12, symbol='diamond'))
                        fig_pca.update_layout(
                            xaxis_title=f"PC1 ({variance[0]:.1%})",
                            yaxis_title=f"PC2 ({variance[1]:.1%})",
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        fig_pca.for_each_trace(lambda t: t.update(showlegend=False))
                        st.plotly_chart(fig_pca, use_container_width=True)
                        
                        with st.chat_message("assistant", avatar="🚀"):
                            st.write("### 🤖 Reporte de Ordenación PCA")
                            st.markdown(nlg.ExperimentalInterpretation.generate_multivariate_summary(pca_variance=variance))
                else:
                    st.warning("No hay suficientes datos numéricos para PCA.")
            
            with tab_nmds:
                if not comm_df.empty:
                    try:
                        nmds_df, stress = AdvancedStatsEngine.run_nmds(comm_df)
                        
                        with st.container(border=True):
                            fig_nmds = px.scatter(
                                nmds_df, x='NMDS1', y='NMDS2', 
                                text=nmds_df.index,
                                title="Afinidad de Sitios (NMDS Bray-Curtis)",
                                color_discrete_sequence=['#bf360c']
                            )
                            fig_nmds.update_traces(textposition='top center', marker=dict(size=12, symbol='circle'))
                            fig_nmds.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
                            fig_nmds.for_each_trace(lambda t: t.update(showlegend=False))
                            st.plotly_chart(fig_nmds, use_container_width=True)
                            
                            with st.chat_message("assistant", avatar="🌌"):
                                st.write("### 🤖 Reporte de Ordenación NMDS")
                                st.markdown(nlg.ExperimentalInterpretation.generate_multivariate_summary(nmds_stress=stress))
                    except Exception as e:
                        st.warning(f"El NMDS requiere una matriz de abundancias mayor o balanceada. Detalle: {e}")
                else:
                    st.warning("No hay suficientes datos numéricos para NMDS.")
            
            with tab_sim:
                st.subheader("Matriz de Bray-Curtis")
                sim_df = StatsProEngine.calculate_similarity(comm_df)
                fig_sim = px.imshow(sim_df, color_continuous_scale='Greens', title="Similitud entre Sitios")
                st.plotly_chart(fig_sim, use_container_width=True)
                
            # --- NUEVO: VALOR INDICADOR (INDVAL) ---
            st.divider()
            with st.expander("🔬 Análisis de Especies Indicadoras (IndVal)"):
                st.markdown("Identifica especies que caracterizan a grupos de sitios (requiere clasificación previa o clustering).")
                if not comm_df.empty:
                    # Simular clusters si no hay (ej. basado en nombres de sitios o simple split)
                    sim_clusters = [1 if i < len(comm_df)/2 else 2 for i in range(len(comm_df))]
                    st.info("Nota: Usando clusters automáticos (Mitad A vs Mitad B) para demostración.")
                    iv_df = BiodiversityEngine.run_indval(comm_df, np.array(sim_clusters))
                    st.dataframe(iv_df, use_container_width=True)
                    st.caption("A: Especificidad | B: Fidelidad | iv: Valor Indicador (0-100)")
                    
        except Exception as e:
            st.error(f"Error: {e}")

# 5. DISEÑO EXPERIMENTAL
elif menu == "🧪 Diseño Experimental":
    st.header("🧪 Diseño Experimental Avanzado")
    st.markdown("*Análisis ANOVA y Pruebas No Paramétricas con rigor científico.*")
    
    method_type = st.radio("Tipo de Prueba", ["ANOVA (Paramétrica)", "Kruskal-Wallis / Friedman (No Paramétrica)"], horizontal=True)
    
    if "ANOVA" in method_type:
        design_type = st.radio("Selecciona el Diseño", ["DCA", "DBCA", "Cuadro Latino"], horizontal=True)
    else:
        design_type = st.radio("Selecciona la Prueba", ["Kruskal-Wallis (Independientes)", "Friedman (Dependientes)"], horizontal=True)

    if 'exp_results' not in st.session_state:
        st.session_state.exp_results = None

    # Configuración de Columnas para Entrada
    col_input, col_setup = st.columns([1, 1.2])
    
    with col_input:
        st.subheader("1. Obtener Plantilla")
        if "Kruskal" in design_type or "DCA" in design_type:
            template = templates.create_dca_template()
            file_name_t = "plantilla_DCA_ANCHO_v1.xlsx"
        elif "Friedman" in design_type or "DBCA" in design_type:
            template = templates.create_dbca_template()
            file_name_t = "plantilla_DBCA_ANCHO_v1.xlsx"
        else:
            template = templates.create_latino_template()
            file_name_t = "plantilla_latino_v1.xlsx"
            
        templates.render_download_button(template, file_name_t, "⬇️ Descargar Formato Oficial (Nuevo)")
        

    with col_setup:
        st.subheader("2. Cargar y Analizar")
        exp_file = st.file_uploader("Subir Excel", type=["xlsx"], key="exp_up_all")
        
        if exp_file:
            try:
                exp_df = pd.read_excel(exp_file)
                
                if design_type == "Cuadro Latino":
                    st.success("✅ **Datos de Cuadro Latino cargados correctamente**.")
                else:
                    st.success("✅ **¡Datos cargados en formato ancho!** (Detección automática de tratamientos activa)")
                    
                st.dataframe(exp_df.head(), use_container_width=True)
                
                # Botón adicional para mostrar/ocultar resultados si ya se corrieron
                if st.session_state.exp_results:
                    st.info("💡 Los resultados se muestran en el dashboard de la izquierda.")
                
                cols = exp_df.columns.tolist()
                
                if "ANOVA" in method_type:
                    st.subheader("⚙️ Configuración del Análisis")
                    if design_type == "DCA":
                        # Detección automática de ID
                        auto_id = "Repeticion" if "Repeticion" in cols else None
                        id_vars = [auto_id] if auto_id else []
                        
                        # Tratamientos = numéricos que no sean de sistema
                        treatments = [c for c in cols if c not in id_vars and c.lower() not in ['repeticion', 'rep', 'id', 'bloque', 'muestras']]
                        
                        st.success(f"✅ **Análisis configurado**: Comparando {len(treatments)} tratamientos.")
                        st.info(f"Tratamientos: {', '.join(treatments)}")
                        
                        with st.expander("⚙️ Configuración Avanzada (Opcional)"):
                            id_col_manual = st.selectbox("Cambiar Columna de Identificación", ["Ninguna"] + cols, index=cols.index(auto_id)+1 if auto_id else 0)
                            if id_col_manual != "Ninguna": id_vars = [id_col_manual]
                            treatments = [c for c in cols if c not in id_vars]
                        
                        if st.button("🚀 Ejecutar ANOVA"):
                            long_df = ExperimentalEngine.melt_wide_to_long(exp_df, id_vars=id_vars)
                            res_col, fac_col = "Respuesta", "Tratamiento"
                            
                            # Ejecutar ANOVA
                            tab, mod = ExperimentalEngine.run_anova(long_df, res_col, [fac_col], design="DCA")
                            exp_metrics = ExperimentalEngine.calculate_experimental_metrics(long_df, mod, res_col)
                            
                            # Poder
                            n_g = len(long_df[fac_col].unique())
                            n_p_g = len(long_df) / n_g
                            pwr = ExperimentalEngine.run_power_analysis(n_g, n_p_g)
                            
                            # Tukey HSD y Agrupamiento (SIEMPRE VISIBLE POR SOLICITUD DE USUARIO)
                            grouping_df, tukey_df = ExperimentalEngine.get_tukey_groups(long_df, res_col, fac_col)
                            summary_text = nlg.ExperimentalInterpretation.generate_anova_summary(long_df, tab, exp_metrics, "DCA", tukey_df=tukey_df, power=pwr)
                            
                            # Gráfico de cajas (Exploratorio)
                            fig_exp = px.box(long_df, x=fac_col, y=res_col, color=fac_col, template="plotly_white")
                            
                            st.session_state.exp_results = {
                                'tab': tab, 'metrics': exp_metrics, 'fig': fig_exp,
                                'summary': summary_text, 'tukey_df': tukey_df,
                                'grouping_df': grouping_df,
                                'power': pwr, 'design': "DCA",
                                'res_col': res_col, 'fac_col': fac_col
                            }
                            st.rerun()

                    elif design_type == "DBCA":
                        # Detección automática de Bloque
                        auto_blo = "Bloque" if "Bloque" in cols else cols[0]
                        
                        st.success(f"✅ **Análisis de Bloque configurado**: '{auto_blo}'")
                        treatments = [c for c in cols if c != auto_blo and c.lower() not in ['repeticion', 'rep', 'id', 'muestras']]
                        st.info(f"Tratamientos: {', '.join(treatments)}")
                        
                        with st.expander("⚙️ Configuración Avanzada (Opcional)"):
                            blo_col_manual = st.selectbox("Cambiar Columna de Bloque", cols, index=cols.index(auto_blo))
                            auto_blo = blo_col_manual
                        
                        if st.button("🚀 Ejecutar ANOVA (Bloques)"):
                            long_df = ExperimentalEngine.melt_wide_to_long(exp_df, id_vars=[auto_blo])
                            res_col, fac_col = "Respuesta", "Tratamiento"
                            
                            tab, mod = ExperimentalEngine.run_anova(long_df, res_col, [fac_col, auto_blo], design="DBCA")
                            exp_metrics = ExperimentalEngine.calculate_experimental_metrics(long_df, mod, res_col)
                            
                            # Poder
                            n_g = len(long_df[fac_col].unique())
                            n_p_g = len(long_df) / n_g
                            pwr = ExperimentalEngine.run_power_analysis(n_g, n_p_g)
                            
                            # Tukey HSD y Agrupamiento (SIEMPRE VISIBLE)
                            grouping_df, tukey_df = ExperimentalEngine.get_tukey_groups(long_df, res_col, fac_col)
                            summary_text = nlg.ExperimentalInterpretation.generate_anova_summary(long_df, tab, exp_metrics, "DBCA", tukey_df=tukey_df, power=pwr)
                            
                            # Perfil de respuesta (Para bloques)
                            fig_exp = px.line(long_df, x=fac_col, y=res_col, color=auto_blo, markers=True, template="plotly_white")
                            fig_exp.update_traces(line=dict(width=1.5), marker=dict(size=8))
                            
                            st.session_state.exp_results = {
                                'tab': tab, 'metrics': exp_metrics, 'fig': fig_exp,
                                'summary': summary_text, 'tukey_df': tukey_df,
                                'grouping_df': grouping_df,
                                'power': pwr, 'design': "DBCA",
                                'res_col': res_col, 'fac_col': fac_col
                            }
                            st.rerun()

                    elif design_type == "Cuadro Latino":
                        st.info("💡 **Dato**: El Cuadro Latino usa Fila, Columna y Tratamiento para el análisis.")
                        
                        # Intentar detectar automáticamente
                        f_col = "Fila" if "Fila" in cols else cols[0]
                        c_col = "Columna" if "Columna" in cols else cols[1]
                        t_col = "Tratamiento" if "Tratamiento" in cols else cols[2]
                        r_col = "Respuesta" if "Respuesta" in cols else cols[-1]
                        
                        # Limpieza de datos (Refuerzo)
                        if exp_df[r_col].dtype == object:
                            exp_df[r_col] = exp_df[r_col].astype(str).str.replace(',', '.', regex=True)
                        exp_df[r_col] = pd.to_numeric(exp_df[r_col], errors='coerce')
                        exp_df = exp_df.dropna(subset=[r_col])
                        
                        if st.button("🚀 Ejecutar ANOVA (Latino)"):
                            tab, mod = ExperimentalEngine.run_anova(exp_df, r_col, [t_col, f_col, c_col], design="Latino")
                            exp_metrics = ExperimentalEngine.calculate_experimental_metrics(exp_df, mod, r_col)
                            
                            # Poder
                            n_g = len(exp_df[t_col].unique())
                            n_p_g = len(exp_df) / n_g
                            pwr = ExperimentalEngine.run_power_analysis(n_g, n_p_g)
                            
                            # Tukey HSD y Agrupamiento (SIEMPRE VISIBLE)
                            grouping_df, tukey_df = ExperimentalEngine.get_tukey_groups(exp_df, r_col, t_col)
                            summary_text = nlg.ExperimentalInterpretation.generate_anova_summary(exp_df, tab, exp_metrics, "Cuadro Latino", tukey_df=tukey_df, power=pwr)
                            
                            fig_lat = px.scatter(exp_df, x=c_col, y=f_col, size=r_col, color=t_col, title="Distribución de Tratamientos en el Cuadro", template="plotly_white")
                            
                            st.session_state.exp_results = {
                                'tab': tab, 'metrics': exp_metrics, 'fig': fig_lat,
                                'summary': summary_text, 'tukey_df': tukey_df,
                                'grouping_df': grouping_df,
                                'power': pwr, 'design': "Cuadro Latino",
                                'res_col': r_col, 'fac_col': t_col
                            }
                            st.rerun()
                else:
                    st.warning("Para pruebas no paramétricas también usaremos el formato ancho.")
                    if st.button(f"🚀 Ejecutar {design_type}"):
                        if "Friedman" in design_type:
                            id_col = cols[0]
                            long_df = ExperimentalEngine.melt_wide_to_long(exp_df, id_vars=[id_col])
                            res = ExperimentalEngine.run_non_parametric(long_df, "Respuesta", "Tratamiento", design="Friedman")
                        else:
                            long_df = ExperimentalEngine.melt_wide_to_long(exp_df, id_vars=[])
                            res = ExperimentalEngine.run_non_parametric(long_df, "Respuesta", "Tratamiento", design="Kruskal")
                        
                        st.write(res)
                        fig_np = px.violin(long_df, x="Tratamiento", y="Respuesta", color="Tratamiento", box=True)
                        st.plotly_chart(fig_np, use_container_width=True)
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    # --- REPORTE DE RESULTADOS FINAL (ANCHO COMPLETO - EXIGIDO) ---
    if st.session_state.exp_results:
        res = st.session_state.exp_results
        
        st.markdown("---")
        st.header(f"📊 Reporte Técnico de Diseño Experimental ({res.get('design', 'Análisis')})")
        
        # 1. Diagnóstico de Hipótesis y Decisión (NUEVO / EXIGIDO)
        st.subheader("🎯 Diagnóstico de Hipótesis (H0)")
        
        anova_fmt = ExperimentalEngine.format_anova_to_df(res['tab'])
        
        # Identificar qué fuentes de variación evaluar
        sources_to_check = []
        design_str = res.get('design', '')
        if design_str in ["DBCA", "Cuadro Latino"]:
            for idx in anova_fmt.index:
                idx_str = str(idx).lower()
                if "error" not in idx_str and "residual" not in idx_str and "total" not in idx_str:
                    sources_to_check.append(idx)
        else:
            for idx in anova_fmt.index:
                if "Tratamiento" in str(idx) or "factor" in str(idx).lower():
                    sources_to_check.append(idx)
                    break
        
        if not sources_to_check:
            st.warning("⚠️ No se encontraron fuentes de variación principales para el diagnóstico.")
            
        for source in sources_to_check:
             source_row = anova_fmt.loc[source]
             if hasattr(source_row, "shape") and len(source_row.shape) > 1:
                 source_row = source_row.iloc[0]
                 
             try:
                 f_calc = source_row.get("FCAL (F-Calc)", source_row.iloc[3] if len(source_row) > 3 else "-")
                 f_tab = source_row.get("FTAB (0.05)", source_row.iloc[4] if len(source_row) > 4 else "-")
                 decision = source_row.get("Regla de Decisión", source_row.iloc[6] if len(source_row) > 6 else "Sin Decisión")
                 
                 # Elemento visual para la fuente
                 st.markdown(f"**🔹 Efecto: {source}**")
                 col_d1, col_d2 = st.columns([1, 2])
                 with col_d1:
                     dec_str = str(decision)
                     if "Rechaza H0" in dec_str:
                         st.error(f"### Decisión: {dec_str}")
                     else:
                         st.info(f"### Decisión: {dec_str}")
                 
                 with col_d2:
                     st.write(f"**Justificación Estadística**:")
                     st.markdown(f"Dado que el valor calculado **FCAL ({f_calc})** es **{'mayor' if 'Rechaza' in str(decision) else 'menor'}** que el valor crítico de tablas **FTAB ({f_tab})**, podemos concluir que existe evidencia suficiente para **{'RECHAZAR' if 'Rechaza' in str(decision) else 'NO RECHAZAR'}** la hipótesis nula ($H_0$) con un nivel de significancia del 5%.")
                 st.markdown("<br>", unsafe_allow_html=True)
             except Exception as diag_err:
                 st.warning(f"⚠️ Nota: El diagnóstico detallado no pudo generarse automáticamente para {source} ({diag_err}).")

        # 2. Resumen de Cálculo Manual
        st.subheader("⚙️ Componentes del Cálculo (Varianza)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Factor de Corrección (FC)", f"{res['metrics'].get('FC', 0):.4f}")
        m2.metric("Sumatoria Total (ΣY)", f"{res['metrics'].get('Sumatoria', 0):.2f}")
        m3.metric("R-cuadrado (R²)", f"{res['metrics'].get('R2', 0):.4f}")
        m4.metric("C.V. (%)", f"{res['metrics'].get('CV', 0):.2f}%")

        # 3. Interpretación Narrativa
        with st.chat_message("assistant", avatar="🧠"):
            st.write("### 🔬 Interpretación Técnica")
            st.markdown(res.get('summary', "Análisis completado."))

        # 4. Tabla ANOVA Profesional
        st.subheader("📝 Tabla ANOVA Estándar")
        st.dataframe(anova_fmt, use_container_width=True)
        
        # 5. RESULTADOS DE AGRUPACIÓN (TUKEY) - NUEVO / ESTILO PUBLICACIÓN
        if res.get('grouping_df') is not None:
            st.divider()
            st.subheader("🧬 Agrupamiento de Tratamientos (Conectividad)")
            
            col_t1, col_t2 = st.columns([1, 1.2])
            
            with col_t1:
                st.write("**Resumen de Medias y Grupos**")
                st.dataframe(res['grouping_df'], use_container_width=True)
                st.caption("Nota: Medias que comparten la misma letra no presentan diferencias significativas entre sí (α=0.05).")
            
            with col_t2:
                # Gráfico de Barras con Letras (Tipo imagen de ejemplo)
                gdf = res['grouping_df']
                fig_bar = px.bar(gdf, x='Tratamiento', y='Media', 
                                 error_y='Desv. Est.',
                                 text='Grupo',
                                 color='Tratamiento',
                                 title="Comparación de Medias con Significación",
                                 template="plotly_white")
                
                fig_bar.update_traces(textposition='outside', 
                                      textfont_size=16,
                                      marker_line_color='black',
                                      marker_line_width=1.5)
                
                fig_bar.update_layout(showlegend=False, 
                                      yaxis_title=res.get('res_col', 'Respuesta'),
                                      xaxis_title=res.get('fac_col', 'Tratamiento'))
                
                st.plotly_chart(fig_bar, use_container_width=True)
        
        # 6. Visualización Exploratoria
        with st.expander("📈 Ver Visualización de Distribución / Perfiles"):
            st.plotly_chart(res['fig'], use_container_width=True)
            
        # 7. Conclusión de Potencia
        pwr_val = res.get('power', 0)
        st.write(f"**Análisis de Potencia Real ($1-\\beta$):** `{pwr_val:.2f}`")
        st.caption("💡 La potencia estadística indica la probabilidad de detectar diferencias reales si existen. Un valor ≥ 0.80 es el estándar científico; valores menores sugieren que el tamaño de muestra es pequeño o la variabilidad es muy alta (Riesgo de Error Tipo II).")

        if st.button("🧹 Limpiar Reporte y Nueva Carga", use_container_width=True):
            st.session_state.exp_results = None
            st.rerun()

# 6. MODELOS Y REGRESIÓN
elif menu == "📈 Modelos y Regresión":
    st.header("📈 Modelos Biométricos y Regresión")
    st.markdown("*Modelado predictivo, crecimiento y regresión avanzada.*")
    
    tab_reg, tab_growth = st.tabs(["📉 Regresión", "🌲 Crecimiento"])
    
    with tab_reg:
        col_reg1, col_reg2 = st.columns([1, 1])
        with col_reg1:
            templates.render_download_button(templates.create_regression_template(), "plantilla_regresion.xlsx", "⬇️ Plantilla Regresión")
            r_file = st.file_uploader("Sube datos para revisión", type="xlsx", key="r_up")
        
        if r_file:
            r_df = pd.read_excel(r_file)
            y_c = st.selectbox("Respuesta (Y)", r_df.columns)
            x_c = st.multiselect("Predictores (X)", r_df.columns)
            m_t = st.selectbox("Tipo de Modelo", ["Linear", "Logistic"])
            
            if st.button("🚀 Ajustar Modelo"):
                model = AdvancedStatsEngine.run_regression(r_df, y_c, x_c, m_t)
                
                if m_t == "Linear":
                    st.subheader("🎯 Calidad del Ajuste")
                    rm1, rm2, rm3, rm4 = st.columns(4)
                    rm1.metric("R2 Ajustado", f"{model.adj_r2:.4f}")
                    rm2.metric("AIC", f"{model.aic_val:.2f}")
                    rm3.metric("BIC", f"{model.bic_val:.2f}")
                    rm4.metric("RMSE", f"{model.rmse:.4f}")
                
                with st.expander("📄 Ver Resumen Estadístico Completo", expanded=True):
                    st.text(model.summary())
                
                if len(x_c) == 1:
                    fig_reg = px.scatter(r_df, x=x_c[0], y=y_c, trendline="ols" if m_t=="Linear" else None, title=f"Ajuste {m_t}")
                    st.plotly_chart(fig_reg, use_container_width=True)

    with tab_growth:
        st.subheader("Modelado de Crecimiento Forestal")
        st.write("Ajuste de modelos no lineales (Gompertz / Richards).")
        g_file = st.file_uploader("Sube cronosecuencia", type="xlsx", key="g_up")
        if g_file:
            from scipy.optimize import curve_fit
            g_df = pd.read_excel(g_file)
            st.dataframe(g_df.head())
            t_col = st.selectbox("Eje Tiempo/Edad", g_df.columns)
            v_col = st.selectbox("Eje Volumen/Altura", g_df.columns)
            m_g = st.selectbox("Modelo", ["Gompertz", "Chapman-Richards"])
            
            if st.button("🚀 Ajustar Crecimiento"):
                func = AdvancedStatsEngine.growth_model(0, m_g)
                # Estimación inicial de parámetros (A, B, K)
                popt, _ = curve_fit(func, g_df[t_col], g_df[v_col], p0=[max(g_df[v_col]), 2, 0.05])
                st.success(f"Parámetros ajustados: {popt}")
                
                x_fine = np.linspace(0, max(g_df[t_col])*1.2, 100)
                y_fine = func(x_fine, *popt)
                
                fig_g = px.scatter(g_df, x=t_col, y=v_col, title=f"Crecimiento - {m_g}")
                fig_g.add_scatter(x=x_fine, y=y_fine, mode='lines', name='Ajuste')
                st.plotly_chart(fig_g, use_container_width=True)

# 6. ACERCA DE ECOMETRICS
elif menu == "📖 Acerca de ECOMETRICS":
    st.header("💡 Acerca de ECOMETRICS")
    st.markdown("*Visión, historia e innovación tecnológica.*")

    st.markdown("""
    ### I. La Visión del Proyecto
    **ECOMETRICS** no es simplemente un calculador de índices; es una herramienta tecnológica diseñada para decodificar la complejidad de los ecosistemas a través de los datos. En un contexto de crisis climática y pérdida acelerada de biodiversidad, el monitoreo preciso se ha vuelto esencial. ECOMETRICS nace para cerrar la brecha entre la captura masiva de datos en campo y la obtención de estadísticas ecológicas robustas, permitiendo que la naturaleza sea comprendida con rigor científico.

    ### II. La Dualidad del Nombre: Ecología y Métricas
    El nombre **ECOMETRICS** surge de la intersección entre la ecología de comunidades y la precisión matemática:
    - **El Vínculo con la Tierra**: Representa el compromiso con la conservación y el entendimiento de los procesos biológicos que sostienen la vida.
    - **La Analítica Técnica**: En bioestadística, las métricas son el lenguaje que nos permite interpretar patrones invisibles al ojo humano. ECOMETRICS actúa como un procesador maestro que transforma observaciones en conocimiento aplicable.

    ### III. Perfil del Desarrollador y Respaldo Científico
    **ECOMETRICS** ha sido conceptualizado y desarrollado por **Erick Elio Chavez Gurrola**, Biólogo por el **TecNM**. 
    Con una sólida formación en estadística ecológica, diseño experimental y manejo forestal sustentable, el desarrollador integra la biología de campo con la ingeniería de datos. Su experiencia previa en el desarrollo de plataformas de análisis (como TANIA, FORXIME y CHANNEL) garantiza que ECOMETRICS sea una herramienta de análisis científico robusta y confiable.

    ### IV. Innovación Metodológica
    El núcleo de **ECOMETRICS** está impulsado por el framework **iNEXT (Interpolation and Extrapolation)** para curvas de acumulación basadas en individuos y muestras. 
    Para garantizar la reproducibilidad y el rigor científico exigido en publicaciones y estudios de impacto ambiental, el sistema implementa:
    - **Números de Hill**: Diversidad verdadera (Riqueza, Shannon, Simpson).
    - **Estimadores Asintóticos**: Uso del estimador no paramétrico **Chao 1** para proyectar la riqueza potencial.
    - **Estandarización por Cobertura**: Permite comparar comunidades con diferentes esfuerzos de muestreo de manera justa.

    ---
    ### 📄 Cita Sugerida y Resumen (Para Publicaciones)
    Si utilizas **ECOMETRICS** en tu investigación, puedes basarte en el siguiente fragmento para tu sección de *Métodos*:
    
    > "Los datos de biodiversidad fueron analizados utilizando la plataforma bioestadística **ECOMETRICS v1.2 (Chavez Gurrola, 2026)**. La riqueza de especies y la completitud del inventario se evaluaron mediante modelos de rarefacción y extrapolación analítica basados en individuos, utilizando el estimador asintótico Chao1 para proyectar la diversidad potencial y estandarizar la comparación bajo el framework iNEXT."

    ---
    #### 🔗 Enlaces Profesionales
    - **ORCID**: [0009-0007-7054-6999](https://orcid.org/0009-0007-7054-6999)
    - **ResearchGate**: [Perfil de Investigador](https://www.researchgate.net/profile/Erick-Elio-Chavez-Gurrola-2)
    """)

# 7. AVISO LEGAL
elif menu == "⚠️ Aviso Legal":
    st.header("⚠️ Aviso de Responsabilidad")
    st.markdown("*Términos de uso y limitaciones del software ECOMETRICS.*")

    st.info("""
    Esta plataforma de software ha sido desarrollada y evaluada por el **Biólogo Erick Elio Chavez Gurrola** con el objetivo de facilitar el procesamiento y análisis de datos de biodiversidad y monitoreo ecológico.
    
    **IMPORTANTE**: Si bien la plataforma integra modelos estadísticos avanzados y algoritmos de extrapolación probados, los resultados y proyecciones de riqueza generados por este software están sujetos a la calidad de los datos de entrada.
    """)

    st.markdown("""
    **Es responsabilidad exclusiva del usuario:**
    - Validar la coherencia biológica y de distribución geográfica de los análisis.
    - Interpretar correctamente los intervalos de confianza y niveles de cobertura en su respectivo contexto.
    - No utilizar los resultados a ciegas sin corroboración experta previa en publicaciones científicas o informes técnicos de consultoría.

    > **Exención de Responsabilidad**: El desarrollador (Erick Elio Chavez Gurrola) no asume ninguna responsabilidad, legal ni ética, por el mal uso de los datos generados, errores en la interpretación que deriven en decisiones equivocadas, ni daños consecuentes del uso de esta herramienta. Todo resultado debe ser tratado como una sugerencia estadística que requiere curación profesional.
    """)

    st.subheader("🐛 Reporte de Errores y Sugerencias")
    st.write("Si detecta algún error durante el análisis o tiene sugerencias de mejora, por favor contacte al desarrollador a través de:")
    st.markdown("- **Email**: eliogurrcla5@gmail.com")
    st.markdown("- **ResearchGate**: [Mensaje directo al perfil](https://www.researchgate.net/profile/Erick-Elio-Chavez-Gurrola-2)")

    st.markdown("""
    ---
    *"La precisión en la métrica es el primer paso hacia la conservación efectiva."*
    """)

else:
    st.header(f"🚧 Módulo {menu}")
    st.warning("Estamos trabajando en la implementación de este módulo para garantizar resultados de rigor científico.")

# --- FOOTER PREMIUM (ESTILO CHANNEL) ---
st.markdown(f"""
<div class="footer">
    <div class="footer-content">
        <div class="footer-col">
            <h4>ECOMETRICS</h4>
            <p>Suite Bioestadística avanzada para el monitoreo y gestión de ecosistemas forestales. Desarrollada bajo estándares de rigor científico y precisión biométrica.</p>
        </div>
        <div class="footer-col">
            <h4>Desarrollador</h4>
            <p><b>Erick Elio Chavez Gurrola</b><br>
            Biólogo<br>
            <a href="https://orcid.org/0009-0007-7054-6999" style="color:#2e7d32; text-decoration:none; font-weight:700;">ORCID: 0009-0007-7054-6999</a></p>
        </div>
        <div class="footer-col">
            <h4>Enlaces y Contacto</h4>
            <ul class="footer-links">
                <li><a href="https://www.researchgate.net/profile/Erick-Elio-Chavez-Gurrola-2" target="_blank">ResearchGate</a></li>
                <li><a href="mailto:eliogurrcla5@gmail.com">Soporte Técnico</a></li>
                <li><a href="https://github.com/eliogurrcla5" target="_blank">Open Source</a></li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        &copy; 2026 ECOMETRICS. Todos los derechos reservados. | "La precisión en la métrica es el primer paso hacia la conservación efectiva."
    </div>
</div>
""", unsafe_allow_html=True)
