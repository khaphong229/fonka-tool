#main.py
import os
import time
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pytubefix import YouTube
from video_editor.editor import VideoEditor
from tiktok_uploader.uploader import TikTokUploader
from tkinter import simpledialog
import shutil
import json

class VideoConfig:
    def __init__(self):
        self.video_path = ""
        self.caption = ""
        self.hashtags = ""
        self.comments = ""

class YouTubeDownloader:
    def __init__(self, frame):
        self.frame = frame
        self.links_file = StringVar()
        self.save_folder = StringVar()
        self.current_download = StringVar()
        self.setup_ui()

    def setup_ui(self):
        # File selection frame
        file_frame = ttk.LabelFrame(self.frame, text="Input Selection")
        file_frame.pack(padx=10, pady=5, fill="x")

        # Links file selection
        Label(file_frame, text="Links File:").grid(row=0, column=0, padx=5, pady=5)
        Entry(file_frame, textvariable=self.links_file, width=50).grid(row=0, column=1, padx=5)
        Button(file_frame, text="Browse", command=self.select_links_file).grid(row=0, column=2, padx=5)

        # Output folder selection
        Label(file_frame, text="Save Folder:").grid(row=1, column=0, padx=5, pady=5)
        Entry(file_frame, textvariable=self.save_folder, width=50).grid(row=1, column=1, padx=5)
        Button(file_frame, text="Browse", command=self.select_save_folder).grid(row=1, column=2, padx=5)

        # Status frame
        status_frame = ttk.LabelFrame(self.frame, text="Download Status")
        status_frame.pack(padx=10, pady=5, fill="x")

        # Current download label
        Label(status_frame, textvariable=self.current_download, wraplength=500).pack(padx=5, pady=5)

        # Download button
        Button(self.frame, text="Start Download", command=self.start_download).pack(pady=10)

    def select_links_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            self.links_file.set(file_path)

    def select_save_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder.set(folder)

    def download_single_video(self, link, index, total):
        try:
            # Update status
            status = f"Downloading video {index + 1}/{total}\nURL: {link}"
            self.current_download.set(status)

            # Initialize YouTube object with use_oauth=True
            yt = YouTube(link, use_oauth=True)
            
            # Get video title and update status
            title = yt.title
            self.current_download.set(f"Downloading video {index + 1}/{total}\nTitle: {title}\nURL: {link}")
            
            # Download video
            stream = yt.streams.get_highest_resolution()
            out_file = stream.download(self.save_folder.get())
            
            # Rename if filename is too long
            if len(os.path.basename(out_file)) > 100:
                new_name = os.path.join(self.save_folder.get(), f"video_{index + 1}.mp4")
                if os.path.exists(out_file):
                    os.rename(out_file, new_name)
            
            return True
        except Exception as e:
            error_msg = f"Error downloading {link}: {str(e)}"
            self.current_download.set(error_msg)
            print(error_msg)
            return False

    def start_download(self):
        if not self.links_file.get() or not self.save_folder.get():
            messagebox.showerror("Error", "Please select both links file and save folder")
            return

        def download_thread():
            try:
                with open(self.links_file.get(), "r") as file:
                    links = [link.strip() for link in file.readlines() if link.strip()]

                successful = 0
                total = len(links)

                for i, link in enumerate(links):
                    if self.download_single_video(link, i, total):
                        successful += 1

                final_message = f"Download completed!\nSuccessfully downloaded: {successful}/{total} videos"
                self.current_download.set(final_message)
                messagebox.showinfo("Complete", final_message)

            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
                self.current_download.set("Download failed. Check error message.")

        # Start download in a separate thread
        threading.Thread(target=download_thread, daemon=True).start()

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Tool Auto Upload Videos TikTok")
        self.root.geometry("900x700")
        
        # Video Editor Variables
        self.input_folder = StringVar()
        self.output_folder = StringVar()
        self.text_var = StringVar(value="Sample Text")
        self.font_size = StringVar(value="50")
        self.position = StringVar(value="bottom")
        
        # TikTok Upload Variables
        self.tiktok_video_path = StringVar()
        self.tiktok_caption = StringVar()
        self.tiktok_hashtags = StringVar()
        
        self.setup_ui()
        
    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, expand=True, fill=BOTH)
        
        # YouTube Downloader Tab
        youtube_frame = self.create_youtube_tab(notebook)
        notebook.add(youtube_frame, text="YouTube Downloader")
        
        # Video Editor Tab
        editor_frame = self.create_editor_tab(notebook)
        notebook.add(editor_frame, text="Video Editor")
        
        # TikTok Uploader Tab
        tiktok_frame = self.create_tiktok_tab(notebook)
        notebook.add(tiktok_frame, text="TikTok Uploader")
        
    def create_youtube_tab(self, notebook):
        frame = ttk.Frame(notebook)
        Label(frame, text="Download YouTube Videos", font=("Arial", 14)).pack(pady=10)
        downloader = YouTubeDownloader(frame)
        return frame
    
    def create_editor_tab(self, notebook):
        frame = ttk.Frame(notebook)
        
        # Folder selection
        folder_frame = ttk.LabelFrame(frame, text="Folder Selection")
        folder_frame.pack(padx=10, pady=5, fill="x")
        
        Label(folder_frame, text="Input Folder:").grid(row=0, column=0, padx=5, pady=5)
        Entry(folder_frame, textvariable=self.input_folder, width=50).grid(row=0, column=1, padx=5)
        Button(folder_frame, text="Browse", command=self.select_input_folder).grid(row=0, column=2, padx=5)
        
        Label(folder_frame, text="Output Folder:").grid(row=1, column=0, padx=5, pady=5)
        Entry(folder_frame, textvariable=self.output_folder, width=50).grid(row=1, column=1, padx=5)
        Button(folder_frame, text="Browse", command=self.select_output_folder).grid(row=1, column=2, padx=5)
        
        # Editing options
        edit_frame = ttk.LabelFrame(frame, text="Editing Options")
        edit_frame.pack(padx=10, pady=5, fill="x")
        
        # Text overlay options
        Label(edit_frame, text="Text Overlay:").grid(row=0, column=0, padx=5, pady=5)
        Entry(edit_frame, textvariable=self.text_var, width=40).grid(row=0, column=1, padx=5)
        
        # Font size selection
        Label(edit_frame, text="Font Size:").grid(row=1, column=0, padx=5, pady=5)
        ttk.Spinbox(edit_frame, from_=10, to=100, textvariable=self.font_size, width=10).grid(row=1, column=1, sticky="w", padx=5)
        
        # Position selection
        Label(edit_frame, text="Position:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Combobox(edit_frame, textvariable=self.position, values=["top", "bottom", "center"], width=10).grid(row=2, column=1, sticky="w", padx=5)
        
        # Process button
        Button(frame, text="Process Videos", command=self.process_videos).pack(pady=10)
        
        return frame
    
    def create_tiktok_tab(self, notebook):
        frame = ttk.Frame(notebook)
        
        # Profile Management Frame
        profile_frame = ttk.LabelFrame(frame, text="Profile Management")
        profile_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # Profile list with extended selection mode
        self.profile_listbox = Listbox(profile_frame, selectmode=EXTENDED, height=10)
        self.profile_listbox.pack(side=LEFT, padx=5, pady=5, fill=BOTH, expand=True)
        
        # Profile buttons frame
        profile_buttons = ttk.Frame(profile_frame)
        profile_buttons.pack(side=RIGHT, padx=5, pady=5)
        
        # Add profile button
        Button(profile_buttons, text="Add Profile", command=self.add_new_profile).pack(pady=2)
        
        # Delete profile button
        Button(profile_buttons, text="Delete Profile", command=self.delete_profile).pack(pady=2)
        
        # Create context menus
        self.single_menu = Menu(frame, tearoff=0)
        self.single_menu.add_command(label="Configure Video", command=self.configure_video)
        self.single_menu.add_command(label="Start Upload", command=self.start_single_upload)
        
        self.multi_menu = Menu(frame, tearoff=0)
        self.multi_menu.add_command(label="Start Batch Upload", command=self.start_batch_upload)
        
        # Bind right-click event
        self.profile_listbox.bind("<Button-3>", self.show_context_menu)
        
        # Initialize profile configs
        self.profile_configs = {}
        self.load_profile_configs()
        
        self.update_profile_list()
        return frame
    
    def select_input_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)
    
    def select_tiktok_video(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Video Files", "*.mp4 *.avi *.mkv"),
            ("All Files", "*.*")
        ])
        if file_path:
            self.tiktok_video_path.set(file_path)
    
    def process_videos(self):
        if not self.input_folder.get() or not self.output_folder.get():
            messagebox.showerror("Error", "Please select both input and output folders")
            return
            
        editor = VideoEditor()
        try:
            editor.process_batch(
                self.input_folder.get(),
                self.output_folder.get(),
                text=self.text_var.get(),
                font_size=int(self.font_size.get()),
                position=self.position.get()
            )
            messagebox.showinfo("Success", "Videos processed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def update_profile_list(self):
        """Update the profile listbox"""
        self.profile_listbox.delete(0, END)
        uploader = TikTokUploader()
        profiles = uploader.get_profiles()
        for profile_name in profiles:
            self.profile_listbox.insert(END, profile_name)

    def add_new_profile(self):
        """Add new Chrome profile"""
        profile_name = simpledialog.askstring("New Profile", "Enter profile name:")
        if profile_name:
            uploader = TikTokUploader()
            try:
                # Create new profile and start login process
                uploader.create_driver(profile_name)
                uploader.manual_login(profile_name)
                messagebox.showinfo("Success", "Profile created successfully!")
                self.update_profile_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create profile: {str(e)}")
            finally:
                if uploader.driver:
                    uploader.driver.quit()

    def delete_profile(self):
        """Delete selected Chrome profile"""
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile to delete")
            return
            
        profile_name = self.profile_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Delete", f"Delete profile '{profile_name}'?"):
            uploader = TikTokUploader()
            if uploader.delete_profile(profile_name):
                messagebox.showinfo("Success", "Profile deleted successfully!")
                self.update_profile_list()
            else:
                messagebox.showerror("Error", "Failed to delete profile")

    def upload_to_tiktok(self):
        # Get selected profile
        selection = self.profile_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a profile")
            return

        profile_name = self.profile_listbox.get(selection[0])
        
        # Validate video path
        if not self.tiktok_video_path.get():
            messagebox.showerror("Error", "Please select a video file")
            return
        
        # Get other inputs
        hashtags = [tag.strip() for tag in self.tiktok_hashtags.get().split(',') if tag.strip()]
        
        def upload_thread():
            try:
                uploader = TikTokUploader()
                uploader.create_driver(profile_name)
                
                success = uploader.upload_video(
                    video_path=self.tiktok_video_path.get(),
                    caption=self.tiktok_caption.get(),
                    hashtags=hashtags
                )
                
                if success:
                    messagebox.showinfo("Success", "Video uploaded successfully!")
                else:
                    messagebox.showerror("Error", "Upload failed")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Upload failed: {str(e)}")
            finally:
                if uploader and uploader.driver:
                    uploader.driver.quit()
        
        threading.Thread(target=upload_thread, daemon=True).start()

    def load_profile_configs(self):
        config_path = os.path.join(os.path.expanduser('~'), '.tiktok_profiles', 'video_configs.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    for profile, config in data.items():
                        video_config = VideoConfig()
                        video_config.video_path = config.get('video_path', '')
                        video_config.caption = config.get('caption', '')
                        video_config.hashtags = config.get('hashtags', '')
                        video_config.comments = config.get('comments', '')
                        self.profile_configs[profile] = video_config
            except Exception as e:
                print(f"Error loading configs: {e}")
    def save_profile_configs(self):
        config_path = os.path.join(os.path.expanduser('~'), '.tiktok_profiles', 'video_configs.json')
        try:
            data = {}
            for profile, config in self.profile_configs.items():
                data[profile] = {
                    'video_path': config.video_path,
                    'caption': config.caption,
                    'hashtags': config.hashtags,
                    'comments': config.comments
                }
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving configs: {e}")
    def show_context_menu(self, event):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        if len(selection) == 1:
            self.single_menu.tk_popup(event.x_root, event.y_root)
        else:
            self.multi_menu.tk_popup(event.x_root, event.y_root)

    def configure_video(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        profile_name = self.profile_listbox.get(selection[0])
        config = self.profile_configs.get(profile_name, VideoConfig())
        
        # Create configuration window
        config_window = Toplevel(self.root)
        config_window.title(f"Configure Video - {profile_name}")
        config_window.geometry("600x400")
        
        # Video path
        ttk.Label(config_window, text="Video File:").pack(pady=5)
        video_path_var = StringVar(value=config.video_path)
        video_frame = ttk.Frame(config_window)
        video_frame.pack(fill='x', padx=5)
        ttk.Entry(video_frame, textvariable=video_path_var).pack(side='left', expand=True, fill='x')
        ttk.Button(video_frame, text="Browse", command=lambda: self.browse_video(video_path_var)).pack(side='right')
        
        # Caption
        ttk.Label(config_window, text="Caption:").pack(pady=5)
        caption_var = StringVar(value=config.caption)
        ttk.Entry(config_window, textvariable=caption_var).pack(fill='x', padx=5)
        
        # Hashtags
        ttk.Label(config_window, text="Hashtags (comma separated):").pack(pady=5)
        hashtags_var = StringVar(value=config.hashtags)
        ttk.Entry(config_window, textvariable=hashtags_var).pack(fill='x', padx=5)
        
        # Comments
        ttk.Label(config_window, text="Comments:").pack(pady=5)
        comments_text = Text(config_window, height=5)
        comments_text.pack(fill='x', padx=5)
        comments_text.insert('1.0', config.comments)
        
        # Save button
        def save_config():
            config.video_path = video_path_var.get()
            config.caption = caption_var.get()
            config.hashtags = hashtags_var.get()
            config.comments = comments_text.get('1.0', END).strip()
            self.profile_configs[profile_name] = config
            self.save_profile_configs()
            config_window.destroy()
            
        ttk.Button(config_window, text="Save", command=save_config).pack(pady=10)

    def browse_video(self, video_path_var):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4;*.mov;*.avi")]
        )
        if file_path:
            video_path_var.set(file_path)

    def start_single_upload(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        profile_name = self.profile_listbox.get(selection[0])
        config = self.profile_configs.get(profile_name)
        
        if not config or not config.video_path:
            messagebox.showerror("Error", "Please configure video settings first")
            return
            
        threading.Thread(target=self.upload_for_profile, 
                        args=(profile_name, config)).start()

    def start_batch_upload(self):
        selection = self.profile_listbox.curselection()
        if not selection:
            return
            
        profiles_to_upload = [self.profile_listbox.get(idx) for idx in selection]
        
        # Verify all profiles have configurations
        unconfigured = [p for p in profiles_to_upload 
                       if p not in self.profile_configs or 
                       not self.profile_configs[p].video_path]
        
        if unconfigured:
            messagebox.showerror("Error", 
                               f"Please configure video settings for: {', '.join(unconfigured)}")
            return
            
        threading.Thread(target=self.run_batch_upload, 
                        args=(profiles_to_upload,)).start()

    def upload_for_profile(self, profile_name, config):
        try:
            messagebox.showinfo("Upload Starting", 
                              f"Starting upload for profile: {profile_name}")
            
            uploader = TikTokUploader()
            uploader.create_driver(profile_name)
            
            try:
                hashtags = [tag.strip() for tag in config.hashtags.split(',') if tag.strip()]
                
                success = uploader.upload_video(
                    video_path=config.video_path,
                    caption=config.caption,
                    hashtags=hashtags
                )
                
                if success:
                    messagebox.showinfo("Success", 
                                      f"Upload completed for profile: {profile_name}")
                else:
                    messagebox.showerror("Error", 
                                       f"Upload failed for profile: {profile_name}")
            finally:
                if uploader.driver:
                    uploader.driver.quit()
                    
        except Exception as e:
            messagebox.showerror("Error", 
                               f"Error uploading for {profile_name}: {str(e)}")

    def run_batch_upload(self, profiles):
        total = len(profiles)
        completed = 0
        
        for profile_name in profiles:
            try:
                config = self.profile_configs[profile_name]
                self.upload_for_profile(profile_name, config)
                completed += 1
                
            except Exception as e:
                print(f"Error in batch upload for {profile_name}: {e}")
                
        messagebox.showinfo("Batch Upload Complete", 
                          f"Completed {completed}/{total} uploads")

def create_requirements_file():
    requirements = [
        "moviepy==1.0.3",
        "opencv-python==4.8.0.76",
        "pytubefix==1.9.2",
        "selenium==4.15.2",
        "undetected_chromedriver==3.5.3",
        "webdriver_manager==4.0.1"
    ]
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))

if __name__ == "__main__":
    create_requirements_file()  # Create requirements file
    root = Tk()
    app = Dashboard(root)
    root.mainloop()