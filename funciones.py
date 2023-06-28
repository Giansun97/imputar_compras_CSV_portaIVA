from typing import Tuple
import pandas as pd
import os
import numpy as np
import openpyxl
from pandas import DataFrame


def leer_archivo_proveedores(ubicacion_archivo: str,
                             nombre_archivo: str
                             ) -> pd.DataFrame:

    ruta_archivo = ubicacion_archivo + '/' + nombre_archivo

    df = pd.read_excel(ruta_archivo)
    return df


def agregar_columna_periodo(df: pd.DataFrame,
                            archivo_csv: str
                            ) -> tuple[DataFrame, str]:
    """
    Esta funcion extrae el periodo del nombre del archivo csv.
    Crea una nueva columna en el DataFrame con el periodo extraido
    -------------
    :param df: DataFrame
    :param archivo_csv: ruta y nombre del archivo csv.
    -------------
    :return: DataFrame con la columna del periodo, variable con el periodo extraido
    """
    nombre_archivo = os.path.basename(archivo_csv).split('.')[0]

    periodo = nombre_archivo.split("_")[2] if len(nombre_archivo.split("_")) >= 3 else ''

    df.insert(0, "Periodo", periodo)

    return df, periodo


def crear_asiento_compras(merged, pivot):
    # Creamos una lista de DataFrames a concatenar Percep IVA, Percep IIBB, IVA Credito fiscal
    df_list = [pivot,
               pd.DataFrame({'Haber': np.nan, 'Debe': merged['Importe de Percepciones o Pagos a Cuenta de IVA'].sum()},
                            index=['Percep IVA']),
               pd.DataFrame({'Haber': np.nan, 'Debe': merged['Importe de Percepciones de Ingresos Brutos'].sum()},
                            index=['Percep IIBB']),
               pd.DataFrame({'Haber': np.nan, 'Debe': merged['Total IVA'].sum()}, index=['IVA Credito Fiscal']),
               pd.DataFrame({'Haber': np.nan, 'Debe': merged['Importe de Impuestos Internos'].sum()},
                            index=['Impuestos Internos'])
               ]

    # Concatenar los DataFrames de la lista
    df_asiento = pd.concat(df_list)

    # Creo el dataframe de total proveedores
    proveedores = pd.DataFrame({'Debe': np.nan, 'Haber': df_asiento['Debe'].sum()}, index=['Proveedores'])

    # Lo concateno al Asiento IVA Compras
    df_asiento = pd.concat([df_asiento, proveedores])

    # Completo los NaN con ceros
    df_asiento = df_asiento.fillna(0)

    return df_asiento, merged


def mostrar_resultados_terminal(df_asiento, merged, periodo):

    total_nan = sum(merged['Imputacion'] == 'N/A')
    total_haber = round(df_asiento['Haber'].sum(), 2)
    total_compras = round(merged['Importe Total'].sum(), 2)
    control = abs(round(total_haber - total_compras, 2))
    umbral_diferencia = 3

    print('--------------------------------------')
    print(f'Resultados del periodo {periodo}')
    print('--------------------------------------')
    print(f'Total de compras: ${total_compras}')
    print(f'Total del haber: ${total_haber}')
    print(f'Diferencia: ${control}')
    if control <= umbral_diferencia:
        if total_nan > 0:
            print(f'ATENCION: En el periodo {periodo} hay un total de {total_nan} proveedores sin imputación.')
        print('--------------------------------------')
        print(f'Asiento IVA compras del periodo {periodo}:')
        print(df_asiento)
    else:
        print(f'ATENCION: Revisar el asiento del periodo {periodo}.')
        print(f'Hay una diferencia entre el total de compras y el total de proveedores en el haber de {control}.')
        if total_nan > 0:
            print(f'ATENCION: En el periodo {periodo} hay un total de {total_nan} proveedores sin imputación.')


def convertir_columnas_float(compras, columns_to_numeric):
    for column in columns_to_numeric:
        compras[column] = compras[column].str.replace(',', '.')
        compras[column] = compras[column].astype('float')


