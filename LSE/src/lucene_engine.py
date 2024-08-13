import sys
import lucene
from tqdm import tqdm
import time
import csv
from java.nio.file import Files, Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, TextField, IntPoint, FieldType
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import FSDirectory

def init_lucene():
    lyrics_array = ["id", "artist", "song_name", "lyrics"]
    albums_array = ["id", "artist", "album_type", "album_name", "album_year"]

    initial_csv_data("modified", "lyrics", lyrics_array)
    initial_csv_data("original", "lyrics", lyrics_array)
    initial_csv_data("modified", "albums", albums_array)
    initial_csv_data("original", "albums", albums_array)

def initial_csv_data(folder, filename, array):
    analyzer = StandardAnalyzer()

    song_file = f"./data/{folder}/{filename}.csv"

    indexPath = Paths.get(f"./lucene/{folder}/{filename}")
    indexDir = FSDirectory.open(indexPath)

    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(indexDir, config)

    with open(song_file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in tqdm(csv_reader):
            doc = Document()

            for element in array:
                if ("id" or "years") in element:
                    temp = int(row.get(element, 0))
                    doc.add(IntPoint(element, temp))

                else:
                    temp = row.get(element, '')
                    doc.add(TextField(element, temp, Field.Store.YES))

            writer.addDocument(doc)

    writer.close()

def append_to_index(folder, filename, array):
    analyzer = StandardAnalyzer()

    index_dir_path = f"./lucene/{folder}/{filename}"
    index_dir = FSDirectory.open(Paths.get(index_dir_path))

    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)

    writer = IndexWriter(index_dir, config)

    doc = Document()

    for element in array:
        if "id" in element or "years" in element:
            temp = int(array[element])
            doc.add(IntPoint(element, temp))
        else:
            temp = array[element]
            doc.add(TextField(element, temp, Field.Store.YES))

    writer.addDocument(doc)

    writer.close()

def get_length(folder, filename):
    indexPath = Paths.get(f"./lucene/{folder}/{filename}")
    indexDir = FSDirectory.open(indexPath)

    reader = DirectoryReader.open(indexDir)
    length = reader.numDocs()
    reader.close()

    return length

def del_entry(folder, doc_id):  # TODO must re-see
    analyzer = StandardAnalyzer()

    file_1 = f"./lucene/modified/{folder}"
    file_2 = f"./lucene/original/{folder}"
    file_array = [file_1, file_2]

    for i in range(len(file_array)):
        config = IndexWriterConfig(analyzer)
        indexDir = FSDirectory.open(Paths.get(file_array[i]))
        writer = IndexWriter(indexDir, config)

        writer.deleteDocuments(IntPoint.newExactQuery("id", int(doc_id)))
        print(f"doc with an id of {doc_id} was deleted in {file_array[i]}")

        writer.commit()

        writer.close()

    print("Both files deleted successfully")

def search_index(folder, column, query_string, max_results=500):  # to search in the modified folder
    analyzer = StandardAnalyzer()

    indexPath = Paths.get(f"./lucene/modified/{folder}")
    indexDir = FSDirectory.open(indexPath)

    reader = DirectoryReader.open(indexDir)
    searcher = IndexSearcher(reader)

    query = QueryParser(column, analyzer).parse(query_string)

    hits = searcher.search(query, max_results)

    print(f"Found {hits.totalHits.value} document(s) that matched query '{query_string}' in {column}")

    docs_array = []
    scores_array= []
    for hit in hits.scoreDocs:
        # print(hit)
        print(f"Score: {str(hit.score)[:5]}, doc_id: {hit.doc}")
        docs_array.append(hit.doc)
        scores_array.append(hit.score)
        # doc = searcher.doc(hit.doc)
        # print(doc.get("text").encode("utf-8"))
    
    return docs_array, scores_array

# def search_album()

def search_entry(folder, doc_id):  # to retrieve the original data
    indexPath = Paths.get(f"./lucene/original/{folder}")
    indexDir = FSDirectory.open(indexPath)

    reader = DirectoryReader.open(indexDir)
    searcher = IndexSearcher(reader)

    query = IntPoint.newExactQuery("id", doc_id)

    hits = searcher.search(query, 1)

    matching_documents = []
    for hit in hits.scoreDocs:
        doc = searcher.doc(hit.doc)
        matching_documents.append(doc)
    
    return matching_documents
