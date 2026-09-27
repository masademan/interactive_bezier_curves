import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BezierGUI:
    def __init__(self, title="Bezier GUI"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x400")

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.x = np.linspace(0, 10, 100)
        (self.line,) = self.ax.plot(self.x, np.sin(self.x), "b-", lw=2)
        self.ax.set_title("Sine Wave (Phase: 0)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Label(self.right_frame, text="controls", font=("Arial", 12, "bold")).pack(pady=10)

        btn_update = tk.Button(self.right_frame, text="Randomize Phase", command=self.update_plot)
        btn_update.pack(fill=tk.X, pady=5)

        btn_quit = tk.Button(self.right_frame, text="Quit", command=self.quit_app)
        btn_quit.pack(fill=tk.X, pady=5)

    def update_plot(self):
        phase = np.random.uniform(0, 2 * np.pi)
        self.line.set_ydata(np.sin(self.x + phase))
        self.ax.set_title(f"Sine Wave (Phase: {phase:.2f})")
        self.canvas.draw()

    def quit_app(self):
        plt.close("all")
        self.root.destroy()

    def run_gui(self):
        self.root.mainloop()


class TestPltGUI:
    def __init__(self, title="Test GUI"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x400")

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.x = np.linspace(0, 10, 100)
        (self.line,) = self.ax.plot(self.x, np.sin(self.x), "b-", lw=2)
        self.ax.set_title("Sine Wave (Phase: 0)")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.left_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        tk.Label(self.right_frame, text="controls", font=("Arial", 12, "bold")).pack(pady=10)

        btn_update = tk.Button(self.right_frame, text="Randomize Phase", command=self.update_plot)
        btn_update.pack(fill=tk.X, pady=5)

        btn_quit = tk.Button(self.right_frame, text="Quit", command=self.quit_app)
        btn_quit.pack(fill=tk.X, pady=5)

    def update_plot(self):
        phase = np.random.uniform(0, 2 * np.pi)
        self.line.set_ydata(np.sin(self.x + phase))
        self.ax.set_title(f"Sine Wave (Phase: {phase:.2f})")
        self.canvas.draw()

    def quit_app(self):
        plt.close("all")
        self.root.destroy()

    def run_gui(self):
        self.root.mainloop()


class TestCanvasGUI:
    def __init__(self, title="Test GUI"):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("600x400")

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = tk.Frame(self.main_frame, bg="white")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_frame = tk.Frame(self.main_frame, width=200, padx=10)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.x = np.linspace(0, 10, 100)
        (self.line,) = self.ax.plot(self.x, np.sin(self.x), "b-", lw=2)
        self.ax.set_title("Sine Wave (Phase: 0)")

        self.canvas = tk.Canvas(self.left_frame, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        tk.Label(self.right_frame, text="controls", font=("Arial", 12, "bold")).pack(pady=10)

        btn_quit = tk.Button(self.right_frame, text="Quit", command=self.quit_app)
        btn_quit.pack(fill=tk.X, pady=5)

    def quit_app(self):
        plt.close("all")
        self.root.destroy()

    def run_gui(self):
        self.root.mainloop()


if __name__ == "__main__":
    # test_gui = TestPltGUI()
    # test_gui.run_gui()

    test_gui = TestCanvasGUI()
    test_gui.run_gui()

    # bezier_gui = BezierGUI()
    # bezier_gui.run_gui()
