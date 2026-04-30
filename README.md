# 🌿 ECOMETRICS

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)](https://streamlit.io/)

**ECOMETRICS** es una suite bioestadística premium diseñada para científicos, ingenieros forestales y ecólogos. Combina el rigor de los modelos matemáticos avanzados con una interfaz moderna e intuitiva para el monitoreo de la biodiversidad y la gestión de recursos naturales.

## ✨ Características Principales

### 📊 Biodiversidad y Rarefacción

- **Modelos iNEXT**: Curvas de rarefacción y extrapolación basadas en Hill numbers.
- **Estimadores Asintóticos**: Cálculo de riqueza potencial usando Chao1, Jackknife y más.
- **Diversidad Alpha y Beta**: Índices de Shannon, Simpson, Bray-Curtis y matrices de disimilitud.
- **Prueba de Hutcheson**: Comparación estadística de diversidad entre comunidades.

### 🌲 Silvicultura e Inventarios

- **Existencias Real**: Cálculo de volumen, área basal y densidad por hectárea.
- **Biomasa y Carbono**: Estimación de captura de CO2e mediante modelos biométricos.
- **IVI (Índice de Valor de Importancia)**: Análisis estructural de la importancia ecológica de las especies.
- **Modelos GADA**: Índice de sitio y ahusamiento (Fang) para proyecciones de crecimiento.

### 🔬 Bioestadística Pro

- **Diseños Experimentales**: ANOVA (DCA, DBCA, Cuadro Latino) con pruebas de Tukey.
- **Análisis de Poder**: Validación estadística de la robustez del diseño.
- **Interpretación Inteligente**: Motor de lenguaje natural que explica los resultados científicos.

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**

   ```bash
   git clone https://github.com/Biochavezforester/ECOMETRICS.git
   cd ECOMETRICS
   ```

2. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**

   ```bash
   streamlit run app/main.py
   ```

## 📈 Ejemplo de Uso

1. Al abrir la aplicación, dirígete al módulo **"Silvicultura e Inventarios"**.
2. Selecciona la pestaña de **Análisis de IVI**.
3. Carga el archivo de prueba ubicado en la carpeta `data/test_ivi.csv`.
4. Observa cómo el sistema calcula automáticamente las frecuencias, densidades y dominancias relativas, generando un informe estructural completo y los gráficos correspondientes.
5. Puedes exportar los resultados a Excel utilizando el botón de descarga en la interfaz.

## 📖 Citación

Si utilizas **ECOMETRICS** en tu investigación académica, por favor cítalo de la siguiente manera:

```bibtex
@software{ecometrics2026,
  author = {Chávez-Gurrola, Eríck Elío},
  title = {ECOMETRICS: Suite Bioestadística para Monitoreo Ecológico},
  version = {1.0.0},
  year = {2026},
  doi = {10.5281/zenodo.XXXXXXX},
  url = {https://github.com/Biochavezforester/ECOMETRICS}
}
```

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---
*Desarrollado para la comunidad científica y forestal.*
