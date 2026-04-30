import pytest
import pandas as pd
import numpy as np
from modules.forestry_engine import ForestryEngine

def test_estimate_volume():
    # Caso base: Pinus cooperi (ID 1)
    # V = b0 * D^b1 * H^b2
    # b0: 5.9522e-05, b1: 2.10893, b2: 0.78958
    dap = 30
    h = 20
    vol = ForestryEngine.estimate_volume(dap, h, species="1")
    
    expected = 5.9522e-05 * (30**2.10893) * (20**0.78958)
    assert pytest.approx(vol, rel=1e-4) == expected
    assert vol > 0

def test_calculate_basal_area():
    dap = 20
    g = ForestryEngine.calculate_basal_area(dap)
    expected = (np.pi * (20**2)) / 40000
    assert pytest.approx(g) == expected

def test_calculate_dcq():
    g_ha = 25.0
    n_ha = 500
    dcq = ForestryEngine.calculate_dcq(g_ha, n_ha)
    expected = np.sqrt((40000 * 25.0) / (np.pi * 500))
    assert pytest.approx(dcq) == expected

def test_estimate_biomass_carbon():
    dap = 25
    h = 15
    biomass, carbon = ForestryEngine.estimate_biomass_carbon(dap, h, species="2")
    vol = ForestryEngine.estimate_volume(dap, h, species="2")
    assert biomass == vol * 0.65
    assert carbon == biomass * 0.5

def test_calculate_ivi():
    data = {
        'Especie': ['Pinus A', 'Pinus A', 'Quercus B', 'Pinus A', 'Quercus B'],
        'Sitio': [1, 1, 1, 2, 2],
        'DAP_cm': [20, 25, 15, 30, 20]
    }
    df = pd.DataFrame(data)
    ivi_df = ForestryEngine.calculate_ivi(df, species_col='Especie', site_col='Sitio', dap_col='DAP_cm')
    
    assert 'IVI' in ivi_df.columns
    assert len(ivi_df) == 2
    # El IVI total debe sumar aproximadamente 300
    assert pytest.approx(ivi_df['IVI'].sum()) == 300

def test_calculate_reineke_sdi():
    n_ha = 600
    dcq = 25.4
    sdi = ForestryEngine.calculate_reineke_sdi(n_ha, dcq)
    # A 25.4 cm (10 pulgadas), SDI == N_ha
    assert pytest.approx(sdi) == 600

def test_calculate_stand_rating():
    assert ForestryEngine.calculate_stand_rating(100, 1000) == "Subpoblado (Crecimiento Libre)"
    assert ForestryEngine.calculate_stand_rating(900, 1000) == "Saturado"
