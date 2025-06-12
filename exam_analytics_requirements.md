# Requisitos del Sistema - Aplicación de Análisis de Exámenes

## 1. INFORMACIÓN GENERAL DEL PROYECTO

### 1.1 Nombre del Proyecto
**ExamAnalytics Desktop** - Sistema de Análisis de Resultados de Exámenes

### 1.2 Objetivo
Desarrollar una aplicación de escritorio intuitiva para visualizar y analizar resultados de exámenes académicos, enfocándose en las métricas más críticas e importantes.

### 1.3 Tecnologías Principales
- **Framework GUI**: ttkbootstrap (Material Design para tkinter)
- **Visualización**: matplotlib + seaborn
- **Procesamiento de datos**: pandas, numpy
- **Formato de datos**: JSON

## 2. REQUISITOS FUNCIONALES

### 2.1 Gestión de Datos
- **RF-001**: Cargar archivos JSON con datos de exámenes
- **RF-002**: Validar estructura de datos al cargar
- **RF-003**: Mostrar resumen de datos cargados (número de estudiantes, exámenes, etc.)
- **RF-004**: Permitir recarga de datos sin reiniciar aplicación
- **RF-005**: Manejar errores de carga de archivos con mensajes informativos

### 2.2 Estadísticas Básicas (Prioridad 5)
- **RF-006**: Generar histograma de distribución de notas finales
- **RF-007**: Calcular y mostrar estadísticas descriptivas por examen (media, mediana, moda, desviación estándar)
- **RF-008**: Mostrar gráfico de barras con porcentaje de acierto por pregunta
- **RF-009**: Crear boxplot de notas por tipo de examen
- **RF-010**: Realizar análisis de dificultad relativa entre versiones de examen

### 2.3 Estadísticas Avanzadas (Prioridad 4)
- **RF-011**: Calcular percentiles de rendimiento (P25, P50, P75, P90, P95)
- **RF-012**: Comparar medias entre diferentes versiones del examen
- **RF-013**: Identificar preguntas más difíciles y más fáciles
- **RF-014**: Analizar distribución de respuestas por opción (A, B, C, D)
- **RF-015**: Mostrar rendimiento por año de ingreso (cohorte)
- **RF-016**: Generar perfiles individuales de estudiantes
- **RF-017**: Comparar estudiante individual vs promedio de clase
- **RF-018**: Calcular índices de dificultad y discriminación por pregunta
- **RF-019**: Identificar preguntas problemáticas
- **RF-020**: Analizar efectividad de distractores por pregunta
- **RF-021**: Crear panel de control con métricas clave

### 2.4 Navegación y Interfaz
- **RF-022**: Implementar navegación por pestañas/secciones
- **RF-023**: Permitir filtrado por tipo de examen
- **RF-024**: Incluir búsqueda de estudiantes por código o nombre
- **RF-025**: Mostrar tooltips explicativos en gráficas
- **RF-026**: Permitir exportar gráficas como imágenes (PNG/PDF)

## 3. REQUISITOS NO FUNCIONALES

### 3.1 Usabilidad
- **RNF-001**: Interfaz intuitiva siguiendo principios de Material Design
- **RNF-002**: Tiempo de respuesta < 3 segundos para generar cualquier gráfica
- **RNF-003**: Navegación clara con máximo 3 clics para cualquier función
- **RNF-004**: Mensajes de error comprensibles para usuarios no técnicos
- **RNF-005**: Responsive design que se adapte a diferentes resoluciones de pantalla

### 3.2 Rendimiento
- **RNF-006**: Soportar archivos con hasta 1000 estudiantes sin degradación notable
- **RNF-007**: Consumo de memoria < 500MB para datasets típicos
- **RNF-008**: Carga inicial de aplicación < 5 segundos

### 3.3 Compatibilidad
- **RNF-009**: Compatible con Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **RNF-010**: Resolución mínima soportada: 1024x768
- **RNF-011**: Python 3.8+ como requisito mínimo

### 3.4 Mantenibilidad
- **RNF-012**: Código modular con separación clara de responsabilidades
- **RNF-013**: Documentación interna del código
- **RNF-014**: Configuración centralizada para temas y estilos

## 4. ESTRUCTURA DE LA INTERFAZ

### 4.1 Ventana Principal
```
┌─────────────────────────────────────────────────────────────┐
│ ExamAnalytics Desktop                              [_ □ ×] │
├─────────────────────────────────────────────────────────────┤
│ [Cargar Datos] [Exportar] [Configuración]     Estado: ✓    │
├─────────────────────────────────────────────────────────────┤
│ [Resumen] [Distribuciones] [Por Pregunta] [Por Estudiante] │
│                        [Comparaciones]                      │
├─────────────────────────────────────────────────────────────┤
│                                                            │
│                    ÁREA DE CONTENIDO                       │
│                   (Gráficas y Tablas)                     │
│                                                            │
│                                                            │
├─────────────────────────────────────────────────────────────┤
│ Filtros: [Examen: Todos ▼] [Estudiantes: Todos ▼]         │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Pestañas Principales
1. **Resumen General**: Dashboard con métricas clave
2. **Distribuciones**: Histogramas, boxplots, estadísticas descriptivas
3. **Análisis por Pregunta**: Dificultad, discriminación, distractores
4. **Análisis por Estudiante**: Perfiles individuales, comparaciones
5. **Comparaciones**: Entre exámenes, cohortes, versiones

## 5. DATOS DE ENTRADA

### 5.1 Formato de Archivo
- **Tipo**: JSON
- **Estructura**: Array de objetos con la estructura mostrada en el ejemplo
- **Campos obligatorios**: codigo, apellidos_nombres, examen, correctas, incorrectas, nota, respuestas_estudiante, respuestas_correctas

### 5.2 Validaciones
- Verificar que todas las preguntas tengan respuestas (Q1-Q20)
- Validar que las respuestas sean A, B, C, o D
- Confirmar coherencia entre correctas/incorrectas y respuestas individuales
- Verificar formato de códigos de estudiante

## 6. SALIDAS DEL SISTEMA

### 6.1 Visualizaciones
- Gráficas interactivas con matplotlib/seaborn
- Tablas de estadísticas formateadas
- Reportes exportables (PNG, PDF)

### 6.2 Métricas Calculadas
- Estadísticas descriptivas básicas
- Percentiles y rankings
- Índices psicométricos (dificultad, discriminación)
- Comparaciones entre grupos

## 7. RESTRICCIONES Y LIMITACIONES

### 7.1 Técnicas
- Sin conexión a internet requerida (aplicación offline)
- Un solo archivo de datos por sesión
- Máximo 20 preguntas por examen
- Opciones de respuesta limitadas a A, B, C, D

### 7.2 Funcionales
- No incluye edición de datos (solo lectura y análisis)
- No guarda estados de sesión entre ejecuciones
- No incluye funcionalidades de prioridad 1, 2 y 3 en versión inicial

## 8. CASOS DE USO PRINCIPALES

### 8.1 Docente/Coordinador Académico
1. Cargar resultados de examen
2. Revisar distribución general de notas
3. Identificar preguntas problemáticas
4. Comparar rendimiento entre versiones
5. Generar reportes para reuniones académicas

### 8.2 Analista de Datos Educativos
1. Analizar calidad psicométrica de preguntas
2. Evaluar efectividad de distractores
3. Comparar cohortes de estudiantes
4. Exportar visualizaciones para presentaciones

## 9. CRITERIOS DE ACEPTACIÓN

### 9.1 Funcionalidad Mínima Viable (MVP)
- Carga exitosa de archivos JSON
- Generación de al menos 8 tipos de gráficas (prioridad 5 y 4)
- Interfaz navegable con Material Design
- Exportación básica de gráficas

### 9.2 Criterios de Calidad
- Zero crashes con datos válidos
- Mensajes de error claros con datos inválidos
- Tiempo de respuesta aceptable para todos los gráficos
- Interfaz visualmente coherente y profesional