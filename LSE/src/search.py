import string
import re
import numpy as np
import src.lyrics_processing as lyr_proc
import src.lucene_engine as luc_engine
from lucene import JArray_char
from org.tartarus.snowball.ext import EnglishStemmer, SpanishStemmer, FrenchStemmer

def clean_search_string(text):
    en_stemmer = EnglishStemmer()
    text = lyr_proc.remove_punctuation(text).lower()

    words_array = text.split()
    stemmed_words = [lyr_proc.english_stemming(en_stemmer, word) for word in words_array]
    text = " ".join(stemmed_words)

    return text

# def search

def search_string_func(normal_text, text, active_settings):  # 

    artist = active_settings[0]
    song_name = active_settings[1]
    album_type = active_settings[2]
    album_name = active_settings[3]
    album_year = active_settings[4]
    lyrics = active_settings[5]
    top_k = int(active_settings[6])
    score = 0
    lyr_docs_array = []
    lyr_scores_array = []
    alb_docs_array = []
    alb_scores_array = []

    if artist:
        # docs_array, scores_array = luc_engine.search_index("albums", "artist", normal_text, top_k)
        # alb_docs_array.extend(docs_array)
        # alb_scores_array.extend(scores_array)

        docs_array, scores_array = luc_engine.search_index("lyrics", "artist", normal_text, top_k)
        lyr_docs_array.extend(docs_array)
        lyr_scores_array.extend(scores_array)

    if song_name:
        docs_array, scores_array = luc_engine.search_index("lyrics", "song_name", normal_text, top_k)
        lyr_docs_array.extend(docs_array)
        lyr_scores_array.extend(scores_array)
        
    if lyrics:
        docs_array, scores_array = luc_engine.search_index("lyrics", "lyrics", text, top_k)
        lyr_docs_array.extend(docs_array)
        lyr_scores_array.extend(scores_array)

    temp_lyc_dict = {}
    for i in range(len(lyr_docs_array)):
        temp_lyc_dict[lyr_docs_array[i]] = lyr_scores_array[i]
    
    lyc_dict = dict(sorted(temp_lyc_dict.items(), key = lambda item: item[1], reverse=True))

    lyr_docs_array.clear()
    lyr_scores_array.clear()

    lyr_docs_array = list(lyc_dict.keys())
    lyr_scores_array = list(lyc_dict.values())

    # print(lyr_docs_array)

    lyr_docs_array = get_unmodified_lyrics(lyr_docs_array, "lyrics")  # this is an array of all the matches/songs
    # print("LYR_DOCS_ARRAY", lyr_docs_array)
    all_song_data = separate_lyrics(lyr_docs_array)

    for i in range(len(all_song_data)):
        try:
            all_song_data[i].append(lyr_scores_array[i])
        except Exception as e:
            pass
    
    return all_song_data  # array of arrays


# for lyrics:
def get_unmodified_lyrics(docs_array, case):  # to get the unmodified data from both lyrics/albums
    temp_array = []
    for doc in docs_array:
        temp_array.append(luc_engine.search_entry("lyrics", doc))

    for element in temp_array:
        print(element)
        pass
    
    return temp_array

def separate_lyrics(array):
    all_song_data = []

    for song in array:
        string = splice_lyr_string(song)
        all_song_data.append(string)

    return all_song_data

def splice_lyr_string(string):
    try:
        string = f"{string[0]}"  # convert the json into a string?
    except Exception as e:
        print("Exception occurred:", e)
        print("TYPE STRING:", type(string), string)
        
        if string:
            print("TYPE STRING[0]:", type(string[0]))
        else:
            print("The list is empty")
            return


    artist_start = string.index("artist") + len("artist") + 1
    artist_end = string[artist_start:].index(">")
    artist = string[artist_start:artist_start + artist_end]

    song_name_start = string.index("song_name") + len("song_name") + 1
    song_name_end = string[song_name_start:].index(">")
    song_name =string[song_name_start:song_name_start + song_name_end]

    lyrics_start = string.index("lyrics") + len("lyrics") + 1
    lyrics_end = string[lyrics_start:].index(">")
    lyrics = string[lyrics_start:lyrics_start + lyrics_end]

    song_data = [artist, song_name, lyrics]

    return song_data

def scores_array_func(scores_array):
    pass



def clean_search_stringg(text):
    from src.lyrics_processing import global_vars as lyr_global
    lyr_proc.data_as_tuple("modified", "lyrics")  # ? unnecessary?

    import src.lucene_engine as luc_engine
    luc_engine.search_index(text, 5)






    # import Miscellaneous.one as one
    # tuple_array = lyr_global["tuple_array"]
    # print(tuple_array)



    # * token_text = []  TO UNCOMMENT

    # for word in text.split():
    #     token_text.append(word)
    #     try:
    #         token = lyr_global["token_dict"][word]
    #         token_text.append(str(token))            
    #     except Exception as e:
    #         print(f"The word '{word}' does not exist in all of the songs")
    #         token_text.append('-')

    # numbers = " ".join(token_text)
    # print(numbers)

    # for i, (key, value) in enumerate(lyr_global["token_dict"].items()):
    #     print(f"{key}: {value}")

    #     if np.any(value == 9):
    #         break

    # import Miscellaneous.two as one



# for albums:
def search_artist_func(artist):
    alb_docs_array = []
    alb_scores_array = []

    docs_array, scores_array = luc_engine.search_index("albums", "artist", artist, 50)
    alb_docs_array.extend(docs_array)
    alb_scores_array.extend(scores_array)

    # print(docs_array)

    alb_doc_array = get_albums_from_artist(docs_array)
    all_albums_data = separate_albums(alb_doc_array)

    # print(all_albums_data)

    return all_albums_data

    # docs_array, scores_array = luc_engine.search_index("albums", "album_type", normal_text, top_k)

def get_albums_from_artist(docs_array):
    temp_array = []
    for album in docs_array:
        temp_array.append(luc_engine.search_entry("albums", album))

    for element in temp_array:
        # print(element)
        pass

    return temp_array

def separate_albums(array):
    all_song_data = []
    for album in array:
        album_data = splice_alb_string(album)

        if album_data != None:
            all_song_data.append(album_data)

    return all_song_data

def splice_alb_string(string):
    string = str(string)
    # string = str(string[0])

    artist_start = string.index("artist") + len("artist") + 1
    artist_end = string[artist_start:].index(">")      
    album_type = string[artist_start:artist_start + artist_end]

    album_type_start = string.index("album_type") + len("album_type") + 1
    album_type_end = string[album_type_start:].index(">")
    album_type = string[album_type_start:album_type_start + album_type_end]

    album_name_start = string.index("album_name") + len("album_name") + 1
    album_name_end = string[album_name_start:].index(">")
    album_name = string[album_name_start:album_name_start + album_name_end]

    album_year_start = string.index("album_year") + len("album_year") + 1
    album_year_end = string[album_year_start:].index(">")
    album_year = string[album_year_start:album_year_start + album_year_end]

    if album_year != "-1":
        album_data = [album_type, album_name, album_year]
    else:
        album_data = None

    return album_data

