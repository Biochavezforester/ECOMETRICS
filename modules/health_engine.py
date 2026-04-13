import numpy as np

class HealthEngine:
    """
    Motor para la evaluación de sanidad forestal y riesgos fitosanitarios.
    """
    
    @staticmethod
    def assess_pest_risk(precip_mm, temp_c, species_vulnerability):
        """
        Calcula un índice de riesgo de plagas basado en clima.
        species_vulnerability: escala 1-10 (1:resistente, 10:muy vulnerable)
        """
        # Regla experta simplificada: Temperaturas altas y sequía aumentan el riesgo
        # para descortezadores (Dendroctonus spp.)
        
        temp_factor = np.clip((temp_c - 15) / 10, 0, 1) # Normalizado
        precip_factor = np.clip((500 - precip_mm) / 500, 0, 1) # Normalizado
        
        risk_index = (temp_factor * 0.4 + precip_factor * 0.4 + (species_vulnerability / 10) * 0.2) * 100
        
        return np.clip(risk_index, 0, 100)

    @staticmethod
    def get_health_status(risk_index):
        if risk_index < 30:
            return "Estable", "🟢"
        elif risk_index < 60:
            return "Alerta", "🟡"
        else:
            return "Riesgo Crítico", "🔴"

    @staticmethod
    def calculate_phytosanitary_metrics(df, infestation_col="Grado_Infestacion"):
        """
        Calcula métricas reales de sanidad basadas en datos de campo.
        Grado_Infestacion: 0-5
        """
        n_total = len(df)
        if n_total == 0: return {}
        
        # 1. Incidencia (%)
        n_infested = len(df[df[infestation_col] > 0])
        incidence = (n_infested / n_total) * 100
        
        # 2. Severidad Media (%)
        # Convertir grado 0-5 a porcentaje (Grado 5 = 100%)
        severity = (df[infestation_col].sum() / (n_total * 5)) * 100
        
        # 3. Índice Fitosanitario de Rodal (IFR)
        # Similar a la severidad pero ponderado
        ifr = severity # En modelos simples se asimilan
        
        return {
            "Incidencia": incidence,
            "Severidad": severity,
            "IFR": ifr,
            "N_Sanos": n_total - n_infested,
            "N_Infestados": n_infested
        }
