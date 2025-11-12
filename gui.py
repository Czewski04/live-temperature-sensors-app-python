import queue

import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from main import ModbusBackend
from voter import Voter


class VotingAlgorithmsApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.home_frame = None
        self.sensors_frame = None
        self.top_bar_frame = None
        self.settings_frame = None
        self.smoothing_slider_frame = None
        self.frequency_slider_frame = None
        self.num_sensors_slider_frame = None
        self.check_box_frame = None

        self.choice_button = None
        self.close_button = None
        self.return_button = None
        self.pause_button = None
        self.resume_button = None
        self.restart_button = None
        self.reset_button = None
        self.start_button = None
        self.settings_button = None
        self.smoothing_slider = None
        self.smoothing_slider_label = None
        self.frequency_slider = None
        self.frequency_slider_label = None
        self.num_sensors_slider = None
        self.num_sensors_slider_label = None
        self.avg_check_box = None
        self.median_check_box = None
        self.check_box_label = None

        self.settings_frame_is_visible = False

        self.canvas = None
        self.ax = None
        self.fig = None
        self.is_chart_paused = False

        self.after_id = None
        self.colour_pool = ['#ff0000', '#00fa00', '#0000fa', '#fafa00', '#fa00fa', '#00fafa']
        self.colour_pool_2 = ['#ff9999', '#90ee90', '#9999ff', '#ffff99', '#ff99ff', '#99ffff']

        self.data_queue = queue.Queue()

        self.num_sensors = 6
        self.reading_frequency = 1
        self.smoothing_factor = 1
        self.y_data_lists = [[] for _ in range(self.num_sensors)]
        self.y_data_lists_smoothed = [[] for _ in range(self.num_sensors)]
        self.x_data = []

        self.voting_alg = [
            {
                'name': 'Average',
                'is_active': False,
                'data': [],
                'colour': self.colour_pool[0]
            },
            {
                'name': 'Median',
                'is_active': False,
                'data': [],
                'colour': self.colour_pool[1]
            }
        ]

        self.backend = ModbusBackend(self.data_queue, self.num_sensors, self.reading_frequency)
        self.backend.start_reading_thread()

        self.voter = Voter()

        self.geometry("1100x800")
        self.title("Voting Algorithms Visualization")
        self.create_frames()

    def create_frames(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.home_frame = ctk.CTkFrame(self)
        self.home_frame.grid(row=0, column=0, sticky="nsew")

        self.choice_button = ctk.CTkButton(self.home_frame, text="Show all sensors", command=lambda: self.show_chart())
        self.choice_button.place(relx=0.5, rely=0.5, anchor="center")
        self.close_button  = ctk.CTkButton(self.home_frame, text="Close Application", command=self.close_application, fg_color="red")
        self.close_button.place(relx=0.92, rely=0.03, anchor="center")

        self.sensors_frame = ctk.CTkFrame(self)
        self.sensors_frame.grid(row=0, column=0, sticky="nsew")

        self.sensors_frame.grid_rowconfigure(0, weight=0)
        self.sensors_frame.grid_rowconfigure(1, weight=0)
        self.sensors_frame.grid_rowconfigure(2, weight=1)
        self.sensors_frame.grid_columnconfigure(0, weight=1)

        self.top_bar_frame = ctk.CTkFrame(self.sensors_frame, fg_color="transparent")
        self.top_bar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))

        self.return_button = ctk.CTkButton(self.top_bar_frame, text="Back to Home", command=lambda: self.closing_dialog_window())
        self.return_button.pack(side="right", padx=5, pady=5)

        self.reset_button = ctk.CTkButton(self.top_bar_frame, text="Reset", command=lambda: self.delete_chart())
        self.reset_button.pack(side="left", padx=5, pady=5)

        self.restart_button = ctk.CTkButton(self.top_bar_frame, text="Restart", command=lambda: self.restart_chart())
        self.restart_button.pack(side="left", padx=5, pady=5)

        self.resume_button = ctk.CTkButton(self.top_bar_frame, text="Resume", command=lambda: self.resume_chart(),state="disabled")
        self.resume_button.pack(side="left", padx=5, pady=5)

        self.pause_button = ctk.CTkButton(self.top_bar_frame, text="Pause", command=lambda: self.pause_chart())
        self.pause_button.pack(side="left", padx=5, pady=5)

        self.settings_button = ctk.CTkButton(self.top_bar_frame, text="Settings", command=lambda: self.show_hide_settings_frame())
        self.settings_button.pack(side="right", padx=5, pady=5)

        self.settings_frame = ctk.CTkFrame(self.sensors_frame, fg_color="transparent")

        self.smoothing_slider_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.smoothing_slider_frame.pack(side="left", padx=10, pady=0, fill="y")

        self.smoothing_slider_label = ctk.CTkLabel(self.smoothing_slider_frame, text="")
        self.smoothing_slider_label.pack(side="top", pady=(5, 0))

        self.smoothing_slider = ctk.CTkSlider(
            self.smoothing_slider_frame,
            from_=5,
            to=100,
            number_of_steps=19,
            command=self.show_smoothing_slider_value
        )
        self.smoothing_slider.bind("<ButtonRelease-1>", self.set_smoothing_factor_value)
        self.smoothing_slider.pack(side="top", padx=5, pady=(0, 5))

        self.smoothing_slider.set(self.smoothing_factor * 100)
        self.show_smoothing_slider_value(self.smoothing_factor * 100)

        #slider częstotliwosci

        self.frequency_slider_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.frequency_slider_frame.pack(side="left", padx=10, pady=0, fill="y")

        self.frequency_slider_label = ctk.CTkLabel(self.frequency_slider_frame, text="")
        self.frequency_slider_label.pack(side="top", pady=(5, 0))

        self.frequency_slider = ctk.CTkSlider(
            self.frequency_slider_frame,
            from_=10,
            to=1000,
            number_of_steps=99,
            command=self.show_frequency_slider_value
        )
        self.frequency_slider.bind("<ButtonRelease-1>", self.set_reading_frequency_value)
        self.frequency_slider.pack(side="top", padx=5, pady=(0, 5))

        self.frequency_slider.set(self.reading_frequency * 100)
        self.show_frequency_slider_value(self.reading_frequency * 100)


        #slider czujników

        self.num_sensors_slider_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.num_sensors_slider_frame.pack(side="left", padx=10, pady=0, fill="y")

        self.num_sensors_slider_label = ctk.CTkLabel(self.num_sensors_slider_frame, text="")
        self.num_sensors_slider_label.pack(side="top", pady=(5, 0))

        self.num_sensors_slider = ctk.CTkSlider(
            self.num_sensors_slider_frame,
            from_=1,
            to=6,
            number_of_steps=5,
            command=self.show_num_sensors_slider_value
        )
        self.num_sensors_slider.bind("<ButtonRelease-1>", self.set_num_sensors_value)
        self.num_sensors_slider.pack(side="top", padx=5, pady=(0, 5))

        self.num_sensors_slider.set(self.num_sensors)
        self.show_num_sensors_slider_value(self.num_sensors)

        # check boxy

        self.check_box_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.check_box_frame.pack(side="left", padx=10, pady=0, fill="y")

        self.check_box_label = ctk.CTkLabel(self.check_box_frame, text="Voters:")
        max_rows = 1 if len(self.voting_alg) < 4 else 2
        total_cols = (len(self.voting_alg) + max_rows - 1)
        self.check_box_label.grid(row=0, column=0, columnspan=total_cols, pady=(5, 0), sticky="w")
        for i, voter in enumerate(self.voting_alg):
            row_index = (i % max_rows) + 1
            col_index = i // max_rows

            checkbox = ctk.CTkCheckBox(
                self.check_box_frame,
                text=voter['name'],
                command=lambda c=voter: self.update_status(c)
            )

            if voter['is_active']:
                checkbox.select()

            checkbox.grid(row=row_index, column=col_index, sticky="w", padx=10, pady=5)

        self.show_menu()

    def run_chart(self):
        if self.canvas or self.fig or self.ax:
            return
        self.y_data_lists = [[] for _ in range(self.num_sensors)]
        self.y_data_lists_smoothed = [[] for _ in range(self.num_sensors)]
        self.backend.resume()
        self.voter.update_votes(self.voting_alg[0]['is_active'], self.voting_alg[1]['is_active'])
        self.is_chart_paused = False
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.sensors_frame)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.check_queue_and_update_chart()
        self.fig.tight_layout()
        self.pause_button.configure(state="normal")
        self.resume_button.configure(state="disabled")


    def check_queue_and_update_chart(self):
        if not self.canvas:
            return
        if not self.is_chart_paused:
            try:
                data_updated = False
                while not self.data_queue.empty():
                    data = self.data_queue.get_nowait()
                    if not data or len(data) != self.num_sensors:
                        continue
                    data_updated = True
                    voted_data = self.voter.vote(data)

                    self.x_data.append(self.x_data[-1] + self.reading_frequency if self.x_data else 0)
                    for i in range(self.num_sensors):
                        self.y_data_lists[i].append(data[i] if data[i] is not None else (self.y_data_lists[i][-1] if self.y_data_lists[i] else 0))

                        last_smoothed_value = self.y_data_lists_smoothed[i][-1] if self.y_data_lists_smoothed[i] else self.y_data_lists[i][-1]
                        smoothed_value = (self.smoothing_factor * self.y_data_lists[i][-1]) + ((1 - self.smoothing_factor) * last_smoothed_value)
                        self.y_data_lists_smoothed[i].append(smoothed_value)

                    for voter in self.voting_alg:
                        voter_name = voter['name']
                        data_list = voter['data']
                        value = voted_data.get(voter_name)
                        data_list.append(value)

                if data_updated:
                    self.redraw_chart()
            except queue.Empty:
                pass
        self.after_id = self.after(int(self.reading_frequency*1000), self.check_queue_and_update_chart)


    def redraw_chart(self):
        if not (self.ax and self.fig):
            return
        self.ax.cla()
        voting_is_active = False
        for voter in self.voting_alg:
            if voter['is_active'] and voter['data']:
                voting_is_active = True
                name = voter['name']
                data_list = voter['data']
                color = voter['colour']
                last_val = data_list[-1]
                label_text = f'{name}: {last_val:.2f}ºC'
                self.ax.plot(self.x_data, data_list, label=label_text, color=color, linewidth=2)
        for i in range(self.num_sensors):
            if voting_is_active:
                self.ax.plot(self.x_data, self.y_data_lists_smoothed[i], label=f'Sensor {i+1}: {self.y_data_lists[i][-1]}ºC', color=self.colour_pool_2[i % len(self.colour_pool_2)], linestyle='--', linewidth=0.5)
            else:
                self.ax.plot(self.x_data, self.y_data_lists_smoothed[i], label=f'Sensor {i+1}: {self.y_data_lists[i][-1]}ºC', color=self.colour_pool[i % len(self.colour_pool)])
        self.ax.grid(True)
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.legend(loc="upper left")
        self.ax.set_xlabel("Time [s]")
        self.ax.set_ylabel("Temperature [ºC]")
        self.ax.set_title("Temperature Live Data")
        self.canvas.draw()


    def show_menu(self):
        self.home_frame.tkraise()


    def show_chart(self):
        self.sensors_frame.tkraise()
        if not (self.canvas or self.fig or self.ax):
            self.run_chart()


    def close_application(self):
        self.destroy()


    def back_to_menu_and_delete(self):
        self.delete_chart()
        self.show_menu()

    def back_to_menu_and_pause(self):
        self.pause_chart()
        self.show_menu()

    def restart_chart(self):
        self.delete_chart()
        self.run_chart()


    def pause_chart(self):
        if not self.is_chart_paused:
            if self.backend:
                self.backend.pause()
            self.is_chart_paused = True
            self.pause_button.configure(state="disabled")
            self.resume_button.configure(state="normal")


    def resume_chart(self):
        if self.is_chart_paused:
            if self.backend:
                self.backend.resume()
            self.is_chart_paused = False
            self.pause_button.configure(state="normal")
            self.resume_button.configure(state="disabled")


    def delete_chart(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.fig:
            plt.close(self.fig)
            self.fig = None
        if self.ax:
            self.ax = None
        self.pause_button.configure(state="disabled")
        self.resume_button.configure(state="disabled")
        self.y_data_lists = [[] for _ in range(self.num_sensors)]
        self.y_data_lists_smoothed = [[] for _ in range(self.num_sensors)]
        for voter in self.voting_alg:
            voter['data'].clear()
        self.x_data.clear()
        with self.data_queue.mutex:
            self.data_queue.queue.clear()

    def closing_dialog_window(self):
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("600x200")
        dialog.title("Save chart before closing?")

        label = ctk.CTkLabel(dialog, text="Are you want to save chart before back to menu?")
        label.pack(side="top", pady=(20, 10))

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=20, pady=10)

        button_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        button_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        let_work_button = ctk.CTkButton(button_frame, text="Let work it in background", command=lambda: (self.show_menu(), dialog.destroy()))
        let_work_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        pause_button = ctk.CTkButton(button_frame, text="Pause", command=lambda: (self.back_to_menu_and_pause(), dialog.destroy()))
        pause_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        save_button = ctk.CTkButton(button_frame, text="Save to File", fg_color='green', command=lambda: (self.saving_file(), dialog.destroy()))
        save_button.grid(row=1, column=0, sticky="ew", padx=5, pady=5)

        abort_button = ctk.CTkButton(button_frame, text="Abort", fg_color='red', command=lambda: (self.back_to_menu_and_delete(), dialog.destroy()))
        abort_button.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        dialog.grab_set()
        self.wait_window(dialog)

    # def input_sensors(self, message="Type number of sensors (0<x<7):"):
    #     dialog = ctk.CTkInputDialog(text=message, title="Number of Sensors Configuration")
    #     num_sensors = dialog.get_input()
    #     if not num_sensors:
    #         num_sensors = self.input_sensors("Type a number, not letters! 0<x<7:")
    #     elif (not num_sensors.isdigit()) or (not (0 < int(num_sensors) < 7)):
    #         num_sensors = self.input_sensors("Type a number, not letters! Must be greater than 0 and less than 7:")
    #     return int(num_sensors)
    #
    # def input_frequency(self, message="Type reading frequency in seconds (default 1s):"):
    #     dialog = ctk.CTkInputDialog(text=message, title="Reading Frequency Configuration")
    #     frequency = dialog.get_input()
    #     if not frequency:
    #         frequency = 1
    #     try:
    #         frequency = float(frequency)
    #         if frequency < 0:
    #             frequency = self.input_frequency("Type a number, not letters! Must be greater than 0")
    #     except ValueError:
    #         frequency = self.input_frequency("Type a number, not letters! Must be greater than 0")
    #     return float(frequency)

    def saving_file(self):
        dialog = ctk.CTkToplevel(self)
        dialog.geometry("600x200")
        dialog.title("File type")

        label = ctk.CTkLabel(dialog, text="Choose file type to save chart:")
        label.pack(side="top", pady=(20, 10))

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, padx=20, pady=10)

        button_frame.grid_columnconfigure(0, weight=1, uniform="group1")
        button_frame.grid_columnconfigure(1, weight=1, uniform="group1")
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)

        let_work_button = ctk.CTkButton(button_frame, text="PNG",
                                        command=lambda: (self.save_chart_png(), dialog.destroy()))
        let_work_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        pause_button = ctk.CTkButton(button_frame, text="CSV",
                                     command=lambda: (self.save_chart_csv(), dialog.destroy()))
        pause_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        dialog.grab_set()
        self.wait_window(dialog)


    def save_chart_png(self):
        if self.fig:
            file_path = ctk.filedialog.asksaveasfilename(title="Save as: ", defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.fig.savefig(file_path)


    def save_chart_csv(self):
        if self.x_data and self.y_data_lists:
            file_path = ctk.filedialog.asksaveasfilename(title="Save as: ", defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
            if file_path:
                with open(file_path, 'w', encoding="utf-8", newline='') as file:
                    header = "Time [s];" + ";".join([f"Sensor_{i+1} [C]" for i in range(self.num_sensors)]) + "\n"
                    file.write(header)
                    for i in range(len(self.x_data)):
                        time_str = f"{self.x_data[i]:.1f}".replace('.', ',')
                        sensor_values = [str(self.y_data_lists[j][i]).replace('.', ',') for j in range(self.num_sensors)]
                        sensors_str = ";".join(sensor_values)
                        row = f"{time_str};{sensors_str}\n"
                        file.write(row)

    def show_smoothing_slider_value(self, value):
        if self.smoothing_slider_label:
            self.smoothing_slider_label.configure(text=f"Smoothing Factor: {value / 100:.2f}")


    def set_smoothing_factor_value(self, event):
        self.smoothing_factor = self.smoothing_slider.get() / 100


    def show_frequency_slider_value(self, value):
        if self.frequency_slider_label:
            self.frequency_slider_label.configure(text=f"Reading Frequency: {value / 100:.2f} s")


    def set_reading_frequency_value(self, event):
        self.reading_frequency = self.frequency_slider.get() / 100
        self.backend.update_reading_frequency(self.reading_frequency)


    def show_num_sensors_slider_value(self, value):
        if self.num_sensors_slider_label:
            self.num_sensors_slider_label.configure(text=f"Number of Sensors: {int(value)}")


    def set_num_sensors_value(self, event):
        value = self.num_sensors_slider.get()
        self.delete_chart()
        self.num_sensors = int(value)
        self.backend.update_num_sensors(self.num_sensors)
        self.run_chart()

    def show_hide_settings_frame(self):
        if self.settings_frame_is_visible:
            self.settings_frame.grid_forget()
            self.settings_button.configure(text="Settings")
            self.settings_frame_is_visible = False
        else:
            self.settings_frame.grid(row=1, column=0, sticky="ew", padx=10)
            self.settings_button.configure(text="Toggle")
            self.settings_frame_is_visible = True

    def update_status(self, voter):
        voter['is_active'] = not voter['is_active']
        self.voter.update_votes(self.voting_alg[0]['is_active'], self.voting_alg[1]['is_active'])

if __name__ == '__main__':
    app = VotingAlgorithmsApp()
    app.mainloop()