import os
import pandas as pd
import numpy as np
from funciones import leer_archivo_proveedores, agregar_columna_periodo, crear_asiento_compras, \
    mostrar_resultados_terminal, convertir_columnas_float


# Inputs del usuario
# ubicacion = input("Ingrese la ubicación de la carpeta que contiene los archivos CSV: ")
# ubicacion_archivo_proveedores = input("Ingrese la ubicación del archivo proveedores:")
# nombre_archivo_proveedores = input('Ingrese el nombre del archivo de proveedores:')


def ejecutar_script_compras(ubicacion,
                            ubicacion_archivo_proveedores,
                            nombre_archivo_proveedores):
    # Leer archivo de proveedores
    df_proveedores = leer_archivo_proveedores(ubicacion_archivo_proveedores, nombre_archivo_proveedores)

    # Obtener una lista de todos los archivos en la carpeta
    archivos = os.listdir(ubicacion)

    # Filtrar la lista para obtener solo los archivos CSV que cumplen con el patrón de nombres de archivo esperado
    archivos_csv = [archivo for archivo in archivos if archivo.endswith('.csv')]

    # Iterar sobre cada archivo CSV y procesarlo como antes
    for archivo_csv in archivos_csv:
        # Leemos el csv de compras
        compras = pd.read_csv(os.path.join(ubicacion, archivo_csv), delimiter=';')

        # Agregamos la columna periodo (guardamos también la variable periodo)
        compras, periodo = agregar_columna_periodo(compras, archivo_csv)

        # Creamos una lista de las columnas que vamos a pasar a formato float
        columns_to_numeric = ['Importe No Gravado', 'Importe Exento', 'Importe de Per. o Pagos a Cta. de Otros Imp. '
                                                                      'Nac.',
                              'Importe de Percepciones de Ingresos Brutos', 'Importe de Impuestos Municipales',
                              'Importe de Percepciones o Pagos a Cuenta de IVA', 'Importe de Impuestos Internos',
                              'Importe Otros Tributos', 'Total Neto Gravado', 'Total IVA', 'Importe Total']

        # Convertimos las columnas en tipo float
        convertir_columnas_float(compras, columns_to_numeric)

        # Filtrar las filas donde el Tipo de Comprobante es igual a 11 y ponerlas como No Gravado
        filt = compras['Tipo de Comprobante'] == 11
        compras.loc[filt, 'Importe No Gravado'] = compras.loc[filt, 'Importe Total'] * 1

        # Creamos la columna Debe
        compras['Debe'] = compras['Total Neto Gravado'] + compras['Importe No Gravado'] + compras['Importe Exento']

        # Renombramos la columna Nro. Doc. Vendedor
        compras = compras.rename(columns={'Nro. Doc. Vendedor': 'CUIT'})

        # Mergeamos los archivos de iva compras y proveedores por el ID "Cuit"
        merged = pd.merge(compras, df_proveedores[['CUIT', 'Imputacion']], on='CUIT', how='left')

        # Completamos los N/A de la columna imputacion
        merged['Imputacion'] = merged['Imputacion'].fillna('N/A')

        # Creamos una pivot table
        pivot = pd.pivot_table(merged,
                               index=['Imputacion'],
                               values='Debe',
                               aggfunc=np.sum)

        # Creamos asiento IVA Compras
        df_asiento, merged = crear_asiento_compras(merged, pivot)

        # Exportamos a excel los resultados
        merged.to_excel(f'WP_imputaciones_periodo_{periodo}.xlsx',
                        index=False)
        df_asiento.to_excel(f'AsientoIvaCompras_periodo_{periodo}.xlsx')


