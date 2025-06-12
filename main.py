"""
ExamAnalytics Desktop - MVP
Sistema de Análisis de Resultados de Exámenes

Requisitos:
pip install ttkbootstrap pandas matplotlib seaborn numpy

Autor: FLORES LUERA, Miguel
Versión: 1.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading
from collections import Counter

# Configuración global de matplotlib
plt.style.use('default')
sns.set_palette("husl")


class DataManager:
    """Gestor de datos para el análisis de exámenes"""

    def __init__(self):
        self.data: List[Dict] = []
        self.df: Optional[pd.DataFrame] = None
        self.is_loaded = False

    def load_data(self, file_path: str) -> Tuple[bool, str]:
        """Carga y valida los datos del archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            # Validar estructura
            if not self.data or not isinstance(self.data, list):
                return False, "El archivo debe contener una lista de registros"

            # Validar campos requeridos
            required_fields = ['codigo', 'apellidos_nombres', 'examen', 'correctas',
                               'incorrectas', 'nota', 'respuestas_estudiante', 'respuestas_correctas']

            for i, record in enumerate(self.data):
                missing_fields = [field for field in required_fields if field not in record]
                if missing_fields:
                    return False, f"Registro {i + 1}: Faltan campos {missing_fields}"

            # Crear DataFrame
            self.df = pd.DataFrame(self.data)
            self.is_loaded = True
            return True, f"Datos cargados exitosamente: {len(self.data)} registros"

        except json.JSONDecodeError:
            return False, "Error: El archivo no es un JSON válido"
        except FileNotFoundError:
            return False, "Error: Archivo no encontrado"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"

    def get_summary(self) -> Dict:
        """Retorna resumen de los datos cargados"""
        if not self.is_loaded:
            return {}

        return {
            'total_estudiantes': len(self.df),
            'tipos_examen': self.df['examen'].nunique(),
            'examen_tipos': list(self.df['examen'].unique()),
            'nota_promedio': self.df['nota'].mean(),
            'nota_max': self.df['nota'].max(),
            'nota_min': self.df['nota'].min(),
            'std_nota': self.df['nota'].std()
        }

    def get_questions_analysis(self) -> pd.DataFrame:
        """Analiza el rendimiento por pregunta"""
        if not self.is_loaded:
            return pd.DataFrame()

        questions_data = []
        for i in range(1, 21):  # Q1 to Q20
            q_key = f"Q{i}"
            correct_count = 0
            total_count = len(self.df)

            for _, row in self.df.iterrows():
                student_answer = row['respuestas_estudiante'].get(q_key)
                correct_answer = row['respuestas_correctas'].get(q_key)
                if student_answer == correct_answer:
                    correct_count += 1

            difficulty_index = correct_count / total_count if total_count > 0 else 0

            questions_data.append({
                'pregunta': q_key,
                'correctas': correct_count,
                'total': total_count,
                'porcentaje_acierto': difficulty_index * 100,
                'dificultad': 'Fácil' if difficulty_index > 0.7 else 'Difícil' if difficulty_index < 0.3 else 'Moderada'
            })

        return pd.DataFrame(questions_data)


class VisualizationEngine:
    """Motor de visualizaciones para la aplicación"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def create_histogram_notas(self, parent_frame) -> FigureCanvasTkAgg:
        """Crea histograma de distribución de notas"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        if self.data_manager.is_loaded:
            notas = self.data_manager.df['nota']
            ax.hist(notas, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_xlabel('Nota')
            ax.set_ylabel('Frecuencia')
            ax.set_title('Distribución de Notas Finales')
            ax.grid(True, alpha=0.3)

            # Añadir línea de promedio
            mean_nota = notas.mean()
            ax.axvline(mean_nota, color='red', linestyle='--',
                       label=f'Promedio: {mean_nota:.2f}')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No hay datos cargados',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas

    def create_boxplot_exams(self, parent_frame) -> FigureCanvasTkAgg:
        """Crea boxplot comparando notas por tipo de examen"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        if self.data_manager.is_loaded:
            df = self.data_manager.df
            exam_types = df['examen'].unique()
            data_for_boxplot = [df[df['examen'] == exam]['nota'].values for exam in exam_types]

            ax.boxplot(data_for_boxplot, labels=exam_types)
            ax.set_xlabel('Tipo de Examen')
            ax.set_ylabel('Nota')
            ax.set_title('Distribución de Notas por Tipo de Examen')
            ax.grid(True, alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'No hay datos cargados',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas

    def create_questions_difficulty(self, parent_frame) -> FigureCanvasTkAgg:
        """Crea gráfico de barras con porcentaje de acierto por pregunta"""
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)

        if self.data_manager.is_loaded:
            questions_df = self.data_manager.get_questions_analysis()

            colors = ['green' if x > 70 else 'red' if x < 30 else 'orange'
                      for x in questions_df['porcentaje_acierto']]

            bars = ax.bar(questions_df['pregunta'], questions_df['porcentaje_acierto'],
                          color=colors, alpha=0.7)

            ax.set_xlabel('Pregunta')
            ax.set_ylabel('Porcentaje de Acierto (%)')
            ax.set_title('Dificultad por Pregunta')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)

            # Añadir líneas de referencia
            ax.axhline(70, color='green', linestyle='--', alpha=0.5, label='Fácil (>70%)')
            ax.axhline(30, color='red', linestyle='--', alpha=0.5, label='Difícil (<30%)')
            ax.legend()

            # Rotar etiquetas del eje x
            plt.setp(ax.get_xticklabels(), rotation=45)
        else:
            ax.text(0.5, 0.5, 'No hay datos cargados',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas

    def create_performance_by_cohort(self, parent_frame) -> FigureCanvasTkAgg:
        """Crea gráfico de rendimiento por cohorte (año de ingreso)"""
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)

        if self.data_manager.is_loaded:
            df = self.data_manager.df.copy()
            # Extraer año de ingreso del código (primeros 4 dígitos)
            df['año_ingreso'] = df['codigo'].astype(str).str[:4]

            cohort_stats = df.groupby('año_ingreso')['nota'].agg(['mean', 'count']).reset_index()
            cohort_stats = cohort_stats[cohort_stats['count'] >= 5]  # Solo cohortes con al menos 5 estudiantes

            if not cohort_stats.empty:
                bars = ax.bar(cohort_stats['año_ingreso'], cohort_stats['mean'],
                              alpha=0.7, color='lightcoral')
                ax.set_xlabel('Año de Ingreso')
                ax.set_ylabel('Nota Promedio')
                ax.set_title('Rendimiento Promedio por Cohorte')
                ax.grid(True, alpha=0.3)

                # Añadir valores en las barras
                for bar, value in zip(bars, cohort_stats['mean']):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                            f'{value:.1f}', ha='center', va='bottom')
            else:
                ax.text(0.5, 0.5, 'Datos insuficientes para análisis por cohorte',
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=12)
        else:
            ax.text(0.5, 0.5, 'No hay datos cargados',
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=14)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        return canvas


class StatsPanel:
    """Panel de estadísticas descriptivas"""

    def __init__(self, parent_frame, data_manager: DataManager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk_bs.Frame(self.parent_frame)
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Título
        title_label = ttk_bs.Label(main_frame, text="Estadísticas Descriptivas",
                                   font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Frame para estadísticas
        self.stats_frame = ttk_bs.Frame(main_frame)
        self.stats_frame.pack(fill=BOTH, expand=True)

        self.update_stats()

    def update_stats(self):
        # Limpiar frame
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        if not self.data_manager.is_loaded:
            no_data_label = ttk_bs.Label(self.stats_frame,
                                         text="No hay datos cargados",
                                         font=("Arial", 12))
            no_data_label.pack(pady=20)
            return

        summary = self.data_manager.get_summary()
        df = self.data_manager.df

        # Crear grid de estadísticas
        stats_data = [
            ("Total de Estudiantes", summary['total_estudiantes']),
            ("Tipos de Examen", summary['tipos_examen']),
            ("Nota Promedio", f"{summary['nota_promedio']:.2f}"),
            ("Nota Máxima", summary['nota_max']),
            ("Nota Mínima", summary['nota_min']),
            ("Desviación Estándar", f"{summary['std_nota']:.2f}"),
            ("Percentil 25", f"{df['nota'].quantile(0.25):.2f}"),
            ("Percentil 50 (Mediana)", f"{df['nota'].quantile(0.50):.2f}"),
            ("Percentil 75", f"{df['nota'].quantile(0.75):.2f}"),
            ("Percentil 90", f"{df['nota'].quantile(0.90):.2f}")
        ]

        # Crear cards de estadísticas
        row = 0
        col = 0
        for label, value in stats_data:
            card_frame = ttk_bs.Frame(self.stats_frame, relief="raised", borderwidth=1)
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

            ttk_bs.Label(card_frame, text=str(value),
                         font=("Arial", 14, "bold")).pack(pady=(10, 0))
            ttk_bs.Label(card_frame, text=label,
                         font=("Arial", 10)).pack(pady=(0, 10))

            col += 1
            if col > 2:  # 3 columnas
                col = 0
                row += 1

        # Configurar grid
        for i in range(3):
            self.stats_frame.columnconfigure(i, weight=1)


class ExamAnalyticsApp:
    """Aplicación principal de análisis de exámenes"""

    def __init__(self):
        self.root = ttk_bs.Window(themename="flatly")
        self.root.title("ExamAnalytics Desktop - v1.0")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)

        # Managers
        self.data_manager = DataManager()
        self.viz_engine = VisualizationEngine(self.data_manager)

        # Variables
        self.current_file = tk.StringVar(value="Ningún archivo cargado")

        self.setup_ui()
        self.center_window()

    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Header
        self.create_header()

        # Notebook (pestañas)
        self.create_notebook()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Crea la barra de herramientas superior"""
        header_frame = ttk_bs.Frame(self.root)
        header_frame.pack(fill=X, padx=10, pady=5)

        # Botones principales
        ttk_bs.Button(header_frame, text="📁 Cargar Datos",
                      command=self.load_data, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        ttk_bs.Button(header_frame, text="💾 Exportar Gráfica",
                      command=self.export_current_chart, bootstyle=SUCCESS).pack(side=LEFT, padx=5)

        ttk_bs.Button(header_frame, text="🔄 Actualizar",
                      command=self.refresh_all, bootstyle=INFO).pack(side=LEFT, padx=5)

        # Archivo actual
        file_label = ttk_bs.Label(header_frame, textvariable=self.current_file,
                                  font=("Arial", 10))
        file_label.pack(side=RIGHT, padx=10)

    def create_notebook(self):
        """Crea el notebook con las pestañas principales"""
        self.notebook = ttk_bs.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=5)

        # Pestaña 1: Resumen
        self.tab_summary = ttk_bs.Frame(self.notebook)
        self.notebook.add(self.tab_summary, text="📊 Resumen")
        self.setup_summary_tab()

        # Pestaña 2: Distribuciones
        self.tab_distributions = ttk_bs.Frame(self.notebook)
        self.notebook.add(self.tab_distributions, text="📈 Distribuciones")
        self.setup_distributions_tab()

        # Pestaña 3: Análisis por Pregunta
        self.tab_questions = ttk_bs.Frame(self.notebook)
        self.notebook.add(self.tab_questions, text="❓ Por Pregunta")
        self.setup_questions_tab()

        # Pestaña 4: Análisis por Estudiante
        self.tab_students = ttk_bs.Frame(self.notebook)
        self.notebook.add(self.tab_students, text="👨‍🎓 Por Estudiante")
        self.setup_students_tab()

        # Pestaña 5: Comparaciones
        self.tab_comparisons = ttk_bs.Frame(self.notebook)
        self.notebook.add(self.tab_comparisons, text="⚖️ Comparaciones")
        self.setup_comparisons_tab()

    def setup_summary_tab(self):
        """Configura la pestaña de resumen"""
        self.stats_panel = StatsPanel(self.tab_summary, self.data_manager)

    def setup_distributions_tab(self):
        """Configura la pestaña de distribuciones"""
        # Frame para gráficas
        charts_frame = ttk_bs.Frame(self.tab_distributions)
        charts_frame.pack(fill=BOTH, expand=True)

        # Histograma de notas
        self.hist_frame = ttk_bs.LabelFrame(charts_frame, text="Distribución de Notas")
        self.hist_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.refresh_histogram()

    def setup_questions_tab(self):
        """Configura la pestaña de análisis por pregunta"""
        # Frame para gráfica de dificultad
        self.questions_frame = ttk_bs.LabelFrame(self.tab_questions, text="Dificultad por Pregunta")
        self.questions_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.refresh_questions_chart()

    def setup_students_tab(self):
        """Configura la pestaña de análisis por estudiante"""
        # Frame principal
        main_frame = ttk_bs.Frame(self.tab_students)
        main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Frame de búsqueda
        search_frame = ttk_bs.Frame(main_frame)
        search_frame.pack(fill=X, pady=(0, 10))

        ttk_bs.Label(search_frame, text="Buscar Estudiante:").pack(side=LEFT, padx=5)
        self.student_search = ttk_bs.Entry(search_frame, width=20)
        self.student_search.pack(side=LEFT, padx=5)
        ttk_bs.Button(search_frame, text="Buscar",
                      command=self.search_student, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

        # Frame de resultados
        self.student_results_frame = ttk_bs.Frame(main_frame)
        self.student_results_frame.pack(fill=BOTH, expand=True)

        # Mensaje inicial
        ttk_bs.Label(self.student_results_frame,
                     text="Ingrese un código o nombre de estudiante para buscar",
                     font=("Arial", 12)).pack(pady=20)

    def setup_comparisons_tab(self):
        """Configura la pestaña de comparaciones"""
        # Frame para comparaciones
        comp_frame = ttk_bs.Frame(self.tab_comparisons)
        comp_frame.pack(fill=BOTH, expand=True)

        # Boxplot por examen
        self.boxplot_frame = ttk_bs.LabelFrame(comp_frame, text="Comparación por Tipo de Examen")
        self.boxplot_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.refresh_boxplot()

        # Análisis por cohorte
        self.cohort_frame = ttk_bs.LabelFrame(comp_frame, text="Rendimiento por Cohorte")
        self.cohort_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.refresh_cohort_analysis()

    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_bar = ttk_bs.Label(self.root, text="Listo", relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)

    def load_data(self):
        """Carga los datos desde un archivo JSON"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            self.status_bar.config(text="Cargando datos...")
            self.root.update()

            success, message = self.data_manager.load_data(file_path)

            if success:
                self.current_file.set(f"Archivo: {os.path.basename(file_path)}")
                self.status_bar.config(text=message)
                self.refresh_all()
                messagebox.showinfo("Éxito", message)
            else:
                self.status_bar.config(text="Error al cargar datos")
                messagebox.showerror("Error", message)

    def refresh_all(self):
        """Actualiza todas las visualizaciones"""
        self.refresh_summary()
        self.refresh_histogram()
        self.refresh_boxplot()
        self.refresh_questions_chart()
        self.refresh_cohort_analysis()

    def refresh_summary(self):
        """Actualiza el panel de resumen"""
        self.stats_panel.update_stats()

    def refresh_histogram(self):
        """Actualiza el histograma de notas"""
        for widget in self.hist_frame.winfo_children():
            widget.destroy()

        canvas = self.viz_engine.create_histogram_notas(self.hist_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas.draw()

    def refresh_boxplot(self):
        """Actualiza el boxplot de comparación"""
        for widget in self.boxplot_frame.winfo_children():
            widget.destroy()

        canvas = self.viz_engine.create_boxplot_exams(self.boxplot_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas.draw()

    def refresh_questions_chart(self):
        """Actualiza el gráfico de análisis por pregunta"""
        for widget in self.questions_frame.winfo_children():
            widget.destroy()

        canvas = self.viz_engine.create_questions_difficulty(self.questions_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas.draw()

    def refresh_cohort_analysis(self):
        """Actualiza el análisis por cohorte"""
        for widget in self.cohort_frame.winfo_children():
            widget.destroy()

        canvas = self.viz_engine.create_performance_by_cohort(self.cohort_frame)
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        canvas.draw()

    def search_student(self):
        """Busca y muestra información de un estudiante específico"""
        if not self.data_manager.is_loaded:
            messagebox.showwarning("Advertencia", "Debe cargar datos primero")
            return

        search_term = self.student_search.get().strip()
        if not search_term:
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return

        # Buscar estudiante
        df = self.data_manager.df
        mask = (df['codigo'].astype(str).str.contains(search_term, case=False) |
                df['apellidos_nombres'].str.contains(search_term, case=False))

        results = df[mask]

        # Limpiar frame de resultados
        for widget in self.student_results_frame.winfo_children():
            widget.destroy()

        if results.empty:
            ttk_bs.Label(self.student_results_frame,
                         text="No se encontraron estudiantes",
                         font=("Arial", 12)).pack(pady=20)
        else:
            # Mostrar resultados
            for _, student in results.iterrows():
                self.create_student_card(student)

    def create_student_card(self, student_data):
        """Crea una tarjeta con información del estudiante"""
        card_frame = ttk_bs.LabelFrame(self.student_results_frame,
                                       text=f"Código: {student_data['codigo']}")
        card_frame.pack(fill=X, padx=5, pady=5)

        # Información básica
        info_frame = ttk_bs.Frame(card_frame)
        info_frame.pack(fill=X, padx=10, pady=5)

        ttk_bs.Label(info_frame, text=f"Nombre: {student_data['apellidos_nombres']}",
                     font=("Arial", 10, "bold")).pack(anchor=W)
        ttk_bs.Label(info_frame, text=f"Examen: {student_data['examen']}").pack(anchor=W)
        ttk_bs.Label(info_frame, text=f"Nota: {student_data['nota']}").pack(anchor=W)
        ttk_bs.Label(info_frame, text=f"Correctas: {student_data['correctas']} | "
                                      f"Incorrectas: {student_data['incorrectas']}").pack(anchor=W)

        # Comparación con promedio
        avg_score = self.data_manager.df['nota'].mean()
        diff = student_data['nota'] - avg_score
        comparison_text = f"Diferencia con promedio: {diff:+.2f}"
        color = "success" if diff >= 0 else "danger"

        ttk_bs.Label(info_frame, text=comparison_text,
                     bootstyle=color).pack(anchor=W)

    def export_current_chart(self):
        """Exporta la gráfica actual"""
        if not self.data_manager.is_loaded:
            messagebox.showwarning("Advertencia", "No hay datos cargados")
            return

        current_tab = self.notebook.index(self.notebook.select())
        tab_names = ["resumen", "distribuciones", "preguntas", "estudiantes", "comparaciones"]

        file_path = filedialog.asksaveasfilename(
            title="Guardar gráfica",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")]
        )

        if file_path:
            try:
                # Obtener la figura actual basada en la pestaña
                if current_tab == 1:  # Distribuciones
                    canvas = list(self.hist_frame.winfo_children())[0]
                elif current_tab == 2:  # Preguntas
                    canvas = list(self.questions_frame.winfo_children())[0]
                elif current_tab == 4:  # Comparaciones
                    canvas = list(self.boxplot_frame.winfo_children())[0]
                else:
                    messagebox.showinfo("Info", "La pestaña actual no tiene gráficas exportables")
                    return

                canvas.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfica guardada en: {file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()


def main():
    """Función principal"""
    try:
        # Verificar dependencias
        import ttkbootstrap
        import pandas
        import numpy
        import matplotlib.pyplot
        import seaborn
        # Crear y ejecutar aplicacion
        app = ExamAnalyticsApp()
        app.run()
    except ImportError as e:
        print("Error: Faltan dependencias requeridas.")
        print("Por favor instale las siguientes librerías:")
        print("pip install ttkbootstrap pandas matplotlib seaborn numpy")
        print(f"\nError específico: {e}")
        input("Presione Enter para salir...")
    except Exception as e:
        print(f"Error inesperado: {e}")
        input("Presione Enter para salir...")


if __name__ == "__main__":
    main()
