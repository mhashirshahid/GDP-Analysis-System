import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import os
import textwrap

sns.set_theme(style="whitegrid")

def aggregate_data(data, limit=10, specific_country=None):
    if not data: return []
    if len(data) <= limit: return data

    sorted_data = sorted(data, key=lambda x: x['GDP'], reverse=True)
    
    top_n = sorted_data[:limit]
    rest = sorted_data[limit:]

    if specific_country:
        target = next((r for r in rest if r['Country'] == specific_country), None)
        if target:
            rest.remove(target)
            top_n.append(target)
            
    if rest:
        other_gdp = sum(row['GDP'] for row in rest)
        other_entry = {'Country': f'Other ({len(rest)})', 'GDP': other_gdp, 'Year': top_n[0]['Year'], 'Region': top_n[0]['Region']}
        return top_n + [other_entry]
    
    return top_n

def create_dashboard(comparison_data, trend_data, config, highlight_country=None):
    if not comparison_data and not trend_data:
        print("No data available to visualize.")
        return

    target_country = config.get('filters', {}).get('country')
    
    if target_country:
        fig = plt.figure(figsize=(16, 9))
        fig.suptitle(f"Country Analysis: {target_country}", fontsize=20, fontweight='bold')
        gs = fig.add_gridspec(2, 1)
        ax_hist = fig.add_subplot(gs[0, 0])
        ax_growth = fig.add_subplot(gs[1, 0])

        if trend_data: 
            sorted_data = sorted(trend_data, key=lambda x: x['Year'])
            years = [r['Year'] for r in sorted_data]
            values = [r['GDP'] / 1e9 for r in sorted_data]
            
            sns.barplot(x=years, y=values, color="#3498db", ax=ax_hist)
            ax_hist.set_title("GDP Performance History")
            ax_hist.set_ylabel("GDP (Billions USD)")

            for ind, label in enumerate(ax_hist.get_xticklabels()):
                if ind % 2 != 0: label.set_visible(False)

        if trend_data and len(trend_data) > 1:
            sorted_data = sorted(trend_data, key=lambda x: x['Year'])
            years = []
            rates = []
            prev = sorted_data[0]['GDP']
            
            for i in range(1, len(sorted_data)):
                curr = sorted_data[i]['GDP']
                rate = ((curr - prev) / prev) * 100
                years.append(sorted_data[i]['Year'])
                rates.append(rate)
                prev = curr
                
            sns.lineplot(x=years, y=rates, marker='o', color='green', ax=ax_growth)
            ax_growth.axhline(0, color='black', linewidth=1, linestyle='--')
            ax_growth.set_title("Year-Over-Year Growth Rate (%)")
            ax_growth.set_ylabel("Growth (%)")
            ax_growth.grid(True)

    else:
        #REGIONAL MODE (Standard)
        agg_comp_data = aggregate_data(comparison_data, limit=15, specific_country=highlight_country)

        fig = plt.figure(figsize=(16, 9)) 
        fig.suptitle(f"GDP Analysis Dashboard", fontsize=20, fontweight='bold')
        
        gs = fig.add_gridspec(2, 2)
        ax_bar = fig.add_subplot(gs[0, 0])
        ax_pie = fig.add_subplot(gs[0, 1])
        ax_line = fig.add_subplot(gs[1, :])

        if agg_comp_data:
            countries = [row['Country'] for row in agg_comp_data]
            values_bn = [row['GDP'] / 1e9 for row in agg_comp_data]
            
            palette = "viridis"
            if highlight_country:
                palette = ["#e74c3c" if c == highlight_country else "#3498db" for c in countries]

            if len(agg_comp_data) > 8:
                sns.barplot(x=values_bn, y=countries, palette=palette, ax=ax_bar)
                ax_bar.set_title(f"Regional Economies (Top 15 + Other)")
                ax_bar.set_xlabel("GDP (Billions USD)")
            else:
                sns.barplot(x=countries, y=values_bn, palette=palette, ax=ax_bar)
                ax_bar.set_title("Regional Comparison")
                ax_bar.set_ylabel("GDP (Billions USD)")
                wrapped = [textwrap.fill(c, 10) for c in countries]
                ax_bar.set_xticklabels(wrapped, rotation=0)

        if comparison_data:
            pie_data = aggregate_data(comparison_data, limit=9, specific_country=highlight_country)
            countries = [row['Country'] for row in pie_data]
            values = [row['GDP'] for row in pie_data]

            explode = [0] * len(pie_data)
            if highlight_country:
                explode = [0.15 if c == highlight_country else 0 for c in countries]
            elif "Other" in countries[-1]:
                explode[-1] = 0.1 

            ax_pie.pie(values, labels=countries, autopct='%1.1f%%', startangle=140,
                       explode=explode, colors=sns.color_palette("pastel"))
            ax_pie.set_title("Market Share Distribution")

        if trend_data:
            years = [row['Year'] for row in trend_data]
            trend_vals = [row['GDP'] / 1e9 for row in trend_data]
            sns.lineplot(x=years, y=trend_vals, marker='o', linewidth=2.5, ax=ax_line, color='crimson')
            ax_line.set_title(f"GDP Growth Trend: {trend_data[0]['Country']}")
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

def get_bar_figure(data, highlight_country=None):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        agg_data = aggregate_data(data, limit=15, specific_country=highlight_country)
        countries = [row['Country'] for row in agg_data]
        values = [row['GDP'] / 1e9 for row in agg_data]

        palette = "viridis"
        if highlight_country:
            palette = ["#e74c3c" if c == highlight_country else "#3498db" for c in countries]

        if len(agg_data) > 8:
            sns.barplot(x=values, y=countries, palette=palette, ax=ax)
            ax.set_title("Top Economies vs Rest")
            ax.set_xlabel("GDP (Billions USD)")
            fig.subplots_adjust(left=0.25, right=0.95, top=0.9, bottom=0.15)
        else:
            sns.barplot(x=countries, y=values, palette=palette, ax=ax)
            ax.set_title("Regional Comparison")
            ax.set_ylabel("GDP (Billions USD)")
            wrapped_labels = [textwrap.fill(c, 12) for c in countries]
            ax.set_xticklabels(wrapped_labels, rotation=0)
            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
            
    return fig

def get_pie_figure(data, highlight_country=None):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        agg_data = aggregate_data(data, limit=9, specific_country=highlight_country)
        countries = [row['Country'] for row in agg_data]
        values = [row['GDP'] for row in agg_data]

        explode = [0] * len(agg_data)
        if highlight_country:
            explode = [0.15 if c == highlight_country else 0 for c in countries]
        elif "Other" in countries[-1]:
            explode[-1] = 0.1

        ax.pie(values, labels=countries, autopct='%1.1f%%', startangle=140, 
               explode=explode, colors=sns.color_palette("pastel"))
        ax.set_title("Market Share (Total = 100%)")
    
    fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    return fig

def get_histogram_figure(data, highlight_country=None):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        values = [row['GDP'] / 1e9 for row in data]
        sns.histplot(values, bins=15, kde=True, color="purple", ax=ax)
        
        if highlight_country:
            target_row = next((r for r in data if r['Country'] == highlight_country), None)
            if target_row:
                target_val = target_row['GDP'] / 1e9
                ax.axvline(target_val, color='#e74c3c', linestyle='--', linewidth=2, label=highlight_country)
                ax.legend()

        ax.set_xlabel("GDP (Billions USD)")
        ax.set_ylabel("Count")
    
    ax.set_title("Wealth Distribution (Histogram)")
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    return fig

def get_line_figure(data):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    title = "Growth Trend"
    if data:
        years = [row['Year'] for row in data]
        values = [row['GDP'] / 1e9 for row in data]
        sns.lineplot(x=years, y=values, marker='o', ax=ax, color='crimson')
        title = f"Growth Trend: {data[0]['Country']}"
    
    ax.set_title(title)
    ax.set_ylabel("GDP (Billions USD)")
    ax.grid(True, linestyle='--')
    
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    return fig

def get_country_year_bar(data, country_name):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data:
        sorted_data = sorted(data, key=lambda x: x['Year'])
        years = [r['Year'] for r in sorted_data]
        values = [r['GDP'] / 1e9 for r in sorted_data]
        
        sns.barplot(x=years, y=values, color="#3498db", ax=ax)
        ax.set_title(f"{country_name}: GDP Performance by Year")
        ax.set_ylabel("GDP (Billions USD)")
        
        if len(years) > 10:
            for ind, label in enumerate(ax.get_xticklabels()):
                if ind % 2 != 0: label.set_visible(False)
                
    fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
    return fig

def get_growth_rate_line(data, country_name):
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    if data and len(data) > 1:
        sorted_data = sorted(data, key=lambda x: x['Year'])
        years = []
        growth_rates = []
        
        prev_gdp = sorted_data[0]['GDP']
        
        for i in range(1, len(sorted_data)):
            curr_gdp = sorted_data[i]['GDP']
            curr_year = sorted_data[i]['Year']
            rate = ((curr_gdp - prev_gdp) / prev_gdp) * 100
            
            years.append(curr_year)
            growth_rates.append(rate)
            prev_gdp = curr_gdp
            
        sns.lineplot(x=years, y=growth_rates, marker='o', color='green', ax=ax)
        ax.axhline(0, color='black', linewidth=1, linestyle='--')
        ax.set_title(f"{country_name}: Year-Over-Year Growth Rate (%)")
        ax.set_ylabel("Growth (%)")
        
    return fig