from itertools import combinations
import matplotlib.pyplot as plt
import natsort
import numpy as np
import os
import pandas as pd
import seaborn as sns
from tabulate import tabulate
import warnings


class GeneCocktailAnalyser:
    def __init__(self, cocktail_file, filters_file, cocktail_columns=None, filters_columns=None):
        """
        Initialize the GeneCocktailAnalyser object with the given dataset name, cocktail file, and filters file.
        """
        self.cocktail = pd.read_csv(cocktail_file)
        self.filters = pd.read_csv(filters_file)
        self.dataset_name = os.path.splitext(os.path.basename(cocktail_file))[0].split('_')[0]  # Extract dataset name from file name
        self.results = {}
        self.multiple_filter_ids = {}

        # Set default column names if not provided
        self.cocktail_columns = cocktail_columns if cocktail_columns else ["Sequence",
                                                                           "Count",
                                                                           "Amino Acid"]
        self.filters_columns = filters_columns if filters_columns else ["ID",
                                                                        "Name",
                                                                        "Filter Sequence",
                                                                        "Mutation Codon"]

        # Check the column names in the provided datasets
        self.validate_cocktail_columns()
        self.validate_filters_columns()

    def validate_cocktail_columns(self):
        """
        Check if the columns in the cocktail DataFrame match the expected columns.
        """
        if not all(col in self.cocktail.columns for col in self.cocktail_columns) or len(self.cocktail.columns) != len(self.cocktail_columns):
            warnings.warn(
                f"Cocktail DataFrame columns should be {self.cocktail_columns}. Found {list(self.cocktail.columns)} instead.")

    def validate_filters_columns(self):
        """
        Check if the columns in the filters DataFrame match the expected columns.
        """
        expected_columns = self.filters_columns.copy()
        if "Mutation Codon" not in self.filters.columns:
            expected_columns.remove("Mutation Codon")
        if not all(col in self.filters.columns for col in expected_columns) or len(self.filters.columns) != len(expected_columns):
            warnings.warn(
                f"Filters DataFrame columns should be {expected_columns}. Found {list(self.filters.columns)} instead.")

        # Check for empty rows in filters DataFrame
        empty_rows = self.filters[self.filters.isnull().all(axis=1)].index.tolist()
        if empty_rows:
            warnings.warn(
                f"Empty rows found in Filters DataFrame at indices: {empty_rows}. These rows will be skipped.")
            self.filters.drop(empty_rows, inplace=True)

    def save_to_file(self, data, headers, filename):
        """
        Save the data to a file with the given headers and filename.
        """
        os.makedirs("results", exist_ok=True)  # Ensure the results directory exists
        with open(filename, 'w') as f:
            f.write(tabulate(data, headers=headers))

    def process_data(self, count_multiple_hits=True):
        """
        Process the data to analyze gene cocktail samples and filter matches.
        """
        # Using column names
        sequence_col = self.cocktail_columns[0]
        filter_sequence_col = self.filters_columns[2]
        id_col = self.filters_columns[0]

        # Handling NaNs
        nan_rows = self.cocktail[self.cocktail[sequence_col].isna()].index.tolist()
        self.results["nan_rows"] = len(nan_rows)
        self.cocktail.dropna(subset=[sequence_col], inplace=True)

        # Handling empty rows in filters dataset and sorting
        self.filters.dropna(subset=[filter_sequence_col], inplace=True)
        self.filters = self.filters.sort_values(by=id_col)

        # Initialize variables for tracking filter matches
        matches_count = {}
        sequences_with_match = set()
        multiple_hits = {row[id_col]: 0 for _, row in self.filters.iterrows()}

        for _, row in self.filters.iterrows():
            matches_count[row[id_col]] = 0

        for _, row in self.cocktail.iterrows():
            sequence = row[sequence_col]
            filter_occurrences = []

            for _, filter_row in self.filters.iterrows():
                filter_seq = filter_row[filter_sequence_col]
                occurrences = sequence.count(filter_seq)

                if occurrences:
                    filter_occurrences.append((filter_row[id_col], occurrences))

                    # Count the total number of occurrences of this filter sequence in the sample sequence
                    matches_count[filter_row[id_col]] += occurrences
                    sequences_with_match.add(row[sequence_col])

                    # Track the occurrences hitting more than once
                    if occurrences > 1:
                        # Track the occurrences hitting more than once by filter ID
                        multiple_hits[filter_row[id_col]] += occurrences

            # Check if there are any filters that appeared more than once, or if there's more than one filter in the sequence
            total_filters = sum([1 for _, count in filter_occurrences if count > 0])
            multiple_occurrences = any([count > 1 for _, count in filter_occurrences])

            if total_filters > 1 or multiple_occurrences:
                self.multiple_filter_ids[self.cocktail.index.get_loc(row.name)] = [filter_id for filter_id, occurrences
                                                                                   in filter_occurrences if
                                                                                   occurrences > 0]

        # Store the results of data processing
        self.results["total_samples"] = len(self.cocktail)
        self.results["filter_matches"] = matches_count
        self.results["samples_with_match"] = len(sequences_with_match)
        self.results["no_filter_match"] = self.results["total_samples"] - len(sequences_with_match)
        self.results["two_or_more_matches"] = len([count for count in matches_count.values() if count >= 2])

        if count_multiple_hits:
            self.results["multiple_hits"] = multiple_hits

    def display_results(self):
        """
        Display the processed results in a formatted table and save to a TXT file.
        """
        headers = ["Section", "Description", "Value", "Fraction"]
        report_data = []

        # 1. Summary Section
        total_samples = self.results['total_samples']
        samples_with_match = total_samples - self.results['no_filter_match']
        samples_with_multiple_matches = self.results['two_or_more_matches']

        report_data.extend([
            ("Summary", "Total Cocktail Samples", total_samples, "-"),
            ("Summary", "Cocktail samples (after removing NaNs)", total_samples, "100%"),
            ("Summary", "Samples with no filter match", self.results['no_filter_match'],
             "{:.2f}%".format((self.results['no_filter_match'] / total_samples) * 100)),
            ("Summary", "Samples with one filter match", samples_with_match,
             "{:.2f}%".format((samples_with_match / total_samples) * 100)),
            ("Summary", "Samples with two or more filter matches", samples_with_multiple_matches,
             "{:.2f}%".format((samples_with_multiple_matches / total_samples) * 100))
        ])

        report_data.append(("", "", "", ""))  # Add an empty row for spacing
        report_data.append(("Category", "Description: ID | Mutation | Mutation Codon", "Value", "Fraction"))
        # Compute the max lengths based on all the data so far, including headers
        columns = list(zip(*report_data))
        current_max_lengths = [max(max(len(str(item)) for item in column), len(header)) for column, header in
                               zip(columns, headers)]
        separator = tuple('-' * length for length in current_max_lengths)
        report_data.append(separator)

        # 2. Filter Match Section
        sorted_filter_matches = natsort.natsorted(self.results["filter_matches"].items())
        total_filter_matches = sum(count for ref, count in sorted_filter_matches)
        filter_match_data = []
        for ref, count in sorted_filter_matches:
            filter_row = self.filters[self.filters[self.filters_columns[0]] == ref].iloc[0]
            description = f"{ref} | {filter_row['Name']}"
            if "Mutation Codon" in self.filters.columns and pd.notnull(filter_row["Mutation Codon"]):
                description += f" | {filter_row['Mutation Codon']}"
            filter_match_data.append(("Filter Match", description, count, "{:.2f}%".format(
                (count / total_samples) * 100) if total_samples != 0 else "0.00%", total_filter_matches))

        report_data.extend(filter_match_data)
        report_data.append(("Total Filter Matches", "", total_filter_matches, "", ""))  # Add total sum row
        report_data.append(("", "", "", "", ""))  # Add an empty row as a separator

        # 3. Sequences with Multiple Filter IDs Section
        sorted_multiple_filter_ids = natsort.natsorted(self.multiple_filter_ids.items())
        multiple_filter_ids_data = []

        for idx, filter_ids in sorted_multiple_filter_ids:
            if len(filter_ids) > 1:
                description_list = []
                for filter_id in filter_ids:
                    filter_row = self.filters[self.filters[self.filters_columns[0]] == filter_id].iloc[0]
                    description_part = f"{filter_id} | {filter_row['Name']}"
                    if "Mutation Codon" in self.filters.columns and pd.notnull(filter_row["Mutation Codon"]):
                        description_part += f" | {filter_row['Mutation Codon']}"
                    description_list.append(description_part)
                description = ', '.join(description_list)

                multiple_filter_ids_data.append(
                    ("Multiple Filter Matches per Sequence", description, f"index: {idx}", "-", ""))

        report_data.extend(multiple_filter_ids_data)

        # Print the formatted table
        print(f"Unified Gene Cocktail Report: {self.dataset_name}\n")
        max_lengths = [max(len(str(item)) for item in column) for column in zip(*report_data)]

        print(" | ".join(format(header, f"{length}s") for header, length in zip(headers, max_lengths)))
        print("-" * sum(max_lengths) + "-" * (len(max_lengths) - 1) * 3)
        for row in report_data:
            print(" | ".join(format(str(item), f"{length}s") for item, length in zip(row, max_lengths)))

        # Saving to TXT file
        consolidated_filename = f"results/{self.dataset_name}_consolidated_report.txt"
        self.save_to_file(report_data, headers, consolidated_filename)

    def plot_visualizations(self):
        self.plot_summary_data()
        self.plot_frequency_of_matches()
        self.plot_heatmap()

    def plot_summary_data(self):
        total_samples = self.results['total_samples']
        samples_with_match = total_samples - self.results['no_filter_match']
        samples_with_multiple_matches = self.results['two_or_more_matches']

        # Data for donut chart
        sizes = [samples_with_match, self.results['no_filter_match'], samples_with_multiple_matches]
        labels = ['With Matches', 'Without Matches', 'With Multiple Matches']
        colors = sns.color_palette("viridis", len(sizes))

        # Plotting
        plt.figure(figsize=(8, 8))
        wedges, texts, autotexts = plt.pie(sizes, labels=None, colors=colors, startangle=90,
                                           wedgeprops={'linewidth': 7, 'edgecolor': 'white'},
                                           autopct=lambda p: f'{p:.1f}%')  # Display percentages

        for text, label, color in zip(texts, labels, colors):
            text.set_text(label)  # Set label text
            text.set_color(color)  # Set label text color to match wedge colors
            text.set_fontsize(15)  # Adjust font size of labels

        for autotext, color in zip(autotexts, colors):
            autotext.set_color(color)  # Set percentage text color to match wedge colors
            autotext.set_fontsize(12)  # Adjust font size of percentages

        plt.gca().add_artist(
            plt.Circle((0, 0), 0.70, color='white'))  # Draw a white circle at the center to create the donut hole

        plt.title(f'{self.dataset_name} Summary Chart')
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.tight_layout()

        # Save donut chart
        donut_chart_filename = f"results/plots/{self.dataset_name}_summary_chart"
        plt.savefig(donut_chart_filename + ".pdf", dpi=300)
        plt.savefig(donut_chart_filename + ".png", dpi=300)
        plt.show()

    def plot_frequency_of_matches(self, include_codons=False):
        # Getting filter matches and sorting them by count
        sorted_filter_matches = natsort.natsorted(self.results["filter_matches"].items(), key=lambda x: x[1],
                                                  reverse=True)
        labels = [str(ref) for ref, _ in sorted_filter_matches]
        values = [count for _, count in sorted_filter_matches]

        # Check if the "Mutation Codon" column exists
        id_col = self.filters_columns[self.filters_columns.index("ID")]
        mutation_codon_col = "Mutation Codon"

        # Create sorted filter dataframe
        sorted_filters_df = self.filters.set_index(id_col).loc[labels].reset_index()

        has_mutation_codon = mutation_codon_col in self.filters.columns
        mutation_codons = sorted_filters_df[mutation_codon_col] if has_mutation_codon else []

        # Plotting
        plt.figure(figsize=(10, 7))  # Adjust the figure size as needed
        bars = plt.bar(labels, values, color=sns.color_palette("viridis", len(labels)), alpha=0.7)

        if has_mutation_codon:
            # Calculate dynamic y-axis limit
            max_value = max(values)
            y_limit = max_value + max_value * 0.1  # Increase the y-axis limit by 10% of the maximum value

            # Annotate each bar with mutation codons
            for bar, codon in zip(bars, mutation_codons):
                annotation_padding = max_value * 0.02  # 2% of max value
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = bar.get_height() + annotation_padding
                ha = 'center'
                va = 'bottom'
                plt.text(x_pos, y_pos, codon, ha=ha, va=va, fontsize=15)

            plt.ylim(0, y_limit)

        plt.xlabel('Filters', fontsize=17, labelpad=10)
        plt.ylabel('Number of Matches', fontsize=17)
        plt.title(f'Frequency of Filter Matches for {self.dataset_name}', fontsize=20)
        plt.xticks(rotation=45, ha='right', fontsize=12)  # Rotate x-axis labels at 45 degrees
        plt.yticks(fontsize=12)
        # Set the y-axis tick parameters to point inwards and remove x-axis ticks
        plt.gca().tick_params(axis='y', direction='in', which='both', length=4)
        plt.gca().tick_params(axis='x', which='both', bottom=False)  # This line removes the x-axis ticks

        plt.tight_layout()
        plt.grid(axis='y', linestyle='--', alpha=0.6)

        # Save histogram plot
        histogram_filename = f"results/plots/{self.dataset_name}_histogram"
        plt.savefig(histogram_filename + ".png", dpi=300)
        plt.savefig(histogram_filename + ".pdf", dpi=300)

        plt.grid(False)  # Disable grids
        plt.show()

    def plot_heatmap(self):
        """
        Generate a heatmap for samples with multiple filter matches.
        """
        # Extract multiple filter IDs from the instance variable
        multiple_filter_ids = self.multiple_filter_ids

        # Create a set to store all unique filters
        all_filters = set()
        for filters in multiple_filter_ids.values():
            all_filters.update(filters)
        all_filters = sorted(list(all_filters))

        # Create an empty matrix to store co-occurrences
        matrix = np.zeros((len(all_filters), len(all_filters)))

        # Compute co-occurrences
        for filters in multiple_filter_ids.values():
            n = len(filters)
            for i in range(n):
                for j in range(i + 1, n):  # This will ensure that we only get the unique pairs
                    idx_i = all_filters.index(filters[i])
                    idx_j = all_filters.index(filters[j])
                    matrix[idx_i][idx_j] += 1
                    matrix[idx_j][idx_i] += 1  # the matrix is symmetric

        # Step 1: Create a mask for the entire matrix
        mask = np.zeros_like(matrix, dtype=bool)

        # Step 2: Set the upper triangle (including the diagonal) in the mask to True
        mask[np.triu_indices_from(mask, k=1)] = True  # k=1 excludes the diagonal from the mask

        # Plotting the heatmap with the adjusted mask
        plt.figure(figsize=(10, 8))
        heatmap = sns.heatmap(matrix, annot=True, cmap="viridis", xticklabels=all_filters,
                              yticklabels=all_filters, mask=mask,  # Use the adjusted mask
                              cbar_kws={'label': 'Co-occurrence count'})
        cbar = heatmap.collections[0].colorbar  # Get the colorbar instance
        cbar.set_label('Co-occurrence count', fontsize=15)  # Set colorbar label font size
        heatmap.set_title("Filter Co-occurrences in Samples with Multiple Matches", fontsize=15)
        heatmap.set_xlabel("Filters", fontsize=15)
        heatmap.set_ylabel("Filters", fontsize=15)

        # Save heatmap plot
        heatmap_filename = f"results/plots/{self.dataset_name}_heatmap"
        plt.savefig(heatmap_filename + ".png", dpi=300)
        plt.savefig(heatmap_filename + ".pdf", dpi=300)
        plt.show()