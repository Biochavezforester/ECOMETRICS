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

    @staticmethod
    def run_indval(community_matrix, site_groups):
        """
        Calcula el Valor Indicador (IndVal) de Dufrêne & Legendre (1997).
        Devuelve DataFrame ordenado con Especies, Grupos e IndVal score.
        """
        import pandas as pd
        import numpy as np
        
        # Aseguramos que site_groups sea un dict mapeable
        if isinstance(site_groups, pd.Series):
            site_groups = site_groups.to_dict()
            
        groups = np.unique(list(site_groups.values()))
        
        cm = community_matrix.copy()
        cm['__Group__'] = cm.index.map(site_groups)
        
        results = []
        
        for sp in community_matrix.columns:
            if sp == '__Group__': continue
            
            # Promedio de abundancia por sitio dentro de cada grupo
            mean_abund = cm.groupby('__Group__')[sp].mean()
            sum_mean_abund = mean_abund.sum()
            
            # Conteo de presencias (abundancia > 0)
            presence = cm[sp] > 0
            count_pres = presence.groupby(cm['__Group__']).sum()
            n_sites = cm.groupby('__Group__').size()
            
            for g in groups:
                A = mean_abund.get(g, 0) / sum_mean_abund if sum_mean_abund > 0 else 0
                B = count_pres.get(g, 0) / n_sites.get(g, 1)
                
                indval = A * B * 100
                
                if indval > 0:
                     results.append({
                         "Especie": sp,
                         "Asociación / Grupo": g,
                         "Especificidad (A)": round(A, 4),
                         "Fidelidad (B)": round(B, 4),
                         "IndVal (%)": round(indval, 2)
                     })
                     
        df_indval = pd.DataFrame(results)
        if not df_indval.empty:
            df_indval = df_indval.sort_values(by="IndVal (%)", ascending=False).reset_index(drop=True)
             
        return df_indval

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
        
        # -----------------------------------------------------
        # IMPLEMENTACIÓN DE ESTIMACIÓN DE DATOS PERDIDOS (YATES)
        # -----------------------------------------------------
        missing_mask = df_sec["__Y__"].isna()
        n_missing = missing_mask.sum()
        
        yates_applied = False
        yates_info = None
        
        if n_missing == 1 and design == "DBCA":
            try:
                # Identificar el registro con el valor faltante
                missing_idx = df_sec[missing_mask].index[0]
                
                trat_missing = df_sec.loc[missing_idx, "__F1__"] # Tratamiento
                bloq_missing = df_sec.loc[missing_idx, "__F2__"] # Bloque
                
                # 't' y 'r' son el número total de tratamientos y bloques en el diseño
                t_count = len(df_sec["__F1__"].unique())
                r_count = len(df_sec["__F2__"].unique())
                
                # T = Suma del tratamiento donde está el dato perdido
                T_sum = df_sec.loc[df_sec["__F1__"] == trat_missing, "__Y__"].dropna().sum()
                # B = Suma del bloque donde está el dato perdido
                B_sum = df_sec.loc[df_sec["__F2__"] == bloq_missing, "__Y__"].dropna().sum()
                # G = Gran total de todos los datos válidos
                G_sum = df_sec["__Y__"].dropna().sum()
                
                # Fórmula matemática de Yates: X = (r*B + t*T - G) / ((r-1)*(t-1))
                X = (r_count * B_sum + t_count * T_sum - G_sum) / ((r_count - 1) * (t_count - 1))
                
                # Imputar dato
                df_sec.loc[missing_idx, "__Y__"] = X
                yates_applied = True
                
                # Guardar info original para mostrar en UI
                rev_mapping_tmp = {v: k for k, v in mapping.items()}
                yates_info = {
                    "val": X,
                    "trat_name": rev_mapping_tmp.get("__F1__", "Tratamiento"),
                    "trat_val": trat_missing,
                    "bloq_name": rev_mapping_tmp.get("__F2__", "Bloque"),
                    "bloq_val": bloq_missing
                }
            except Exception as e:
                pass # Si ocurre error numérico, se rinde y dropea
                
        # Remueve cualquier otro NA restante (o si no se aplicó Yates)
        df_sec.dropna(subset=["__Y__"], inplace=True)
        
        # 3. Construcción de fórmula con nombres seguros
        if design == "DCA":
            formula = "__Y__ ~ C(__F1__)"
        elif design == "DBCA":
            formula = "__Y__ ~ C(__F1__) + C(__F2__)"
        elif design == "Latino":
            formula = "__Y__ ~ C(__F1__) + C(__F2__) + C(__F3__)"
        elif design == "AxB Factorial":
            if len(factors) == 2:
                formula = "__Y__ ~ C(__F1__) * C(__F2__)"
            else:
                # factors[2] asume bloque
                formula = "__Y__ ~ C(__F3__) + C(__F1__) * C(__F2__)"
        elif design == "Split-Plot":
            # F1: Parcela Mayor, F2: Bloque, F3: Parcela Menor
            # Modelo = Bloque + A + Error(A) + B + AB + Error(B)
            # Error(A) matemáticamente es F1:F2 (A*Bloque)
            formula = "__Y__ ~ C(__F2__) + C(__F1__) + C(__F1__):C(__F2__) + C(__F3__) + C(__F1__):C(__F3__)"
        
        model = ols(formula, data=df_sec).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        if design == "Split-Plot":
            try:
                import scipy.stats as stats
                error_a_idx = "C(__F1__):C(__F2__)"
                
                ms_error_a = anova_table.loc[error_a_idx, 'sum_sq'] / anova_table.loc[error_a_idx, 'df']
                ms_A = anova_table.loc['C(__F1__)', 'sum_sq'] / anova_table.loc['C(__F1__)', 'df']
                
                new_f_A = ms_A / ms_error_a
                new_p_A = stats.f.sf(new_f_A, anova_table.loc['C(__F1__)', 'df'], anova_table.loc[error_a_idx, 'df'])
                
                anova_table.loc['C(__F1__)', 'F'] = new_f_A
                anova_table.loc['C(__F1__)', 'PR(>F)'] = new_p_A
            except:
                pass

        
        # 3.5 Si se aplicó método de Yates, reducir 1 grado de libertad del Error
        if yates_applied and "Residual" in anova_table.index:
            anova_table.loc["Residual", "df"] -= 1
            # Pasar la info al objeto modelo para la Interfaz Web
            model.yates_info = yates_info
        
        # 4. Restaurar nombres originales en los índices de la tabla ANOVA para el reporte
        rev_mapping = {v: k for k, v in mapping.items()}
        # Mapeo de términos de patsy: C(__F1__) -> C(NombreOriginal)
        index_mapping = {}
        for idx in anova_table.index:
            new_idx = idx
            for v, k in rev_mapping.items():
                new_idx = new_idx.replace(v, k)
            
            # Limpieza cosmética de interacciones extrañas de StatsModels
            new_idx = new_idx.replace("C(", "").replace(")", "")
            
            # Etiqueta especial de Split-Plot
            if design == "Split-Plot":
                pm = rev_mapping.get("__F1__", "Mayor")
                blo = rev_mapping.get("__F2__", "Bloque")
                pmn = rev_mapping.get("__F3__", "Menor")
                
                if new_idx == pm: new_idx = f"Parcela Mayor ({pm})"
                elif new_idx == blo: new_idx = f"Bloque ({blo})"
                elif new_idx == f"{pm}:{blo}": new_idx = "Error (a)"
                elif new_idx == pmn: new_idx = f"Parcela Menor ({pmn})"
                elif new_idx == f"{pm}:{pmn}": new_idx = f"Interacción ({pm} x {pmn})"
                elif new_idx == "Residual": new_idx = "Error (b) Residual"
                
            index_mapping[idx] = new_idx
            
        anova_table.rename(index=index_mapping, inplace=True)
        
        # Limpieza Adicional para Factorial
        if design == "AxB Factorial":
            anova_table.index = [str(i).replace(":", " x ") for i in anova_table.index]
        
        return anova_table, model

    @staticmethod
    def run_posthoc(df, response, factor, anova_table=None):
        """Prueba de Tukey HSD."""
        # Se redirige a la nueva implementación robusta
        _, tukey_df = ExperimentalEngine.get_tukey_groups(df, response, factor, anova_table)
        return tukey_df

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
    def get_tukey_groups(df, response, factor, anova_table=None):
        """Genera agrupaciones por letras (a, ab, b) usando el algoritmo de conectividad de medias."""
        import pandas as pd
        import numpy as np
        
        # 1. Calcular estadísticos descriptivos por tratamiento
        stats_df = df.groupby(factor)[response].agg(['mean', 'std', 'count']).sort_values('mean', ascending=False)
        stats_df['se'] = stats_df['std'] / np.sqrt(stats_df['count'])
        trats = stats_df.index.tolist()
        n = len(trats)
        
        # 2. Prueba de Tukey (Obtener matriz de rechazos)
        # Buscar MSE y DF del Error si se provee una tabla ANOVA (para DBCA, Latino, etc)
        mse = None
        df_error = None
        
        if anova_table is not None:
            # Buscar la fila de residuales
            res_key = next((k for k in anova_table.index if "Residual" in str(k) or "Error" in str(k)), None)
            if res_key:
                df_error = anova_table.loc[res_key, 'df']
                mse = anova_table.loc[res_key, 'sum_sq'] / df_error
        
        tukey_sum = None
        
        if mse is not None and df_error is not None:
            # Implementación manual avanzada de Tukey (Aisla el ruido de los bloques)
            from statsmodels.stats.multicomp import tukeyhsd
            groupsunique = np.unique(df[factor])
            
            gmeans, gnobs = [], []
            for g in groupsunique:
                g_data = df[df[factor] == g][response].dropna()
                gmeans.append(g_data.mean())
                gnobs.append(len(g_data))
                
            res = tukeyhsd(np.array(gmeans), np.array(gnobs), mse, df=df_error, alpha=0.05)
            idx1, idx2 = res[0]
            reject = res[1]
            meandiffs = res[2]
            confint = res[4]
            pvals = res[8]
            
            resarr = []
            for i in range(len(idx1)):
                resarr.append({
                    "group1": groupsunique[idx1[i]],
                    "group2": groupsunique[idx2[i]],
                    "meandiff": meandiffs[i],
                    "p-adj": pvals[i],
                    "lower": confint[i][0],
                    "upper": confint[i][1],
                    "reject": reject[i]
                })
            tukey_sum = pd.DataFrame(resarr)
        else:
            # Fallback a Tukey básico (DCA o sin tabla ANOVA)
            from statsmodels.stats.multicomp import pairwise_tukeyhsd
            tukey = pairwise_tukeyhsd(df[response], df[factor], alpha=0.05)
            tukey_sum = pd.DataFrame(tukey.summary().data[1:], columns=tukey.summary().data[0])
        
        # Matriz de adyacencia (Significancia)
        adj_matrix = pd.DataFrame(False, index=trats, columns=trats)
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
        
        # Convertir nombres del DataFrame de Tukey
        traduccion = {
            "group1": "Grupo A",
            "group2": "Grupo B",
            "meandiff": "Diferencia de Medias",
            "p-adj": "p-valor (adj)",
            "lower": "IC Inferior (95%)",
            "upper": "IC Superior (95%)",
            "reject": "Diferencia Significativa"
        }
        tukey_sum.rename(columns=traduccion, inplace=True)
        tukey_sum["Diferencia Significativa"] = tukey_sum["Diferencia Significativa"].map({True: "SÍ ✅", False: "No ❌"})
        
        return res_df, tukey_sum

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
