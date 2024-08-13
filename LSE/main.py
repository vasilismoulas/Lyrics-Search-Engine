import time
import lucene
# time.sleep(100)
import src.csv_related as csv_related
import src.lyrics_processing as lyr_proc
import src.gui as gui
import src.lucene_engine as lucene_engine
# import src.test as test

def init_lucene_vm():
    try:
        lucene.initVM()
        print("Lucene version:", lucene.VERSION)
        # stemming.stemming()

    except Exception as e:
        print("Error initializing Lucene VM:", e)

def init():

    t1 = time.time()
    csv_related.main()  # beautify the csv files before the text processing

    lyr_proc.repeat_lyrics("lyrics", "lyrics")  # repeat lyrics, remove brackets, stemming
    lyr_proc.tokenize_all_lyrics()
    
    lucene_engine.init_lucene()

    csv_related.delete_column("tokenize", "lyrics", "Unnamed: 0")

    t2 = time.time() - t1
    print(f"It took {t2}secs")

    gui.init_gui()


if __name__ == "__main__":
    init_lucene_vm()
    init()
