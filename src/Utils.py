import re
import pandas

import src.Chronometer as Chronometer
from src.Constants import *

def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    return [atoi(c) for c in re.split('(\d+)', text)]


def merge_dicts(dict1: dict, dict2: dict):
    assert set(dict1.keys()) == set(dict2.keys())
    for key in dict1.keys():
        assert isinstance(dict1[key], list)
        assert isinstance(dict2[key], list)
        dict1[key] += dict2[key]
    return dict1


def flat_nested_dict(dict_to_flat: dict):
    d = {}
    for k, v in dict_to_flat.items():
        if not isinstance(v, dict):
            d[k] = v
        else:
            d.update(flat_nested_dict(v))
    return d


def make_lists_values(d: dict):
    for k, v in d.items():
        if not isinstance(v, list):
            d[k] = [v]
    return d


def add_column(dataframe, column):
    if WORD_ID in dataframe.columns:
        return dataframe.join(column, on=WORD_ID)
    else:
        return dataframe.join(column)


def dataframe_to_csv(dataframe, dataset_name, path):
    mkdir(BUILD_CSV_FOLDER(dataset_name))
    dataframe.to_csv(path, decimal=",", sep=";")


def save_dataframes(dataset_name, dataframes_dict, dataframe_type, message, to_csv, frames_to_add_column, csv_column):
    mkdir(BUILD_GENERATED_FOLDER(dataset_name))
    chrono = Chronometer.Chrono(message)
    for label, v in dataframes_dict.items():
        v.to_pickle(PATHS_FUN[dataframe_type][PICKLE_EXTENSION](dataset_name, label))
        if to_csv:
            if frames_to_add_column and csv_column is not None and label in frames_to_add_column:
                v = add_column(v, csv_column)
            dataframe_to_csv(v, dataset_name, PATHS_FUN[dataframe_type][CSV_EXTENSION](dataset_name, label))
    chrono.end()


def init_dict(labels, length):
    return {x: [None] * length for x in labels}

def mkdir(path):
    if not os.path.isdir(path):
        os.makedirs(path)

def get_infos(wordid_userid, user_data, wordid):
    # join con l'user id_data
    a = pandas.DataFrame(wordid_userid).join(user_data, on=USER_ID)

    # consideriamo l'user che ci interessa
    a = a[a[USER_ID] == wordid_userid[wordid]]

    # contiamo quante parole ha già fatto
    word_number = len(a.loc[: wordid]) - 1

    # prendiamo il resto dei dati
    row = a.loc[wordid].to_dict()
    row[WORD_NUMBER] = word_number
    return row

def get_wordidfrom_wordnumber_name_surname(wordid_userid, user_data, name, surname, handwriting, word_number):
    # join con l'user id_data
    a = pandas.DataFrame(wordid_userid).join(user_data[[NAME, SURNAME, HANDWRITING]], on=USER_ID)

    # consideriamo l'user e lo stile che ci interessa e prendiamo l'index corrispondente a word_number
    b = (a.loc[(a[NAME] ==  name.lower()) & (a[SURNAME] == surname.lower()) & (a[HANDWRITING] == handwriting)])
    assert not b.empty, "Controlla i parametri di ricerca, non è stata trovata nessuna entry"
    return b.index[word_number]


def prettify_name(s):
    return " ".join(s.split("_")).title()

