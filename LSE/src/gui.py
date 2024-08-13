import customtkinter as ctk
import os
from PIL import Image, ImageTk
from CTkTable import *
import requests
from bs4 import BeautifulSoup, Comment
import re
import string
import src.lyrics_processing as lyr_proc
import src.csv_related as csv_related
import src.search as search
import src.lucene_engine as luc_engine

# miscellaneous
def select_all(event):
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')
    
    return 'break'

def select_all_textbox(event):
    global_vars["add_song"]["lyrics_entry"].tag_add(ctk.SEL, "1.0", ctk.END)
    global_vars["add_song"]["lyrics_entry"].mark_set(ctk.INSERT, "1.0")
    global_vars["add_song"]["lyrics_entry"].see(ctk.INSERT)

    return 'break'

# search_tab
def search_tab_gui():  # creates the search_tab
    logo_font = ctk.CTkFont("Helvetica", 70)
    search_font = ctk.CTkFont("Helvetica", 25)
    ctk_vars["search_tab"].columnconfigure(0, weight = 1)
    
    for i in range(8):
        if i == 1:
            row_weight = 4
        elif i == 3 or i == 6:
            row_weight = 2
        else:
            row_weight = 1

        ctk_vars["search_tab"].rowconfigure(i, weight = row_weight)

    search_label = ctk.CTkLabel(ctk_vars["search_tab"], corner_radius = 10, text = "F.A.L.S.E.", text_color = "#1a6096",
                                font = logo_font,)
    search_label.grid(row = 1, column = 0, padx = 5, sticky = "nsew")
    

    search_entry = ctk.CTkEntry(ctk_vars["search_tab"], corner_radius = 10, font = search_font,)
    search_entry.grid(row = 3, column = 0, padx = 25, sticky = "nsew")
    global_vars["search_entry"] = search_entry
    search_entry.bind('<Control-a>', select_all)


    file_path = os.path.dirname(os.path.realpath(__file__))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "..", "assets", "search.png")

    search_png = ctk.CTkImage(Image.open(image_path), size = (20, 20))
    search_button = ctk.CTkButton(ctk_vars["search_tab"], text="Search", image = search_png, fg_color = "#1f2021",  
                                  font = search_font, command = search_engine)
    search_button.grid(row = 6, column = 0, padx = 150, sticky = "nsew")

def search_engine():
    active_settings = get_settings()
    search_string = global_vars["search_entry"].get()
    if search_string == "" or search_string == " ": return
    search_normal = search_string
    search_string = search.clean_search_string(search_string)
    
    table_cols = 0
    for boolean in range(len(active_settings) - 1):
        if boolean:
            table_cols += 1

    all_song_data = search.search_string_func(search_normal, search_string, active_settings)

    results_tab_gui(table_cols, int(active_settings[6]), all_song_data)
    ctk_vars["tab_view"].set("Results")

def results_tab_gui(table_cols, top_k, data):  # creates the results tab

    try:
        for widget in ctk_vars["results_tab"].winfo_children():
            widget.destroy()
    except Exception as e:
        pass

    cols = [["Artist", "Song", "Details"]]
    view_data = data
    results["song_lyr_data"] = view_data

    lyrics_array = []

    for song in data:
        try:
            print(song)
            modified_song = song.copy()
            modified_song[2] = "View"
            cols.append(modified_song)
            lyrics_array.append(song[2])
        except Exception as e:
            continue


    table = CTkTable(ctk_vars["results_tab"], row = top_k + 1, column = 3, values = cols, command = view_song_details)
    table.pack(expand=True, fill="both", padx=20, pady=20)

    ctk_vars["table"] = table

def view_song_details(cell_data):
    cell_row = cell_data["row"]
    cell_col = cell_data["column"]

    if cell_col == 0:
        show_artist_related(cell_row)
    elif cell_col == 2:
        create_view_gui(cell_row)

def create_view_gui(cell_row):  # creates the pop-up for the details of the song

    songs_data = results["song_lyr_data"]

    pop_up = ctk.CTkToplevel()
    pop_up.title(f"{songs_data[cell_row - 1][1]} by {songs_data[cell_row - 1][0]}")
    pop_up.geometry("300x450")
    pop_up.minsize(width = 300, height = 450)

    frame = ctk.CTkFrame(pop_up, width = 300, height = 450)
    frame.pack_configure(fill = "both", expand = True, padx = 5, pady = 5)

    frame.columnconfigure((0, 1), weight = 1)

    for i in range(10):
        frame.rowconfigure(i, weight = 1)

    artist_label = ctk.CTkLabel(frame, text = "Artist:")
    artist_label.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)

    artist_info = ctk.CTkLabel(frame, text = songs_data[cell_row - 1][0], bg_color = "#333333")
    artist_info.grid(row = 0, column = 1, sticky = "nsew", padx = 2, pady = 2)

    song_name_label = ctk.CTkLabel(frame, text = "Song:")
    song_name_label.grid(row = 1, column = 0, sticky = "nsew", padx = 5, pady = 5)

    song_name_info = ctk.CTkLabel(frame, text = songs_data[cell_row - 1][1], bg_color = "#333333")
    song_name_info.grid(row = 1, column = 1, sticky = "nsew", padx = 2, pady = 2)

    song_name_label = ctk.CTkLabel(frame, text = "Lucene Score:")
    song_name_label.grid(row = 2, column = 0, sticky = "nsew", padx = 5, pady = 5)

    lucene_score = str(songs_data[cell_row - 1][3])[:7]
    song_name_info = ctk.CTkLabel(frame, text = lucene_score, bg_color = "#333333")  # TODO
    song_name_info.grid(row = 2, column = 1, sticky = "nsew", padx = 2, pady = 2)

    lyrics_label = ctk.CTkLabel(frame, text = "Lyrics:")
    lyrics_label.grid(row = 3, column = 0, columnspan = 2, sticky = "nsew", padx = 5, pady = 5)

    lyrics_scroll = ctk.CTkScrollableFrame(frame, bg_color = "#333333")
    lyrics_scroll.grid(row = 4, column = 0, rowspan = 6, columnspan = 2, sticky = "nsew", padx = 2, pady = 2)

    lyrics_info = ctk.CTkLabel(lyrics_scroll, text = songs_data[cell_row - 1][2])
    lyrics_info.pack()

def show_artist_related(cell_row):

    songs_data = results["song_lyr_data"]
    artist = songs_data[cell_row - 1][0]

    all_album_data = search.search_artist_func(artist)

    headers = [["Type", "Name", "Year"]]

    for album in all_album_data:
        headers.append(album)

    pop_up = ctk.CTkToplevel()
    pop_up.title(f"Albums by {songs_data[cell_row - 1][0]}")
    pop_up.geometry("450x450")
    pop_up.minsize(width = 450, height = 450)

    frame = ctk.CTkFrame(pop_up, width = 450, height = 450)
    frame.pack_configure(fill = "both", expand = True, padx = 5, pady = 5)

    frame.columnconfigure(0, weight = 1)

    for i in range(10):
        frame.rowconfigure(i, weight = 1)

    table = CTkTable(frame, row = len(all_album_data) + 1, column = 3, values = headers)
    table.pack(expand=True, fill="both", padx=20, pady=20)


# settings_tab
def settings_tab_gui():  # creates the settings tab
    ctk_vars["settings_tab"].columnconfigure((0, 1, 2, 3, 4), weight = 1)

    for i in range(3):
        ctk_vars["settings_tab"].rowconfigure(i, weight = 1)

    label_array = ["Artist", "Song", "Lyrics", "Album Type", "Album Name", "Album Year"]
    settings_array = ["artist", "song", "lyrics", "album_type", "album_name", "album_year"]
    row_array = [0, 0, 0, 1, 1, 1]
    col_array = [1, 2, 3, 1, 2, 3]

    for i in range(len(label_array)):

        settings["booleans"][settings_array[i]] = ctk.BooleanVar(value = False)
        temp_var_checkbox = ctk.CTkCheckBox(ctk_vars["settings_tab"], text = label_array[i], variable = settings["booleans"][settings_array[i]], 
                                        onvalue = True, offvalue = False, command = settings["functions"][settings_array[i]])
        temp_var_checkbox.grid(row = row_array[i], column = col_array[i], sticky = "nsew", padx = 5, pady = 5)

    top_k_warning = ctk.CTkLabel(ctk_vars["settings_tab"], text = "")
    top_k_warning.grid(row = 2, column = 1, sticky = "nsew", padx = 5, pady = 5)
    settings["top_k"]["warning"] = top_k_warning

    top_k_frame = ctk.CTkFrame(ctk_vars["settings_tab"])
    top_k_frame.grid(row = 2, column = 2, sticky = "nsew", padx = 5, pady = 5)

    top_k_frame.columnconfigure((0, 1), weight = 1)
    top_k_frame.rowconfigure(0, weight = 1)

    top_k_label = ctk.CTkLabel(top_k_frame, text = "Top-K")
    top_k_label.grid(row = 0, column = 0, padx = 5, pady = 5)

    top_k_entry = ctk.CTkEntry(top_k_frame, corner_radius = 10, width = 50)
    top_k_entry.grid(row = 0, column = 1, padx = 5, pady = 5)
    top_k_entry.bind('<Control-a>', select_all)
    # top_k_entry.bind('<KeyRelease>', top_k_results)
    top_k_entry.insert(0, settings["top_k"]["value"])

    settings["top_k"]["entry"] = top_k_entry


def get_settings():
    artist = artist_checkbox()
    song = song_checkbox()
    album_type = album_type_checkbox()
    album_name = album_name_checkbox()
    album_year = album_year_checkbox()
    lyrics = lyrics_checkbox()
    top_k = top_k_results()

    active_settings = [artist, song, album_type, album_name, album_year, lyrics, top_k]

    return active_settings

def artist_checkbox():
    if settings["booleans"]["artist"].get():
        return True
    else:
        return False

def song_checkbox():
    if settings["booleans"]["song"].get():
        return True
    else:
        return False

def album_type_checkbox():
    if settings["booleans"]["album_type"].get():
        return True
    else:
        return False

def album_name_checkbox():
    if settings["booleans"]["album_name"].get():
        return True
    else:
        return False

def album_year_checkbox():
    if settings["booleans"]["album_year"].get():
        return True
    else:
        return False

def lyrics_checkbox():
    if settings["booleans"]["lyrics"].get():
        return True
    else:
        return False

def top_k_results():
    top_k = settings["top_k"]["entry"].get()

    if not isinstance(top_k, int):
        top_k = 5

    return top_k


# add_song_tab
def add_song_tab_gui():  # creates the add_song_tab
    ctk_vars["add_song_tab"].columnconfigure((0, 2), weight = 1)
    ctk_vars["add_song_tab"].columnconfigure((1, 3), weight = 2)

    for i in range(8):
        ctk_vars["add_song_tab"].rowconfigure(i, weight = 1)
    
    artist_label = ctk.CTkLabel(ctk_vars["add_song_tab"], corner_radius = 10, text = "Artist:",)
    artist_label.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)

    artist_entry = ctk.CTkEntry(ctk_vars["add_song_tab"], corner_radius = 10)
    artist_entry.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
    artist_entry.bind('<Control-a>', select_all)
    global_vars["add_song"]["artist_entry"] = artist_entry

    song_label = ctk.CTkLabel(ctk_vars["add_song_tab"], corner_radius = 10, text = "Song:")
    song_label.grid(row = 0, column = 2, sticky = "nsew", padx = 5, pady = 5)

    song_entry = ctk.CTkEntry(ctk_vars["add_song_tab"], corner_radius = 10)
    song_entry.grid(row = 0, column = 3, sticky = "nsew", padx = 5, pady = 5)
    song_entry.bind('<Control-a>', select_all)
    global_vars["add_song"]["song_entry"] = song_entry

    album_text_array = ["Album Type:", "Album Name:", "Album Year:"]
    album_var_array = ["album_type_entry", "album_name_entry", "album_year_entry"]

    for i in range(1, 4):
        temp_var_label = ctk.CTkLabel(ctk_vars["add_song_tab"], corner_radius = 10, text=album_text_array[i - 1])
        temp_var_label.grid(row = i * 2 - 1, column = 3, sticky = "nsew", padx = 5, pady = 5)

        temp_var_entry = ctk.CTkEntry(ctk_vars["add_song_tab"], corner_radius = 10)
        temp_var_entry.grid(row = i * 2, column = 3, sticky = "nsew", padx = 5, pady =5)
        temp_var_entry.bind('<Control-a>', select_all)

        global_vars["add_song"][album_var_array[i - 1]] = temp_var_entry


    add_button = ctk.CTkButton(ctk_vars["add_song_tab"], text = "Add this song!", fg_color = "#1f2021",  command = add_song_func)
    add_button.grid(row = 7, column = 3, sticky = "nsew", padx = 5, pady = 5)

    lyrics_entry = ctk.CTkTextbox(ctk_vars["add_song_tab"])
    lyrics_entry.grid(row = 1, column = 0, rowspan = 6, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
    lyrics_entry.bind('<Control-a>', select_all_textbox)
    global_vars["add_song"]["lyrics_entry"] = lyrics_entry

    result_label = ctk.CTkLabel(ctk_vars["add_song_tab"], corner_radius = 10, text = "Enter the info of the song!")
    result_label.grid(row = 7, column = 0, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
    global_vars["add_song"]["result_label"] = result_label

def add_song_func():  # the functionality of the add_song_tab
    input_array = []
    items_list = list(global_vars["add_song"].items())

    for key, value in items_list[:-1]:
        if key == "lyrics_entry":  # lyrics must be more than 10 chars in length
            temp_var = '"\n' + value.get(0.1, ctk.END) + '"'
            if len(temp_var) < 10:
                failed_add_song(key)
                return
        elif key == "album_year_entry":  # album_year must be a 4-digit number
            temp_var = value.get()
            if (not str.isdigit(temp_var) or len(temp_var) < 4) and temp_var != "":
                failed_add_song(key)
                return
        elif key == "artist_entry" or key == "song_entry":  # artist_entry & song_entry must not be empty
            temp_var = value.get()
            if temp_var == "":
                failed_add_song(key)
                return
        else:
            temp_var = value.get()

        input_array.append(temp_var)

    exists_boolean = add_to_library(input_array)

    if exists_boolean:
        successful_add_song(input_array, "updated")
    else:
        successful_add_song(input_array, "added")

def failed_add_song(reason):  # changes the result_label if the input isn't valid
    result_label = global_vars["add_song"]["result_label"]

    if reason == "album_year_entry":
        output = "Album Year isn't a valid number"
    elif reason == "lyrics_entry":
        output = "There are no Lyrics"
    elif reason == "artist_entry":
        output = "The Artist field must not be blank"
    elif reason == "song_entry":
        output = "The Song field must not be blank"

    result_label.configure(text = output, text_color = "#ed4e4c")

def successful_add_song(user_input, case):
    output = f"'{user_input[1]}' by {user_input[0]} was {case}!"
    global_vars["add_song"]["result_label"].configure(text = output, text_color = "#00e09d")

def del_song_func_2(artist, song):

    del_array = [artist.lower(), song.lower()]
    text = " ".join(del_array)

    artist_docs, artist_scores = luc_engine.search_index("lyrics", "artist", artist, 300)
    song_name_docs, song_name_scores = luc_engine.search_index("lyrics", "song_name", song, 50)

    try:
        common_song_doc_id = examine_songs_to_delete(artist_docs, artist_scores, song_name_docs, song_name_scores)
    except Exception as e:
        common_song_doc_id = None

    if common_song_doc_id != None:
        luc_engine.del_entry("lyrics", common_song_doc_id)
        return True
    else:
        return False


# del_song_tab
def del_song_tab_gui():  # creates the del_song_tab
    del_tab_font = ctk.CTkFont("Helvetica", 25)

    ctk_vars["del_song_tab"].columnconfigure((0, 1, 3, 4), weight = 1)
    ctk_vars["del_song_tab"].columnconfigure((2), weight = 2)

    for i in range(5):
        ctk_vars["del_song_tab"].rowconfigure(i, weight = 1)

    artist_label = ctk.CTkLabel(ctk_vars["del_song_tab"], corner_radius = 10, font = del_tab_font, text = "Artist:",)
    artist_label.grid(row = 1, column = 1, sticky = "nsew", padx = 5, pady = 5)

    artist_entry = ctk.CTkEntry(ctk_vars["del_song_tab"], corner_radius = 10, font = del_tab_font)
    artist_entry.grid(row = 1, column = 2, sticky = "nsew", padx = 5, pady = 5)
    artist_entry.bind('<Control-a>', select_all)
    global_vars["del_song"]["artist_entry"] = artist_entry

    song_label = ctk.CTkLabel(ctk_vars["del_song_tab"], corner_radius = 10, font = del_tab_font, text = "Song:")
    song_label.grid(row = 2, column = 1, sticky = "nsew", padx = 5, pady = 5)

    song_entry = ctk.CTkEntry(ctk_vars["del_song_tab"], corner_radius = 10, font = del_tab_font)
    song_entry.grid(row = 2, column = 2, sticky = "nsew", padx = 5, pady = 5)
    song_entry.bind('<Control-a>', select_all)
    global_vars["del_song"]["song_entry"] = song_entry

    delete_button = ctk.CTkButton(ctk_vars["del_song_tab"], text = "Delete this song!", fg_color = "#1f2021", 
                                  font = del_tab_font, command = del_song_func)
    delete_button.grid(row = 3, column = 1, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)

    result_label = ctk.CTkLabel(ctk_vars["del_song_tab"], text = " ", font = del_tab_font)
    result_label.grid(row = 4, column = 1, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)
    global_vars["del_song"]["result_label"] = result_label


def examine_songs_to_delete(artists, artists_scores, songs, songs_scores):
    artists_dict = {}
    for i in range(len(artists)):
        artists_dict[artists[i]] = artists_scores[i]

    songs_dict = {}
    for i in range(len(songs)):
        songs_dict[songs[i]] = songs_scores[i]

    common_docs = []
    for song in songs:
        for artist in artists:
            if song == artist:
                common_docs.append(song)
                
    scores = []
    docs_dict = {}
    for i in range(len(common_docs)):
        score_1 = artists_dict[common_docs[i]]
        score_2 = songs_dict[common_docs[i]]
        score = score_1 + score_2
        scores.append(score)

        docs_dict[common_docs[i]] = [score_1, score_2, score]

    scores.sort(reverse = True)

    for key, value in docs_dict.items():
            if value[2] == scores[0]:
                final = key

    print(f"doc_id of file to remove: {final}")

    return final

def del_song_func():  # the functionality of the del_song_tab
    artist = global_vars["del_song"]["artist_entry"].get()
    song = global_vars["del_song"]["song_entry"].get()

    del_array = [artist.lower(), song.lower()]
    text = " ".join(del_array)

    artist_docs, artist_scores = luc_engine.search_index("lyrics", "artist", artist, 300)
    song_name_docs, song_name_scores = luc_engine.search_index("lyrics", "song_name", song, 50)

    try:
        common_song_doc_id = examine_songs_to_delete(artist_docs, artist_scores, song_name_docs, song_name_scores)
    except Exception as e:
        common_song_doc_id = None

    if common_song_doc_id != None:
        # doc_id = artist_docs[0]
        luc_engine.del_entry("lyrics", common_song_doc_id)
        successful_del_song(del_array)
    else:
        failed_del_song(del_array)   



def failed_del_song(user_input):
    output = f"'{user_input[1]}' by {user_input[0]} wasn't found!"
    global_vars["del_song"]["result_label"].configure(text = output, text_color = "#ed4e4c")

def successful_del_song(user_input):
    output = f"'{user_input[1]}' by {user_input[0]} was deleted!"
    global_vars["del_song"]["result_label"].configure(text = output, text_color = "#00e09d")


# scraping_tab
def scraping_tab_gui():  # creates the scraping tab
    ctk_vars["scraping_tab"].columnconfigure((0, 2), weight = 1)
    ctk_vars["scraping_tab"].columnconfigure((1, 3), weight = 2)
    
    for i in range(20):
        ctk_vars["scraping_tab"].rowconfigure(i, weight = 1)
    
    artist_label = ctk.CTkLabel(ctk_vars["scraping_tab"], corner_radius = 10, text = "Artist",)
    artist_label.grid(row = 0, column = 0, sticky = "nsew", padx = 5, pady = 5)

    artist_entry = ctk.CTkEntry(ctk_vars["scraping_tab"], corner_radius = 10)
    artist_entry.grid(row = 0, column = 1, sticky = "nsew", padx = 5, pady = 5)
    artist_entry.bind('<Control-a>', select_all)
    global_vars["scraping"]["artist_entry"] = artist_entry

    song_label = ctk.CTkLabel(ctk_vars["scraping_tab"], corner_radius = 10, text = "Song")
    song_label.grid(row = 0, column = 2, sticky = "nsew", padx = 5, pady = 5)

    song_entry = ctk.CTkEntry(ctk_vars["scraping_tab"], corner_radius = 10)
    song_entry.grid(row = 0, column = 3, sticky = "nsew", padx = 5, pady = 5)
    song_entry.bind('<Control-a>', select_all)
    global_vars["scraping"]["song_entry"] = song_entry

    search_button = ctk.CTkButton(ctk_vars["scraping_tab"], text = "Add this song!", fg_color = "#1f2021",  command = scraping_tab_func)
    search_button.grid(row = 1, column = 3, sticky = "nsew", padx = 5, pady = 5)

    response_label = ctk.CTkLabel(ctk_vars["scraping_tab"], corner_radius = 10, text = "Enter a song!")
    response_label.grid(row = 1, column = 0, sticky = "nsew", columnspan = 3, padx = 5, pady = 5)
    global_vars["scraping"]["response_label"] = response_label

    response_frame = ctk.CTkFrame(ctk_vars["scraping_tab"], corner_radius = 10)
    response_frame.grid(row = 3, column = 0, rowspan = 7, columnspan = 4, sticky = "nsew", padx = 5, pady = 5)
    global_vars["scraping"]["response_frame"] = response_frame

    response_frame_gui()

def response_frame_gui():   # creates the elements withing the response_frame such as "Lyrics", "Album Type", "Album Name", "Album Year"
    response_frame = global_vars["scraping"]["response_frame"]

    response_frame.columnconfigure((0, 2), weight = 1)
    response_frame.columnconfigure((1, 3), weight = 2)
    response_frame.rowconfigure((0, 1, 2, 3, 4, 5), weight = 1)

    text_array = ["Album Type:", "-", "Album Name:", "-", "Album Year:", "-", "Lyrics:"]
    row_array = [0, 1, 2, 3, 4, 5, 0]
    row_span_array = [1, 1, 1, 1, 1, 1, 1]
    col_array = [3, 3, 3, 3, 3, 3, 0, 0]
    col_span_array = [1, 1, 1, 1, 1, 1, 3]
    color_array = ["2b2b2b", "333333", "2b2b2b", "333333", "2b2b2b", "333333", "2b2b2b"]
    var_names_array = ["album_type_label", "album_type", "album_name_label", "album_name", "album_year_label", "album_year", "lyrics_label"]

    for i in range(len(text_array)):
        temp_var =  ctk.CTkLabel(response_frame, text = text_array[i], bg_color = f"#{color_array[i]}")
        temp_var.grid(row = row_array[i], column = col_array[i], rowspan = row_span_array[i], columnspan = col_span_array[i], sticky = "nsew", padx = 5, pady = 5)

        if i == 6 or i == 7:
            # temp_var.configure(anchor=ctk.W)
            pass

        if not i % 2 == 0:
            global_vars["scraping"][var_names_array[i]] = temp_var

    scrollable_frame = ctk.CTkScrollableFrame(response_frame)
    scrollable_frame.grid(row = 1, column = 0, rowspan = 5, columnspan = 3, sticky = "nsew", padx = 5, pady = 5)

    lyrics = ctk.CTkLabel(scrollable_frame, text = "-")
    lyrics.pack()
    global_vars["scraping"]["lyrics"] = lyrics
        
def scraping_tab_func():  # the functionality of the scraping_tab
    input_array = []

    artist_raw = global_vars["scraping"]["artist_entry"].get()
    artist = artist_raw.replace(" ", "").lower()
    artist = "".join([i for i in artist if i not in string.punctuation])
    input_array.append(artist)

    song_raw = global_vars["scraping"]["song_entry"].get()
    song = song_raw.replace(" ", "").lower()
    song = "".join([i for i in song if i not in string.punctuation])
    input_array.append(song)

    url = f"https://www.azlyrics.com/lyrics/{artist}/{song}.html"
    scraping_results = scrape_azlyrics(url)
    
    if not isinstance(scraping_results, list):  # for unexpected https responses (which would be numbers)
        failed_scraping(scraping_results)
        return

    exists_boolean = add_to_library(scraping_results)

    if exists_boolean:
        successful_scraping(scraping_results, "updated")
    else:
        successful_scraping(scraping_results, "added")
    present_scraping_data(scraping_results)

def scrape_azlyrics(url):  # get the data from the url: "https://www.azlyrics.com/lyrics/{artist}/{song}.html"
    song_info = []

    index_dot_com = url.find(".com")
    link = ".." + url[index_dot_com + 4:]
    
    response = requests.get(url)
    if not response.status_code == 200:
        return response.status_code
    
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        album_info = soup.select_one('.songinalbum_title').get_text(strip=True)
    except Exception as e:
        print(f"There isn't an album for the son ({link})")

    artist = soup.select_one('.col-xs-12.col-lg-8.text-center > *:nth-child(3)').get_text()
    artist = artist.replace(" Lyrics", "").replace("\n", "")

    song = soup.select_one('.col-xs-12.col-lg-8.text-center > *:nth-child(5)').get_text()
    song = song.replace('"', '')

    commented_contents = soup.find_all(string=lambda text: isinstance(text, Comment))

    az_warning = "Usage of azlyrics.com content"
    lyrics_div = next((comment for comment in commented_contents if az_warning in str(comment)), None)

    lyrics = lyrics_div.find_parent('div').get_text()

    try:
        colon_index = album_info.find(":")
        album_type = album_info[:colon_index]

        quote_1_index = album_info.find('"')
        quote_2_index = album_info.find('"', quote_1_index  +1)
        album_name = album_info[quote_1_index + 1:quote_2_index]

        parenthesis_1_index = album_info.find("(")
        parenthesis_2_index = album_info.find(")")
        album_year = album_info[parenthesis_1_index + 1:parenthesis_2_index]
    except Exception as e:
        album_type = "Not Defined"
        album_name = "Not Defined"
        album_year = "Not Defined"

    song_info.extend([artist, song, album_type, album_name, album_year, f'"{lyrics}"'])

    return song_info

def failed_scraping(scraping_results):  # if response.status_code != 200
    
    if scraping_results == 404:
        output = "Page not found (404)"
    elif scraping_results == 429:
        output = "Too Many Requests (429)"
    elif scraping_results == 500:
        output = "Internal Server Error (500)"
    elif scraping_results == 502:
        output = "Bad Gateway (502)"
    elif scraping_results == "exists_already":
        output = "The song already exists"
    else:
        output = f"Unusual Response Code {scraping_results}"

    global_vars["scraping"]["response_label"].configure(text = output, text_color = "#ed4e4c")
    global_vars["scraping"]["album_type"].configure(text = "-")
    global_vars["scraping"]["album_name"].configure(text = "-")
    global_vars["scraping"]["album_year"].configure(text = "-")
    global_vars["scraping"]["lyrics"].configure(text = "")

def successful_scraping(scraping_results, case):  # if response.status_code == 200
    output = f"'{scraping_results[1]}' by {scraping_results[0]} was {case}!"
    global_vars["scraping"]["response_label"].configure(text = output, text_color = "#00e09d")

def present_scraping_data(scraping_results):  # presents the data in the scraping_tab
    global_vars["scraping"]["album_type"].configure(text = scraping_results[2])
    global_vars["scraping"]["album_name"].configure(text = scraping_results[3])
    global_vars["scraping"]["album_year"].configure(text = scraping_results[4])

    pattern = re.compile(r'^\s+')
    song_lyrics = re.sub(pattern, '', scraping_results[5])
    global_vars["scraping"]["lyrics"].configure(text = song_lyrics)

entry_id = {
    "lyrics_id": None,
    "album_id": None,
    "counter": 0,
}

# for add_song_tab & scraping_tab
def add_to_library(array):

    singer = array[0]
    song = array[1]
    album_type = array[2]
    album_name = array[3]
    album_year = array[4]
    lyrics = array[5]

    raw_lyrics = lyrics

    song_exists = del_song_func_2(singer, song)


    lyrics_col_mod = lyr_proc.each_song(lyrics)

    if entry_id["counter"] == 0:
        lyrics_id = luc_engine.get_length("modified", "lyrics") + 1
        entry_id["lyrics_id"] = lyrics_id

        album_id = luc_engine.get_length("modified", "albums") + 1
        entry_id["album_id"] = album_id

        entry_id["counter"] += 1

    else:
        entry_id["lyrics_id"] += 1
        lyrics_id = entry_id["lyrics_id"]

        entry_id["album_id"] += 1
        album_id = entry_id["album_id"]


    print("LYRICS ID", lyrics_id)
    print("ALBUM ID", album_id)

    lyrics_mod = {"id": lyrics_id , "artist": singer.lower(), "song_name": song.lower(), "lyrics": lyrics_col_mod}
    lyrics_og = {"id": lyrics_id, "artist": singer, "song_name": song, "lyrics": lyrics}
    
    albums_mod = {"id": album_id, "artist": singer.lower(), "album_type": album_type.lower(), "album_name": album_name.lower(), "album_year": album_year}
    albums_og = {"id": album_id, "artist": singer, "album_type": album_type, "album_name": album_name, "album_year": album_year}




    luc_engine.append_to_index("modified", "lyrics", lyrics_mod)
    luc_engine.append_to_index("original", "lyrics", lyrics_og)

    luc_engine.append_to_index("modified", "albums", albums_mod)
    luc_engine.append_to_index("original", "albums", albums_og)

    print(f"'{song}' by {singer} was added/updated")

    return song_exists

def update_dict(lyrics):
    from src.lyrics_processing import global_vars as lyr_global

    temp = lyrics.split()

    for word in temp:
        if word not in lyr_global["token_dict"]:
            lyr_global["token_dict"][word] = len(lyr_global["token_dict"])
            # print(word, lyr_global["token_dict"][word])



# tab creation
  





def init_gui():
    ctk.set_appearance_mode("Dark")
    window = ctk.CTk()
    window.title("F.A.L.S.E.")
    window.geometry("500x300")
    window.minsize(width = 600, height = 400)
    window.maxsize(width = 600, height = 400)
    tab_view = ctk.CTkTabview(window, width = 550, height = 380, segmented_button_selected_color = "#1a6096",
                            segmented_button_selected_hover_color = "#2078bc")
    ctk_vars["tab_view"] = tab_view
    
    ctk_vars["search_tab"] = tab_view.add("Search")
    ctk_vars["results_tab"] = tab_view.add("Results")
    ctk_vars["settings_tab"] = tab_view.add("Settings")
    ctk_vars["add_song_tab"] = tab_view.add("Add Song")
    ctk_vars["del_song_tab"] = tab_view.add("Delete Song")
    ctk_vars["scraping_tab"] = tab_view.add("Scraping")

    tab_view.pack()

    search_tab_gui()
    # results_tab_gui()
    settings_tab_gui()
    add_song_tab_gui()
    del_song_tab_gui()
    scraping_tab_gui()
    # ctk_vars["tab_view"].set("Results")  # TO REMOVE

    window.mainloop()

results = {
    "pop_up": None,
    "song_lyr_data": None,
    "album_data": None,
}

ctk_vars = {
    "window": None,
    "tab_view": None,
    "search_tab": None,
    "results_tab": None,
    "table": None,
    "settings_tab": None,
    "add_song_tab": None,
    "del_song_tab": None,
    "scraping_tab": None,
}

settings = {
    "booleans": {
        "artist": None,
        "song": None,
        "lyrics": None,
        "album_type": None,
        "album_name": None,
        "album_year": None,
    },
    "functions": {
        "artist": artist_checkbox,
        "song": song_checkbox,
        "lyrics": lyrics_checkbox,
        "album_type": album_type_checkbox,
        "album_name": album_name_checkbox,
        "album_year": album_year_checkbox,
    },
    "top_k": {
      "value":  5,
      "entry": None,
      "warning": None,
    }
}

global_vars = {
    "search": {
        "search_entry": None,
    },
    "settings": {
        "artist": None,
        "song": None,
        "album_type": None,
        "album_name": None,
        "album_year": None,
        "lyrics": None,
    },
    "add_song": {
        "artist_entry": None,
        "song_entry": None,
        "album_type_entry": None,
        "album_name_entry": None,
        "album_year_entry": None,
        "lyrics_entry": None,
        "result_label": None,
    },
    "del_song": {
        "artist_entry": None,
        "song_entry": None,
        "result_label": None,
    },
    "scraping": {
        "artist_entry": None,
        "song_entry": None,
        "response_label": None,
        "response_frame": None,
        "album_type": None,
        "album_name": None,
        "album_year": None,
        "lyrics": None,
    }
}

# init_gui()


# TODO create 5 checkboxes, one for each attribute plus the K results to show
# TODO if the user enters empty artist/song input