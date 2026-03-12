#!/usr/bin/env python3
"""
scripts/eda_plots.py
Genera gráficas PNG para README / exploración
Uso:
python scripts/eda_plots.py --input outputs/cleaned_data.csv --outdir outputs/figures
"""

import argparse
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set(style="whitegrid", rc={'figure.figsize':(10,5)})

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def plot_time_series(df, outdir):
    df_group = df.groupby('date').agg(total_revenue=('revenue','sum')).reset_index()
    plt.figure(figsize=(12,5))
    plt.plot(pd.to_datetime(df_group['date']), df_group['total_revenue'])
    plt.title('Revenue over time (daily)')
    plt.xlabel('Date')
    plt.ylabel('Revenue')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'revenue_over_time.png'))
    plt.close()

def plot_top_coffees(df, outdir, n=10):
    top = df.groupby('coffee_name').agg(total_revenue=('revenue','sum')).reset_index()
    top = top.sort_values('total_revenue', ascending=False).head(n)
    plt.figure(figsize=(10,6))
    sns.barplot(x='total_revenue', y='coffee_name', data=top)
    plt.title('Top coffees by revenue')
    plt.xlabel('Revenue')
    plt.ylabel('Coffee')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'top_coffees.png'))
    plt.close()

def plot_hourly_heatmap(df, outdir):
    pivot = df.groupby(['hour','coffee_name']).agg(revenue=('revenue','sum')).reset_index()
    # pivot table: hour x coffee_name
    table = pivot.pivot(index='hour', columns='coffee_name', values='revenue').fillna(0)
    plt.figure(figsize=(14,6))
    sns.heatmap(table, cmap='YlGnBu')
    plt.title('Revenue heatmap: hour vs coffee_name')
    plt.xlabel('Coffee')
    plt.ylabel('Hour of day')
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, 'hourly_heatmap.png'))
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--outdir', default='outputs/figures')
    args = parser.parse_args()

    safe_mkdir(args.outdir)
    df = pd.read_csv(args.input, parse_dates=['datetime'])
    plot_time_series(df, args.outdir)
    plot_top_coffees(df, args.outdir)
    plot_hourly_heatmap(df, args.outdir)
    print(f"Plots saved to {args.outdir}")

if __name__ == "__main__":
    main()