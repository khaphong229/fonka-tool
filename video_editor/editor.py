#video_editor/editor.py
import os
import cv2
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import moviepy.editor as mp
from moviepy.audio.fx import volumex
from moviepy.video.fx.speedx import speedx

class VideoEditor:
    def __init__(self):
        self.supported_formats = ['.mp4', '.avi', '.mkv']
        self.video = None
        self.audio = None
        
    def add_text_overlay(self, video, text, font_size=50, position='bottom'):
        # Create text clip
        text_clip = TextClip(text, fontsize=font_size, color='white', bg_color='black')
        
        # Set position
        if position == 'bottom':
            text_pos = ('center', 'bottom')
        elif position == 'top':
            text_pos = ('center', 'top')
        else:
            text_pos = 'center'
            
        text_clip = text_clip.set_position(text_pos).set_duration(video.duration)
        return CompositeVideoClip([video, text_clip])
        
    def process_batch(self, input_folder, output_folder, **kwargs):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        for filename in os.listdir(input_folder):
            if any(filename.lower().endswith(fmt) for fmt in self.supported_formats):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, f"edited_{filename}")
                
                # Load video
                video = VideoFileClip(input_path)
                
                # Add text overlay if specified
                if kwargs.get('text'):
                    video = self.add_text_overlay(
                        video,
                        kwargs['text'],
                        kwargs.get('font_size', 50),
                        kwargs.get('position', 'bottom')
                    )
                
                # Write output video
                video.write_videofile(output_path, codec="libx264")
                video.close()
    def load_video(self, video_path):
        """Load video file"""
        self.video = mp.VideoFileClip(video_path)
    def add_text(self, text, position="bottom", font_size=50, color="white"):
        """Add text overlay to video"""
        txt_clip = mp.TextClip(text, fontsize=font_size, color=color)
        
        # Calculate position
        if position == "bottom":
            pos = ("center", self.video.h - txt_clip.h - 20)
        elif position == "top":
            pos = ("center", 20)
        else:  # center
            pos = "center"
            
        self.video = mp.CompositeVideoClip([
            self.video,
            txt_clip.set_position(pos).set_duration(self.video.duration)
        ])
        
    def add_background_music(self, music_path, volume=0.5):
        """Add background music to video"""
        background_audio = mp.AudioFileClip(music_path)
        
        # Loop music if shorter than video
        if background_audio.duration < self.video.duration:
            background_audio = mp.afx.audio_loop(background_audio, duration=self.video.duration)
        else:
            background_audio = background_audio.subclip(0, self.video.duration)
            
        # Mix original and background audio
        original_audio = self.video.audio.volumex(1.0)
        background_audio = background_audio.volumex(volume)
        
        final_audio = mp.CompositeAudioClip([original_audio, background_audio])
        self.video = self.video.set_audio(final_audio)
        
    def trim_video(self, start_time, end_time):
        """Trim video to specified time range"""
        self.video = self.video.subclip(start_time, end_time)
        
    def concat_videos(self, video_paths):
        """Concatenate multiple videos"""
        clips = [self.video]  # Include current video
        for path in video_paths:
            clips.append(mp.VideoFileClip(path))
        self.video = mp.concatenate_videoclips(clips)
        
    def adjust_speed(self, speed_factor):
        """Adjust video speed"""
        self.video = self.video.fx(speedx, speed_factor)
        
    def save_video(self, output_path):
        """Save edited video"""
        self.video.write_videofile(output_path)
        self.video.close()
        
    def process_batch(self, input_folder, output_folder, **kwargs):
        """Process multiple videos with same settings"""
        os.makedirs(output_folder, exist_ok=True)
        
        for filename in os.listdir(input_folder):
            if filename.lower().endswith(('.mp4', '.avi', '.mov')):
                input_path = os.path.join(input_folder, filename)
                output_path = os.path.join(output_folder, f"edited_{filename}")
                
                try:
                    self.load_video(input_path)
                    
                    # Apply effects based on kwargs
                    if 'text' in kwargs:
                        self.add_text(kwargs['text'], 
                                    kwargs.get('position', 'bottom'),
                                    kwargs.get('font_size', 50))
                                    
                    if 'music_path' in kwargs:
                        self.add_background_music(kwargs['music_path'],
                                               kwargs.get('music_volume', 0.5))
                                               
                    if 'speed' in kwargs:
                        self.adjust_speed(kwargs['speed'])
                        
                    if 'trim' in kwargs:
                        start, end = kwargs['trim']
                        self.trim_video(start, end)
                    
                    self.save_video(output_path)
                    
                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                finally:
                    if self.video:
                        self.video.close()