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
        self.apply_defaults()

    def load_data(self):
        path = self.config.get('data_file', 'data/gdp_data.csv')
        try:
            self.raw_data = loader.load_data(path)
            self.regions = sorted(list(set(r['Region'] for r in self.raw_data if r['Region'])))
            self.years = sorted(list(set(r['Year'] for r in self.raw_data if r['Year'])))
            
            self.region_map = {region: set() for region in self.regions}
            for row in self.raw_data:
                if row['Region'] and row['Country']:
                    self.region_map[row['Region']].add(row['Country'])
        except:
            self.raw_data = []

    def apply_defaults(self):
        def_reg = self.config.get('filters', {}).get('region', '')
        if def_reg in self.regions:
            self.region_var.set(def_reg)
            self.update_country_list()
        
        def_year = str(self.config.get('filters', {}).get('year', ''))
        if def_year in [str(y) for y in self.years]:
            self.year_var.set(def_year)
            
        self.refresh_view()

    def create_sidebar(self):
        sidebar = tk.Frame(self, bg="#2c3e50", width=300)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="GDP ANALYZER", bg="#2c3e50", fg="white", font=("Helvetica", 18, "bold")).pack(pady=30)

        filter_frame = tk.LabelFrame(sidebar, text="Data Filters", bg="#2c3e50", fg="#ecf0f1")
        filter_frame.pack(padx=15, pady=10, fill="x")

        #Country Wise Mode Checkbox
        self.country_mode_var = tk.BooleanVar(value=False)
        self.chk_mode = tk.Checkbutton(filter_frame, text="Country-Wise Mode", variable=self.country_mode_var,
                                       bg="#2c3e50", fg="#f1c40f", selectcolor="#2c3e50", activebackground="#2c3e50",
                                       command=self.toggle_mode)
        self.chk_mode.pack(fill="x", padx=10, pady=10)

        tk.Label(filter_frame, text="Region:", bg="#2c3e50", fg="#bdc3c7").pack(anchor="w", padx=10)
        self.region_var = tk.StringVar() 
        self.cb_region = ttk.Combobox(filter_frame, textvariable=self.region_var, values=self.regions, state="readonly")
        self.cb_region.pack(fill="x", padx=10, pady=5)
        self.cb_region.bind("<<ComboboxSelected>>", self.update_country_list)

        tk.Label(filter_frame, text="Country:", bg="#2c3e50", fg="#bdc3c7").pack(anchor="w", padx=10)
        self.country_var = tk.StringVar()
        self.cb_country = ttk.Combobox(filter_frame, textvariable=self.country_var, state="readonly")
        self.cb_country.pack(fill="x", padx=10, pady=5)
        self.cb_country.bind("<<ComboboxSelected>>", self.refresh_view)

        self.lbl_year = tk.Label(filter_frame, text="Year:", bg="#2c3e50", fg="#bdc3c7")
        self.lbl_year.pack(anchor="w", padx=10)
        self.year_var = tk.StringVar()
        self.cb_year = ttk.Combobox(filter_frame, textvariable=self.year_var, values=self.years, state="readonly")
        self.cb_year.pack(fill="x", padx=10, pady=10)
        self.cb_year.bind("<<ComboboxSelected>>", self.refresh_view)

        self.stats_frame = tk.LabelFrame(sidebar, text="Statistics", bg="#2c3e50", fg="#f1c40f")
        self.stats_frame.pack(padx=15, pady=10, fill="x")
        self.lbl_stat1 = tk.Label(self.stats_frame, text="-", bg="#2c3e50", fg="white", anchor="w")
        self.lbl_stat1.pack(fill="x", padx=10)
        self.lbl_stat2 = tk.Label(self.stats_frame, text="-", bg="#2c3e50", fg="white", anchor="w")
        self.lbl_stat2.pack(fill="x", padx=10)

        self.nav_frame = tk.LabelFrame(sidebar, text="Visualizations", bg="#2c3e50", fg="#ecf0f1")
        self.nav_frame.pack(padx=15, pady=20, fill="x")
        self.nav_var = tk.StringVar(value="Chart 1")
        
        self.radio_btns = []
        self.create_radio_buttons()

    def create_radio_buttons(self):
        for btn in self.radio_btns: btn.destroy()
        self.radio_btns.clear()

        if self.country_mode_var.get():
            options = [("GDP History (Bar)", "History"), ("Growth Rate (%)", "Growth")]
        else:
            options = [("Comparison (Bar)", "Bar Chart"), ("Market Share (Pie)", "Pie Chart"), 
                       ("Wealth Dist (Hist)", "Histogram"), ("Trend (Line)", "Line Chart")]
            
        self.nav_var.set(options[0][1]) #Reset selection
        
        for text, val in options:
            btn = tk.Radiobutton(self.nav_frame, text=text, variable=self.nav_var, value=val, 
                                 indicatoron=0, bg="#34495e", fg="white", selectcolor="#27ae60",
                                 command=self.refresh_view)
            btn.pack(fill="x", padx=5, pady=2)
            self.radio_btns.append(btn)

    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)

    def toggle_mode(self):
        #Disable/Enable Year dropdown based on mode
        if self.country_mode_var.get():
            self.cb_year.config(state="disabled")
        else:
            self.cb_year.config(state="readonly")
            
        self.create_radio_buttons() #Switch Menu Options
        self.refresh_view()

    def update_country_list(self, event=None):
        reg = self.region_var.get()
        if reg in self.region_map:
            ctrys = sorted(list(self.region_map[reg]))
            self.cb_country['values'] = ["All Countries"] + ctrys if not self.country_mode_var.get() else ctrys
            self.country_var.set(ctrys[0] if ctrys else "")
        self.refresh_view()

    def refresh_view(self, event=None):
        for w in self.content_frame.winfo_children(): w.destroy()
        
        mode_country = self.country_mode_var.get()
        sel_region = self.region_var.get()
        sel_country = self.country_var.get()
        
        if mode_country:
            data = processor.filter_data(self.raw_data, country=sel_country)

            if data:
                avg = processor.get_gdp_stats(data, "average")
                total = processor.get_gdp_stats(data, "sum") #Total historical GDP (weird metric but ok)
                self.lbl_stat1.config(text=f"Avg GDP: ${avg/1e9:,.2f} B")
                self.lbl_stat2.config(text=f"Records: {len(data)} Years")
            
            view = self.nav_var.get()
            fig = None
            if view == "History":
                fig = visualizer.get_country_year_bar(data, sel_country)
            elif view == "Growth":
                fig = visualizer.get_growth_rate_line(data, sel_country)
                
        else:
            try: sel_year = int(self.year_var.get())
            except: return

            data = processor.filter_data(self.raw_data, region=sel_region, year=sel_year)
            
            if data:
                total = processor.get_gdp_stats(data, "sum")
                avg = processor.get_gdp_stats(data, "average")
                self.lbl_stat1.config(text=f"Total: ${total/1e9:,.2f} B")
                self.lbl_stat2.config(text=f"Avg:   ${avg/1e9:,.2f} B")
            
            highlight = sel_country if sel_country != "All Countries" else None
            view = self.nav_var.get()
            fig = None
            
            if view == "Bar Chart": fig = visualizer.get_bar_figure(data, highlight)
            elif view == "Pie Chart": fig = visualizer.get_pie_figure(data, highlight)
            elif view == "Histogram": fig = visualizer.get_histogram_figure(data, highlight)
            elif view == "Line Chart": 
                t_data = []
                if highlight: t_data = processor.filter_data(self.raw_data, country=highlight)
                elif data: 
                    largest = sorted(data, key=lambda x: x['GDP'], reverse=True)[0]['Country']
                    t_data = processor.filter_data(self.raw_data, country=largest)
                fig = visualizer.get_line_figure(t_data)

        if fig:
            canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)