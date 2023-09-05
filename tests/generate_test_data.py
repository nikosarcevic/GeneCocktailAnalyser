import os
import pandas as pd
import random


def create_filter_data():
    """
    Create filter data and save it to a CSV file.
    """
    # Create the 'test_data' directory if it doesn't exist
    if not os.path.exists("test_data"):
        os.makedirs("test_data", exist_ok=True)

    else:
        print("test_data directory already exists.")

    # Create filter data using a dictionary
    filters_data = {
        "ID": ["Ref1", "Ref2", "Ref3", "Ref4", "Ref5", "Ref6", "Ref7"],
        "Name": ["Filter1", "Filter2", "Filter3", "Filter4", "Filter5", "Filter6", "Filter7"],
        "Filter Sequence": ["AAA", "BBB", "CCC", "ABC", "BCA", "AAB", "BBA"]
    }

    # Convert the dictionary to a DataFrame and save it as a CSV file
    filters_df = pd.DataFrame(filters_data)
    filters_df.to_csv("test_data/test_filters.csv", index=False)
    print(f"Filter data saved to: {os.path.abspath('test_data/test_filters.csv')}")


# noinspection PyShadowingNames
def create_sequence_data(sequence_length=20, num_sequences=100):
    """
    Create sequence data and save it to a CSV file. Return metadata about the created sequences.
    """
    # Ensure the 'test_data' directory exists
    if not os.path.exists("test_data"):
        os.mkdir("test_data")
    else:
        print("test_data directory already exists.")

    # Define filter sequences and their occurrence counts
    filters = {
        "AAA": 2,
        "BBB": 1,
        "CCC": 3,
        "ABC": 4,
        "BCA": 0,
        "AAB": 2,
        "BBA": 3
    }

    sequences = []

    # Generate sequences with inserted filter occurrences
    for filter_seq, count in filters.items():
        for _ in range(count):
            seq = ''.join(random.choices("XYZ", k=sequence_length - len(filter_seq)))
            insert_idx = random.randint(0, sequence_length - len(filter_seq))
            seq = seq[:insert_idx] + filter_seq + seq[insert_idx:]
            sequences.append(seq)

    # Insert additional sequences with specific filter occurrences
    for _ in range(filters["AAB"]):
        random_seq = ''.join(random.choices("XYZ", k=(sequence_length - 6)))
        seq = random_seq[:4] + "AAB" + random_seq[4:8] + "AAB" + random_seq[8:]
        sequences.append(seq)

    for _ in range(filters["BBA"]):
        random_seq = ''.join(random.choices("XYZ", k=(sequence_length - 9)))
        seq = random_seq[:3] + "BBA" + random_seq[3:6] + "BBA" + random_seq[6:9] + "BBA" + random_seq[9:]
        sequences.append(seq)

    # Insert a sequence containing both AAB and BBA
    random_seq = ''.join(
        random.choices("XYZ", k=(sequence_length - 6)))  # Adjust for the length of both filter sequences
    insert_idx_aab = random.randint(0, sequence_length - 6)
    seq = random_seq[:insert_idx_aab] + "AAB" + random_seq[insert_idx_aab:]
    insert_idx_bba = random.randint(0, len(seq) - 3)
    seq = seq[:insert_idx_bba] + "BBA" + seq[insert_idx_bba:]
    sequences.append(seq)

    # Generate sequences with random data to complete the total count
    while len(sequences) < num_sequences:
        sequences.append(''.join(random.choices("XYZ", k=sequence_length)))

    # Create a DataFrame from generated sequences and save it as a CSV file
    df = pd.DataFrame({
        "Sequence": sequences,
        "Count": [random.randint(1, 10) for _ in range(len(sequences))],
        "Amino Acid": [random.choice("XYZ") for _ in range(len(sequences))]
    })
    df.to_csv("test_data/test_sequence_data.csv", index=False)
    print(f"Sequence data saved to: {os.path.abspath('test_data/test_sequence_data.csv')}")

    # Define metadata about the generated sequences
    metadata = {
        "nan_rows": 2,  # Updated to 2 for the sequences with NaN
        "total_samples": num_sequences,  # Updated to include the sequences with NaN
        "filters": filters,
        "double_AAB_sequences": filters["AAB"],
        "triple_BBA_sequences": filters["BBA"]
    }

    return metadata


# Create filter data CSV
create_filter_data()

# Create sequence data CSV and get metadata
# noinspection PyArgumentEqualDefault
metadata = create_sequence_data(sequence_length=20, num_sequences=100)

# Verification code
sequences_df = pd.read_csv("test_data/test_sequence_data.csv")

print("AAA:", sequences_df["Sequence"].str.count("AAA").sum())
print("BBB:", sequences_df["Sequence"].str.count("BBB").sum())
print("CCC:", sequences_df["Sequence"].str.count("CCC").sum())
print("ABC:", sequences_df["Sequence"].str.count("ABC").sum())
print("BCA:", sequences_df["Sequence"].str.count("BCA").sum())
print("AAB:", metadata["double_AAB_sequences"])
print("BBA:", metadata["triple_BBA_sequences"])
