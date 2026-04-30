import pytest
import pandas as pd
import numpy as np
from modules.stats_pro_v2 import StatsProEngine, ExperimentalEngine

def test_calculate_correlation():
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 5],
        'B': [5, 4, 3, 2, 1],
        'C': [2, 3, 2, 3, 2]
    })
    corr = StatsProEngine.calculate_correlation(df)
    assert corr.loc['A', 'B'] == -1.0
    assert corr.loc['A', 'A'] == 1.0

def test_get_community_matrix():
    df = pd.DataFrame({
        'Sitio': ['S1', 'S1', 'S2', 'S2'],
        'Especie': ['Sp1', 'Sp2', 'Sp1', 'Sp3'],
        'Abundancia': [10, 5, 8, 12]
    })
    cm = StatsProEngine.get_community_matrix(df, 'Sitio', 'Especie', 'Abundancia')
    assert cm.shape == (2, 3)
    assert cm.loc['S1', 'Sp1'] == 10
    assert cm.loc['S2', 'Sp2'] == 0

def test_experimental_engine_melt():
    df = pd.DataFrame({
        'Bloque': [1, 2, 3],
        'T1': [10, 12, 11],
        'T2': [15, 14, 16]
    })
    melted = ExperimentalEngine.melt_wide_to_long(df, id_vars=['Bloque'], value_name='Respuesta', var_name='Tratamiento')
    assert melted.shape == (6, 3)
    assert 'Tratamiento' in melted.columns
    assert melted['Respuesta'].dtype == float

def test_run_anova_dca():
    data = {
        'Tratamiento': ['A', 'A', 'A', 'B', 'B', 'B', 'C', 'C', 'C'],
        'Respuesta': [10, 12, 11, 20, 22, 21, 30, 32, 31]
    }
    df = pd.DataFrame(data)
    anova_table, model = ExperimentalEngine.run_anova(df, 'Respuesta', ['Tratamiento'], design='DCA')
    
    # En este dataset, el tratamiento es altamente significativo
    assert anova_table.loc['Tratamiento', 'PR(>F)'] < 0.05
    assert model.rsquared > 0.9

def test_hutcheson_t_test():
    # Comparando dos diversidades
    h1, n1, s1 = 2.5, 100, 20
    h2, n2, s2 = 2.4, 100, 18
    t_stat, p_val, df_val = ExperimentalEngine.run_hutcheson_t_test(h1, n1, h2, n2, s1, s2)
    assert isinstance(t_stat, float)
    assert 0 <= p_val <= 1
