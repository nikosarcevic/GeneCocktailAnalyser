import unittest
import os
import pandas as pd
from gene_cocktail_analyser import GeneCocktailAnalyser


class TestGeneCocktailAnalyser(unittest.TestCase):

    def setUp(self):
        # Sample test data files
        self.cocktail_file = 'tests/cocktail_sample.csv'
        self.filters_file = 'tests/filters_sample.csv'

        # Sample data for cocktail and filters
        cocktail_data = {
            'Sequence': ['ABC', 'DEF', 'GHI'],
            'Count': [10, 20, 30],
            'Amino Acid': ['A', 'B', 'C']
        }
        filters_data = {
            'ID': [1, 2, 3],
            'Name': ['FilterA', 'FilterB', 'FilterC'],
            'Filter Sequence': ['ABC', 'DEF', 'XYZ']
        }

        # Write sample data to files
        pd.DataFrame(cocktail_data).to_csv(self.cocktail_file, index=False)
        pd.DataFrame(filters_data).to_csv(self.filters_file, index=False)

        # Instantiate the GeneCocktailAnalyser object
        self.gca = GeneCocktailAnalyser(self.cocktail_file, self.filters_file)

    def tearDown(self):
        # Clean up the sample test data files after the tests
        os.remove(self.cocktail_file)
        os.remove(self.filters_file)

    def test_validate_cocktail_columns(self):
        # For this example, assuming that the default columns are correct
        self.gca.validate_cocktail_columns()

    def test_validate_filters_columns(self):
        self.gca.validate_filters_columns()

    def test_process_data(self):
        self.gca.process_data()


if __name__ == '__main__':
    unittest.main()
