import src.FileLoader as fLoader

a, b = fLoader.FileLoader(fLoader.RES_FOLDER).get_dataframes()
print(a)

