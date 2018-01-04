import unittest
import src.DataManager as dm
import src.FeatureManager as fm
import sys


class Tests(unittest.TestCase):
    f = dm.JsonLoader()

    series, A, dataframes = f.get_dataframes()

    idword_dataword_mapping = f.idword_dataword_mapping
    iduser_datauser_mapping = f.iduser_datauser_mapping
    idword_iduser_mapping = f.idword_iduser_mapping

    def test_timed_points_in_dataframe(self):
        for label in [dm.MOVEMENT_POINTS, dm.TOUCH_DOWN_POINTS, dm.TOUCH_UP_POINTS]:
            dataframe = self.dataframes[label]
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                for point in json_data[label]:
                    self.assertTrue(dataframe.at[counter, dm.WORD_ID] == word_id)
                    for field in dm.TIMED_POINTS:
                        self.assertTrue(point[field] == dataframe.at[counter, field])
                    counter += 1
            print("Checked {} {}".format(counter, label))

    def test_untimed_points_in_dataframe(self):
        for label in [dm.SAMPLED_POINTS]:
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                dataframe = self.dataframes[label]
                for current_component, list_of_points in enumerate(json_data[label]):
                    for point in list_of_points:
                        self.assertTrue(dataframe.at[counter, dm.WORD_ID] == word_id)
                        for field in dm.POINTS:
                            if field == dm.COMPONENT:
                                self.assertTrue(current_component == dataframe.at[counter, field])
                            else:
                                self.assertTrue(point[field] == dataframe.at[counter, field])
                        counter += 1
            print("Checked {} {}".format(counter, label))

    def test_dataframes_lenght(self):
        aspected_number_of_words = sum(x[dm.TOTAL_WORD_NUMBER] for x in self.iduser_datauser_mapping.values())
        number_word = len(self.f._jsons_data)
        mov_total_number = sum(len(word[dm.MOVEMENT_POINTS]) for word in self.f._jsons_data)
        up_total_number = sum(len(word[dm.TOUCH_UP_POINTS]) for word in self.f._jsons_data)
        down_total_number = sum(len(word[dm.TOUCH_DOWN_POINTS]) for word in self.f._jsons_data)
        sampled_total_number = sum(len(component) for word in self.f._jsons_data
                                   for component in word[dm.SAMPLED_POINTS])
        string = "Asp word number: {}\nWord number: {}\nMovs number: {}\n" \
                 "Ups number: {}\nDowns number: {}\nSampled number: {}".format(aspected_number_of_words, number_word,
                                                                               mov_total_number, up_total_number,
                                                                               down_total_number, sampled_total_number)
        print(string)

        self.assertTrue(aspected_number_of_words == number_word ==
                        len(self.idword_dataword_mapping) == len(self.idword_iduser_mapping))

        self.assertTrue(up_total_number == down_total_number)
        self.assertTrue(mov_total_number == len(self.dataframes[dm.MOVEMENT_POINTS]))
        self.assertTrue(up_total_number == len(self.dataframes[dm.TOUCH_UP_POINTS]))
        self.assertTrue(down_total_number == len(self.dataframes[dm.TOUCH_DOWN_POINTS]))
        self.assertTrue(sampled_total_number == len(self.dataframes[dm.SAMPLED_POINTS]))

        self.assertTrue(set(self.iduser_datauser_mapping.keys()) == set(self.idword_iduser_mapping.values()))
        self.assertTrue(set(self.idword_iduser_mapping.keys()) == set(self.idword_dataword_mapping.keys()))

    def test_dataframes_pickle_saving(self):
        dm.JsonLoader().save_dataframes()
        for read, gen in zip(fm.FeaturesExtractor._read_pickles(), fm.FeaturesExtractor._regen_dataframes()):
            self.assertTrue(read.equals(gen))


if __name__ == '__main__':
    unittest.main()
