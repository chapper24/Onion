import os
import warnings
import PIL.Image
import ffmpeg
import pytubefix.request
import random
import json
import customtkinter as ctk
import playsound3 as playsound

from pytubefix import YouTube
from threading import Thread
from PIL import Image, ImageTk
from tkinter import filedialog

BUTTON_COLOR = "#b361fa"
BUTTON2_COLOR = "#bd74fc"
BUTTON_HOVER_COLOR = "#9652d1"
BACKGROUND_COLOR = "#4d3f4d"
MESSAGE_COLOR = "#d0eb02"
MESSAGE_COLOR2 = "#ff4fb9"
HEADING_COLOR = "#911d4f"
BOX_COLOR = "#333033"
BOX_TEXT_COLOR = "#bfb6bf"
BOX_TEMP_TEXT_COLOR = "#8a878a"
BOX_BORDER_COLOR = "#5c515c"
PROGRESS_BAR_COLOR = "#87ff2b"
READ_ONLY_TEXT_COLOR = "#807e82"
READ_ONLY_BG_COLOR = "#444245"

GEOMETRY_X = "600"
GEOMETRY_Y = "500"
CANVAS_SIZE_FIX = 2

FRAME_MS_TIME = 225

pytubefix.request.default_range_size = 1048576

class VideoDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.save_data)

        # the data frfr
        with open('data.json', 'r') as f:
            self.data = json.load(f)

        # sigma file selelelctor
        class FilePathButton(ctk.CTkFrame):
            def __init__(self, master, x, y):
                super().__init__(master, fg_color="transparent")
                self.master = master

                self.new_entry = ctk.CTkEntry(
                    self.master,
                    placeholder_text="output path",
                    width=150,
                    fg_color=BOX_COLOR,
                    border_color=BOX_BORDER_COLOR,
                    text_color=BOX_TEXT_COLOR,
                    placeholder_text_color=BOX_TEMP_TEXT_COLOR
                )

                pil_folder = PIL.Image.open("Images/FolderOpen.png")
                itk_folder = ImageTk.PhotoImage(pil_folder)

                self.new_button = ctk.CTkButton(
                    self.master,
                    image=itk_folder,
                    text="",
                    command=self.open_explorer,
                    fg_color=BUTTON_COLOR,
                    hover_color=BUTTON_HOVER_COLOR,
                    width=30,
                    font=("Helvetica", 16)
                )

                self.y = y
                self.x = x

                self.true_width = self.new_button._current_width + self.new_entry._current_width
                self.true_height = self.new_button._current_height/CANVAS_SIZE_FIX
                self.start_x = x - (self.true_width / CANVAS_SIZE_FIX)

                self.new_button.place(x=x + self.new_entry._current_width - (self.true_width/CANVAS_SIZE_FIX), y=y)
                self.new_entry.place(x=x - (self.true_width/CANVAS_SIZE_FIX), y=y)


            def open_explorer(self):
                file_path = filedialog.askdirectory(title="pick where you want the file to go to fr")

                if file_path:
                    self.new_entry.delete(0, "end")
                    self.new_entry.insert(0, file_path)

                    return file_path

        # window
        self.title("thy onion")
        self.geometry(GEOMETRY_X + "x" + GEOMETRY_Y)
        self.configure(fg_color=BACKGROUND_COLOR)
        self.iconbitmap("OnionIcon.ico")

        # other
        self.widget_positions = {}

        # paths
        self.file_path_base = os.path.join(os.path.expanduser("~"), "Downloads")
        self.file_path_video = None
        self.file_path_sound = None
        self.file_path_music = None

        self.project_folder = os.path.dirname(os.path.abspath(__file__))

        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.canvas.place(relwidth=1, relheight=1)

        # background
        self.pil_bg = Image.open("Images/GrassBackground.png").resize((1200, 1200))
        self.itk_bg = ImageTk.PhotoImage(self.pil_bg)
        self.bg1 = self.canvas.create_image(
            0,
            -175,
            image=self.itk_bg,
            anchor="nw"
        )

        # background 2, its just a smooth rectangle lmao
        self.bg2 = self.canvas.create_polygon(
            self.get_rounded_rect_points(100, 90, 1100, 700, 80),
            fill=BACKGROUND_COLOR,
            outline=BOX_BORDER_COLOR,
            width=12.5,
            smooth=True
        )

        # it's him
        self.pil_onion = Image.open("Images/OnionIcon.png").resize((500, 300))
        self.itk_onion = ImageTk.PhotoImage(self.pil_onion)
        self.onion = self.canvas.create_image(
            (int(GEOMETRY_X) / 2) * CANVAS_SIZE_FIX, # x position
            530*CANVAS_SIZE_FIX, # y position
            image=self.itk_onion,
            anchor="s"
        )
        self.canvas.tag_bind(self.onion, "<Button-1>", self.onion_click)

        # ???
        self.pil_l = Image.open("Images/Lm.png").resize((400, 400))
        self.itk_l = ImageTk.PhotoImage(self.pil_l)
        self.l = self.canvas.create_image(
            (int(GEOMETRY_X) / 2) * CANVAS_SIZE_FIX, # x position
            (666+66+66)*CANVAS_SIZE_FIX, # y position
            image=self.itk_l,
            anchor="s"
        )

        # the heading
        self.label1 = self.canvas.create_text(
            (int(GEOMETRY_X)/2)*CANVAS_SIZE_FIX, # x position
            20*CANVAS_SIZE_FIX, # y position
            text="Onion downloada",
            font="Helvetica 35 bold",
            fill=MESSAGE_COLOR2,

        )

        # im watching you... :eyes:
        self.label2 = self.canvas.create_text(
            (int(GEOMETRY_X) / 2) * CANVAS_SIZE_FIX, # x position
            370 * CANVAS_SIZE_FIX, # y position
            text="im watching you",
            font="Helvetica 20",
            fill=MESSAGE_COLOR
        )

        # youtube video title
        self.video_title_label = self.canvas.create_text(
            (int(GEOMETRY_X)-190)/CANVAS_SIZE_FIX,  # x position
            200,  # y position
            text="no video detected... :(",
            font="Helvetica 20",
            fill=MESSAGE_COLOR2,
            width=350,
            justify=ctk.LEFT,
            anchor="nw"
        )

        # link entry
        self.link_entry = ctk.CTkEntry(
            self,
            placeholder_text="youtube video link here!",
            width=400,
            fg_color=BOX_COLOR,
            border_color=BOX_BORDER_COLOR,
            text_color=BOX_TEXT_COLOR,
            placeholder_text_color=BOX_TEMP_TEXT_COLOR,
        )
        self.link_entry.place(
            x=(int(GEOMETRY_X) + 400) / CANVAS_SIZE_FIX - (self.link_entry._current_width),
            y=65
        )
        self.link_entry.bind("<KeyRelease>", self.update_title_label)

        # name entry
        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="file name here! (if its blank it'll just be the title)",
            width=325,
            fg_color=BOX_COLOR,
            border_color=BOX_BORDER_COLOR,
            text_color=BOX_TEXT_COLOR,
            placeholder_text_color=BOX_TEMP_TEXT_COLOR
        )
        self.name_entry.place(
            x=(int(GEOMETRY_X) + 250) / CANVAS_SIZE_FIX - (self.name_entry._current_width),
            y=245
        )

        # format menu
        self.format_menu = ctk.CTkOptionMenu(
            self,
            values=[".mp4", ".mp3", ".wav"],
            fg_color=BUTTON_COLOR,
            button_color=BUTTON2_COLOR,
            button_hover_color=BUTTON_HOVER_COLOR,
            command=self.format_changed,
            width=72
        )
        self.format_menu.set(".mp4")
        self.format_menu.place(
            x=(int(GEOMETRY_X) + (self.name_entry._current_width - self.format_menu._current_width)) / CANVAS_SIZE_FIX,
            y=245
        )

        # pregress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=400,
            height=20,
            corner_radius=0,
            progress_color=PROGRESS_BAR_COLOR,
            mode="determinate",
        )
        self.progress_bar.set(-100)
        self.progress_bar.place(
            x=(int(GEOMETRY_X)-400) / CANVAS_SIZE_FIX,
            y=315,
        )

        # progress entry
        self.progress_entry = ctk.CTkEntry(
            self,
            width=325,
            text_color=READ_ONLY_TEXT_COLOR,
            placeholder_text_color=READ_ONLY_TEXT_COLOR,
            fg_color=READ_ONLY_BG_COLOR,
            placeholder_text="download progress will go here, start downloading!",
        )
        self.progress_entry.place(
            x=(int(GEOMETRY_X)-400) / CANVAS_SIZE_FIX,
            y=280,
        )
        self.progress_entry.configure(state="readonly")

        # download button
        self.download_button = ctk.CTkButton(
            self,
            text="Download",
            command=self.start_download_thread,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            width=72
        )
        self.download_button.place(
            x=(int(GEOMETRY_X) + (self.progress_entry._current_width - self.download_button._current_width)) / CANVAS_SIZE_FIX,
            y=280
        )

        # video fpb
        self.video_fpb = FilePathButton(
            self,
            x=(int(GEOMETRY_X) + 220) / CANVAS_SIZE_FIX,
            y=100
        )
        self.video_fpb.update_idletasks()

        # set to base path first, but if the user has the separate paths it'll update to the correct path fr
        self.video_fpb.new_entry.insert(0, self.data["base_path"])
        if self.data["separate_paths_"]:
            self.video_fpb.new_entry.delete(0, "end")
            self.video_fpb.new_entry.insert(0, self.data["video_path"])

        self.video_fpb.new_entry.bind("<KeyRelease>", self.base_path_check)
        self.video_fpb.new_button.bind("<Button-1>", self.base_path_check)

        # video icon
        self.pil_video_icon = Image.open("Images/VideoIcon.png")
        self.itk_video_icon = ImageTk.PhotoImage(self.pil_video_icon)
        self.video_icon = self.canvas.create_image(
            (self.video_fpb.start_x - 15) * CANVAS_SIZE_FIX,  # x position
            (self.video_fpb.y + self.video_fpb.true_height + 5) * CANVAS_SIZE_FIX,  # y position
            image=self.itk_video_icon,
            anchor="s"
        )

        # sound fpb
        self.sound_fpb = FilePathButton(
            self,
            x=(int(GEOMETRY_X) + 220) / CANVAS_SIZE_FIX,
            y=140)
        self.sound_fpb.update_idletasks()
        self.sound_fpb.new_entry.insert(0, self.data["sound_path"])

        # sound icon
        self.pil_sound_icon = Image.open("Images/SoundIcon.png")
        self.itk_sound_icon = ImageTk.PhotoImage(self.pil_sound_icon)
        self.sound_icon = self.canvas.create_image(
            (self.sound_fpb.start_x - 15) * CANVAS_SIZE_FIX,  # x position
            (self.sound_fpb.y + self.sound_fpb.true_height + 5) * CANVAS_SIZE_FIX,  # y position
            image=self.itk_sound_icon,
            anchor="s"
        )

        # music fpb
        self.music_fpb = FilePathButton(
            self,
            x=(int(GEOMETRY_X) + 220) / CANVAS_SIZE_FIX,
            y=180)
        self.music_fpb.update_idletasks()
        self.music_fpb.new_entry.insert(0, self.data["music_path"])

        # music icon
        self.pil_music_icon = Image.open("Images/MusicIcon.png")
        self.itk_music_icon = ImageTk.PhotoImage(self.pil_music_icon)
        self.music_icon = self.canvas.create_image(
            (self.music_fpb.start_x - 15) * CANVAS_SIZE_FIX,  # x position
            (self.music_fpb.y + self.music_fpb.true_height + 6) * CANVAS_SIZE_FIX,  # y position
            image=self.itk_music_icon,
            anchor="s"
        )

        # can i quit my job if this is music
        self.is_music_toggle = ctk.CTkCheckBox(
            self,
            100,
            10,
            text="is music",
            command=self.separate_music_sound_setting,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.is_music_toggle.place(
            x=(int(GEOMETRY_X)-400) / CANVAS_SIZE_FIX,
            y=180
        )

        # setting button
        self.settings_button = ctk.CTkButton(
            self,
            text="Settings",
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.settings_button.place(
            x=(int(GEOMETRY_X) - 259) / CANVAS_SIZE_FIX - (self.settings_button.current_width / CANVAS_SIZE_FIX),
            y=210
        )
        self.settings_button.bind("<Button-1>", self.open_settings_frame)
        self.settings_button.bind("<Leave>", self.hide_settings_frame)

        # setting frame
        self.mouse_on_settings_frame = False

        self.settings_frame = ctk.CTkFrame(self, 400, 200)
        self.settings_frame.place(
            x=int(GEOMETRY_X) / CANVAS_SIZE_FIX - (self.settings_frame._current_width / CANVAS_SIZE_FIX),
            y=10
        )
        self.settings_frame.bind("<Enter>", self.is_on_settings_frame)
        self.settings_frame.bind("<Leave>", self.isnt_on_settings_frame)

        # separate video and audio output setting
        self.separate_paths_toggle = ctk.CTkCheckBox(
            self.settings_frame,
            100,
            10,
            text="Separate video and sound output paths",
            command=self.separate_paths_setting,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.separate_paths_toggle.place(x=10, y=10)

        self.separate_paths_toggle.deselect()
        if self.data["separate_paths_"] == 1:
            self.separate_paths_toggle.select()

        # separate music and sound output setting
        self.separate_music_sound_toggle = ctk.CTkCheckBox(
            self.settings_frame,
            100,
            10,
            text="Separate sound and music output paths",
            command=self.separate_music_sound_setting,
            fg_color=BUTTON_COLOR,
            hover_color=BUTTON_HOVER_COLOR
        )
        self.separate_music_sound_toggle.place(x=10, y=50)

        # set the data
        self.separate_music_sound_toggle.deselect()
        if self.data["separate_sound_music_paths_"] == 1:
            self.separate_music_sound_toggle.select()

        # music threshold setting
        self.music_threshold_entry = ctk.CTkEntry(
            self.settings_frame,
            placeholder_text="30 (recommended)",
            width=130
        )
        self.music_threshold_entry.place(x=110, y=90)
        self.music_threshold_entry.bind("<KeyRelease>", self.adm_arg_fix)

        # set the data
        if self.data["music_threshold"] != "":
            self.music_threshold_entry.insert(0, self.data["music_threshold"])

        self.music_setting_label1 = ctk.CTkLabel(
            self.settings_frame,
            text="Music threshold:"
        )
        self.music_setting_label1.place(x=10, y=90)

        self.music_setting_label2 = ctk.CTkLabel(
            self.settings_frame,
            text="(this will automatically mark your sound as music if the length of it is over the threshold. if it isn't correct, you can manually change it. set to 0 if you always want to manually decide)",
            font=("Helvetica", 9),
            wraplength=380
        )
        self.music_setting_label2.place(x=10, y=120)

        # bind all the children of the settings frame so it doesn't die lol
        for child in self.settings_frame.winfo_children():
            child.bind("<Enter>", self.is_on_settings_frame)
            child.bind("<Leave>", self.isnt_on_settings_frame)


        ## hide this stuff initially
        self.hide_widget(self.settings_frame, True)

        # fbp's
        self.hide_widget(self.sound_fpb.new_button, not self.data["separate_paths_"])
        self.hide_widget(self.sound_fpb.new_entry, not self.data["separate_paths_"])

        self.hide_widget(self.music_fpb.new_button, not self.data["separate_sound_music_paths_"])
        self.hide_widget(self.music_fpb.new_entry, not self.data["separate_sound_music_paths_"])

        if not self.data["separate_paths_"]:
            self.canvas.itemconfig(self.sound_icon, state="hidden")
            self.canvas.itemconfig(self.video_icon, state="hidden")

        if not self.data["separate_sound_music_paths_"]:
            self.canvas.itemconfig(self.music_icon, state="hidden")


        # the settings
        self.hide_widget(self.separate_music_sound_toggle, not self.data["separate_paths_"])

        self.hide_widget(self.music_setting_label1, not self.data["separate_sound_music_paths_"])
        self.hide_widget(self.music_setting_label2, not self.data["separate_sound_music_paths_"])
        self.hide_widget(self.music_threshold_entry, not self.data["separate_sound_music_paths_"])

        # other
        self.hide_widget(self.is_music_toggle, True)


    # ----------------------- functions ----------------------- #

    # on hover for settings button idk
    hide_timer = None

    def open_settings_frame(self, arg):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
            self.hide_timer = None
        self.hide_widget(self.settings_frame, False)


    def hide_settings_frame(self, arg):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
        self.hide_timer = self.after(FRAME_MS_TIME, self._check_and_hide)


    def _check_and_hide(self):
        if not self.mouse_on_settings_frame:
            self.hide_widget(self.settings_frame, True)
        self.hide_timer = None


    def is_on_settings_frame(self, arg):
        self.mouse_on_settings_frame = True
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
            self.hide_timer = None


    def isnt_on_settings_frame(self, arg):
        self.mouse_on_settings_frame = False
        self.hide_settings_frame(None)
        self.focus()


    # when toggled it unhides the music path and stuff
    def separate_paths_setting(self):
        separate_paths_state = self.separate_paths_toggle.get()

        if separate_paths_state == 1:

            self.video_fpb.new_entry.delete(0, "end")
            self.video_fpb.new_entry.insert(0, self.data["video_path"])

            self.hide_widget(self.sound_fpb.new_button, False)
            self.hide_widget(self.sound_fpb.new_entry, False)
            self.canvas.itemconfig(self.sound_icon, state="normal")

            self.canvas.itemconfig(self.video_icon, state="normal")

            self.hide_widget(self.separate_music_sound_toggle, False)

            self.separate_music_sound_toggle.deselect()
            self.focus()

        else:

            self.video_fpb.new_entry.delete(0, "end")
            self.video_fpb.new_entry.insert(0, self.data["base_path"])

            self.hide_widget(self.sound_fpb.new_button, True)
            self.hide_widget(self.sound_fpb.new_entry, True)
            self.canvas.itemconfig(self.sound_icon, state="hidden")

            self.canvas.itemconfig(self.video_icon, state="hidden")

            self.hide_widget(self.separate_music_sound_toggle, True)

            self.hide_widget(self.music_fpb.new_button, True)
            self.hide_widget(self.music_fpb.new_entry, True)
            self.canvas.itemconfig(self.music_icon, state="hidden")

            self.hide_widget(self.music_setting_label1, True)
            self.hide_widget(self.music_setting_label2, True)
            self.hide_widget(self.music_threshold_entry, True)

            self.hide_widget(self.is_music_toggle, True)


    # sound music toggle thing
    def separate_music_sound_setting(self):
        separate_music_sound_state = self.separate_music_sound_toggle.get()

        if separate_music_sound_state == 1:

            self.hide_widget(self.music_fpb.new_button, False)
            self.hide_widget(self.music_fpb.new_entry, False)
            self.canvas.itemconfig(self.music_icon, state="normal")

            self.hide_widget(self.music_setting_label1, False)
            self.hide_widget(self.music_setting_label2, False)
            self.hide_widget(self.music_threshold_entry, False)

            if self.format_menu.get() != ".mp4":
                self.hide_widget(self.is_music_toggle, False)

        else:

            self.hide_widget(self.music_fpb.new_button, True)
            self.hide_widget(self.music_fpb.new_entry, True)
            self.canvas.itemconfig(self.music_icon, state="hidden")

            self.hide_widget(self.music_setting_label1, True)
            self.hide_widget(self.music_setting_label2, True)
            self.hide_widget(self.music_threshold_entry, True)

            self.hide_widget(self.is_music_toggle, True)
            self.focus()


    # since base and video use the same textbox, we gotta make sure which is which for saving data!!
    def base_path_check(self, arg):
        if self.separate_paths_toggle.get() == 1:
            self.data["video_path"] = self.video_fpb.new_entry.get()
        else:
            self.data["base_path"] = self.video_fpb.new_entry.get()

        with open('data.json', 'w') as f:
            json.dump(self.data, f, indent=2)


    # onion is watching 👀
    def onion_click(self, arg):
        playsound.playsound("Sounds/ImWatchingYou.mp3", block=False)


    # get video if it exists fr
    def get_video(self):
        link = self.link_entry.get()

        yt = YouTube(link)

        if yt:
            return yt
        else:
            print("no video detected!! D:")
            return None


    # who is this?
    def auto_define_music(self):
        format = self.format_menu.get()

        yt = None
        try:
            yt = self.get_video()
        except:
            return

        if format != ".mp4" and self.separate_music_sound_toggle.get() == 1:
            try:
                if self.music_threshold_entry.get() == "":
                    threshold = 30
                    print("theres no threshold put in, so its gonna be 30 lol")
                else:
                    threshold = int(self.music_threshold_entry.get())
            except:
                warnings.warn("threshold is NOT a valid number, defaulted to 30!! >:(")
                threshold = 30

            if yt.length >= threshold:
                print("its over the threshold, so it's probably music")
                self.is_music_toggle.select()
            else:
                print("probably not, its under the threshold")
                self.is_music_toggle.deselect()


    # because python is stupid, i had to add ts
    def adm_arg_fix(self, arg):
        self.auto_define_music()


    # detect when file format type changes
    def format_changed(self, arg):
        format = self.format_menu.get()

        self.auto_define_music()

        if self.separate_music_sound_toggle.get() == 0:
            return

        if format == ".mp4":
            self.hide_widget(self.is_music_toggle, True)
        else:
            self.hide_widget(self.is_music_toggle, False)


    # it hides the widget what else do you want from me
    def hide_widget(self, widget, should_hide):
        if should_hide:
            info = widget.place_info()
            if info:
                self.widget_positions[widget] = info
                widget.place_forget()
        else:
            if widget in self.widget_positions:
                info = self.widget_positions[widget]

                widget.place(
                    x=int(info["x"])/CANVAS_SIZE_FIX,
                    y=int(info["y"])/CANVAS_SIZE_FIX
                )


    # good for checking if the video is the video you want
    def update_title_label(self, args):
        try:
            yt = self.get_video()
            self.auto_define_music()

            if yt:
                self.canvas.itemconfig(self.video_title_label, text=yt.title)
        except:
            self.canvas.itemconfig(self.video_title_label, text="no video detected... :(")
            pass


    # update the progress bar so you know its downloading!!!
    def progress_update(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = bytes_downloaded / total_size

        self.progress_entry.configure(state="normal")
        self.progress_entry.configure(placeholder_text=f"{int(percentage * 100)}%")
        self.progress_entry.configure(state="readonly")

        if random.randint(1, 500) == 1:
            self.progress_entry.configure(state="normal")
            self.progress_entry.configure(placeholder_text=f"INSTALLING EVIL MALWARE MAUHAHAH!!! ...jk")
            self.progress_entry.configure(state="readonly")

        self.progress_bar.set(percentage)


    # get the correct file path when downloading fr
    def get_download_path(self):
        file_type = self.format_menu.get()

        self.file_path_video = self.video_fpb.new_entry.get()
        self.file_path_sound = self.sound_fpb.new_entry.get()
        self.file_path_music = self.music_fpb.new_entry.get()

        if file_type == ".mp4" and self.file_path_video:
            return self.file_path_video
        elif (file_type == ".mp3" or file_type == ".wav") and (self.file_path_sound or self.file_path_music):

            if self.separate_music_sound_toggle.get() == 1 and self.is_music_toggle.get() == 1:
                return self.file_path_music
            else:
                return self.file_path_sound
        else:
            return self.file_path_base


    # threading so nerdy heh
    def start_download_thread(self):
        thread = Thread(target=self.download_video)
        thread.start()


    # woooo downloadd
    def download_video(self):
        link = self.link_entry.get()
        name = self.name_entry.get()
        file_type = self.format_menu.get()

        if not link:
            self.progress_entry.configure(state="normal")
            self.progress_entry.configure(placeholder_text="i think you're forgetting something..? ծ_ô")
            self.progress_entry.configure(state="readonly")
            return

        try:
            self.download_button.configure(state="disabled")

            yt = YouTube(link, on_progress_callback=self.progress_update)

            if not name:
                name = yt.title

            final_filename = f"{name}{file_type}"
            final_path = os.path.join(self.get_download_path(), final_filename)

            if file_type == ".mp4":

                fixed_path = self.get_download_path()

                yt.streams.get_highest_resolution().download(
                    output_path=fixed_path,
                    filename=f"{name}.mp4"
                )
            else:
                audio_stream = yt.streams.get_audio_only()

                temp_file = audio_stream.download(output_path=self.project_folder, filename="temp_audio_file")

                ffmpeg_exe = os.path.join(self.project_folder, "ffmpeg", "ffmpeg.exe")

                self.progress_entry.configure(state="normal")
                self.progress_entry.configure(placeholder_text=f"converting to {file_type}...")
                self.progress_entry.configure(state="readonly")

                input_file = ffmpeg.input(temp_file)
                if file_type == ".wav":
                    stream = ffmpeg.output(input_file, final_path, acodec='pcm_s16le')
                else:
                    stream = ffmpeg.output(input_file, final_path, acodec='libmp3lame')

                self.progress_bar.configure(mode="indeterminate")
                self.progress_bar.start()

                ffmpeg.run(stream, cmd=ffmpeg_exe, overwrite_output=True, quiet=True)

                if os.path.exists(temp_file):
                    os.remove(temp_file)

            # when the download is done
            self.progress_entry.configure(state="normal")
            self.progress_entry.configure(placeholder_text=f"downloaded to {final_path}!")
            self.progress_entry.configure(state="readonly")

            self.progress_bar.configure(mode="determinate")
            self.progress_bar.set(100)
            self.progress_bar.stop()

        except Exception as e:
            self.progress_entry.configure(state="normal")
            self.progress_entry.configure(placeholder_text="error!! i dont think that link was valid... :(")
            self.progress_entry.configure(state="readonly")
        finally:
            self.download_button.configure(state="normal")


     # wowowo so smooth :)
    def get_rounded_rect_points(self, x1, y1, x2, y2, radius, **kwargs):
        return [x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1,
                x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius,
                x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2,
                x1 + radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius,
                x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1]


    # save the data before the window DIES
    def save_data(self):
        self.data["sound_path"] = self.sound_fpb.new_entry.get()
        self.data["music_path"] = self.music_fpb.new_entry.get()

        self.data["separate_paths_"] = self.separate_paths_toggle.get()

        if self.data["separate_paths_"] == 0:
            self.data["separate_sound_music_paths_"] = 0
        else:
            self.data["separate_sound_music_paths_"] = self.separate_music_sound_toggle.get()

        self.data["music_threshold"] = self.music_threshold_entry.get()

        # ok now copy the new data to the json!!
        with open('data.json', 'w') as f:
            json.dump(self.data, f, indent=2)

        # now delete the window because we saved :)
        self.destroy()

if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()