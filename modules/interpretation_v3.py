import numpy as np
import pandas as pd

"""
Módulo de interpretación científica para ECOMETRICS.
"""

def interpret_inext_metrics(s_obs, chao1, coverage):
    """
    Genera una interpretación detallada de los resultados de iNEXT.
    
    Args:
        s_obs (int): Número de especies observadas.
        chao1 (float): Riqueza asintótica estimada.
        coverage (float): Porcentaje de cobertura del inventario.
        
    Returns:
        str: Interpretación científica en Markdown.
    """
    
    # 1. Análisis de Riqueza
    interpretation = f"### 🧠 Interpretación Científica Detallada\n\n"
    interpretation += f"El análisis revela que se han identificado **{s_obs} especies** en el muestreo actual. "
    
    # 2. Análisis de Chao1 y especies faltantes
    missing_species = max(0, int(np.ceil(chao1 - s_obs)))
    interpretation += f"El estimador asintótico **Chao1** proyecta una riqueza potencial de **{chao1:.2f} especies**. "
    
    if missing_species > 0:
        interpretation += f"Esto sugiere que, estadísticamente, aún existen aproximadamente **{missing_species} especies raras** no detectadas en el área de estudio que podrían aparecer con un mayor esfuerzo de muestreo. "
    else:
        interpretation += "Esta cifra coincide estrechamente con lo observado, lo que indica que se han capturado casi todas las especies presentes en esta comunidad vegetal. "

    # 3. Análisis de Cobertura (Completeness)
    interpretation += f"\n\n**Completitud del Inventario (Cobertura: {coverage:.1f}%):**\n"
    
    if coverage >= 95:
        interpretation += "✅ **Nivel de Completitud Óptimo**: La cobertura es superior al 95%, lo que significa que el inventario es altamente representativo. Los resultados de diversidad son estables y confiables para tomar decisiones de manejo o publicaciones científicas."
    elif coverage >= 85:
        interpretation += "🟡 **Nivel Aceptable**: Se ha capturado la mayor parte de la diversidad dominante. Sin embargo, para un estudio de biodiversidad exhaustivo, se recomendaría incrementar ligeramente el número de muestras para detectar especies de muy baja frecuencia."
    else:
        interpretation += "🔴 **Nivel Deficiente**: La cobertura es baja. La curva de acumulación aún no alcanza la asíntota. Los índices de diversidad calculados podrían estar subestimados debido a la falta de representatividad."

    # 4. Recomendación Técnica
    interpretation += "\n\n**Recomendación de Manejo:**\n"
    if coverage < 90:
        interpretation += "- **Incrementar Esfuerzo**: Se sugiere duplicar el número de cuadrantes o transectos en el pastizal para alcanzar la fase de saturación del inventario."
    else:
        interpretation += "- **Estabilidad**: La comunidad de pastos ha sido bien caracterizada. Se recomienda proceder con el análisis de biomasa o composición funcional con confianza en la base taxonómica."

    return interpretation

class ExperimentalInterpretation:
    """Provee resúmenes científicos extensos para diseños experimentales."""
    
    @staticmethod
    def generate_anova_summary(df, anova_table, metrics, design_name, tukey_df=None, power=None):
        """Genera un reporte científico detallado sobre el experimento."""
        import pandas as pd
        import numpy as np
        
        # 1. Datos del Experimento y Detección de Faltantes
        n_total = len(df)
        n_trats = len(df['Tratamiento'].unique()) if 'Tratamiento' in df.columns else "N/A"
        
        # Detectar datos perdidos (NaN)
        n_missing = df['Respuesta'].isna().sum() if 'Respuesta' in df.columns else 0
        n_valid = n_total - n_missing
        
        summary = f"## 📄 Resumen Científico del Experimento ({design_name})\n\n"
        summary += f"Se analizó un diseño estadístico **{design_name}** con un total de **{n_total} unidades experimentales**. "
        
        if n_missing > 0:
            summary += f"⚠️ **Atención**: Se detectaron **{n_missing} datos perdidos** o nulos. El análisis se ejecutó con las **{n_valid} observaciones válidas** restantes. "
        
        if n_trats != "N/A":
            summary += f"Los datos están distribuidos en **{n_trats} tratamientos**. "
        
        # 2. Análisis de Significancia
        p_val = None
        for idx in anova_table.index:
            if "Tratamiento" in str(idx) or "C(Tratamiento)" in str(idx):
                p_val = anova_table.loc[idx, "PR(>F)"]
                break
        
        interpretation_sig = ""
        anova_significant = False
        if p_val is not None:
            if p_val < 0.05:
                anova_significant = True
                interpretation_sig = "✅ **Se rechaza la hipótesis nula ($H_0$)**. Existen diferencias altamente significativas entre los tratamientos (p < 0.05). Esto indica que al menos uno de los tratamientos produce una respuesta distinta, validando la hipótesis de investigación."
            else:
                interpretation_sig = "❌ **No se rechaza la hipótesis nula ($H_0$)**. No se detectaron diferencias significativas (p > 0.05). Estadísticamente, los tratamientos se comportaron de manera similar y las variaciones observadas se deben al azar."
        
        summary += f"\n\n### ⚖️ Análisis de Significancia\n{interpretation_sig}\n"
        
        # 3. Detección de Paradoja ANOVA vs Tukey
        if anova_significant and tukey_df is not None:
            # Verificar si Tukey tiene alguna diferencia significativa
            # Buscamos la columna 'Diferencia Significativa' o similar
            has_tukey_diff = False
            for col in tukey_df.columns:
                if "Significativa" in col:
                    if any(tukey_df[col].astype(str).str.contains("Sí|✅")):
                        has_tukey_diff = True
                    break
            
            if not has_tukey_diff:
                summary += "\n> [!IMPORTANT]\n"
                summary += "> **Paradoja Estadística Detectada**: El ANOVA global es significativo, pero la prueba de Tukey no logra identificar qué par de tratamientos es diferente. "
                summary += "Esto ocurre frecuentemente cuando las diferencias son marginales, hay alta variabilidad residual (CV alto) o el tamaño de muestra es pequeño. "
                summary += "Se recomienda reportar la tendencia observada o aumentar el número de repeticiones para ganar poder de resolución.\n"

        # 4. Calidad del Experimento (CV y R2)
        cv = metrics['CV']
        r2 = metrics['R2']
        
        summary += f"\n### 🎯 Calidad y Precisión\n"
        summary += f"- **Ajuste del Modelo ($R^2$):** El modelo explica el **{r2*100:.2f}%** de la variabilidad. "
        if r2 > 0.7: summary += "Ajuste sólido."
        else: summary += "Existe mucho ruido no explicado por el modelo."
        
        summary += f"\n- **Estabilidad (CV):** Coeficiente de Variación de **{cv:.2f}%**. "
        if cv < 15: summary += "Precisión excelente."
        elif cv < 30: summary += "Variabilidad moderada, aceptable en biología."
        else: summary += "⚠️ **Alta variabilidad**: Los resultados deben interpretarse con cautela."
        
        # 6. Análisis de Potencia Estadística (NUEVO)
        if power is not None:
            summary += f"\n### ⚡ Potencia Real del Diseño (1-β)\n"
            summary += f"- **Valor Obtenido:** {power:.2f}\n"
            if power >= 0.8:
                summary += "- **Interpretación:** La potencia es **alta**. El experimento tiene una probabilidad robusta de detectar diferencias si realmente existen. Los resultados son confiables.\n"
            elif power >= 0.5:
                summary += "- **Interpretación:** La potencia es **moderada**. Existe un riesgo aceptable pero presente de no detectar diferencias pequeñas. Se sugiere precaución si el resultado fue 'No Significativo'.\n"
            else:
                summary += "- **Interpretación:** ⚠️ **Baja Potencia**. El tamaño de la muestra o el diseño son insuficientes para detectar efectos moderados. Existe un alto riesgo de Error Tipo II (falso negativo).\n"

        return summary
            
    @staticmethod
    def generate_correlation_summary(corr_matrix):
        """Analiza la matriz de correlación y destaca relaciones fuertes."""
        import pandas as pd
        
        summary = "### 🧠 Análisis de Interrelaciones (Correlación)\n"
        
        # Encontrar pares con alta correlación (abs(r) > 0.7)
        high_corr = []
        cols = corr_matrix.columns
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                r = corr_matrix.iloc[i, j]
                if abs(r) >= 0.7:
                    high_corr.append((cols[i], cols[j], r))
        
        if not high_corr:
            summary += "No se detectaron asociaciones lineales extremadamente fuertes ($|r| > 0.7$). Sin embargo, esto puede indicar que las variables son independientes entre sí, lo cual es útil para evitar la multicolinealidad en modelos posteriores.\n"
        else:
            summary += "Se detectaron las siguientes asociaciones significativas:\n"
            for v1, v2, r in high_corr:
                tipo = "positiva" if r > 0 else "negativa"
                fuerza = "muy fuerte" if abs(r) > 0.9 else "fuerte"
                summary += f"- **{v1}** vs **{v2}**: Relación **{fuerza} {tipo}** ($r = {r:.3f}$). "
                if r > 0: summary += "A medida que aumenta una, la otra también tiende a subir.\n"
                else: summary += "A medida que aumenta una, la otra tiende a disminuir.\n"
        
        summary += "\n> [!TIP]\n"
        summary += "> Las correlaciones altas sugieren que una variable podría estar influyendo directamente en la otra, o que ambas responden a un tercer factor no medido.\n"
        
        return summary

    @staticmethod
    def generate_descriptive_summary(df, selected_var):
        """Analiza la distribución y tendencia central de una variable."""
        if selected_var not in df.columns:
            return ""
            
        stats = df[selected_var].describe()
        mean = stats['mean']
        median = df[selected_var].median()
        std = stats['std']
        cv = (std / mean * 100) if mean != 0 else 0
        
        summary = f"### 📊 Perfil de la Variable: {selected_var}\n"
        
        # 1. Tendencia Central y Simetría
        diff_pct = abs(mean - median) / mean if mean != 0 else 0
        if diff_pct < 0.05:
            summary += f"- **Tendencia Central**: La media ({mean:.2f}) y la mediana ({median:.2f}) son muy similares, lo que sugiere una **distribución simétrica** (posiblemente normal).\n"
        elif mean > median:
            summary += f"- **Tendencia Central**: La media es mayor que la mediana, indicando un **sesgo positivo** (presencia de valores atípicos altos).\n"
        else:
            summary += f"- **Tendencia Central**: La media es menor que la mediana, indicando un **sesgo negativo** (presencia de valores atípicos bajos).\n"
            
        # 2. Variabilidad
        summary += f"- **Dispersión (CV)**: El Coeficiente de Variación es del **{cv:.1f}%**. "
        if cv < 15: summary += "Los datos son muy homogéneos y estables.\n"
        elif cv < 35: summary += "Existe una variabilidad moderada, típica en datos naturales.\n"
        else: summary += "⚠️ **Alta Heterogeneidad**: Los datos están muy dispersos; la media podría no ser totalmente representativa del conjunto.\n"
        
        return summary
        
    @staticmethod
    def generate_multivariate_summary(pca_variance=None, nmds_stress=None):
        """Genera un análisis científico para ordenaciones multivariadas."""
        summary = "### 🧩 Interpretación Multivariada\n"
        
        if pca_variance is not None:
            total_var = sum(pca_variance[:2]) * 100
            summary += f"- **AEP (Componentes Principales)**: Los dos primeros componentes explican el **{total_var:.2f}%** de la varianza total. "
            if total_var > 70: summary += "Esto representa una excelente captura de la estructura de los datos.\n"
            elif total_var > 40: summary += "Es una explicación moderada; los datos tienen una complejidad dimensional considerable.\n"
            else: summary += "⚠️ Baja explicación: Existen factores no capturados en estas dos dimensiones.\n"
            
        if nmds_stress is not None:
            summary += f"- **NMDS (Escalamiento No Métrico)**: El estrés del modelo es **{nmds_stress:.4f}**. "
            if nmds_stress < 0.1: summary += "✅ **Ordenación Ideal**: La representación en 2D es altamente confiable.\n"
            elif nmds_stress < 0.2: summary += "🟡 **Ordenación Aceptable**: Existe buena correspondencia con las distancias reales.\n"
            else: summary += "🔴 **Ordenación Pobre**: Riesgo de malas interpretaciones; considere aumentar dimensiones o revisar outliers.\n"
            
        return summary


class ForestryInterpretation:
    """Provee resúmenes narrativos para resultados de inventarios forestales."""
    
    @staticmethod
    def generate_biometry_summary(reineke_sdi, canopy_pct, stand_rating):
        """Genera una interpretación de la densidad y vigor del rodal."""
        summary = "### 🌲 Diagnóstico de Biometría y Densidad\n"
        
        # Interpretación de Reineke y Rating
        summary += f"El rodal ha sido calificado como **{stand_rating}**. "
        
        if "Cierre de Copas" in stand_rating:
            summary += "Esto indica que el bosque está en su **punto de productividad máxima**. Las copas han comenzado a tocarse, optimizando la captura de luz sin llegar aún a una competencia que cause muertes masivas. Es el momento ideal para observar crecimientos vigorosos en diámetro y altura.\n\n"
        elif "Subpoblado" in stand_rating:
            summary += "El rodal tiene espacio disponible. Los árboles crecen de forma libre, pero el sitio no se está aprovechando al 100%. Podría haber presencia de malezas o pastos en el sotobosque debido a la entrada de luz.\n\n"
        elif "Sobrepoblado" in stand_rating:
            summary += "⚠️ **Alerta de Competencia**: El rodal está llegando a su límite de capacidad de carga. Es probable que el crecimiento se estanque pronto y comience la mortalidad natural de los individuos más débiles.\n\n"

        # Cobertura de Copa
        summary += f"La **Cobertura de Copa ({canopy_pct:.1f}%)** confirma que el dosel "
        if canopy_pct > 75:
            summary += "está prácticamente cerrado, lo cual protege el suelo de la erosión y mantiene la humedad interna del bosque."
        elif canopy_pct > 40:
            summary += "es semicerrado, permitiendo el desarrollo de estratos medios de vegetación."
        else:
            summary += "es abierto, típico de zonas en regeneración o bosques degradados."
            
        return summary

    @staticmethod
    def generate_ivi_summary(ivi_df):
        """Analiza la estructura de importancia de las especies."""
        if ivi_df.empty: return ""
        
        # Obtener la especie líder (excluyendo la fila de sumatoria si existe)
        clean_ivi = ivi_df.drop('SUMATORIA TOTAL', errors='ignore')
        top_sp = clean_ivi.index[0]
        top_val = clean_ivi.iloc[0]['IVI']
        
        summary = f"### 💎 Análisis de Estructura (IVI)\n"
        summary += f"La especie ecológicamente dominante en este rodal es ***{top_sp}***, con un Índice de Valor de Importancia de **{top_val:.2f}**. "
        
        # Analizar por qué es dominante
        row = clean_ivi.iloc[0]
        reasons = []
        if row['AR_pct'] > 40: reasons.append("gran abundancia numérica")
        if row['DR_pct'] > 40: reasons.append("dominancia física (biomasa/área basal)")
        if row['FR_pct'] > 40: reasons.append("distribución uniforme en todo el sitio")
        
        if reasons:
            summary += f"Su liderazgo se debe principalmente a su " + " y ".join(reasons) + ". "
        
        summary += "\n\n**¿Qué significa esto?** El IVI nos dice quién 'manda' en el bosque. Una especie con IVI alto es la que más influye en el microclima, el ciclo de nutrientes y el hábitat para la fauna local."
        return summary

    @staticmethod
    def generate_biodiversity_summary(indices):
        """Traduce los índices de diversidad a salud ecosistémica."""
        shannon = indices.get('Shannon_H', 0)
        simpson = indices.get('Simpson_D', 0)
        
        summary = "### 🌿 Salud del Ecosistema (Biodiversidad)\n"
        
        # Shannon
        if shannon > 3:
            summary += f"Con un índice de Shannon de **{shannon:.2f}**, el bosque presenta una **diversidad alta**. Es un ecosistema maduro o con gran variedad de nichos ecológicos. "
        elif shannon > 1.5:
            summary += f"La diversidad es **moderada ({shannon:.2f})**. Existe una estructura estable pero con margen para enriquecimiento. "
        else:
            summary += f"La diversidad es **baja ({shannon:.2f})**. El sitio está dominado por muy pocas especies, lo cual lo hace más vulnerable a plagas o cambios climáticos. "

        # Simpson (Dominancia)
        if simpson < 0.3:
            summary += "La baja dominancia de Simpson indica que los recursos están bien repartidos entre las especies, evitando el monopolio de una sola."
        else:
            summary += "Existe una dominancia marcada; una especie está acaparando la mayor parte del espacio vital."
            
        return summary
