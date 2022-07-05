from moviepy import editor as mp
import numpy as np

def typing_animate(text, duration):
    N = len(text)
    durations = np.random.uniform(1, 3, size=(N,))
    durations = durations / durations.sum() * duration
    videos = []
    for i in range(len(text)):
        txt_clip = mp.TextClip(text[:i+1], fontsize=70, color='white', size=(1280, 720), method='caption', align='West')
        txt_clip = txt_clip.set_pos('center').set_duration(durations[i])
        videos.append(txt_clip)
    return mp.concatenate_videoclips(videos)

video = typing_animate("Hello World", 5)

video.write_videofile("hello.webm", fps=24)


video = typing_animate("Kriemhild and Luzia are sitting in the desert. They have been camping out for weeks, and they have started having strange dreams. They don't know yet why it is happening , but it has started giving them nightmares about cowboys. This is what they discuss. In the middle, they start to fight. You'll never believe at the end why this is happening.", 20)
video.write_videofile("long.webm", fps=24)