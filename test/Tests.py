import unittest
import src.DataManager as fLoader
import sys


class Tests(unittest.TestCase):
    f = fLoader.JsonLoader()

    series, A, dataframes = f.get_dataframes()

    idword_dataword_mapping = f.idword_dataword_mapping
    iduser_datauser_mapping = f.iduser_datauser_mapping
    idword_iduser_mapping = f.idword_iduser_mapping

    def test_timed_points_in_dataframe(self):
        for label in [fLoader.MOVEMENT_POINTS, fLoader.TOUCH_DOWN_POINTS, fLoader.TOUCH_UP_POINTS]:
            dataframe = self.dataframes[label]
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                for point in json_data[label]:
                    self.assertTrue(dataframe.at[counter, fLoader.WORD_ID] == word_id)
                    for field in fLoader.TIMED_POINTS:
                        self.assertTrue(point[field] == dataframe.at[counter, field])
                    counter += 1
            print("Checked {} {}".format(counter, label))

    def test_untimed_points_in_dataframe(self):
        for label in [fLoader.SAMPLED_POINTS]:
            counter = 0
            for word_id, json_data in self.idword_dataword_mapping.items():
                dataframe = self.dataframes[label]
                for current_component, list_of_points in enumerate(json_data[label]):
                    for point in list_of_points:
                        self.assertTrue(dataframe.at[counter, fLoader.WORD_ID] == word_id)
                        for field in fLoader.POINTS:
                            if field == fLoader.COMPONENT:
                                self.assertTrue(current_component == dataframe.at[counter, field])
                            else:
                                self.assertTrue(point[field] == dataframe.at[counter, field])
                        counter += 1
            print("Checked {} {}".format(counter, label))

    def test_lenght(self):
        aspected_number_of_words = sum(x[fLoader.TOTAL_WORD_NUMBER] for x in self.iduser_datauser_mapping.values())
        number_word = len(self.f._jsons_data)
        mov_total_number = sum(len(word[fLoader.MOVEMENT_POINTS]) for word in self.f._jsons_data)
        up_total_number = sum(len(word[fLoader.TOUCH_UP_POINTS]) for word in self.f._jsons_data)
        down_total_number = sum(len(word[fLoader.TOUCH_DOWN_POINTS]) for word in self.f._jsons_data)
        sampled_total_number = sum(len(component) for word in self.f._jsons_data
                                   for component in word[fLoader.SAMPLED_POINTS])
        string = "Asp word number: {}\nWord number: {}\nMovs number: {}\n" \
                 "Ups number: {}\nDowns number: {}\nSampled number: {}".format(aspected_number_of_words, number_word,
                                                                               mov_total_number, up_total_number,
                                                                               down_total_number, sampled_total_number)
        print(string)

        self.assertTrue(aspected_number_of_words == number_word ==
                        len(self.idword_dataword_mapping) == len(self.idword_iduser_mapping))

        self.assertTrue(up_total_number == down_total_number)
        self.assertTrue(mov_total_number == len(self.dataframes[fLoader.MOVEMENT_POINTS]))
        self.assertTrue(up_total_number == len(self.dataframes[fLoader.TOUCH_UP_POINTS]))
        self.assertTrue(down_total_number == len(self.dataframes[fLoader.TOUCH_DOWN_POINTS]))
        self.assertTrue(sampled_total_number == len(self.dataframes[fLoader.SAMPLED_POINTS]))

        self.assertTrue(set(self.iduser_datauser_mapping.keys()) == set(self.idword_iduser_mapping.values()))
        self.assertTrue(set(self.idword_iduser_mapping.keys()) == set(self.idword_dataword_mapping.keys()))


if __name__ == '__main__':
    unittest.main()
