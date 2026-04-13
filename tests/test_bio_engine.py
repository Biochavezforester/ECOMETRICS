from modules.bio_engine import BiodiversityEngine

def test_engine():
    # Dataset de prueba (Abundancias)
    data = [10, 5, 2, 1, 1, 1]
    
    print("--- Probando ECOMETRICS Bio-Engine ---")
    
    # Pruebas de Números de Hill
    q0 = BiodiversityEngine.calculate_hill_numbers(data, q=0)
    q1 = BiodiversityEngine.calculate_hill_numbers(data, q=1)
    q2 = BiodiversityEngine.calculate_hill_numbers(data, q=2)
    
    print(f"Riqueza (q=0): {q0} (Esperado: 6)")
    print(f"Shannon Div (q=1): {q1:.2f}")
    print(f"Simpson Div (q=2): {q2:.2f}")
    
    # Prueba de Chao1
    chao1 = BiodiversityEngine.chao1_estimator(data)
    print(f"Estimador Chao1: {chao1:.2f} (Esperado: 6.5 - asumiendo f1=3, f2=0 o similar)")
    
    # Prueba de Rarefacción (Mao Tau) para m=10 individuos
    m = 10
    e_s = BiodiversityEngine.iNEXT_rarefaction(data, m)
    print(f"Riqueza esperada para {m} individuos: {e_s:.2f}")

if __name__ == "__main__":
    test_engine()
