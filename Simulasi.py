import tkinter as tk
from tkinter import ttk, Frame, Scale, HORIZONTAL, StringVar, DoubleVar
import pygame
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
from matplotlib.figure import Figure
import time
import threading
import random
import sys
from PIL import Image, ImageTk
import colorsys

class ModernTooltip:
    """Modern tooltip implementation for Tkinter widgets"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = tk.Frame(self.tooltip, bg="#2c3e50", bd=1)
        frame.pack(fill="both", expand=True)
        
        label = tk.Label(frame, text=self.text, justify="left", bg="#2c3e50", fg="#ecf0f1",
                       font=("Helvetica", 9), padx=10, pady=5)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class ModernSlider(tk.Frame):
    """Custom modern slider with value display"""
    def __init__(self, master, min_val, max_val, resolution, variable, label_text, width=250, **kwargs):
        bg_color = kwargs.pop('bg', '#f5f5f5')  # ambil & hapus 'bg' dari kwargs
        super().__init__(master, bg=bg_color, **kwargs)
        
        self.variable = variable
        self.min_val = min_val
        self.max_val = max_val
        
        # Label frame
        label_frame = tk.Frame(self, bg=kwargs.get('bg', '#f5f5f5'))
        label_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Label
        self.label = tk.Label(label_frame, text=label_text, bg=kwargs.get('bg', '#f5f5f5'), 
                            fg="#2c3e50", font=("Helvetica", 9))
        self.label.pack(side=tk.LEFT)
        
        # Value display
        self.value_var = tk.StringVar(value=f"{float(variable.get()):.3f}")
        self.value_label = tk.Label(label_frame, textvariable=self.value_var, bg=kwargs.get('bg', '#f5f5f5'), 
                                  fg="#2980b9", font=("Helvetica", 9, "bold"))
        self.value_label.pack(side=tk.RIGHT)
        
        # Slider
        self.slider = Scale(self, from_=min_val, to=max_val, resolution=resolution,
                          orient=HORIZONTAL, variable=variable,
                          bg=kwargs.get('bg', '#f5f5f5'), fg="#2c3e50",
                          highlightthickness=0, troughcolor="#3498db",
                          length=width, command=self.update_value)
        self.slider.pack(fill=tk.X)
    
    def update_value(self, value):
        self.value_var.set(f"{float(value):.3f}")

class BacterialResistanceSimulation:
    def __init__(self, master):
        self.master = master
        self.master.title("Antibiotic Resistance Evolution Simulator")
        self.master.geometry("1280x800")
        
        # Set theme colors
        self.colors = {
            "background": "#f5f5f5",
            "card_bg": "#ffffff",
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "accent": "#e74c3c",
            "text": "#2c3e50",
            "text_light": "#7f8c8d",
            "border": "#e0e0e0"
        }
        
        # Apply theme
        self.master.configure(bg=self.colors["background"])
        self.style = ttk.Style()
        self.configure_styles()
        
        # Initialize variables
        self.running = False
        self.paused = False
        self.population_size = 1000
        self.initial_resistance_range = (0.0, 0.1)
        self.antibiotic_concentration = 0.3
        self.mutation_std = 0.01
        self.reproduction_rate = 1.2
        self.carrying_capacity = 2000
        self.bacteria_population = []
        self.generation = 0
        self.avg_resistance_history = []
        self.population_history = []
        self.visualize_type = "scatter"
        
        # Setup pygame for visualization
        pygame.init()
        self.pygame_surface_size = (600, 500)
        self.pygame_surface = pygame.Surface(self.pygame_surface_size)
        
        # Create main frames
        self.create_frames()
        
        # Initialize status var early
        self.status_var = tk.StringVar()
        self.status_var.set("Ready. Press Start to begin simulation.")
        
        # Create control panel
        self.create_control_panel()
        
        # Create visualization area
        self.create_visualization_area()
        
        # Create charts
        self.create_charts()
        
        # Status bar
        self.status_bar = tk.Label(self.master, textvariable=self.status_var, 
                                 bd=1, relief=tk.SUNKEN, anchor=tk.W, 
                                 bg=self.colors["card_bg"], fg=self.colors["text"],
                                 font=("Helvetica", 9), padx=10, pady=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize population
        self.initialize_population()
        
        # Update pygame visualization
        self.update_pygame_visualization()
        
        # Bind window close event
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Bind window resize event
        self.master.bind("<Configure>", self.on_resize)
    
    def configure_styles(self):
        """Configure ttk styles for modern look"""
        self.style.configure("TButton", 
                           font=("Helvetica", 10),
                           background=self.colors["primary"],
                           foreground=self.colors["text"])
        
        self.style.map("TButton",
                     background=[("active", self.colors["primary"])],
                     foreground=[("active", self.colors["card_bg"])])
        
        self.style.configure("Start.TButton", 
                           background=self.colors["secondary"],
                           foreground=self.colors["card_bg"])
        
        self.style.map("Start.TButton",
                     background=[("active", self.colors["secondary"])],
                     foreground=[("active", self.colors["card_bg"])])
        
        self.style.configure("Reset.TButton", 
                           background=self.colors["accent"],
                           foreground=self.colors["card_bg"])
        
        self.style.map("Reset.TButton",
                     background=[("active", self.colors["accent"])],
                     foreground=[("active", self.colors["card_bg"])])
        
        self.style.configure("TEntry", 
                           fieldbackground=self.colors["card_bg"],
                           foreground=self.colors["text"])
        
        self.style.configure("TCombobox", 
                           fieldbackground=self.colors["card_bg"],
                           foreground=self.colors["text"])
    
    def create_frames(self):
        # Create title frame
        self.title_frame = Frame(self.master, bg=self.colors["background"], pady=15)
        self.title_frame.pack(fill=tk.X, padx=20)
        
        title_label = tk.Label(self.title_frame, 
                             text="Bacterial Antibiotic Resistance Evolution Simulator", 
                             font=("Helvetica", 20, "bold"), 
                             bg=self.colors["background"], 
                             fg=self.colors["text"])
        title_label.pack(side=tk.LEFT)
        
        # Main content frame with 2 columns
        self.content_frame = Frame(self.master, bg=self.colors["background"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Left column for controls
        self.control_frame = Frame(self.content_frame, bg=self.colors["card_bg"], 
                                 width=320, padx=15, pady=15,
                                 highlightbackground=self.colors["border"],
                                 highlightthickness=1)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        self.control_frame.pack_propagate(False)  # Prevent shrinking
        
        # Right column for visualization and charts
        self.viz_frame = Frame(self.content_frame, bg=self.colors["background"])
        self.viz_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top frame for pygame visualization
        self.pygame_frame = Frame(self.viz_frame, bg=self.colors["card_bg"], 
                                bd=0, padx=15, pady=15,
                                highlightbackground=self.colors["border"],
                                highlightthickness=1)
        self.pygame_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Bottom frame for matplotlib charts
        self.chart_frame = Frame(self.viz_frame, bg=self.colors["card_bg"], 
                               bd=0, padx=15, pady=15, height=250,
                               highlightbackground=self.colors["border"],
                               highlightthickness=1)
        self.chart_frame.pack(fill=tk.X)
        
    def create_control_panel(self):
        # Control Panel Header
        control_label = tk.Label(self.control_frame, text="Simulation Controls", 
                               font=("Helvetica", 14, "bold"), 
                               bg=self.colors["card_bg"], 
                               fg=self.colors["text"])
        control_label.pack(anchor=tk.W, pady=(0, 15))
        
        # Control variables frame
        controls_vars_frame = Frame(self.control_frame, bg=self.colors["card_bg"])
        controls_vars_frame.pack(fill=tk.X, pady=5)
        
        # Section: Population Parameters
        section_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        section_label = tk.Label(section_frame, text="Population Parameters", 
                               font=("Helvetica", 11, "bold"), 
                               bg=self.colors["card_bg"], 
                               fg=self.colors["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Initial Population
        param_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="Initial Population:", 
               bg=self.colors["card_bg"], 
               fg=self.colors["text"]).pack(side=tk.LEFT)
        
        self.population_var = tk.StringVar(value=str(self.population_size))
        population_entry = ttk.Entry(param_frame, textvariable=self.population_var, width=8)
        population_entry.pack(side=tk.RIGHT)
        ModernTooltip(population_entry, "Number of bacteria at the start of simulation")
        
        # Initial Resistance Range
        param_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="Initial Resistance Range:", 
               bg=self.colors["card_bg"], 
               fg=self.colors["text"]).pack(side=tk.LEFT)
        
        resistance_frame = Frame(param_frame, bg=self.colors["card_bg"])
        resistance_frame.pack(side=tk.RIGHT)
        
        self.min_resistance_var = tk.StringVar(value=str(self.initial_resistance_range[0]))
        min_entry = ttk.Entry(resistance_frame, textvariable=self.min_resistance_var, width=4)
        min_entry.pack(side=tk.LEFT)
        
        tk.Label(resistance_frame, text=" - ", 
               bg=self.colors["card_bg"], 
               fg=self.colors["text"]).pack(side=tk.LEFT)
        
        self.max_resistance_var = tk.StringVar(value=str(self.initial_resistance_range[1]))
        max_entry = ttk.Entry(resistance_frame, textvariable=self.max_resistance_var, width=4)
        max_entry.pack(side=tk.LEFT)
        ModernTooltip(resistance_frame, "Range of initial resistance values (0.0 to 1.0)")
        
        # Carrying Capacity
        param_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="Carrying Capacity:", 
               bg=self.colors["card_bg"], 
               fg=self.colors["text"]).pack(side=tk.LEFT)
        
        self.capacity_var = tk.StringVar(value=str(self.carrying_capacity))
        capacity_entry = ttk.Entry(param_frame, textvariable=self.capacity_var, width=8)
        capacity_entry.pack(side=tk.RIGHT)
        ModernTooltip(capacity_entry, "Maximum population size the environment can support")
        
        # Section: Simulation Parameters
        section_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        section_frame.pack(fill=tk.X, pady=(15, 10))
        
        section_label = tk.Label(section_frame, text="Simulation Parameters", 
                               font=("Helvetica", 11, "bold"), 
                               bg=self.colors["card_bg"], 
                               fg=self.colors["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Antibiotic Concentration Slider
        self.antibiotic_var = tk.DoubleVar(value=self.antibiotic_concentration)
        antibiotic_slider = ModernSlider(
            controls_vars_frame, 0.0, 1.0, 0.01, self.antibiotic_var,
            "Antibiotic Concentration:", bg=self.colors["card_bg"]
        )
        antibiotic_slider.pack(fill=tk.X, pady=5)
        ModernTooltip(antibiotic_slider, "Concentration of antibiotic in the environment (0.0 to 1.0)")
        
        # Mutation Rate Slider
        self.mutation_var = tk.DoubleVar(value=self.mutation_std)
        mutation_slider = ModernSlider(
            controls_vars_frame, 0.001, 0.1, 0.001, self.mutation_var,
            "Mutation Rate:", bg=self.colors["card_bg"]
        )
        mutation_slider.pack(fill=tk.X, pady=5)
        ModernTooltip(mutation_slider, "Standard deviation of mutations in resistance values")
        
        # Reproduction Rate Slider
        self.reproduction_var = tk.DoubleVar(value=self.reproduction_rate)
        reproduction_slider = ModernSlider(
            controls_vars_frame, 1.0, 2.0, 0.05, self.reproduction_var,
            "Reproduction Rate:", bg=self.colors["card_bg"]
        )
        reproduction_slider.pack(fill=tk.X, pady=5)
        ModernTooltip(reproduction_slider, "Average number of offspring per bacterium")
        
        # Section: Visualization
        section_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        section_frame.pack(fill=tk.X, pady=(15, 10))
        
        section_label = tk.Label(section_frame, text="Visualization", 
                               font=("Helvetica", 11, "bold"), 
                               bg=self.colors["card_bg"], 
                               fg=self.colors["primary"])
        section_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Visualization Type
        param_frame = Frame(controls_vars_frame, bg=self.colors["card_bg"])
        param_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(param_frame, text="Visualization Type:", 
               bg=self.colors["card_bg"], 
               fg=self.colors["text"]).pack(side=tk.LEFT)
        
        self.viz_var = tk.StringVar(value=self.visualize_type)
        viz_combo = ttk.Combobox(param_frame, textvariable=self.viz_var, width=10,
                               values=["scatter", "grid"])
        viz_combo.pack(side=tk.RIGHT)
        viz_combo.bind("<<ComboboxSelected>>", lambda e: self.update_pygame_visualization())
        ModernTooltip(viz_combo, "Choose between scatter plot or grid visualization")
        
        # Simulation Speed
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_slider = ModernSlider(
            controls_vars_frame, 0.1, 3.0, 0.1, self.speed_var,
            "Simulation Speed:", bg=self.colors["card_bg"]
        )
        speed_slider.pack(fill=tk.X, pady=5)
        ModernTooltip(speed_slider, "Speed of simulation (higher values = faster simulation)")
        
        # Button frame for controls
        button_frame = Frame(self.control_frame, bg=self.colors["card_bg"])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.start_button = ttk.Button(button_frame, text="Start", 
                                     command=self.start_simulation, 
                                     style="Start.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", 
                                     command=self.pause_simulation, 
                                     state=tk.DISABLED)
        self.pause_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", 
                                     command=self.reset_simulation, 
                                     style="Reset.TButton")
        self.reset_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def create_visualization_area(self):
        # Pygame visualization
        self.pygame_canvas = tk.Canvas(self.pygame_frame, 
                                     width=self.pygame_surface_size[0], 
                                     height=self.pygame_surface_size[1], 
                                     bg=self.colors["card_bg"],
                                     highlightthickness=0)
        self.pygame_canvas.pack(expand=True)
        
        # Info labels for the current state
        info_frame = Frame(self.pygame_frame, bg=self.colors["card_bg"])
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create a grid for info labels
        info_grid = Frame(info_frame, bg=self.colors["card_bg"])
        info_grid.pack(fill=tk.X)
        
        # Style for info labels
        label_font = ("Helvetica", 10)
        value_font = ("Helvetica", 12, "bold")
        
        # Generation counter
        gen_label_frame = Frame(info_grid, bg=self.colors["card_bg"], padx=10, pady=5)
        gen_label_frame.grid(row=0, column=0, sticky="w")
        
        tk.Label(gen_label_frame, text="Generation:", 
               font=label_font, bg=self.colors["card_bg"], 
               fg=self.colors["text_light"]).pack(anchor=tk.W)
        
        self.generation_var = tk.StringVar(value="0")
        gen_value = tk.Label(gen_label_frame, textvariable=self.generation_var, 
                           font=value_font, bg=self.colors["card_bg"], 
                           fg=self.colors["text"])
        gen_value.pack(anchor=tk.W)
        
        # Population counter
        pop_label_frame = Frame(info_grid, bg=self.colors["card_bg"], padx=10, pady=5)
        pop_label_frame.grid(row=0, column=1, sticky="w")
        
        tk.Label(pop_label_frame, text="Population Size:", 
               font=label_font, bg=self.colors["card_bg"], 
               fg=self.colors["text_light"]).pack(anchor=tk.W)
        
        self.pop_count_var = tk.StringVar(value=f"{self.population_size}")
        pop_value = tk.Label(pop_label_frame, textvariable=self.pop_count_var, 
                           font=value_font, bg=self.colors["card_bg"], 
                           fg=self.colors["text"])
        pop_value.pack(anchor=tk.W)
        
        # Average resistance
        res_label_frame = Frame(info_grid, bg=self.colors["card_bg"], padx=10, pady=5)
        res_label_frame.grid(row=0, column=2, sticky="w")
        
        tk.Label(res_label_frame, text="Average Resistance:", 
               font=label_font, bg=self.colors["card_bg"], 
               fg=self.colors["text_light"]).pack(anchor=tk.W)
        
        self.avg_res_var = tk.StringVar(value="0.05")
        res_value = tk.Label(res_label_frame, textvariable=self.avg_res_var, 
                           font=value_font, bg=self.colors["card_bg"], 
                           fg=self.colors["text"])
        res_value.pack(anchor=tk.W)
        
        # Current antibiotic concentration
        conc_label_frame = Frame(info_grid, bg=self.colors["card_bg"], padx=10, pady=5)
        conc_label_frame.grid(row=0, column=3, sticky="w")
        
        tk.Label(conc_label_frame, text="Antibiotic Concentration:", 
               font=label_font, bg=self.colors["card_bg"], 
               fg=self.colors["text_light"]).pack(anchor=tk.W)
        
        self.conc_var = tk.StringVar(value=f"{self.antibiotic_concentration:.2f}")
        conc_value = tk.Label(conc_label_frame, textvariable=self.conc_var, 
                            font=value_font, bg=self.colors["card_bg"], 
                            fg=self.colors["text"])
        conc_value.pack(anchor=tk.W)
    
    def create_charts(self):
        # Create matplotlib figure with custom style
        plt.style.use('ggplot')
        self.fig = Figure(figsize=(12, 4), dpi=100, facecolor=self.colors["card_bg"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create subplots
        self.ax1 = self.fig.add_subplot(131)  # Population size
        self.ax2 = self.fig.add_subplot(132)  # Average resistance
        self.ax3 = self.fig.add_subplot(133)  # Resistance distribution
        
        # Configure plots with improved styling
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#f8f9fa')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#cccccc')
            ax.spines['left'].set_color('#cccccc')
            ax.tick_params(colors='#666666')
            ax.xaxis.label.set_color('#333333')
            ax.yaxis.label.set_color('#333333')
            ax.title.set_color('#333333')
        
        self.ax1.set_title("Population Size Over Time", fontsize=10, fontweight='bold')
        self.ax1.set_xlabel("Generation", fontsize=9)
        self.ax1.set_ylabel("Population Size", fontsize=9)
        self.ax1.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        
        self.ax2.set_title("Average Resistance Over Time", fontsize=10, fontweight='bold')
        self.ax2.set_xlabel("Generation", fontsize=9)
        self.ax2.set_ylabel("Resistance Value", fontsize=9)
        self.ax2.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        self.ax2.set_ylim(0, 1)
        
        self.ax3.set_title("Resistance Distribution", fontsize=10, fontweight='bold')
        self.ax3.set_xlabel("Resistance Value", fontsize=9)
        self.ax3.set_ylabel("Number of Bacteria", fontsize=9)
        self.ax3.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        
        self.fig.tight_layout()
        self.canvas.draw()
    
    def initialize_population(self):
        try:
            # Parse parameter inputs
            self.population_size = int(self.population_var.get())
            min_res = float(self.min_resistance_var.get())
            max_res = float(self.max_resistance_var.get())
            self.initial_resistance_range = (min_res, max_res)
            
            # Create initial bacteria with resistance values
            self.bacteria_population = []
            for _ in range(self.population_size):
                resistance = random.uniform(self.initial_resistance_range[0], self.initial_resistance_range[1])
                self.bacteria_population.append(resistance)
            
            # Reset history
            self.avg_resistance_history = [np.mean(self.bacteria_population)]
            self.population_history = [len(self.bacteria_population)]
            self.generation = 0
            
            # Update GUI
            self.update_info_labels()
            self.update_charts()
            self.update_pygame_visualization()
            self.status_var.set("Population initialized. Ready to start simulation.")
            
        except ValueError as e:
            self.status_var.set(f"Error initializing population: {str(e)}")
    
    def simulation_step(self):
        # Update parameters from GUI
        self.antibiotic_concentration = self.antibiotic_var.get()
        self.mutation_std = self.mutation_var.get()
        self.reproduction_rate = self.reproduction_var.get()
        self.carrying_capacity = int(self.capacity_var.get())
        
        # Apply selection (bacteria survival based on resistance)
        survived = []
        for resistance in self.bacteria_population:
            # Calculate survival probability
            # Higher resistance means higher survival probability under antibiotic pressure
            survival_prob = max(0, 1 - (self.antibiotic_concentration - resistance))
            if random.random() < survival_prob:
                survived.append(resistance)
        
        # Reproduction with mutation
        next_gen = []
        # Limit reproduction based on carrying capacity
        for resistance in survived:
            # Reproduction rate determines average number of offspring
            num_offspring = 0
            # Using Poisson-like process for number of offspring
            remaining_prob = self.reproduction_rate
            while remaining_prob > 0:
                if random.random() < remaining_prob:
                    num_offspring += 1
                remaining_prob -= 1
            
            # Create offspring with mutations
            for _ in range(num_offspring):
                # Apply mutation
                new_resistance = resistance + random.gauss(0, self.mutation_std)
                # Ensure resistance stays within [0, 1]
                new_resistance = max(0, min(1, new_resistance))
                next_gen.append(new_resistance)
        
        # Apply carrying capacity limit
        if len(next_gen) > self.carrying_capacity:
            next_gen = random.sample(next_gen, self.carrying_capacity)
        
        # Update the population
        self.bacteria_population = next_gen
        
        # Update history
        if len(self.bacteria_population) > 0:
            self.avg_resistance_history.append(np.mean(self.bacteria_population))
        else:
            self.avg_resistance_history.append(0)  # Extinction
        self.population_history.append(len(self.bacteria_population))
        
        # Increment generation
        self.generation += 1
        
        # Update GUI
        self.update_info_labels()
        if self.generation % 5 == 0:  # Update charts every 5 generations for efficiency
            self.update_charts()
        self.update_pygame_visualization()
    
    def update_info_labels(self):
        # Update info labels
        self.generation_var.set(f"{self.generation}")
        self.pop_count_var.set(f"{len(self.bacteria_population)}")
        if len(self.bacteria_population) > 0:
            avg_resistance = np.mean(self.bacteria_population)
            self.avg_res_var.set(f"{avg_resistance:.4f}")
        else:
            self.avg_res_var.set("N/A (Extinct)")
        self.conc_var.set(f"{self.antibiotic_concentration:.2f}")
    
    def update_charts(self):
        # Clear previous plots
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        
        # Configure common style elements
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_facecolor('#f8f9fa')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('#cccccc')
            ax.spines['left'].set_color('#cccccc')
            ax.tick_params(colors='#666666')
            ax.xaxis.label.set_color('#333333')
            ax.yaxis.label.set_color('#333333')
            ax.title.set_color('#333333')
        
        # Population size over time
        self.ax1.plot(self.population_history, color=self.colors["primary"], linewidth=2)
        self.ax1.set_title("Population Size Over Time", fontsize=10, fontweight='bold')
        self.ax1.set_xlabel("Generation", fontsize=9)
        self.ax1.set_ylabel("Population Size", fontsize=9)
        self.ax1.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        
        # Add shaded area under the curve
        self.ax1.fill_between(range(len(self.population_history)), 
                            self.population_history, 
                            color=self.colors["primary"], alpha=0.2)
        
        # Average resistance over time
        self.ax2.plot(self.avg_resistance_history, color=self.colors["secondary"], linewidth=2)
        self.ax2.set_title("Average Resistance Over Time", fontsize=10, fontweight='bold')
        self.ax2.set_xlabel("Generation", fontsize=9)
        self.ax2.set_ylabel("Resistance Value", fontsize=9)
        self.ax2.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
        self.ax2.set_ylim(0, 1)
        
        # Add horizontal line for current antibiotic concentration
        self.ax2.axhline(y=self.antibiotic_concentration, color=self.colors["accent"], 
                       linestyle='--', alpha=0.8, linewidth=1.5)
        self.ax2.text(0, self.antibiotic_concentration + 0.02, 
                    f"Antibiotic Concentration: {self.antibiotic_concentration:.2f}", 
                    color=self.colors["accent"], fontsize=8)
        
        # Add shaded area under the curve
        self.ax2.fill_between(range(len(self.avg_resistance_history)), 
                            self.avg_resistance_history, 
                            color=self.colors["secondary"], alpha=0.2)
        
        # Resistance distribution histogram
        if len(self.bacteria_population) > 0:
            n, bins, patches = self.ax3.hist(self.bacteria_population, bins=30, range=(0, 1), 
                                          color=self.colors["primary"], alpha=0.7)
            
            # Color the bins based on their relationship to antibiotic concentration
            bin_centers = 0.5 * (bins[:-1] + bins[1:])
            for i, center in enumerate(bin_centers):
                if center < self.antibiotic_concentration:
                    # Bacteria with resistance below antibiotic concentration
                    patches[i].set_facecolor(self.colors["accent"])
                else:
                    # Bacteria with resistance above antibiotic concentration
                    patches[i].set_facecolor(self.colors["secondary"])
            
            self.ax3.set_title("Resistance Distribution", fontsize=10, fontweight='bold')
            self.ax3.set_xlabel("Resistance Value", fontsize=9)
            self.ax3.set_ylabel("Number of Bacteria", fontsize=9)
            self.ax3.grid(True, linestyle='--', alpha=0.7, color='#dddddd')
            self.ax3.set_xlim(0, 1)
            
            # Add vertical line for antibiotic concentration
            self.ax3.axvline(x=self.antibiotic_concentration, color='black', 
                           linestyle='--', alpha=0.8, linewidth=1.5)
            self.ax3.text(self.antibiotic_concentration + 0.02, max(n) * 0.9, 
                        f"Antibiotic\nConcentration", 
                        color='black', fontsize=8)
        
        # Update the canvas
        self.fig.tight_layout()
        self.canvas.draw()
    
    def update_pygame_visualization(self):
        # Clear the surface
        self.pygame_surface.fill((255, 255, 255))
        
        # Draw bacteria based on visualization type
        if self.viz_var.get() == "scatter":
            self._draw_scatter_visualization()
        else:  # grid
            self._draw_grid_visualization()
        
        # Convert pygame surface to tkinter PhotoImage
        pygame_img = pygame.image.tostring(self.pygame_surface, 'RGB')
        img = Image.frombytes('RGB', self.pygame_surface_size, pygame_img)
        self.tk_img = ImageTk.PhotoImage(image=img)
        
        # Update canvas
        self.pygame_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
    
    def _draw_scatter_visualization(self):
        width, height = self.pygame_surface_size
        
        # Draw a subtle grid background
        grid_spacing = 50
        for x in range(0, width, grid_spacing):
            pygame.draw.line(self.pygame_surface, (240, 240, 240), (x, 0), (x, height))
        for y in range(0, height, grid_spacing):
            pygame.draw.line(self.pygame_surface, (240, 240, 240), (0, y), (width, y))
        
        # Draw antibiotic concentration indicator
        indicator_height = 10
        pygame.draw.rect(self.pygame_surface, (240, 240, 240), 
                       (0, height - indicator_height, width, indicator_height))
        
        conc_x = int(width * self.antibiotic_concentration)
        pygame.draw.rect(self.pygame_surface, self.hex_to_rgb(self.colors["accent"]), 
                       (0, height - indicator_height, conc_x, indicator_height))
        
        # Draw legend
        legend_y = 20
        legend_x = width - 150
        
        # Susceptible bacteria legend
        pygame.draw.circle(self.pygame_surface, (255, 50, 50), (legend_x, legend_y), 6)
        font = pygame.font.SysFont('Arial', 12)
        text = font.render('Susceptible', True, (50, 50, 50))
        self.pygame_surface.blit(text, (legend_x + 15, legend_y - 6))
        
        # Resistant bacteria legend
        pygame.draw.circle(self.pygame_surface, (50, 200, 50), (legend_x, legend_y + 25), 6)
        text = font.render('Resistant', True, (50, 50, 50))
        self.pygame_surface.blit(text, (legend_x + 15, legend_y + 19))
        
        # Calculate color and size for each bacterium
        for resistance in self.bacteria_population:
            # Position based on random placement
            x = random.randint(10, width - 10)
            y = random.randint(10, height - 20)  # Leave space for indicator
            
            # Use HSV color space for smoother color transitions
            # Map resistance from 0-1 to 0-120 (red to green in HSV)
            hue = 120 * resistance  # 0 = red, 120 = green
            r, g, b = colorsys.hsv_to_rgb(hue/360, 0.8, 0.9)
            color = (int(r*255), int(g*255), int(b*255))
            
            # Size based on how close the resistance is to antibiotic concentration
            resistance_diff = abs(resistance - self.antibiotic_concentration)
            size = max(3, 8 - int(resistance_diff * 10))
            
            # Add glow effect for bacteria near the antibiotic concentration
            if resistance_diff < 0.05:
                glow_size = size + 4
                glow_alpha = 100  # Semi-transparent
                glow_surface = pygame.Surface((glow_size*2, glow_size*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, glow_alpha), (glow_size, glow_size), glow_size)
                self.pygame_surface.blit(glow_surface, (x-glow_size, y-glow_size))
            
            # Draw the bacterium
            pygame.draw.circle(self.pygame_surface, color, (x, y), size)
    
    def _draw_grid_visualization(self):
        width, height = self.pygame_surface_size
        
        # Create a grid representation of bacteria
        grid_size = min(30, int(np.sqrt(len(self.bacteria_population))))
        if grid_size < 2:
            return  # Not enough bacteria for grid
            
        cell_width = width // grid_size
        cell_height = height // grid_size
        
        # Draw grid background
        for i in range(grid_size + 1):
            pygame.draw.line(self.pygame_surface, (230, 230, 230), 
                           (0, i * cell_height), (width, i * cell_height), 1)
            pygame.draw.line(self.pygame_surface, (230, 230, 230), 
                           (i * cell_width, 0), (i * cell_width, height), 1)
        
        # Draw antibiotic concentration indicator at the bottom
        indicator_height = 10
        pygame.draw.rect(self.pygame_surface, (240, 240, 240), 
                       (0, height - indicator_height, width, indicator_height))
        
        conc_x = int(width * self.antibiotic_concentration)
        pygame.draw.rect(self.pygame_surface, self.hex_to_rgb(self.colors["accent"]), 
                       (0, height - indicator_height, conc_x, indicator_height))
        
        # Draw bacteria in grid cells
        for i, resistance in enumerate(self.bacteria_population[:grid_size * grid_size]):
            row = i // grid_size
            col = i % grid_size
            
            # Calculate position
            x = col * cell_width + cell_width // 2
            y = row * cell_height + cell_height // 2
            
            # Use HSV color space for smoother color transitions
            hue = 120 * resistance  # 0 = red, 120 = green
            r, g, b = colorsys.hsv_to_rgb(hue/360, 0.8, 0.9)
            color = (int(r*255), int(g*255), int(b*255))
            
            # Size based on resistance vs antibiotic 
            resistance_diff = abs(resistance - self.antibiotic_concentration)
            size = max(3, min(cell_width // 2 - 2, 10 - int(resistance_diff * 15)))
            
            # Draw cell background based on resistance
            cell_color = (250, 250, 250)
            if resistance < self.antibiotic_concentration:
                # Light red background for susceptible bacteria
                cell_color = (255, 240, 240)
            else:
                # Light green background for resistant bacteria
                cell_color = (240, 255, 240)
                
            pygame.draw.rect(self.pygame_surface, cell_color, 
                           (col * cell_width, row * cell_height, cell_width, cell_height))
            
            # Draw bacterium
            pygame.draw.circle(self.pygame_surface, color, (x, y), size)
            
            # Add a small indicator of resistance value
            font = pygame.font.SysFont('Arial', 8)
            text = font.render(f'{resistance:.2f}', True, (100, 100, 100))
            text_rect = text.get_rect(center=(x, y + cell_height//2 - 8))
            self.pygame_surface.blit(text, text_rect)
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def start_simulation(self):
        # Update parameters
        try:
            self.population_size = int(self.population_var.get())
            self.carrying_capacity = int(self.capacity_var.get())
            min_res = float(self.min_resistance_var.get())
            max_res = float(self.max_resistance_var.get())
            self.initial_resistance_range = (min_res, max_res)
            
            # Handle initialization if needed
            if not self.bacteria_population:
                self.initialize_population()
                
            # If population is extinct, initialize again
            if len(self.bacteria_population) == 0:
                self.initialize_population()
            
            # Start the simulation thread if not already running
            if not self.running:
                self.running = True
                self.paused = False
                self.simulation_thread = threading.Thread(target=self.run_simulation)
                self.simulation_thread.daemon = True
                self.simulation_thread.start()
                
                # Update button states
                self.start_button.config(state=tk.DISABLED)
                self.pause_button.config(state=tk.NORMAL, text="Pause")
                
                self.status_var.set("Simulation running...")
        except ValueError as e:
            self.status_var.set(f"Error starting simulation: {str(e)}")
    
    def pause_simulation(self):
        if self.running:
            self.paused = not self.paused
            if self.paused:
                self.pause_button.config(text="Resume")
                self.status_var.set("Simulation paused.")
            else:
                self.pause_button.config(text="Pause")
                self.status_var.set("Simulation resumed.")
    
    def reset_simulation(self):
        # Stop any running simulation
        self.running = False
        self.paused = False
        
        # Wait for thread to finish
        if hasattr(self, 'simulation_thread') and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        
        # Reset variables
        self.bacteria_population = []
        self.generation = 0
        self.avg_resistance_history = []
        self.population_history = []
        
        # Initialize new population
        self.initialize_population()
        
        # Reset buttons
        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED, text="Pause")
        
        self.status_var.set("Simulation reset.")
    
    def run_simulation(self):
        while self.running:
            if not self.paused:
                # Check if extinction occurred
                if len(self.bacteria_population) == 0:
                    self.status_var.set("Population extinct! Reset to start a new simulation.")
                    self.running = False
                    # Update buttons on main thread
                    self.master.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                    self.master.after(0, lambda: self.pause_button.config(state=tk.DISABLED))
                    break
                
                # Perform simulation step
                self.simulation_step()
                
                # Sleep based on simulation speed
                time.sleep(0.5 / self.speed_var.get())
            else:
                # When paused, just wait a bit
                time.sleep(0.1)
    
    def on_resize(self, event):
        # Only handle resize events from the main window
        if event.widget == self.master:
            # Redraw charts on window resize
            self.fig.tight_layout()
            self.canvas.draw()
    
    def on_closing(self):
        # Stop simulation thread
        self.running = False
        self.paused = True
        
        # Wait for thread to finish
        if hasattr(self, 'simulation_thread') and self.simulation_thread.is_alive():
            self.simulation_thread.join(timeout=1.0)
        
        # Close the window
        pygame.quit()
        self.master.destroy()
        sys.exit()

def main():
    root = tk.Tk()
    app = BacterialResistanceSimulation(root)
    root.mainloop()

if __name__ == "__main__":
    main()