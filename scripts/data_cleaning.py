#!/usr/bin/env python3
"""
scripts/data_cleaning.py
Limpieza y generación de outputs para Power BI.
Uso:
python scripts/data_cleaning.py --input data/raw/index_1.csv --output outputs/cleaned_data.csv
"""

import argparse
import os
import pandas as pd
import numpy as np

print("Script started...")

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def load_data(path):
    # Intenta leer con pandas detectando encoding y parseo de fecha
    df = pd.read_csv(path, dtype=str)
    # normalizar columnas
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    return df

def parse_and_cast(df):
    # si hay columna 'datetime' la convertimos
    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    elif 'date' in df.columns:
        # si solo existe 'date' intentar parseo
        df['datetime'] = pd.to_datetime(df['date'], errors='coerce')

    # money -> numeric
    if 'money' in df.columns:
        df['money'] = pd.to_numeric(df['money'], errors='coerce')
    else:
        # intenta detectar columna de precio por heurística
        possible = [c for c in df.columns if 'price' in c or 'amount' in c]
        if possible:
            df['money'] = pd.to_numeric(df[possible[0]], errors='coerce')
        else:
            df['money'] = np.nan

    # payment method: unificar cash/card
    if 'cash_type' in df.columns:
        df['payment_method'] = df['cash_type'].str.lower().fillna('')
    else:
        df['payment_method'] = np.where(df['card'].notna(), 'card', 'cash')

    # card id
    if 'card' not in df.columns:
        df['card'] = np.nan

    # coffee name
    if 'coffee_name' in df.columns:
        df['coffee_name'] = df['coffee_name'].str.strip()
    else:
        # intenta detectar
        textcols = df.select_dtypes(include='object').columns.tolist()
        candidates = [c for c in textcols if c not in ['datetime','date','cash_type','card','payment_method']]
        if candidates:
            df['coffee_name'] = df[candidates[-1]].astype(str).str.strip()
        else:
            df['coffee_name'] = 'unknown'

    # derived time features
    df['date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['hour'] = df['datetime'].dt.hour

    return df

def basic_clean(df):
    # quitar duplicados exactos
    df = df.drop_duplicates()

    # eliminar filas sin datetime o sin coffee_name
    df = df[~df['datetime'].isna()]
    df = df[~df['coffee_name'].isna()]

    # llenar NAs razonables
    df['card'] = df['card'].fillna('')
    df['payment_method'] = df['payment_method'].replace('', 'unknown')

    # revenue = money (por row)
    df['revenue'] = df['money'].fillna(0.0)

    return df

def save_outputs(df, out_csv):
    safe_mkdir(os.path.dirname(out_csv) or '.')
    df.to_csv(out_csv, index=False)
    print(f"Saved cleaned data to {out_csv}")

    # agregados útiles
    out_dir = os.path.join(os.path.dirname(out_csv), '')
    monthly = (
        df.groupby(['year','month'])
        .agg(total_revenue=('revenue','sum'),
             transactions=('datetime','count'))
        .reset_index()
    )
    monthly.to_csv(os.path.join(out_dir, 'monthly_sales.csv'), index=False)
    print("Saved monthly aggregation to monthly_sales.csv")

    # top coffees
    top_coffees = (
        df.groupby('coffee_name')
        .agg(total_revenue=('revenue','sum'),
             transactions=('datetime','count'))
        .reset_index()
        .sort_values('total_revenue', ascending=False)
    )
    top_coffees.to_csv(os.path.join(out_dir, 'top_coffees.csv'), index=False)
    print("Saved top_coffees.csv")

def main():
    parser = argparse.ArgumentParser(description="Data cleaning for coffee sales dataset")
    parser.add_argument('--input', required=True, help='Path to raw csv (e.g. data/raw/index_1.csv)')
    parser.add_argument('--output', default='outputs/cleaned_data.csv', help='Path to cleaned csv')
    args = parser.parse_args()

    df = load_data(args.input)
    df = parse_and_cast(df)
    df = basic_clean(df)
    save_outputs(df, args.output)

if __name__ == "__main__":
    main()
    
print("Cleaning finished")