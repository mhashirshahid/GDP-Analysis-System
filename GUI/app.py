import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

from modules import loader, processor, visualizer

class GDPApp(tk.Tk):
    def __init__(self, config=None):
        super().__init__()
        
        self.title("GDP Analysis System - Enterprise Edition")
        self.geometry("1200x800")
        self.config = config or {}

        self.load_data()

        self.create_sidebar()
        self.create_content_area()

        default_region = self.config.get('filters', {}).get('region', '')
        default_year = str(self.config.get('filters', {}).get('year', ''))
        
        if default_region in self.regions:
            self.region_var.set(default_region)
        if default_year in [str(y) for y in self.years]:
            self.year_var.set(default_year)

        self.current_chart_type = "Bar Chart"
        self.refresh_view()

    def load_data(self):
        print("... UI Loading Data")
       
        path = self.config.get('data_file', 'data/gdp_data.csv')
        try:
            self.raw_data = loader.load_data(path)
            self.regions = sorted(list(set(r['Region'] for r in self.raw_data if r['Region'])))
            self.years = sorted(list(set(r['Year'] for r in self.raw_data if r['Year'])))
        except Exception as e:
            messagebox.showerror("Error", f"Data Load Failed: {e}")
            self.raw_data = []
            self.regions = ["No Data"]
            self.years = [2022]

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=300)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="GDP ANALYZER", bg="#2c3e50", fg="white", 
                 font=("Helvetica", 18, "bold")).pack(pady=30)

        filter_frame = tk.LabelFrame(sidebar, text="Data Filters", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 10, "bold"))
        filter_frame.pack(padx=15, pady=10, fill="x")

        #Region Dropdown
        tk.Label(filter_frame, text="Region:", bg="#2c3e50", fg="#bdc3c7").pack(anchor="w", padx=10)
        self.region_var = tk.StringVar(value=self.regions[0] if self.regions else "") 
        self.cb_region = ttk.Combobox(filter_frame, textvariable=self.region_var, values=self.regions, state="readonly")
        self.cb_region.pack(fill="x", padx=10, pady=(0, 10))
        self.cb_region.bind("<<ComboboxSelected>>", self.refresh_view)

        #Year Dropdown
        tk.Label(filter_frame, text="Year:", bg="#2c3e50", fg="#bdc3c7").pack(anchor="w", padx=10)
        self.year_var = tk.StringVar(value=str(self.years[-1]) if self.years else "")
        self.cb_year = ttk.Combobox(filter_frame, textvariable=self.year_var, values=self.years, state="readonly")
        self.cb_year.pack(fill="x", padx=10, pady=(0, 15))
        self.cb_year.bind("<<ComboboxSelected>>", self.refresh_view)

        stats_frame = tk.LabelFrame(sidebar, text="Key Statistics", bg="#2c3e50", fg="#f1c40f", font=("Arial", 10, "bold"))
        stats_frame.pack(padx=15, pady=10, fill="x")
        
        self.lbl_total_gdp = tk.Label(stats_frame, text="Total: -", bg="#2c3e50", fg="white", anchor="w", font=("Arial", 9))
        self.lbl_total_gdp.pack(fill="x", padx=10, pady=2)
        
        self.lbl_avg_gdp = tk.Label(stats_frame, text="Avg: -", bg="#2c3e50", fg="white", anchor="w", font=("Arial", 9))
        self.lbl_avg_gdp.pack(fill="x", padx=10, pady=2)
        
        self.lbl_count = tk.Label(stats_frame, text="Count: -", bg="#2c3e50", fg="white", anchor="w", font=("Arial", 9))
        self.lbl_count.pack(fill="x", padx=10, pady=2)


        nav_frame = tk.LabelFrame(sidebar, text="Select View", bg="#2c3e50", fg="#ecf0f1", font=("Arial", 10, "bold"))
        nav_frame.pack(padx=15, pady=20, fill="x")

        modes = [("Regional Comparison", "Bar Chart"), 
                 ("Wealth Distribution", "Histogram"), #New Chart
                 ("Market Share", "Pie Chart"), 
                 ("Historical Trend", "Line Chart")]

        self.nav_var = tk.StringVar(value="Bar Chart")
        
        for text, mode in modes:
            btn = tk.Radiobutton(nav_frame, text=text, variable=self.nav_var, value=mode, 
                                 indicatoron=0, bg="#34495e", fg="white", selectcolor="#27ae60",
                                 font=("Arial", 10), command=self.refresh_view)
            btn.pack(fill="x", padx=5, pady=2)

    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)

    def refresh_view(self, event=None):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        sel_region = self.region_var.get()
        try:
            sel_year = int(self.year_var.get())
        except ValueError:
            return

        view_mode = self.nav_var.get()

        comp_data = processor.filter_data(self.raw_data, region=sel_region, year=sel_year)

        if comp_data:
            total = processor.get_gdp_stats(comp_data, "sum")
            avg = processor.get_gdp_stats(comp_data, "average")
            count = len(comp_data)
            
            self.lbl_total_gdp.config(text=f"Total: ${total/1e9:,.2f} B")
            self.lbl_avg_gdp.config(text=f"Avg:   ${avg/1e9:,.2f} B")
            self.lbl_count.config(text=f"Count: {count} Countries")
        else:
            self.lbl_total_gdp.config(text="Total: -")
            self.lbl_avg_gdp.config(text="Avg: -")
            self.lbl_count.config(text="Count: 0")

        figure = None
        
        if view_mode == "Bar Chart":
            figure = visualizer.get_bar_figure(comp_data)
        elif view_mode == "Pie Chart":
            figure = visualizer.get_pie_figure(comp_data)
        elif view_mode == "Histogram":
            figure = visualizer.get_histogram_figure(comp_data)
        elif view_mode == "Line Chart":
            trend_data = []
            subtitle = "Select a region with data to see trends."
            if comp_data:
                largest_country = sorted(comp_data, key=lambda x: x['GDP'], reverse=True)[0]['Country']
                trend_data = processor.filter_data(self.raw_data, country=largest_country)
                subtitle = f"Showing trend for {largest_country} (Largest Economy in {sel_region})"
            
            figure = visualizer.get_line_figure(trend_data)
            tk.Label(self.content_frame, text=subtitle, bg="white", fg="#7f8c8d", font=("Arial", 10, "italic")).pack(side="top", pady=5)

        if figure:
            canvas = FigureCanvasTkAgg(figure, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=20, pady=20)