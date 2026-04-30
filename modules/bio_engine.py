import numpy as np
import pandas as pd
from scipy.special import comb, gammaln



class BiodiversityEngine:
    """
    Motor central de ECOMETRICS para el cálculo de diversidad.
    Implementa iNEXT (Rarefacción y Extrapolación) basado en Números de Hill.
    """
    
    @staticmethod
    def calculate_hill_numbers(abundances, q=0):
        """
        Calcula la diversidad verdadera (Números de Hill).
        q=0: Riqueza de especies
        q=1: Exponencial de Shannon
        q=2: Inverso de Simpson
        """
        abundances = np.array(abundances)
        abundances = abundances[abundances > 0]
        if len(abundances) == 0: return 0
        
        p = abundances / np.sum(abundances)
        
        if q == 0:
            return len(abundances)
        elif q == 1:
            return np.exp(-np.sum(p * np.log(p)))
        elif q == 2:
            return 1 / np.sum(p**2)
        else:
            return (np.sum(p**q))**(1 / (1 - q))

    @staticmethod
    def calculate_all_indices(abundances):
        """
        Calcula un catálogo completo de índices de biodiversidad.
        """
        abundances = np.array(abundances)
        abundances = abundances[abundances > 0]
        n_total = np.sum(abundances)
        s_obs = len(abundances)
        
        if n_total == 0 or s_obs == 0:
            return {}
            
        p = abundances / n_total
        
        # 1. Índice de Shannon-Wiener (H')
        shannon_h = -np.sum(p * np.log(p))
        
        # 2. Diversidad de Simpson (D)
        simpson_d = np.sum(p**2)
        
        # 3. Equitatividad de Pielou (J')
        pielou_j = shannon_h / np.log(s_obs) if s_obs > 1 else 1.0
        
        # 4. Índice de Margalef (Riqueza)
        margalef = (s_obs - 1) / np.log(n_total) if n_total > 1 else 0
        
        # 5. Índice de Menhinick
        menhinick = s_obs / np.sqrt(n_total)
        
        # 6. Índice de Brillouin (Para muestras no aleatorias)
        # H = (ln(N!) - sum(ln(ni!))) / N
        ln_n_fact = gammaln(n_total + 1)
        ln_ni_fact_sum = np.sum(gammaln(abundances + 1))
        brillouin = (ln_n_fact - ln_ni_fact_sum) / n_total
        
        # 7. Dominancia de Berger-Parker
        berger_parker = np.max(abundances) / n_total
        
        # 8. Índice de McIntosh
        mcintosh_d = (n_total - np.sqrt(np.sum(abundances**2))) / (n_total - np.sqrt(n_total)) if n_total > 1 else 0
        
        return {
            "Shannon_H": shannon_h,
            "Simpson_D": simpson_d,
            "Simpson_Inv": 1/simpson_d,
            "Pielou_J": pielou_j,
            "Margalef": margalef,
            "Menhinick": menhinick,
            "Brillouin": brillouin,
            "Berger_Parker": berger_parker,
            "McIntosh": mcintosh_d,
            "S_obs": s_obs,
            "N_total": n_total
        }

    @staticmethod
    def chao1_estimator(abundances):
        """
        Estimador de riqueza Chao1 (Riqueza asintótica basada en individuos).
        """
        abundances = np.array(abundances)
        s_obs = np.sum(abundances > 0)
        f1 = np.sum(abundances == 1)
        f2 = np.sum(abundances == 2)
        
        if f2 > 0:
            chao1 = s_obs + (f1**2) / (2 * f2)
        else:
            chao1 = s_obs + (f1 * (f1 - 1)) / (2 * (f2 + 1))
        return chao1

    @staticmethod
    def iNEXT_rarefaction(abundances, m):
        """
        Rarefacción basada en individuos (Abundancia).
        """
        abundances = np.array(abundances)
        n = np.sum(abundances)
        s_obs = np.sum(abundances > 0)
        if m >= n: return s_obs
        
        sum_term = 0
        for x_i in abundances:
            if x_i > 0:
                term = comb(n - x_i, m) / comb(n, m)
                sum_term += term
        return s_obs - sum_term

    @staticmethod
    def iNEXT_extrapolation(abundances, m_plus):
        """
        Extrapolación basada en individuos (Abundancia).
        """
        abundances = np.array(abundances)
        n = np.sum(abundances)
        s_obs = np.sum(abundances > 0)
        f1 = np.sum(abundances == 1)
        f2 = np.sum(abundances == 2)
        
        if f2 > 0:
            f0_hat = (f1**2 / (2 * f2))
        else:
            f0_hat = (f1 * (f1 - 1) / 2)
            
        if f0_hat == 0: return s_obs
        
        term = (1 - (f1 / (n * f0_hat + f1)))**m_plus
        return s_obs + f0_hat * (1 - term)

    @staticmethod
    def sample_based_rarefaction(incidence_freqs, t, m):
        """
        Rarefacción basada en muestras (Incidencia).
        incidence_freqs: [T, Q1, Q2, ..., Qk] donde T es el total de sitios.
        m: número de sitios de referencia (esfuerzo).
        """
        T = incidence_freqs[0]
        y = np.array(incidence_freqs[1:])
        s_obs = len(y)
        
        if m > T:
            return s_obs
            
        sum_term = 0
        for y_i in y:
            term = comb(T - y_i, m) / comb(T, m)
            sum_term += term
        return s_obs - sum_term

    @staticmethod
    def sample_based_extrapolation(incidence_freqs, m_plus):
        """
        Extrapolación basada en muestras (Incidencia).
        """
        T = incidence_freqs[0]
        y = np.array(incidence_freqs[1:])
        s_obs = len(y)
        q1 = np.sum(y == 1)
        q2 = np.sum(y == 2)
        
        if q2 > 0:
            q0_hat = ((T - 1) / T) * (q1**2 / (2 * q2))
        else:
            q0_hat = ((T - 1) / T) * (q1 * (q1 - 1) / 2)
            
        if q0_hat == 0: return s_obs
        
        term = (1 - (q1 / (T * q0_hat + q1)))**m_plus
        return s_obs + q0_hat * (1 - term)

    @staticmethod
    def calculate_beta_diversity(comm_matrix):
        """
        Calcula la beta diversidad (Sorensen / Bray-Curtis).
        Descompone en recambio (turnover) y anidamiento (nestedness) simplificado.
        """
        from scipy.spatial.distance import pdist, squareform
        
        # Sorensen (Presencia/Ausencia)
        pres_abs = (comm_matrix > 0).astype(int)
        dist_sorensen = pdist(pres_abs, metric='dice') # 1-dice = Sorensen similarity
        mat_sorensen = squareform(dist_sorensen)
        
        # Bray-Curtis (Abundancia)
        dist_bray = pdist(comm_matrix, metric='braycurtis')
        mat_bray = squareform(dist_bray)
        
        return {
            "Sorensen_Matrix": pd.DataFrame(mat_sorensen, index=comm_matrix.index, columns=comm_matrix.index),
            "Bray_Matrix": pd.DataFrame(mat_bray, index=comm_matrix.index, columns=comm_matrix.index),
            "Media_Sorensen": np.mean(dist_sorensen),
            "Media_Bray": np.mean(dist_bray)
        }

    @staticmethod
    def run_indval(comm_matrix, clusters):
        """
        Análisis de Valor Indicador (IndVal) de Dufrêne & Legendre.
        clusters: serie o lista con la clasificación de los sitios.
        """
        # Calcular especificidad (A) y fidelidad (B)
        # IndVal = A * B * 100
        indval_results = {}
        unique_clusters = np.unique(clusters)
        
        for cluster in unique_clusters:
            sites_in_cluster = comm_matrix.index[clusters == cluster]
            sites_out_cluster = comm_matrix.index[clusters != cluster]
            
            for species in comm_matrix.columns:
                # A: Especificidad (Media abundancia en cluster / Suma medias abundancias en todos)
                mean_in = comm_matrix.loc[sites_in_cluster, species].mean()
                mean_total = comm_matrix[species].mean()
                A = mean_in / (comm_matrix.groupby(clusters)[species].mean().sum()) if mean_total > 0 else 0
                
                # B: Fidelidad (Proporción de sitios del cluster donde está la especie)
                n_sites_cluster = len(sites_in_cluster)
                n_occ_cluster = np.sum(comm_matrix.loc[sites_in_cluster, species] > 0)
                B = n_occ_cluster / n_sites_cluster if n_sites_cluster > 0 else 0
                
                iv = A * B * 100
                if iv > 0:
                    if species not in indval_results or iv > indval_results[species]['iv']:
                        indval_results[species] = {'cluster': cluster, 'iv': iv, 'A': A, 'B': B}
                        
        return pd.DataFrame.from_dict(indval_results, orient='index').sort_values('iv', ascending=False)

    @staticmethod
    def get_inext_curve(data, is_incidence=False, max_multiplier=2):
        """
        Genera una serie de puntos para la curva.
        Si is_incidence=True: data = [T, y1, y2, ...]
        """
        if not is_incidence:
            abundances = np.array(data)
            n = np.sum(abundances)
            points = []
            for m in np.linspace(1, n, 20).astype(int):
                s = BiodiversityEngine.iNEXT_rarefaction(abundances, m)
                points.append({"m": m, "s": s, "type": "Rarefacción"})
            for m_ext in np.linspace(1, n * (max_multiplier - 1), 20).astype(int):
                s = BiodiversityEngine.iNEXT_extrapolation(abundances, m_ext)
                points.append({"m": n + m_ext, "s": s, "type": "Extrapolación"})
        else:
            T = data[0]
            points = []
            for m in np.linspace(1, T, 15).astype(int):
                s = BiodiversityEngine.sample_based_rarefaction(data, T, m)
                points.append({"m": m, "s": s, "type": "Rarefacción"})
            for m_ext in np.linspace(1, T * (max_multiplier - 1), 15).astype(int):
                s = BiodiversityEngine.sample_based_extrapolation(data, m_ext)
                points.append({"m": T + m_ext, "s": s, "type": "Extrapolación"})
                
        return pd.DataFrame(points)
