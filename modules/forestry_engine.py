import numpy as np
import pandas as pd

class ForestryEngine:
    """
    Motor científico para el análisis de inventarios forestales de campo.
    Basado en los sistemas compatibles de ahusamiento y volumen de Fang et al. (2000)
    y modelos de crecimiento GADA (Vargas-Larreta, Cruz-Cobos, 2017).
    """
    
    # CATÁLOGO DE ESPECIES (Sierra Madre Occidental / Durango)
    # Mapeo Nombre Científico -> ID numérico
    SPECIES_CATALOG = {
        "pinus cooperi": "1", "pinus durangensis": "2", "pinus arizonica": "3",
        "pinus leiophylla": "4", "pinus teocote": "5", "pinus engelmannii": "6",
        "pinus lumholtzii": "7", "pinus ayacahuite": "8", "pinus oocarpa": "9",
        "pinus douglasiana": "10", "pinus michoacana": "11", "pinus chihuahuana": "12",
        "pinus cembroides": "13", "pinus tenuifolia": "14", "pinus herrerae": "15",
        "pinus maximinoi": "16", "pinus sp": "30", "juniperus deppeana": "31",
        "juniperus flaccida": "32", "juniperus monticola": "33", "juniperus sp": "34",
        "cupressus lusitanica": "35", "pseudotsuga menziesii": "36", "picea chihuahuana": "37",
        "abies durangensis": "38", "oyamel": "38", "quercus sideroxyla": "41",
        "quercus durifolia": "42", "quercus obtusata": "43", "quercus coccolobifolia": "44",
        "quercus laeta": "45", "quercus grisea": "46", "quercus eduardii": "47",
        "quercus urbanii": "48", "quercus gentryi": "49", "quercus resinosa": "50",
        "quercus crassifolia": "51", "quercus chihuahuensis": "52", "quercus viminea": "53",
        "quercus depressipes": "54", "quercus emoryi": "55", "quercus salicifolia": "56",
        "quercus castanea": "57", "quercus aristata": "58", "quercus magnoliifolia": "59",
        "quercus arizonica": "60", "quercus fulva": "61", "quercus radiata": "62",
        "quercus candicans": "63", "quercus scytophylla": "64", "quercus splendens": "65",
        "quercus rugosa": "66", "quercus subspathulata": "67", "quercus tarahumara": "68",
        "quercus mcvaughii": "69", "quercus conzattii": "70", "quercus acutifolia": "71",
        "quercus sp": "100", "alnus firmifolia": "101", "alnus jorullensis": "102",
        "alnus acuminata": "103", "alnus sp": "104", "arbutus xalapensis": "105",
        "madroño": "105", "arbutus sp": "106", "guazuma ulmifolia": "107",
        "prunus serotina": "108", "capulin": "108", "fraxinus sp": "109", "fresno": "109",
        "populus tremuloides": "110", "cedrela odorata": "111", "otras hojosas": "112"
    }

    # SISTEMA BIOMÉTRICO REGIONAL (Betas Cruz-Cobos / Vargas-Larreta)
    # Formato: id: {b0, b1, b2} para V = b0 * D^b1 * H^b2
    SCIENTIFIC_SYSTEMS = {
        "1": {"b0": 5.9522e-05, "b1": 2.10893, "b2": 0.78958, "nombre": "Pinus cooperi"},
        "2": {"b0": 6.3079e-05, "b1": 1.94656, "b2": 0.94301, "nombre": "Pinus durangensis"},
        "3": {"b0": 8.3007e-05, "b1": 2.04427, "b2": 0.63848, "nombre": "Pinus arizonica"},
        "4": {"b0": 4.9267e-05, "b1": 2.04461, "b2": 0.92302, "nombre": "Pinus leiophylla"},
        "5": {"b0": 4.9267e-05, "b1": 2.04461, "b2": 0.92302, "nombre": "Pinus teocote"},
        "6": {"b0": 5.4016e-05, "b1": 2.04966, "b2": 0.83787, "nombre": "Pinus engelmannii"},
        "7": {"b0": 6.7235e-05, "b1": 2.26804, "b2": 0.56673, "nombre": "Pinus lumholtzii"},
        "8": {"b0": 5.8773e-05, "b1": 2.03463, "b2": 0.82447, "nombre": "Pinus ayacahuite"},
        "9": {"b0": 9.2170e-05, "b1": 2.09228, "b2": 0.65355, "nombre": "Pinus oocarpa"},
        "10": {"b0": 6.4239e-05, "b1": 2.17985, "b2": 0.67787, "nombre": "Pinus douglasiana"},
        "11": {"b0": 5.3210e-05, "b1": 2.06290, "b2": 0.87861, "nombre": "Pinus michoacana"},
        "12": {"b0": 4.9267e-05, "b1": 2.04461, "b2": 0.92302, "nombre": "Pinus chihuahuana"},
        "13": {"b0": 8.3007e-05, "b1": 2.04427, "b2": 0.63848, "nombre": "Pinus cembroides"},
        "14": {"b0": 5.8857e-05, "b1": 2.08693, "b2": 0.79798, "nombre": "Pinus tenuifolia"},
        "15": {"b0": 7.0238e-05, "b1": 2.11996, "b2": 0.69954, "nombre": "Pinus herrerae"},
        "16": {"b0": 5.8857e-05, "b1": 2.08693, "b2": 0.79798, "nombre": "Pinus maximinoi"},
        "172": {"b0": 6.3417e-05, "b1": 2.10871, "b2": 0.75920}
    }
    
    # Grupos extendidos (41-71 share the same beta)
    GROUP_BETAS = {
        "G_41_71": {"b0": 6.1634e-05, "b1": 2.05574, "b2": 0.77583},
        "G_30_40": {"b0": 8.3007e-05, "b1": 2.04427, "b2": 0.63848},
        "G_101_112": {"b0": 8.3007e-05, "b1": 2.04427, "b2": 0.63848}
    }

    # COEFICIENTES GENÉRICOS (Backup Global)
    GENERIC_COEFFICIENTS = {
        "Generica_Conifera": {"b0": 5.95e-05, "b1": 2.0, "b2": 0.8},
        "Generica_Latifoliada": {"b0": 6.42e-05, "b1": 2.1, "b2": 0.7}
    }

    @staticmethod
    def estimate_volume(dbh_cm, height_m, species="1", use_scientific=True):
        """Estimación volumétrica directa con betas del usuario."""
        # 1. Pre-mapeo: Si es un nombre de texto, convertir a ID usando el catálogo oficial
        sp_lower = str(species).strip().lower()
        if sp_lower in ForestryEngine.SPECIES_CATALOG:
            sp_key = ForestryEngine.SPECIES_CATALOG[sp_lower]
        else:
            sp_key = sp_lower.split('.')[0] # "1.0" -> "1"
        
        if use_scientific:
            # 2. Búsqueda en individuales (IDs 1-16, 172)
            if sp_key in ForestryEngine.SCIENTIFIC_SYSTEMS:
                p = ForestryEngine.SCIENTIFIC_SYSTEMS[sp_key]
            else:
                try:
                    # 3. Búsqueda por rangos de IDs numéricos
                    num_key = int(float(sp_key))
                    if 41 <= num_key <= 71 or sp_key in ["100", "171"]:
                        p = ForestryEngine.GROUP_BETAS["G_41_71"]
                    elif 30 <= num_key <= 40:
                        p = ForestryEngine.GROUP_BETAS["G_30_40"]
                    elif 101 <= num_key <= 112:
                        p = ForestryEngine.GROUP_BETAS["G_101_112"]
                    else:
                        p = ForestryEngine.SCIENTIFIC_SYSTEMS["2"]  # Fallback: P. durangensis
                except (ValueError, TypeError):
                    # 4. Fallback final taxonómico si falla todo lo anterior
                    if "pinus" in sp_lower:
                        p = ForestryEngine.SCIENTIFIC_SYSTEMS["2"]
                    elif any(kw in sp_lower for kw in ["quercus", "arbutus", "alnus", "encino"]):
                        p = ForestryEngine.GENERIC_COEFFICIENTS["Generica_Latifoliada"]
                    else:
                        p = ForestryEngine.GENERIC_COEFFICIENTS["Generica_Conifera"]
        else:
            is_pinus = "Pinus" in str(species)
            p = (ForestryEngine.GENERIC_COEFFICIENTS["Generica_Conifera"] 
                 if is_pinus else ForestryEngine.GENERIC_COEFFICIENTS["Generica_Latifoliada"])
            
        try:
            # Fórmula: V = b0 * D^b1 * H^b2
            v = p["b0"] * (dbh_cm**p["b1"]) * (height_m**p["b2"])
            return max(0, v)
        except:
            return 0

    @staticmethod
    def calculate_basal_area(dbh_cm):
        """Calcula el área basal individual (G) en m2."""
        if dbh_cm <= 0: return 0
        return (np.pi * (dbh_cm**2)) / 40000

    @staticmethod
    def calculate_dcq(g_ha, n_ha):
        """Calcula el Diámetro Cuadrático Medio (Dcq) del rodal."""
        if n_ha <= 0: return 0
        return np.sqrt((40000 * g_ha) / (np.pi * n_ha))

    @staticmethod
    def run_fang_taper(dbh_cm, height_m, h_i, species="1"):
        """Modelo de ahusamiento anclado a 1.3m para consistencia física."""
        if h_i >= height_m: return 0
        # Garantiza que a 1.3m el diámetro sea exactamente el DAP
        # d_i = D * ((H - h_i)/(H - 1.3))^k
        k = 0.65 # Exponente promedio para la región
        return dbh_cm * ((height_m - h_i) / (height_m - 1.3))**k

    @staticmethod
    def calculate_site_index_gada(height_m, age_years, species="1"):
        """Modelo GADA para Índice de Sitio."""
        if age_years <= 0: return 0
        b1, b2, b3 = 25.0, 1.5, -0.04
        age_base = 50
        try:
            si = height_m * ( (1 - np.exp(b3 * age_base)) / (1 - np.exp(b3 * age_years)) )**b2
            return si
        except:
            return height_m

    @staticmethod
    def estimate_biomass_carbon(dbh_cm, height_m, species="1", use_scientific=True):
        """Estimación simplificada de biomasa y carbono (IPCC)."""
        vol = ForestryEngine.estimate_volume(dbh_cm, height_m, species, use_scientific)
        # Biomasa = Vol * 0.65 (Densidad + Expansión combinados)
        biomass = vol * 0.65
        # Carbono = Biomasa * 0.5
        carbon = biomass * 0.5
        return biomass, carbon

    @staticmethod
    def calculate_annual_increment(vol_ha, tiempo_paso=10):
        """Calcula el Incremento Corriente Anual (ICA) en m3/ha/año."""
        if tiempo_paso <= 0: return 0
        # Basado en la relación estándar de crecimiento para la región
        # ICA = (Volumen Actual / Tiempo de Paso) * Factor de Crecimiento
        # Usamos un factor de 0.4 para aproximar el incremento neto anual vs el stock total
        return (vol_ha / tiempo_paso) * 0.4

    @staticmethod
    def expand_metrics(df, dap_col="DAP_cm", height_col="Altura_m", species_col="Especie", plot_area_col="Tamaño_Sitio_m2", use_scientific=True):
        """Expande métricas individuales a por hectárea con control de rigor autónomo."""
        df['FE'] = 10000 / df[plot_area_col]
        df['G_m2'] = df[dap_col].apply(ForestryEngine.calculate_basal_area)
        
        # Volumen con betas regionales
        df['V_m3'] = df.apply(lambda row: ForestryEngine.estimate_volume(row[dap_col], row[height_col], row[species_col], use_scientific), axis=1)
        df['Esbeltez'] = (df[height_col] / df[dap_col]) * 100
        
        # Carbono con betas regionales (estimate_biomass_carbon devuelve toneladas)
        res_bc = df.apply(lambda row: ForestryEngine.estimate_biomass_carbon(row[dap_col], row[height_col], row[species_col], use_scientific), axis=1)
        df['B_ha_ton_ind'] = res_bc.apply(lambda x: x[0]) * df['FE']
        df['C_ha_ton_ind'] = res_bc.apply(lambda x: x[1]) * df['FE']
        
        df['N_ha'] = 1 * df['FE']
        df['G_ha'] = df['G_m2'] * df['FE']
        df['V_ha'] = df['V_m3'] * df['FE']
        
        # Asignar totales (ya expandidos individualmente para mayor precisión)
        df['B_ha_ton'] = df['B_ha_ton_ind']
        df['C_ha_ton'] = df['C_ha_ton_ind']
        
        return df

    @staticmethod
    def calculate_ivi(df, species_col="Especie", site_col="Sitio", dap_col="DAP_cm"):
        """
        Calcula el Índice de Valor de Importancia (IVI) para cada especie.
        IVI = Abundancia Relativa + Dominancia Relativa + Frecuencia Relativa (0-300).
        """
        if df.empty: return pd.DataFrame()
        
        # 0. Asegurar que tenemos el área basal
        if 'G_m2' not in df.columns:
            df['G_m2'] = df[dap_col].apply(ForestryEngine.calculate_basal_area)
            
        # 1. Métricas Base por Especie
        # Abundancia (N) y Dominancia (G)
        summary = df.groupby(species_col).agg({
            species_col: 'count',
            'G_m2': 'sum'
        }).rename(columns={species_col: 'N_ind', 'G_m2': 'G_total_m2'})
        
        # Frecuencia (en cuántos sitios aparece)
        freq_data = df.groupby(species_col)[site_col].nunique()
        summary['Frecuencia'] = freq_data
        
        # 2. Totales del Rodal
        total_n = summary['N_ind'].sum()
        total_g = summary['G_total_m2'].sum()
        total_f = summary['Frecuencia'].sum()
        
        # 3. Métricas Relativas (%)
        summary['AR_pct'] = (summary['N_ind'] / total_n) * 100 if total_n > 0 else 0
        summary['DR_pct'] = (summary['G_total_m2'] / total_g) * 100 if total_g > 0 else 0
        summary['FR_pct'] = (summary['Frecuencia'] / total_f) * 100 if total_f > 0 else 0
        
        # 4. IVI Final
        summary['IVI'] = summary['AR_pct'] + summary['DR_pct'] + summary['FR_pct']
        
        return summary.sort_values('IVI', ascending=False)

    @staticmethod
    def calculate_reineke_sdi(n_ha, dcq_cm):
        """Calcula el Índice de Densidad de Reineke (SDI)."""
        if n_ha <= 0 or dcq_cm <= 0: return 0
        return n_ha * (dcq_cm / 25.4)**1.605

    @staticmethod
    def calculate_canopy_cover(df, plot_area_m2, crown_diam_col=None, dap_col="DAP_cm"):
        """
        Calcula el porcentaje de cobertura de copa.
        Si no hay diámetro de copa, estima mediante alometría DAP.
        """
        if df.empty or plot_area_m2 <= 0: return 0
        
        if crown_diam_col and crown_diam_col in df.columns:
            # Área de círculo por cada árbol
            df['_crown_area'] = (np.pi * (df[crown_diam_col]**2)) / 4
        else:
            # Estimación alométrica simple: DC = 0.5 + 0.1 * DAP (m)
            # Solo como referencia si no hay dato de campo
            df['_crown_area'] = (np.pi * ((0.5 + 0.1 * df[dap_col])**2)) / 4
            
        # Sumar áreas de copa expandidas por el Factor de Expansión
        total_crown_area_ha = (df['_crown_area'] * (10000 / plot_area_m2)).sum()
        
        # Cobertura en porcentaje (máximo 100% teóricamente, aunque puede haber traslape)
        coverage_pct = (total_crown_area_ha / 10000) * 100
        return min(100.0, coverage_pct)

    @staticmethod
    def calculate_stand_rating(sdi, sdi_max=1000):
        """Calificación del rodal basada en el Índice de Densidad Relativa (IDR)."""
        if sdi <= 0: return "No Clasificado"
        idr = sdi / sdi_max
        if idr < 0.25: return "Subpoblado (Crecimiento Libre)"
        elif idr < 0.35: return "Transición (Inicio de Competencia)"
        elif idr < 0.60: return "Cierre de Copas (Crecimiento Máximo)"
        elif idr < 0.80: return "Sobrepoblado (Mortalidad Inminente)"
        else: return "Saturado"
