import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox, Text, Scrollbar, VERTICAL, RIGHT, Y, LEFT, BOTH
from tkinter import ttk
import folium
from folium.plugins import HeatMap
import webview
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageTk
import tempfile  # Importar tempfile
import os



class VisualizacionAccidentes:
    def __init__(self, root):

        self.root = root
        self.root.title("Visualización de Datos de Accidentes de Tráfico en Perú")
        self.root.geometry("1200x800")
        self.root.configure(background="#f0f0f0")

        self.coordenadas_departamentos = {
            'AMAZONAS': [-5.0727, -78.0452],
            'ANCASH': [-9.5293, -77.5297],
            'APURIMAC': [-14.0383, -73.0281],
            'AREQUIPA': [-16.4090, -71.5375],
            'AYACUCHO': [-13.1588, -74.2236],
            'CAJAMARCA': [-7.1617, -78.5127],
            'CALLAO': [-12.0566, -77.1181],
            'CUSCO': [-13.5319, -71.9675],
            'HUANCAVELICA': [-12.7885, -74.9727],
            'HUANUCO': [-9.9306, -76.2422],
            'ICA': [-14.0681, -75.7255],
            'JUNIN': [-11.5413, -74.8659],
            'LA LIBERTAD': [-8.1150, -79.0282],
            'LAMBAYEQUE': [-6.7011, -79.9074],
            'LIMA': [-12.0464, -77.0428],
            'LORETO': [-3.7491, -73.2538],
            'MADRE DE DIOS': [-12.5933, -69.1891],
            'MOQUEGUA': [-17.1954, -70.9357],
            'PASCO': [-10.6832, -76.2569],
            'PIURA': [-5.1945, -80.6328],
            'PUNO': [-15.8402, -70.0219],
            'SAN MARTIN': [-6.4417, -76.3752],
            'TACNA': [-18.0146, -70.2536],
            'TUMBES': [-3.5669, -80.4515],
            'UCAYALI': [-8.3791, -74.5539]
        }
        
        self.cargar_iconos()
        self.pantalla()
        
    def cargar_iconos(self):
        
        def ajustar_icono(ruta, tamaño):
            imagen = Image.open(ruta).convert("RGBA")
            imagen = imagen.resize(tamaño, Image.LANCZOS)
            return ImageTk.PhotoImage(imagen)

        tamaño = (40, 40)
        self.icono_seleccionar = ajustar_icono("iconos/seleccionar.png", tamaño)
        self.icono_mostrar_graficos = ajustar_icono("iconos/barrras.png", tamaño)
        self.icono_mostrar_datos = ajustar_icono("iconos/datos.png", tamaño)
        self.icono_mapa_calor = ajustar_icono("iconos/mapa.png", tamaño)
        self.icono_exportar_pdf = ajustar_icono("iconos/pdf.png", tamaño)
        self.icono_buscar_departamento = ajustar_icono("iconos/buscar.png", tamaño)
        self.icono_imprimir_graficos = ajustar_icono("iconos/imprimir.png", tamaño)

    def pantalla(self):
        frame_izquierdo = tk.Frame(self.root, background="#2655f8")
        frame_izquierdo.pack(side=tk.LEFT, fill=tk.Y)

        self.btn_seleccionar = ttk.Button(frame_izquierdo, image=self.icono_seleccionar, command=self.seleccionar_archivo)
        self.btn_seleccionar.pack(padx=10, pady=10)

        self.btn_mostrar_graficos = ttk.Button(frame_izquierdo, image=self.icono_mostrar_graficos, command=self.mostrar_todos_graficos)
        self.btn_mostrar_graficos.pack(padx=10, pady=10)

        self.btn_mostrar_datos = ttk.Button(frame_izquierdo, image=self.icono_mostrar_datos, command=self.mostrar_datos)
        self.btn_mostrar_datos.pack(padx=10, pady=10)

        self.btn_mapa_calor = ttk.Button(frame_izquierdo, image=self.icono_mapa_calor, command=self.mostrar_mapa)
        self.btn_mapa_calor.pack(padx=10, pady=10)

        self.btn_exportar_pdf = ttk.Button(frame_izquierdo, image=self.icono_exportar_pdf, command=self.exportar_a_pdf)
        self.btn_exportar_pdf.pack(padx=10, pady=10)

        self.btn_imprimir = ttk.Button(frame_izquierdo, image=self.icono_imprimir_graficos, command=self.imprimir_graficos)
        self.btn_imprimir.pack(padx=10, pady=10)

        # Frame derecho
        frame_derecho = tk.Frame(self.root, background="#f1f1fb")
        frame_derecho.pack(fill=tk.BOTH, expand=True)

        frame_derecho_superior = tk.Frame(frame_derecho, background="#f1f1fb")
        frame_derecho_superior.pack(fill=tk.BOTH)

        label_buscar_departamento = ttk.Label(frame_derecho_superior, text="Buscar Departamento:")
        label_buscar_departamento.pack(side=tk.LEFT, padx=10, pady=10)

        #buscador
        self.entry_departamento = ttk.Entry(frame_derecho_superior)
        self.entry_departamento.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_buscar_departamento = ttk.Button(frame_derecho_superior, text="Buscar gráfico", command=lambda: self.buscar_por_departamento('graficos'))
        self.btn_buscar_departamento.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_buscar_datos_departamento = ttk.Button(frame_derecho_superior, text="Buscar Datos", command=lambda: self.buscar_por_departamento('datos'))
        self.btn_buscar_datos_departamento.pack(side=tk.LEFT, padx=10, pady=10)

        self.frame_derecho = tk.Frame(frame_derecho, background="#f1f1fb")
        self.frame_derecho.pack(fill=tk.BOTH, expand=True)
        
        # Agregar un combobox para seleccionar la modalidad de choque
        self.modalidad_choque = ttk.Combobox(frame_derecho_superior, values=['ESPECIAL', 'ATROPELLO', 'CHOQUE', 'DESPISTE'])
        self.modalidad_choque.pack(side=tk.LEFT, padx=10, pady=10)
        self.modalidad_choque.current(0)  # Seleccionar la primera opción por defecto

        # Cambiar el comando del botón para llamar a la función con el argumento adecuado
        self.btn_buscar_modalidad = ttk.Button(frame_derecho_superior, text="Buscar por Modalidad", command=self.buscar_por_modalidad)
        self.btn_buscar_modalidad.pack(side=tk.LEFT, padx=10, pady=10)

    def seleccionar_archivo(self):
        
        file_path = filedialog.askopenfilename(title="Selecciona el archivo CSV", filetypes=[("CSV files", "*.csv")])
        
        if not file_path:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo.")
            return
        
        self.datos = pd.read_csv(file_path, delimiter=',')  

        if 'FECHA' in self.datos.columns:
            self.datos['FECHA'] = pd.to_datetime(self.datos['FECHA'], format='%Y%m%d')
        
        
        self.mostrar_datos()
        self.mostrar_mapa_calor()
    
    def limpiar_canvas(self):
        for widget in self.frame_derecho.winfo_children():
            widget.destroy()
            
    
    def exportar_a_pdf(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf_pages = PdfPages(file_path)

            self.mostrar_todos_graficos()
            canvas = plt.gcf().canvas
            canvas.draw()
            fig = canvas.figure
            pdf_pages.savefig(fig)

            pdf_pages.close()

            messagebox.showinfo("Exportación Exitosa", f"Los gráficos han sido exportados correctamente a:\n{file_path}")

    def imprimir_graficos(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        self.mostrar_todos_graficos()
        canvas = plt.gcf().canvas
        canvas.draw()
        fig = canvas.figure

        # Guardar la figura en un archivo temporal
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        fig.savefig(temp_file.name, dpi=300)

        # Usar PIL para abrir la imagen y lanzar el diálogo de impresión
        img = Image.open(temp_file.name)
        img.show("Imprimir Gráficos")

        # Eliminar el archivo temporal después de mostrar la imagen
        temp_file.close()
        os.remove(temp_file.name)



    def mostrar_todos_graficos(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        self.limpiar_canvas()

        self.datos['MES'] = self.datos['FECHA'].dt.month_name(locale='es_ES')
        
        #el color y tamaño de los cuadros
        fig, axs = plt.subplots(2, 2, figsize=(12, 10), facecolor='#ffffff')
        fig.patch.set_facecolor('#f1f1fb')
        
        # Gráfico de Líneas
        fallecidos_por_mes = self.datos.groupby('MES')['FALLECIDOS'].sum()
        heridos_por_mes = self.datos.groupby('MES')['HERIDOS'].sum()
        ax = axs[0, 0]
        
        ax.plot(fallecidos_por_mes.index, fallecidos_por_mes, label='Fallecidos', color='#2655f8')
        ax.plot(heridos_por_mes.index, heridos_por_mes, label='Heridos', color='#b353d5')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Cantidad')
        ax.set_title('Fallecidos y Heridos por Mes')
        ax.legend()
        ax.set_xticklabels(fallecidos_por_mes.index, rotation=45, ha='right')

        # Gráfico de Barras Fallecidos
        fallecidos_por_mes = self.datos.groupby('MES')['FALLECIDOS'].sum()
        ax = axs[0, 1]
        ax.bar(fallecidos_por_mes.index, fallecidos_por_mes, color='#2655f8')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Número de Fallecidos')
        ax.set_title('Número de Fallecidos por Mes')
        ax.set_xticklabels(fallecidos_por_mes.index, rotation=45, ha='right')

        # Gráfico de Barras Heridos
        heridos_por_mes = self.datos.groupby('MES')['HERIDOS'].sum()
        ax = axs[1, 0]
        ax.bar(heridos_por_mes.index, heridos_por_mes, color='#b353d5')
        ax.set_xlabel('Mes')
        ax.set_ylabel('Número de Heridos')
        ax.set_title('Número de Heridos por Mes')
        ax.set_xticklabels(heridos_por_mes.index, rotation=45, ha='right')

        # Gráfico de Tarta
        fallecidos_por_departamento = self.datos.groupby('DEPARTAMENTO')['FALLECIDOS'].sum()
        otros = fallecidos_por_departamento[fallecidos_por_departamento/fallecidos_por_departamento.sum() < 0.019].sum()
        fallecidos_por_departamento = fallecidos_por_departamento[fallecidos_por_departamento/fallecidos_por_departamento.sum() >= 0.019]
        fallecidos_por_departamento['OTROS'] = otros

        # Agrupar Ucayali, Tacna y San Martín en 'OTROS'
        fallecidos_por_departamento.loc['OTROS'] += fallecidos_por_departamento[['UCAYALI', 'TACNA', 'SAN MARTIN']].sum()
        fallecidos_por_departamento.drop(['UCAYALI', 'TACNA', 'SAN MARTIN'], inplace=True, errors='ignore')
        
        #calcular   valor absoluto con respcto al porsentaje 
        def func(pct, allvals):
            absolute = int(np.round(pct/100.*np.sum(allvals)))
            return "{:.1f}%".format(pct)

        ax = axs[1, 1]
        ax.pie(fallecidos_por_departamento, labels=fallecidos_por_departamento.index, autopct=lambda pct: func(pct, fallecidos_por_departamento), startangle=140, textprops={'fontsize': 8})
        ax.set_title('Distribución de Fallecidos por Departamento')

        plt.subplots_adjust(wspace=0.4, hspace=0.4)

        canvas = FigureCanvasTkAgg(fig, master=self.frame_derecho)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)


    def mostrar_datos(self):
            if self.datos is None:
                messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
                return

            self.limpiar_canvas()
            
            frame_datos = tk.Frame(self.frame_derecho)
            frame_datos.pack(fill=tk.BOTH, expand=True)  #fill direccion , 

            text_widget = Text(frame_datos)
            text_widget.pack(side=LEFT, fill=tk.BOTH, expand=True)

            #para deslizar 
            scrollbar_y = Scrollbar(frame_datos, orient=VERTICAL, command=text_widget.yview)
            scrollbar_y.pack(side=RIGHT, fill=Y)
            text_widget.config(yscrollcommand=scrollbar_y.set)
            
            
            text_widget.insert(tk.END, self.datos.to_string(index=False))
            text_widget.configure(state='disabled')
        
    def mostrar_mapa_calor(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        mapa = folium.Map(location=[-9.19, -75.0152], zoom_start=6)

        heat_data = []
        for index, row in self.datos.iterrows():
            departamento = row['DEPARTAMENTO']
            if departamento in self.coordenadas_departamentos:
                lat_lon = self.coordenadas_departamentos[departamento]
                heat_data.append(lat_lon)

        HeatMap(heat_data).add_to(mapa)

        mapa.save('mapa_accidentes.html')
        webview.create_window('Mapa de Calor', 'mapa_accidentes.html')
        webview.start()

    def mostrar_mapa(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        self.mostrar_mapa_calor()

    def buscar_por_departamento(self, mostrar_tipo='graficos'):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return

        departamento = self.entry_departamento.get().upper()
        if departamento not in self.coordenadas_departamentos:
            messagebox.showwarning("Advertencia", "Departamento no encontrado. Intente nuevamente.")
            return

        datos_departamento = self.datos[self.datos['DEPARTAMENTO'] == departamento]

        if mostrar_tipo == 'graficos':
            self.limpiar_canvas()
            fig, axs = plt.subplots(1, 2, figsize=(16, 8), facecolor='#ffffff')
            fig.patch.set_facecolor('#f1f1fb')

            fallecidos_por_mes = datos_departamento.groupby(datos_departamento['FECHA'].dt.month)['FALLECIDOS'].sum()
            heridos_por_mes = datos_departamento.groupby(datos_departamento['FECHA'].dt.month)['HERIDOS'].sum()

            ax = axs[0]
            fallecidos_por_mes.plot(kind='bar', color='#FFA07A', ax=ax)
            ax.set_title(f'Total de Fallecidos por Mes en {departamento}')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Número de Fallecidos')
            ax.grid(True)

            ax = axs[1]
            heridos_por_mes.plot(kind='bar', color='#20B2AA', ax=ax)
            ax.set_title(f'Total de Heridos por Mes en {departamento}')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Número de Heridos')
            ax.grid(True)

            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.frame_derecho)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        elif mostrar_tipo == 'datos':
            self.limpiar_canvas()
            frame_datos = tk.Frame(self.frame_derecho)
            frame_datos.pack(fill=tk.BOTH, expand=True)
            text_widget = Text(frame_datos, wrap='none')
            text_widget.pack(side=LEFT, fill=tk.BOTH, expand=True)

            scrollbar_y = Scrollbar(frame_datos, orient=VERTICAL, command=text_widget.yview)
            scrollbar_y.pack(side=RIGHT, fill=Y)
            text_widget.config(yscrollcommand=scrollbar_y.set)

            text_widget.insert(tk.END, datos_departamento.to_string(index=False))
            text_widget.configure(state='disabled')

    def buscar_por_modalidad(self):
        if self.datos is None:
            messagebox.showwarning("Advertencia", "Primero selecciona un archivo CSV.")
            return
        
        modalidad = self.modalidad_choque.get().upper()
        if modalidad not in self.datos['MODALIDAD'].str.upper().unique():
            messagebox.showwarning("Advertencia", "Modalidad no encontrada.")
            return
        
        datos_modalidad = self.datos[self.datos['MODALIDAD'].str.upper() == modalidad]
        self.limpiar_canvas()
        
        frame_datos = tk.Frame(self.frame_derecho)
        frame_datos.pack(fill=tk.BOTH, expand=True)
        text_widget = Text(frame_datos, wrap='none')
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar_y = Scrollbar(frame_datos, orient=VERTICAL, command=text_widget.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=Y)
        text_widget.config(yscrollcommand=scrollbar_y.set)
        
        text_widget.insert(tk.END, datos_modalidad.to_string(index=False))
        text_widget.configure(state='disabled')
        
if __name__ == "__main__":
    
    root = tk.Tk()
    app = VisualizacionAccidentes(root)
    root.mainloop()
