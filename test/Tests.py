import unittest
import src.FileLoader as fLoader



class Tests(unittest.TestCase):


    def test_timed_points_in_dataframe(self):
        idmapping, dataframes = fLoader.FileLoader().get_dataframes()
        for label in [fLoader.MOVEMENT_POINTS, fLoader.TOUCH_DOWN_POINTS, fLoader.TOUCH_UP_POINTS]:
            for word_id, json_data in idmapping.items():
                dataframe = dataframes[label][word_id]
                for i, point in enumerate(json_data[label]):
                    self.assertTrue(dataframe.get_value(i, fLoader.ID) == word_id)
                    for field in fLoader.TIMED_POINTS:
                        self.assertTrue(point[field] == dataframe.get_value(i, field))

    def test_untimed_points_in_dataframe(self):
        idmapping, dataframes = fLoader.FileLoader().get_dataframes()
        for label in [fLoader.SAMPLED_POINTS]:
            for word_id, json_data in idmapping.items():
                dataframe = dataframes[label][word_id]
                counter = 0
                for current_component, list_of_points in enumerate(json_data[label]):
                    for point in list_of_points:
                        self.assertTrue(dataframe.get_value(counter, fLoader.ID) == word_id)
                        for field in fLoader.POINTS:
                            if field == fLoader.COMPONENT:
                                self.assertTrue(current_component == dataframe.get_value(counter, field))
                            else:
                                self.assertTrue(point[field] == dataframe.get_value(counter, field))
                        counter += 1

if __name__ == '__main__':
    unittest.main()


