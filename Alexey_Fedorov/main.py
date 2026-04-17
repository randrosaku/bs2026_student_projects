import sys
import os
import soundfile as magic_sound_analysis_library
import numpy as magic_calculation_library
import streamlit
import pandas as pd
import matplotlib.pyplot as magic_drawing_library

print("You are using Bass Pickup Analyzer 3000")
#----------------------------------------------------
# Config

standards_setting = input("Standards setting? Y/n:")
if standards_setting == "N" or standards_setting == "n":
    low_pass = float(input("Low pass frequency: "))
    high_pass = float(input("High pass frequency: "))
    number_of_eq_bands = int(input("Number of eq bands: "))
    eq_bands = []
    for band in range(number_of_eq_bands):
        eq_bands.append(float(input(f"Frequency for eq band {band + 1}: ")))
    eq_bands.sort()
else:
    low_pass = 20
    high_pass = 10000    
    eq_bands = [20, 40, 80, 120, 200, 400, 800, 1500, 3000, 6000, 20000]

#------------------------------------------------------
# Importing files

audio_files_folder = sys.argv[1]
print("The folder for analysis is:", audio_files_folder)

queue_for_analysis = []

for audio_file in os.listdir(audio_files_folder):
    if audio_file.endswith(".wav"):
        correct_file_path = audio_files_folder + "/" + audio_file
        queue_for_analysis.append(correct_file_path)

print("Files for analysis are:", queue_for_analysis)

#----------------------------------------------
# Lists for storing the reslts

names_list = []
frequencies_list = []
peak_frequency_list = []
volume_list = []
db_peak_list = []
dynamic_range_list = []

#----------------------------------------------------
# The analsysis

def audio_analysis(audio_file):

    name = audio_file.split("/")
    del(name[0])
    name = name[0].split(".")
    del(name[1])
    name = "".join(name)

    # print("The file shall be named:", name)

    audio, sample_rate = magic_sound_analysis_library.read(audio_file)
    
    if audio.ndim > 1: # proudly taken from internet i didn't know how to convert to mono
        audio = audio.mean(axis=1)

    samples = len(audio)

    # print("Analyzing file:", audio_file)
    # print("Samples:", samples)
    # print("Sample rate:", sample_rate)
    # print("Duration:", round(samples / sample_rate, 2), "seconds")

    fourier_transform_result  = magic_calculation_library.fft.rfft(audio)
    magnitudes  = magic_calculation_library.abs(fourier_transform_result)
    frequencies = magic_calculation_library.fft.rfftfreq(len(audio), d=1/sample_rate)


    db = 20 * magic_calculation_library.log10(magnitudes + 1e-10) # i took this formula from internet, i would never come up with it myself :)
    db = db - db.max()

    # print("Peak db:", db.max())
    # print("Average db:", db.mean())
    # print("Floor db:", db.min())

    peak_frequency = frequencies[magic_calculation_library.argmax(db)]
    dynamic_range = db.max() - db.min()

    # print("Peak frequency:", round(peak_frequency, 2), "hz")
    # print("Dynamic range:", round(dynamic_range, 2), "db")

    names_list.append(name)
    frequencies_list.append(frequencies)
    peak_frequency_list.append(round(peak_frequency, 2))
    volume_list.append(db)
    db_peak_list.append(db.max())
    dynamic_range_list.append(round(dynamic_range, 2))

#------------------------------------------------

for audio_file in queue_for_analysis:
    audio_analysis(audio_file)

# print("Names:", names_list)
# print("Frequencies:", frequencies_list)
# print("Volume:", volume_list)
# print("db peaks:", db_peak_list)
# print("Dynamic ranges:", dynamic_range_list)

#----------------------------------------------------
# Visualisation 

streamlit.title("Bass Pickup Analyzer 3000")

all_pickups = names_list
with streamlit.container(border=True): # i copied this from the documentation and worked on it fit my needs
    pickups = streamlit.multiselect("Pickups", all_pickups, default=all_pickups)

streamlit.title("Frequency spectrum of pickups")
graph, ax = magic_drawing_library.subplots()

index = 0 
for index, name in enumerate(pickups):
    ax.plot(frequencies_list[index], volume_list[index], label=name)

ax.set_xscale('log')
ax.set_xlabel("Frequency (hz)")
ax.set_ylabel("Amplitude (db)")
ax.set_xlim(low_pass, high_pass)
ax.legend()
ax.grid(True)
ax.get_xaxis().set_major_formatter(magic_drawing_library.ScalarFormatter()) # i took this from internet, it doesn't affect the results but makes the graph look better
ax.set_xticks(eq_bands)

streamlit.pyplot(graph)

streamlit.write("The list of pickups:")
streamlit.write(pd.DataFrame({
    'Pickup name': names_list,
    'Peak frequency (hz)': peak_frequency_list,
    'Dynamic range (db)': dynamic_range_list,
    # 'Audio': [streamlit.audio(audio, format="audio/mpeg") for audio in queue_for_analysis]
}))