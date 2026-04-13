class StatsProEngine:
    """
    Motor para análisis bioestadísticos avanzados.
    Incluye correlaciones, ordenación y clustering.
    """
    @staticmethod
    def calculate_correlation(df, method='pearson'):
        """Calcula la matriz de correlación."""
        return df.corr(method=method)

    @staticmethod
    def get_community_matrix(df, site_col, species_col, abundance_col):
        """Convierte datos largos a una matriz de comunidad (sitio x especie)."""
        return df.pivot_table(index=site_col, columns=species_col, values=abundance_col, fill_value=0)

    @staticmethod
    def run_pca(community_matrix):
        """Ejecuta Análisis de Componentes Principales (PCA)."""
        from sklearn.decomposition import PCA
        from sklearn.preprocessing import StandardScaler
        
        # Escalamiento (importante para PCA)
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(community_matrix)
        
        pca = PCA(n_components=2)
        components = pca.fit_transform(scaled_data)
        
        df_pca = pd.DataFrame(data=components, columns=['PC1', 'PC2'])
        df_pca.index = community_matrix.index
        return df_pca, pca.explained_variance_ratio_

    
    @staticmethod
    def calculate_similarity(community_matrix, method='braycurtis'):
        """Calcula matriz de similitud/disimilitud."""
        from scipy.spatial.distance import pdist, squareform
        
        # Nota: scikit-learn o scipy para distancias
        distances = pdist(community_matrix, metric=method if method != 'braycurtis' else 'braycurtis')
        return pd.DataFrame(squareform(distances), index=community_matrix.index, columns=community_matrix.index)

class ExperimentalEngine:
    """
    Motor para diseños experimentales y pruebas de hipótesis.
    Soporta formatos anchos (Columnas = Tratamientos) para facilitar el uso.
    """
    
    @staticmethod
    def melt_wide_to_long(df, id_vars, value_name="Respuesta", var_name="Tratamiento"):
        """Convierte formato ancho a largo y asegura que la respuesta sea numérica."""
        import pandas as pd
        melted = df.melt(id_vars=id_vars, var_name=var_name, value_name=value_name)
        
        # Forzar conversión numérica (maneja comas de Excel español y otros ruidos)
        if melted[value_name].dtype == object:
            melted[value_name] = melted[value_name].astype(str).str.replace(',', '.', regex=True)
            
        melted[value_name] = pd.to_numeric(melted[value_name], errors='coerce')
        
        # Eliminar registros donde la respuesta no sea un número válido
        melted = melted.dropna(subset=[value_name])
        
        # Forzar tipo float64 final para evitar detecciones categóricas en endog
        melted[value_name] = melted[value_name].astype(float)
        
        return melted
    
    @staticmethod
    def check_assumptions(df, response_col, group_col):
        """Valida normatividad y homocedasticidad."""
        from scipy import stats
        
        # Normatividad (Shapiro-Wilk)
        shapiro_results = {}
        for group in df[group_col].unique():
            data = df[df[group_col] == group][response_col]
            if len(data) >= 3:
                _, p = stats.shapiro(data)
                shapiro_results[group] = p
        
        # Homocedasticidad (Levene)
        groups_data = [df[df[group_col] == g][response_col] for g in df[group_col].unique()]
        _, p_levene = stats.levene(*groups_data)
        
        return shapiro_results, p_levene

    @staticmethod
    def run_anova(df, response, factors, design="DCA"):
        """
        Ejecuta ANOVA con blindaje total. 
        Renombra internamente a nombres genéricos para evitar fallos de patsy/statsmodels.
        """
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
        import pandas as pd
        
        # 1. Crear copia y mapear a nombres internos seguros
        mapping = {response: "__Y__"}
        for i, f in enumerate(factors):
            mapping[f] = f"__F{i+1}__"
            
        df_sec = df[list(mapping.keys())].copy()
        df_sec.rename(columns=mapping, inplace=True)
        
        # 2. Asegurar limpieza absoluta de la respuesta
        df_sec["__Y__"] = pd.to_numeric(df_sec["__Y__"], errors='coerce').astype(float)
        df_sec.dropna(subset=["__Y__"], inplace=True)
        
        # 3. Construcción de fórmula con nombres seguros
        if design == "DCA":
            formula = "__Y__ ~ C(__F1__)"
        elif design == "DBCA":
            formula = "__Y__ ~ C(__F1__) + C(__F2__)"
        elif design == "Latino":
            formula = "__Y__ ~ C(__F1__) + C(__F2__) + C(__F3__)"
        
        model = ols(formula, data=df_sec).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        # 4. Restaurar nombres originales en los índices de la tabla ANOVA para el reporte
        rev_mapping = {v: k for k, v in mapping.items()}
        # Mapeo de términos de patsy: C(__F1__) -> C(NombreOriginal)
        index_mapping = {}
        for idx in anova_table.index:
            new_idx = idx
            for v, k in rev_mapping.items():
                new_idx = new_idx.replace(v, k)
            index_mapping[idx] = new_idx
            
        anova_table.rename(index=index_mapping, inplace=True)
        
        return anova_table, model

    @staticmethod
    def run_posthoc(df, response, factor):
        """Prueba de Tukey HSD."""
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        return pairwise_tukeyhsd(endog=df[response], groups=df[factor], alpha=0.05)

    @staticmethod
    def format_tukey_to_df(tukey_result):
        """Convierte el resultado de Tukey a un DataFrame elegante en español."""
        import pandas as pd
        # Extraer datos del objeto SimpleTable
        data = tukey_result.summary().data
        df_res = pd.DataFrame(data[1:], columns=data[0])
        
        # Traducción de columnas
        traduccion = {
            "group1": "Grupo A",
            "group2": "Grupo B",
            "meandiff": "Diferencia de Medias",
            "p-adj": "p-valor (adj)",
            "lower": "IC Inferior (95%)",
            "upper": "IC Superior (95%)",
            "reject": "Diferencia Significativa"
        }
        df_res.rename(columns=traduccion, inplace=True)
        
        # Limpieza de valores booleanos
        df_res["Diferencia Significativa"] = df_res["Diferencia Significativa"].map({True: "SÍ ✅", False: "No ❌"})
        
        return df_res

    @staticmethod
    def get_tukey_groups(df, response, factor):
        """Genera agrupaciones por letras (a, ab, b) usando el algoritmo de conectividad de medias."""
        import pandas as pd
        import numpy as np
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        
        # 1. Calcular estadísticos descriptivos por tratamiento
        stats_df = df.groupby(factor)[response].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)
        stats_df['se'] = stats_df['std'] / np.sqrt(stats_df['count'])
        trats = stats_df.index.tolist()
        n = len(trats)
        
        # 2. Prueba de Tukey (Obtener matriz de rechazos)
        tukey = pairwise_tukeyhsd(df[response], df[factor], alpha=0.05)
        
        # Matriz de adyacencia (Significancia)
        adj_matrix = pd.DataFrame(False, index=trats, columns=trats)
        tukey_sum = pd.DataFrame(tukey.summary().data[1:], columns=tukey.summary().data[0])
        for _, row in tukey_sum.iterrows():
            g1, g2 = row['group1'], row['group2']
            rej = row['reject'] == True or str(row['reject']).lower() == 'true'
            if g1 in adj_matrix.index and g2 in adj_matrix.index:
                adj_matrix.loc[g1, g2] = rej
                adj_matrix.loc[g2, g1] = rej

        # 3. Algoritmo de Agrupamiento
        # Se asignan letras a grupos que NO son significativamente diferentes
        alphabet = list("abcdefghijklmnopqrstuvwxyz")
        res_letters = {t: "" for t in trats}
        active_groups = [] # Listas de tratamientos que pueden compartir una letra
        
        for i in range(n):
            matched = False
            for group_idx, members in enumerate(active_groups):
                # Si el tratamiento 'i' NO es diferente de NINGUNO del grupo, entra
                if all(not adj_matrix.loc[trats[i], m] for m in members):
                    active_groups[group_idx].append(trats[i])
                    matched = True
            
            if not matched:
                active_groups.append([trats[i]])
        
        # Consolidar letras (cada grupo es una letra)
        for idx, members in enumerate(active_groups):
            letter = alphabet[idx % len(alphabet)]
            for m in members:
                res_letters[m] += letter

        # 4. Construir DataFrame final de Grupos
        res_df = pd.DataFrame({
            "Tratamiento": trats,
            "Media": stats_df['mean'].values,
            "Error Est.": stats_df['se'].values,
            "Desv. Est.": stats_df['std'].values,
            "Grupo": [res_letters[t] for t in trats]
        })
        
        return res_df, ExperimentalEngine.format_tukey_to_df(tukey)

    @staticmethod
    def get_human_interpretation(tukey_df):
        """Genera una conclusión en lenguaje natural sobre qué tratamiento es mejor."""
        conclusiones = []
        for _, row in tukey_df.iterrows():
            if "SÍ ✅" in str(row["Diferencia Significativa"]):
                g_a = row["Grupo A"]
                g_b = row["Grupo B"]
                diff = row["Diferencia de Medias"]
                sentido = "mayor" if diff > 0 else "menor"
                conclusiones.append(f"- El tratamiento **{g_b}** obtuvo un valor significativamente **{sentido}** que **{g_a}** (Dif: {abs(diff):.2f}).")
        
        if not conclusiones:
            return "No se encontraron diferencias estadísticas contundentes entre los tratamientos analizados. Todos se comportaron de manera similar."
        
        return "### 💡 Conclusión Directa:\n" + "\n".join(conclusiones)

    @staticmethod
    def run_hutcheson_t_test(h1, n1, h2, n2, s1, s2):
        """
        Prueba de t de Hutcheson para comparar dos índices de Shannon.
        h = Shannon H', n = total individuos, s = número especies.
        Versión simplificada mediante expansión de Taylor (Aproximación Estándar).
        """
        import numpy as np
        from scipy import stats
        
        # Aproximación de varianza (Taylor Series)
        v1 = (s1/n1 - (h1**2)/n1)
        v2 = (s2/n2 - (h2**2)/n2)
        
        v_total = v1 + v2
        if v_total <= 0:
            return 0.0, 1.0, 1.0
        
        # t-statistic
        t_stat = (h1 - h2) / np.sqrt(v_total)
        
        # Grados de libertad corregidos
        df_num = v_total**2
        df_den = (v1**2 / n1) + (v2**2 / n2)
        
        if df_den <= 0:
            df_val = max(1.0, n1 + n2 - 2)
        else:
            df_val = df_num / df_den
        
        p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df_val))
        return t_stat, p_val, df_val

    @staticmethod
    def calculate_experimental_metrics(df, model, response_col):
        """Calcula métricas detalladas incluyendo componentes de cálculo manual corregidos (FC)."""
        import numpy as np
        
        # Asegurar datos numéricos
        valid_y = df[response_col].dropna()
        n_obs = len(valid_y)
        sum_y = float(valid_y.sum())
        
        # Factor de Corrección (FC) = (Sumatoria^2) / N
        # Asegurar cálculo con alta precisión decimal
        sum_y_val = float(sum_y)
        n_obs_val = float(n_obs)
        fc = (sum_y_val**2) / n_obs_val if n_obs_val > 0 else 0.0
        
        # Coeficiente de Variación (CV) y R2
        r2 = model.rsquared
        mse = model.mse_resid
        rmse = np.sqrt(mse)
        mean_y = valid_y.mean()
        cv = (rmse / mean_y) * 100 if mean_y != 0 else 0
        
        return {
            "R2": r2,
            "CV": cv,
            "Media": mean_y,
            "Sumatoria": sum_y,
            "FC": fc,
            "N": n_obs
        }

    @staticmethod
    def format_anova_to_df(anova_table):
        """Convierte la tabla ANOVA a un formato profesional expandido para reporte científico."""
        import pandas as pd
        import numpy as np
        from scipy import stats
        
        df_res = anova_table.copy()
        
        # Asegurar nombres de columnas internos (Solo si es la tabla cruda de statsmodels)
        if len(df_res.columns) == 4:
            df_res.columns = ["sum_sq", "df", "F", "PR(>F)"]
        
        # 1. Calcular Cuadrado Medio (C.M.)
        df_res["C.M."] = df_res["sum_sq"] / df_res["df"]
        
        # 2. Calcular F-Tabulado
        df_den = df_res.loc["Residual", "df"]
        def calculate_ftab(row):
            if row.name == "Residual" or pd.isna(row["F"]):
                return np.nan
            return stats.f.ppf(0.95, row["df"], df_den)
        df_res["F-Tabulado"] = df_res.apply(calculate_ftab, axis=1)
        
        # 3. Regla de Decisión de H0
        def decision_rule(row):
            if row.name == "Residual" or pd.isna(row["F"]) or pd.isna(row["F-Tabulado"]):
                return "-"
            if row["F"] > row["F-Tabulado"]:
                return "Rechaza H0 (Sig) ✅"
            else:
                return "No Rechaza H0 (No Sig) ❌"
        df_res["Regla de Decisión"] = df_res.apply(decision_rule, axis=1)
        
        # 4. Traducción de fuentes de variación
        traduccion_idx = {
            "C(Tratamiento)": "Tratamiento (SCTr)",
            "C(Bloque)": "Bloque (SCB)",
            "C(Fila)": "Fila (SCF)",
            "C(Columna)": "Columna (SCC)",
            "Residual": "Error Residual (SCE)"
        }
        df_res.index = [traduccion_idx.get(idx, idx) for idx in df_res.index]
        
        # 5. Agregar Fila TOTAL (SCT)
        total_ss = df_res["sum_sq"].sum()
        total_df = df_res["df"].sum()
        df_res.loc["TOTAL (SCT)"] = [total_ss, total_df, np.nan, np.nan, np.nan, np.nan, "-"]
        
        # Reordenar y traducir columnas finales
        cols_order = ["sum_sq", "df", "C.M.", "F", "F-Tabulado", "PR(>F)", "Regla de Decisión"]
        df_res = df_res[cols_order]
        
        traduccion_cols = {
            "sum_sq": "Suma Cuadrados (SC)",
            "df": "G.L.",
            "C.M.": "C.M. (Varianza)",
            "F": "FCAL (F-Calc)",
            "F-Tabulado": "FTAB (0.05)",
            "PR(>F)": "p-valor"
        }
        df_res = df_res.rename(columns=traduccion_cols)
        
        # Formatear números para reporte
        df_res = df_res.replace([np.inf, -np.inf], np.nan)
        def format_val(val):
            if isinstance(val, str): return val
            if pd.isna(val): return "-"
            if val < 0.0001 and val > 0: return "< 0.0001"
            return f"{val:.4f}"
            
        for col in df_res.columns:
            if col != "Regla de Decisión":
                df_res[col] = df_res[col].apply(format_val)
            
        return df_res

    @staticmethod
    def run_power_analysis(n_groups, n_samples_per_group, effect_size=0.4, alpha=0.05):
        """
        Análisis de Poder Estadístico (F-Test ANOVA).
        Indica la probabilidad de detectar un efecto real.
        """
        from statsmodels.stats.power import FTestAnovaPower
        analysis = FTestAnovaPower()
        power = analysis.solve_power(effect_size=effect_size, nobs=n_groups * n_samples_per_group, alpha=alpha, k_groups=n_groups)
        return power

    @staticmethod
    def run_non_parametric(df, response, group, design="Kruskal"):
        """Pruebas No Paramétricas."""
        from scipy import stats
        groups_data = [df[df[group] == g][response] for g in df[group].unique()]
        
        if design == "Kruskal":
            return stats.kruskal(*groups_data)
        elif design == "Friedman":
            # Requiere matriz balanceada
            pivot = df.pivot(index='Bloque', columns=group, values=response) # Asume columna 'Bloque'
            return stats.friedmanchisquare(*[pivot[c] for c in pivot.columns])
        return None

class AdvancedStatsEngine:
    """
    Modelos de Regresión, Crecimiento y Análisis Multivariado Avanzado.
    """
    
    @staticmethod
    def run_regression(df, y_col, x_cols, model_type="Linear"):
        """Regresión Lineal y Logística."""
        import statsmodels.api as sm
        X = sm.add_constant(df[x_cols])
        y = df[y_col]
        
        if model_type == "Linear":
            model = sm.OLS(y, X).fit()
        elif model_type == "Logistic":
            model = sm.Logit(y, X).fit()
        
        # Añadir métricas extendidas al objeto del modelo
        if model_type == "Linear":
            model.aic_val = model.aic
            model.bic_val = model.bic
            model.adj_r2 = model.rsquared_adj
            model.rmse = np.sqrt(model.mse_resid)
            
        return model

    @staticmethod
    def growth_model(t, model="Gompertz"):
        """Modelos de crecimiento (Para curve_fit)."""
        if model == "Gompertz":
            # V = A * exp(-B * exp(-K * t))
            return lambda t, A, B, K: A * np.exp(-B * np.exp(-K * t))
        elif model == "Chapman-Richards":
            # V = A * (1 - exp(-K * t))^M
            return lambda t, A, K, M: A * (1 - np.exp(-K * t))**M
        return None

    @staticmethod
    def run_nmds(community_matrix):
        """Escalamiento Multidimensional No Métrico."""
        from sklearn.manifold import MDS
        nmds = MDS(n_components=2, metric=False, dissimilarity='precomputed', random_state=42)
        
        # Calcular distancias primero (Bray-Curtis por defecto)
        from scipy.spatial.distance import pdist, squareform
        dist_matrix = squareform(pdist(community_matrix, metric='braycurtis'))
        
        embedding = nmds.fit_transform(dist_matrix)
        df_nmds = pd.DataFrame(embedding, columns=['NMDS1', 'NMDS2'], index=community_matrix.index)
        return df_nmds, nmds.stress_
