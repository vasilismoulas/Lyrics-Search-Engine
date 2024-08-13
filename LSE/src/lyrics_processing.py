import csv
import os
import string
import re
import numpy as np
from tqdm import tqdm
import pandas as pd
from lucene import JArray_char
from org.tartarus.snowball.ext import EnglishStemmer, SpanishStemmer, FrenchStemmer

def repeat_lyrics(filename, column):  #
    file_1 = f"./data/modified/{filename}.csv"
    file_2 = f"./data/modified/{filename}_stemming.csv"

    string.punctuation

    if not os.path.exists(file_1):  # if file doesn't exist
        print(f"repeat_lyrics: problem while locating the '{file_1}' file")
        return
        
    with open(file_1, 'r') as input_csv, open(file_2, 'w', newline='') as output_csv:
        reader = csv.DictReader(input_csv)
        
        if column not in reader.fieldnames:  # checks if the column exists
            print(f"panda: the '{column}' column couldn't be found in the '{filename}.csv' file")
            os.remove(file_2) # deletes the empty file that was just created
            return
        
        fieldnames = [field for field in reader.fieldnames]  # gets all the column names

        writer = csv.DictWriter(output_csv, fieldnames=fieldnames) 
        writer.writeheader()

        for row in tqdm(reader, desc = "Processing songs", unit = " songs"):
            if column in row:  # for the column "lyrics"
                row[column] = each_song(row[column])  # each row[column] here is the whole lyrics of a song
                writer.writerow(row)

    os.remove(file_1)
    os.rename(file_2, file_1)

def each_song(lyrics_row):  # lyrics of each song
    new_line_code = "\n"
    new_line_array = []  # indexes of the "\n" character plus the length of the row (as the end of the row)
    index = lyrics_row.find(new_line_code)

    while index != -1:
        index = lyrics_row.find(new_line_code, index + 1)
        if index == -1:
            new_line_array.append(len(lyrics_row))
        else:
            new_line_array.append(index)

    before_lines = []
    lyrics_by_line = []

    for i in range(len(new_line_array)):  # breaks the lyrics into lines
        try:
            substring = lyrics_row[new_line_array[i]:new_line_array[i+1]]
            before_lines.append(substring)  # pushes each sentence/line of the lyrics into an array
        except Exception as e:
            # print(e)
            pass

    verse_dict = {
        "times": 1,
        "array": [],
    }

    section_dict = {
        "boolean": False,
        "counter": 0,
        "times": 1,
        "array": [],
    }

    for i in range(len(before_lines)):  # for each line of the lyrics of each song 
        lyrics_line = before_lines[i]

        if lyrics_line == "\n":  # reset the booleans/times
            verse_dict["times"] = 1
            if section_dict["boolean"]:
                section_dict["boolean"] = False
                section_dict["counter"] += 1

        line_regexp = re.compile(r'\[x?(\d+)x?\]')  # TODO [2x]
        line_match = line_regexp.search(lyrics_line)

        verse_regexp = re.compile(r'\[x(\d+):\]')
        verse_match = verse_regexp.search(lyrics_line)

        init_regexp = re.compile(r'\[(\w+?\-?\w+)\s?(\w+)?([0-9])?:\s?(\(?(\w+)\)?|((x(\d)|(\d)x)))?\]')  # when you set the verse, e.g. [Chorus:]
        init_match = init_regexp.search(lyrics_line)

        repeat_regexp = re.compile(r'\[(\w+?\-?\w+)\s?\(?(x(\d)|(\d)x|(\w+?\s?\w+?))?\)?\]')  # when you wanna repeat the verse, e.g. [Chorus 2x]
        repeat_match = repeat_regexp.search(lyrics_line)

        if line_match and not section_dict["boolean"]:  # e.g. [x2]
            temp_array = by_line(lyrics_line, line_match)
            lyrics_by_line.extend(temp_array)

        elif verse_match and not section_dict["boolean"]:  # e.g. [x2:]
            times, lyrics_line = by_verse(lyrics_line, verse_match)
            verse_dict["times"] = times
            pass

        elif init_match and not section_dict["boolean"]:  # e.g. [Chorus:]
            section_name, lyrics_line = init_verse(lyrics_line, init_match)
            if section_name == None: continue
            temp_object = {
                section_name: []
            }
            section_dict["array"].append(temp_object)
            section_dict["boolean"] = True
            
        elif repeat_match and not section_dict["boolean"]:  # e.g. [Chorus]
            lines_of_section = section_repeat(lyrics_line, repeat_match, section_dict["array"])
            if lines_of_section != None: lyrics_by_line.extend(lines_of_section)

        else:
            brackets_regexp = re.compile(r'\[.*\]')
            brackets_match = brackets_regexp.search(lyrics_line)
            if brackets_match: 
                lyrics_line = re.sub(brackets_regexp, '', lyrics_line)

            if section_dict["boolean"]:
                current_dict = section_dict["array"][section_dict["counter"]]
                for key, value in current_dict.items():
                    value.append(lyrics_line)
                    # print(f"Key: {key}, Value: {value}")

            for j in range(verse_dict["times"]):
                lyrics_by_line.append(lyrics_line)

    for i in range(len(lyrics_by_line)):
        lyrics_by_line[i] = remove_punctuation(lyrics_by_line[i]).lower().replace("\n", " ")
        # lyrics_by_line[i] = remove_punctuation(lyrics_by_line[i]).lower().replace(" the ", " ")
        words_array = lyrics_by_line[i].split(" ")
        # words_array = [word for word in words_array if word != ""] TO REMOVE
        # print(words_array)
        if len(words_array) == 0:
            continue
        # temp = stemming(words_array).split()
        # temp.append(" ")
        # print(temp)
        # lyrics_by_line[i] = " ".join(temp)
        # print(lyrics_by_line[i])
        lyrics_by_line[i] = stemming(words_array)
        
    # print(section_dict["array"])
                
    return "".join(lyrics_by_line)

def by_line(line, line_match):  # [xd]
    line_regexp = re.compile(r'\[x?(\d+)x?\]')
    temp_array = []

    times = int(line_match.group(1))
    line = re.sub(line_regexp, '', line)

    for i in range(times):
        temp_array.append(line)

    return temp_array

def by_verse(line, verse_match):  # [xd:]
    verse_regexp = re.compile(r'\[x(\d+):\]')
    times = int(verse_match.group(1))
    line = re.sub(verse_regexp, '', line)

    return times, line

def init_verse(line, section_match):  # [Chorus:]
    section_regexp = re.compile(r'\[(\w+?\-?\w+)\s?(\w+)?([0-9])?:\s?(\(?(\w+)\)?|((x(\d)|(\d)x)))?\]')
    section_name = section_match.group(1)
    section_names = ["Bridge", "Chorus", "Intro", "Sample", "Hook"]  # TODO push each letter of each section name into an array, sort it and compare it
    if not (section_name in section_names):
        section_name = None
    if section_match.group(3):  # [Verse 1:]
        section_name = None

    # TODO [Repeat Chorus 2x:], \[.*\]  * = wildcard

    line = re.sub(section_regexp, '', line)

    return section_name, line

def section_repeat(line, section_repeat_match, array):  # [Chorus]
    section_repeat_regexp = re.compile(r'\[(\w+?\-?\w+)\s?\(?(x(\d)|(\d)x|(\w+?\s?\w+?))?\)?\]')
    section_name = section_repeat_match.group(1)
    repeat_times = None
    if section_repeat_match.group(3):
        repeat_times = int(section_repeat_match.group(3))
    elif section_repeat_match.group(4):
        repeat_times = int(section_repeat_match.group(4))
    else:
        repeat_times = 1
    
    line = re.sub(section_repeat_regexp, '', line)
    lines_of_section = []

    for obj in array:
        if section_name in obj:
            for i in range(repeat_times):
                lines_of_section.extend(obj[section_name])
                # print(f"Found object with key '{section_name}', values: {lines_of_section}")

    return lines_of_section

def remove_punctuation(line):
    punctuation = string.punctuation.replace("\\", "")

    no_punctuation = "".join([i for i in line if i not in punctuation])
    return no_punctuation

def stemming(words_array):
    en_stemmer = EnglishStemmer()
    sp_stemmer = SpanishStemmer()
    fr_stemmer = FrenchStemmer()

    if len(words_array) == 0:
        return words_array
    stemmed_words = [english_stemming(en_stemmer, word) for word in words_array]

    return " ".join(stemmed_words)

def english_stemming(en_stemmer, word):
    en_stemmer = EnglishStemmer()
    
    en_stemmer.setCurrent(JArray_char(word), len(word))
    en_stemmer.stem()
    result = en_stemmer.getCurrentBuffer()
    l = en_stemmer.getCurrentBufferLength()
    return ''.join(result)[0:l]

def tokenize_all_lyrics():  # not used
    data = pd.read_csv("./data/modified/lyrics.csv")

    all_lyrics = " ".join(np.array(data.lyrics)).split()

    unique, counts = np.unique(all_lyrics, return_counts=True)
    weights = np.log(len(unique) / counts)
    global_vars["unique"] = unique
    global_vars["counts"] = counts

    idx = counts.argsort()[::-1]
    unique, counts, weights = unique[idx], counts[idx], weights[idx]

    token_dict = dict(zip(unique, np.arange(1, len(unique) + 1)))
    global_vars["token_dict"] = token_dict

    tqdm.pandas()
    data['lyrics'] = data['lyrics'].progress_apply(lambda lyrics: [token_dict[word] for word in lyrics.split()])

    data.to_csv("./data/tokenize/lyrics.csv")

    import src.lucene_engine as luc_engine

def tokenize_lyrics(text):  # not used
    from src.lyrics_processing import global_vars as lyr_global

    temp = text.split()
    array = []

    for word in temp:
        array.append(lyr_global["token_dict"][word])  # append the number which is related with the word
        # array.append(word)
        # print(f"{word}={lyr_global["token_dict"][word]}")
        
    return array


def data_as_tuple(folder, filename):
    file_1 = f'./data/{folder}/{filename}.csv'
    df = pd.read_csv(file_1)

    tuple_array = [tuple(row) for row in df.values]
    global_vars["tuple_array"] = tuple_array

    # for i, tuple_entry in enumerate(tuple_array[3:4]):
    #     print(f'Tuple {i + 1}: {tuple_entry}')


global_vars = {
    "unique": None,
    "counts": None,
    "token_dict": None,
    "tuple_array": None,
}
