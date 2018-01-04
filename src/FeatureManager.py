import src.DataManager as fLoader
from tsfresh import extract_features
from tsfresh import select_features
from tsfresh.utilities.dataframe_functions import impute
import pandas

f = fLoader.JsonLoader(fLoader.BIOTOUCH_FOLDER)
a, b = f._initialize_dataframes()
print(a)
print(b[fLoader.TOUCH_UP_POINTS])
# print(a)

# extracted_features = extract_features(b[fLoader.TOUCH_UP_POINTS], column_id=fLoader.WORD_ID, column_sort="time")
#
# # print(extracted_features)
#
# impute(extracted_features)
# features_filtered = select_features(extracted_features, a)
# print(features_filtered)
# print(len(features_filtered))
# d= features_filtered.join(pandas.DataFrame(a).set_index(fLoader.WORD_ID), on=fLoader.WORD_ID)
#
# d.to_csv("../res/touchup.csv", sep='\t', encoding='utf-8')
