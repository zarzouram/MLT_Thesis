import argparse
import difflib
import os
import re


# Function to clean text (remove newlines)
def clean_text(text: str):
    cleaned_text = re.sub(r"\s+", " ", text)
    return " ".join(cleaned_text.splitlines())


# Function to read and clean text files (remove newlines)
def read_and_clean_files(file_paths):
    combined_text = ""
    for file_path in file_paths:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
            cleaned_text = clean_text(text)
            combined_text += cleaned_text
    return combined_text


# Function to count insertions, deletions, and matches in diff
def count_diffs(reference: str, generated: str):
    s = difflib.SequenceMatcher(None, list(generated), list(reference))
    insertions = 0
    deletions = 0
    matches = 0
    edits = 0

    for tag, i1, i2, j1, j2 in s.get_opcodes():
        if tag == "insert":
            insertions += len(reference[j1:j2])
        elif tag == "delete":
            deletions += len(generated[i1:i2])
        elif tag == "replace":
            edits += len(generated[i1:i2])
        else:
            matches += len(generated[i1:i2])

    return insertions, deletions, edits, matches


# Function to calculate edit distance and accuracy
def calculate_metrics(reference: str, generated: str):
    insertions, deletions, edits, matches = count_diffs(reference, generated)

    # Total characters in the golden standard text
    total_chars = len(generated)

    # Edit distance (absolute)
    edit_distance = insertions + deletions + edits

    # Accuracy as the proportion of matches to total characters in the golden
    # standard
    accuracy = matches / total_chars if total_chars > 0 else 0

    # Relative edit distance
    relative_edit_distance = (
        edit_distance / total_chars if total_chars > 0 else 0
    )

    return edit_distance, relative_edit_distance, accuracy


# Function to read and clean the files (golden and generated)
def process_files(folder_path):
    # List all files in the folder
    txt_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    # Filter for golden standard and generated files
    golden_files = [f for f in txt_files if f.endswith("_golden_standard.txt")]
    generated_files = [
        f for f in txt_files if not f.endswith("_golden_standard.txt")
    ]

    if len(golden_files) != len(generated_files):
        print(golden_files)
        print(generated_files)
        raise ValueError

    # Sort to ensure matching pairs (assuming the naming convention allows
    # simple matching)
    golden_files.sort()
    generated_files.sort()

    # Read and clean files, combine the texts
    golden_text = read_and_clean_files(
        [os.path.join(folder_path, f) for f in golden_files]
    )
    generated_text = read_and_clean_files(
        [os.path.join(folder_path, f) for f in generated_files]
    )

    return golden_text, generated_text


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Compare generated texts with golden standard."
    )
    parser.add_argument(
        "--folder",
        default="data/raw/articles",
        help="Path to the folder containing the text files.",
    )

    args = parser.parse_args()
    folder_path = args.folder

    # Read and clean the files
    golden_text, generated_text = process_files(folder_path)

    # Calculate the metrics
    edit_distance, relative_edit_distance, accuracy = calculate_metrics(
        golden_text, generated_text
    )

    # Output results
    print(
        (
            f"Edit Distance (absolute): {edit_distance} out of "
            f"{len(list(generated_text))}"
        )
    )
    print(f"Edit Distance (relative): {relative_edit_distance:.4%}")
    print(f"Accuracy: {accuracy:.4%}")


if __name__ == "__main__":
    main()
