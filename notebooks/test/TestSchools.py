import unittest
import pandas as pd
import numpy as np
from school_data import schools


class LoadDemographicsTestCase(unittest.TestCase):
    def setUp(self):
        df = schools.load_demo_open_data()
        self.assertIsNotNone(df, "failed to load dataframe")
        self.df = df


    def test_load_demographics(self):
        df = self.df
        self.assertIsNotNone(df, "failed to load dataframe")
        num_records = len(df)
        self.assertTrue(num_records in range(8500, 10800), f"Unexpected number of school records found: {num_records}")

    def test_expected_cols(self):
        "Test to make sure that the columns from open data haven't changed"

        a = np.array(self.df.columns)
        b = pd.Index(['dbn', 'school_name', 'year', 'total_enrollment',
            'grade_3k_pk_half_day_full', 'grade_k', 'grade_1', 'grade_2', 'grade_3',
            'grade_4', 'grade_5', 'grade_6', 'grade_7', 'grade_8', 'grade_9',
            'grade_10', 'grade_11', 'grade_12', 'female', 'female_1', 'male',
            'male_1', 'asian', 'asian_1', 'black', 'black_1', 'hispanic',
            'hispanic_1', 'multiple_race_categories', 'multiple_race_categories_1',
            'white', 'white_1', 'students_with_disabilities',
            'students_with_disabilities_1', 'english_language_learners',
            'english_language_learners_1', 'poverty', 'poverty_1',
            'economic_need_index'],
            dtype='object')
        self.assertTrue(np.array_equal(a, b), "Columns from live data don't match development cols")





class CleanDemographicsTestCase(unittest.TestCase):
    def setUp(self):
        df = schools.load_demographics()
        self.df = df


    def test_load_demographics(self):
        df = schools.load_demo_open_data()
        self.assertIsNotNone(df, "failed to load dataframe")

    def test_pct_to_float(self):

        cols = ['female_1',
                'male_1',
                'asian_1',
                'black_1',
                'hispanic_1',
                'multiple_race_categories_1',
                'white_1',
                'students_with_disabilities_1',
                'english_language_learners_1',
                'poverty_1',
                'non_white_1',
                'black_hispanic_1',
                'white_asian_1',
                'non_white_asian_1']
        df = self.df[cols]
        for col in df:
            series = df[col]
            self.assertEqual(series.dtype.type, np.float64, f"Expected {series.name} to contain float")
            high = series.max()
            low = series.min()

            self.assertTrue(high <= 1, f"Found max pct of {high} in {series.name}")
            self.assertTrue(low >= 0, f"Found min pct of {low} in {series.name}")
