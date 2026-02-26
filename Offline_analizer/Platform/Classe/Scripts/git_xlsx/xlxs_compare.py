# -*- coding: utf-8 -*-
# @file xlxs_compare.py
# @author ADAS_HIL_TEAM
# @date 08-21-2023

##################################################################
# C O P Y R I G H T S
# ----------------------------------------------------------------
# Copyright (c) 2023 by Robert Bosch GmbH. All rights reserved.

# The reproduction, distribution and utilization of this file as
# well as the communication of its contents to others without express
# authorization is prohibited. Offenders will be held liable for the
# payment of damages. All rights reserved in the event of the grant
# of a patent, utility model or design.

##################################################################


import pandas as pd
try:
    pd.set_option('future.no_silent_downcasting', True)
except:
    pass
import sys
import numpy as np
from win32com.client import Dispatch
import os

excel_diff_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\Excel_diff.xlsx"

def make_your_style(val):
    """
    Takes a scalar and returns a string with
    the css property `'background-color: red'` for string with -->

    Args:
      val (int): Value of the style

    Returns (str):
        Changed background color


    """
    color = 'red' if '-->' in str(val) else 'white'
    return f'background-color: {color}'

def open_diff_excel():
    """ Open excel"""
    try:
        xlApp = Dispatch("Excel.Application")
        xlApp.Visible = True
        xlApp.Workbooks.Open(excel_diff_path)
    except Exception as exp:
        print(f"Failed to save Excel: {exp}")


if __name__ == '__main__':
    dataframes = {}
    df1=pd.read_excel(sys.argv[1],sheet_name=None, na_filter=None)
    df2=pd.read_excel(sys.argv[2], sheet_name=None, na_filter=None)
    for sheet in df1.keys():
        if df1[sheet].equals(df2[sheet]) is False:
            if df1[sheet].shape[0] > df2[sheet].shape[0]:
                df2[sheet] = df2[sheet].reindex(list(range(0, df1[sheet].shape[0]))).reset_index(drop=True)
                df2[sheet] = df2[sheet].fillna('')
            elif df1[sheet].shape[0] < df2[sheet].shape[0]:
                df1[sheet] = df1[sheet].reindex(list(range(0, df2[sheet].shape[0]))).reset_index(drop=True)
                df1[sheet] = df1[sheet].fillna('')
            comparison_values = df1[sheet].values == df2[sheet].values
            rows, cols = np.where(comparison_values == False)
            for item in zip(rows,cols):
                df1[sheet].iloc[item[0], item[1]] = f'{df1[sheet].iloc[item[0], item[1]]} --> {df2[sheet].iloc[item[0], item[1]]}'
            dataframes[sheet] = df1[sheet]

    with pd.ExcelWriter(excel_diff_path,mode='w',engine='openpyxl') as writer:
        for new_sheet in dataframes.keys():
            dataframes[new_sheet].style.applymap(make_your_style).to_excel(writer, index=False, header=True , sheet_name=new_sheet)

    open_diff_excel()
