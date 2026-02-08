import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import os
import textwrap

sns.set_theme(style="whitegrid")

def aggregate_data(data, limit=10):
    """
    Returns the Top N countries and aggregates the rest into 'Other'.
    """
    if not data: return []
    if len(data) <= limit: return data

    sorted_data = sorted(data, key=lambda x: x['GDP'], reverse=True)
    
    top_n = sorted_data[:limit]
    rest = sorted_data[limit:]

    other_gdp = sum(row['GDP'] for row in rest)

    other_entry = {'Country': f'Other ({len(rest)})', 'GDP': other_gdp, 'Year': top_n[0]['Year'], 'Region': top_n[0]['Region']}
    
    return top_n + [other_entry]

def create_dashboard(comparison_data, trend_data, config):
    if not comparison_data and not trend_data:
        print("No data available to visualize.")
        return

    agg_comp_data = aggregate_data(comparison_data, limit=15)

    fig = plt.figure(figsize=(16, 9)) 
    fig.suptitle(f"GDP Analysis Dashboard", fontsize=20, fontweight='bold')
    
    gs = fig.add_gridspec(2, 2)
    ax_bar = fig.add_subplot(gs[0, 0])
    ax_pie = fig.add_subplot(gs[0, 1])
    ax_line = fig.add_subplot(gs[1, :])

    #Bar Chart
    if agg_comp_data:
        countries = [row['Country'] for row in agg_comp_data]
        values_bn = [row['GDP'] / 1e9 for row in agg_comp_data]
        
        if len(agg_comp_data) > 8:
            sns.barplot(x=values_bn, y=countries, palette="viridis", ax=ax_bar)
            ax_bar.set_title(f"Regional Economies (Top 15 + Other)")
            ax_bar.set_xlabel("GDP (Billions USD)")
        else:
            sns.barplot(x=countries, y=values_bn, palette="viridis", ax=ax_bar)
            ax_bar.set_title("Regional Comparison")
            ax_bar.set_ylabel("GDP (Billions USD)")
            wrapped = [textwrap.fill(c, 10) for c in countries]
            ax_bar.set_xticklabels(wrapped, rotation=0)

    #Pie Chart
    if comparison_data:
        pie_data = aggregate_data(comparison_data, limit=9)
        countries = [row['Country'] for row in pie_data]
        values = [row['GDP'] for row in pie_data]

        explode = [0] * len(pie_data)
        if "Other" in countries[-1]:
            explode[-1] = 0.1 

        ax_pie.pie(values, labels=countries, autopct='%1.1f%%', startangle=140,
                   explode=explode, colors=sns.color_palette("pastel"))
        ax_pie.set_title("Market Share Distribution")

    #Line Chart
    if trend_data:
        years = [row['Year'] for row in trend_data]
        trend_vals = [row['GDP'] / 1e9 for row in trend_data]
        sns.lineplot(x=years, y=trend_vals, marker='o', linewidth=2.5, ax=ax_line, color='crimson')
        ax_line.set_title("GDP Growth Trend")
        ax_line.set_ylabel("GDP (Billions USD)")
        ax_line.grid(True, linestyle='--')

    plt.subplots_adjust(left=0.08, right=0.95, top=0.9, bottom=0.1, hspace=0.4, wspace=0.3)
    
    save_path = config.get('plot', {}).get('save_path', 'outputs/dashboard.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    try:
        plt.savefig(save_path, dpi=300)
    except: pass
    
    if config.get('plot', {}).get('show_plot', True):
        plt.show()

def get_bar_figure(data):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        agg_data = aggregate_data(data, limit=15)
        countries = [row['Country'] for row in agg_data]
        values = [row['GDP'] / 1e9 for row in agg_data]

        if len(agg_data) > 8:
            #Horizontal
            sns.barplot(x=values, y=countries, palette="viridis", ax=ax)
            ax.set_title("Top Economies vs Rest")
            ax.set_xlabel("GDP (Billions USD)")
            fig.subplots_adjust(left=0.25, right=0.95, top=0.9, bottom=0.15)
        else:
            #Vertical
            sns.barplot(x=countries, y=values, palette="viridis", ax=ax)
            ax.set_title("Regional Comparison")
            ax.set_ylabel("GDP (Billions USD)")
            wrapped_labels = [textwrap.fill(c, 12) for c in countries]
            ax.set_xticklabels(wrapped_labels, rotation=0)
            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
            
    return fig

def get_pie_figure(data):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        agg_data = aggregate_data(data, limit=9)
        countries = [row['Country'] for row in agg_data]
        values = [row['GDP'] for row in agg_data]

        explode = [0] * len(agg_data)
        if "Other" in countries[-1]:
            explode[-1] = 0.1

        ax.pie(values, labels=countries, autopct='%1.1f%%', startangle=140, 
               explode=explode, colors=sns.color_palette("pastel"))
        ax.set_title("Market Share (Total = 100%)")
    
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    return fig

def get_histogram_figure(data):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        values = [row['GDP'] / 1e9 for row in data]
        sns.histplot(values, bins=15, kde=True, color="purple", ax=ax)
        ax.set_xlabel("GDP (Billions USD)")
        ax.set_ylabel("Count")
    
    ax.set_title("Wealth Distribution (Histogram)")
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    return fig

def get_line_figure(data):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        years = [row['Year'] for row in data]
        values = [row['GDP'] / 1e9 for row in data]
        sns.lineplot(x=years, y=values, marker='o', ax=ax, color='crimson')
    
    ax.set_title("Growth Trend")
    ax.set_ylabel("GDP (Billions USD)")
    ax.grid(True, linestyle='--')
    
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    return fig