import os
import tkinter as tk
from tkinter import filedialog
import openpyxl
import numpy as np
import pandas as pd
from compras_ok import ejecutar_script_compras
from funciones import crear_asiento_compras, convertir_columnas_float, agregar_columna_periodo, leer_archivo_proveedores


class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicacion imputaciones compras")
        self.geometry("650x325")

        # Título de la ventana principal
        titulo_label = tk.Label(self, text="Imputaciones de Compras desde CSV\n (Portal IVA)",
                                font=("Arial", 18, "bold"))
        titulo_label.pack(pady=20)

        # UI Ubicacion archivos CSV
        self.frame_ubicacion = tk.Frame(self)
        self.frame_ubicacion.pack(pady=10)

        self.lbl_ubicacion = tk.Label(self.frame_ubicacion,
                                      text="Seleccione la carpeta que contiene los archivos CSV: ")
        self.lbl_ubicacion.pack()

        self.btn_frame_ubicacion = tk.Frame(self.frame_ubicacion)
        self.btn_frame_ubicacion.pack()

        self.btn_ubicacion = tk.Button(self.btn_frame_ubicacion,
                                       text="Seleccionar Carpeta",
                                       command=self.seleccionar_carpeta)
        self.btn_ubicacion.pack(side=tk.LEFT, padx=5)

        self.lbl_estado_ubicacion_compras = tk.Label(self.btn_frame_ubicacion, text="")
        self.lbl_estado_ubicacion_compras.pack(side=tk.LEFT)

        # UI archivo Proveedores
        self.frame_archivo_proveedores = tk.Frame(self)
        self.frame_archivo_proveedores.pack(pady=10)

        self.lbl_archivo_proveedores = tk.Label(self.frame_archivo_proveedores,
                                                text="Seleccione el archivo de imputaciones de proveedores:")
        self.lbl_archivo_proveedores.pack()

        self.btn_frame = tk.Frame(self.frame_archivo_proveedores)
        self.btn_frame.pack()

        self.btn_archivo_proveedores = tk.Button(self.btn_frame,
                                                 text="Seleccionar Archivo",
                                                 command=self.seleccionar_archivo)
        self.btn_archivo_proveedores.pack(side=tk.LEFT, padx=5)

        self.lbl_estado_archivo = tk.Label(self.btn_frame, text="")
        self.lbl_estado_archivo.pack(side=tk.LEFT)

        # UI Boton ejecutar Script
        self.btn_ejecutar = tk.Button(self, text="Ejecutar", command=self.ejecutar_script)
        self.btn_ejecutar.pack(pady=10)

        self.ubicacion = ""
        self.archivo_proveedores = ""

        # UI mensaje de exportacion correcta
        self.lbl_estado_ejecucion = tk.Label(self, text="")
        self.lbl_estado_ejecucion.pack()

    import os

    def seleccionar_carpeta(self):
        ubicacion_compras = filedialog.askdirectory()
        if ubicacion_compras:
            self.ubicacion = ubicacion_compras
            archivos_csv = [archivo for archivo in os.listdir(self.ubicacion) if archivo.endswith(".csv")]
            if archivos_csv:
                self.lbl_estado_ubicacion_compras.config(text="Archivos CSV encontrados",
                                                         fg='green')
            else:
                self.lbl_estado_ubicacion_compras.config(text="No se encontraron archivos CSV",
                                                         fg='red')
        else:
            self.lbl_estado_ubicacion_compras.config(text="No se ha seleccionado ninguna carpeta")

    def seleccionar_archivo(self):
        ruta_archivo = filedialog.askopenfilename()

        if ruta_archivo:
            self.archivo_proveedores = ruta_archivo
            df_proveedores = pd.read_excel(self.archivo_proveedores, engine='openpyxl')

            if 'CUIT' not in df_proveedores.columns or 'Imputacion' not in df_proveedores.columns:
                self.lbl_estado_archivo.config(text="El archivo de proveedores no tiene el formato correcto",
                                               fg='red')
            else:
                self.lbl_estado_archivo.config(text="Archivo seleccionado",
                                               fg='green')

        else:
            self.lbl_estado_archivo.config(text="No se ha seleccionado ningún archivo")

    def ejecutar_script(self):
        ubicacion = self.ubicacion
        ubicacion_archivo_proveedores = os.path.dirname(self.archivo_proveedores)
        nombre_archivo_proveedores = os.path.basename(self.archivo_proveedores)

        ejecutar_script_compras(ubicacion, ubicacion_archivo_proveedores, nombre_archivo_proveedores)

        # Actualizamos el mensaje de ejecución exitosa
        self.lbl_estado_ejecucion.config(text=f"Script ejecutado correctamente. Archivos exportados a: \n {ubicacion}.",
                                         fg='green')


if __name__ == "__main__":
    app = MyApp()
    app.mainloop()
