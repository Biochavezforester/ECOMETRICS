import pytest
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols

def test_anova_latin_square():
    data = {
        'Fila': [1,1,1,1,1, 2,2,2,2,2, 3,3,3,3,3, 4,4,4,4,4, 5,5,5,5,5],
        'Columna': [1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5, 1,2,3,4,5],
        'Tratamiento': ['A','D','C','E','B', 'B','E','D','A','C', 'D','B','A','C','E', 'C','A','E','B','D', 'E','C','B','D','A'],
        'Respuesta': [33.8, 33.7, 30.4, 32.7, 24.4, 37, 28.8, 33.5, 34.6, 33.4, 35.8, 35.6, 36.9, 26.7, 35.1, 33.2, 37.1, 37.4, 38.1, 34.1, 34.8, 39.1, 32.7, 37.4, 36.4]
    }

    df = pd.DataFrame(data)
    # Convertir a variables categóricas
    df['Fila'] = df['Fila'].astype(str)
    df['Columna'] = df['Columna'].astype(str)
    
    model = ols("Respuesta ~ C(Fila) + C(Columna) + C(Tratamiento)", data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    
    assert "C(Fila)" in anova_table.index
    assert "C(Columna)" in anova_table.index
    assert "C(Tratamiento)" in anova_table.index
    assert "Residual" in anova_table.index
    
    # Verificar que el F-value es numérico y se calculó
    assert anova_table.loc["C(Tratamiento)", "F"] > 0
