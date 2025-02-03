#youtube_downloader/downloader.py

from tkinter import filedialog, messagebox
from pytubefix import YouTube
import os

def download_videos():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not file_path:
        messagebox.showerror("Error", "Please select a file containing video links.")
        return
        
    save_folder = filedialog.askdirectory()
    if not save_folder:
        messagebox.showerror("Error", "Please select a folder to save videos.")
        return
        
    try:
        with open(file_path, "r") as file:
            links = file.readlines()
            
        for link in links:
            link = link.strip()
            if link:
                try:
                    # Add use_oauth=True và use_innertube=True để bypass bot detection
                    yt = YouTube(
                        link,
                        use_oauth=True,
                        use_innertube=True,
                        allow_oauth_cache=True
                    )
                    
                    # Get video title để hiển thị thông tin
                    print(f"Downloading: {yt.title}")
                    
                    # Download video với độ phân giải cao nhất
                    stream = yt.streams.get_highest_resolution()
                    
                    # Download và lưu file
                    out_file = stream.download(save_folder)
                    
                    # Rename file nếu tên file quá dài
                    if len(os.path.basename(out_file)) > 100:
                        new_name = os.path.join(save_folder, f"video_{links.index(link)}.mp4")
                        os.rename(out_file, new_name)
                        
                    print(f"Downloaded: {yt.title}")
                    
                except Exception as e:
                    print(f"Error downloading {link}: {str(e)}")
                    continue
                    
        messagebox.showinfo("Success", "All videos downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")