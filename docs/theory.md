# 🧬 Base Científica de ECOMETRICS

ECOMETRICS implementa modelos matemáticos y estadísticos validados por la literatura científica para el monitoreo ecológico y la gestión forestal.

## 1. Biodiversidad y Rarefacción
El motor de biodiversidad se basa en el marco de trabajo de los **Números de Hill** y los modelos **iNEXT** (Interpolación y Extrapolación).

*   **Riqueza y Diversidad:** Implementamos los órdenes de diversidad $q=0$ (riqueza), $q=1$ (Shannon) y $q=2$ (Simpson).
*   **Estimadores Asintóticos:** Se utiliza el estimador **Chao1** para datos de abundancia, ideal para inventarios donde muchas especies son raras (singletons y doubletons).
*   **Rarefacción:** La metodología sigue a Chao et al. (2014), permitiendo comparar comunidades con diferentes esfuerzos de muestreo mediante el método de Mao Tau.

## 2. Ingeniería Forestal
El análisis de existencias reales y biomasa utiliza sistemas biométricos regionales.

*   **Volumen y Ahusamiento:** Se utilizan los modelos de **Fang et al. (2000)**, que son sistemas compatibles de volumen total y comercial.
*   **Crecimiento (GADA):** Los modelos de Índice de Sitio utilizan la metodología **GADA** (Generalized Algebraic Difference Approach), que permite proyecciones polimórficas con asíntotas variables, basándose en trabajos de Vargas-Larreta y Cruz-Cobos.
*   **IVI (Índice de Valor de Importancia):** Basado en Curtis y McIntosh (1951), calculando la importancia ecológica mediante la suma de abundancia, dominancia y frecuencia relativas.

## 3. Bioestadística Experimental
*   **ANOVA:** Implementación robusta de diseños DCA, DBCA y Cuadro Latino utilizando modelos lineales por mínimos cuadrados ordinarios (OLS).
*   **Prueba de Tukey HSD:** Algoritmo de comparación múltiple de medias para identificar grupos significativos ($p < 0.05$).
*   **Análisis de Poder:** Implementado para evaluar la probabilidad de error tipo II, garantizando la robustez de las conclusiones experimentales.

---
*Para más detalles sobre la implementación técnica, consulta el archivo [paper.md](../paper.md).*
