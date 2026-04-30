import pytest
from modules.bio_engine import BiodiversityEngine

def test_hill_numbers():
    data = [10, 5, 2, 1, 1, 1]
    
    q0 = BiodiversityEngine.calculate_hill_numbers(data, q=0)
    q1 = BiodiversityEngine.calculate_hill_numbers(data, q=1)
    q2 = BiodiversityEngine.calculate_hill_numbers(data, q=2)
    
    assert q0 == 6
    assert q1 > 0
    assert q2 > 0
    assert q0 >= q1 >= q2  # Propiedad de los números de Hill

def test_chao1_estimator():
    data = [10, 5, 2, 1, 1, 1]
    chao1 = BiodiversityEngine.chao1_estimator(data)
    assert chao1 >= len(data)

def test_rarefaction():
    data = [10, 5, 2, 1, 1, 1]
    m = 10
    e_s = BiodiversityEngine.iNEXT_rarefaction(data, m)
    assert e_s > 0
    assert e_s <= len(data)
