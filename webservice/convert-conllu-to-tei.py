# Recursively goes through the TEI directory [arg1] and combines each file
# with the corresponding file (and file structure) in the CONLL-U directory [arg2]
# and writes the result to the output directory [arg3], once again preserving the file structure.

# Standard
import os
import time
import sys
from concurrent import futures
import random
import traceback

# Third-party
from tqdm import tqdm
import requests
import requests.exceptions

# Local
import conllu_tei_helper as tei


def directory_tree_file_count(dir: str):
    """
    The number of files in the entire directory tree.
    """
    total = 0
    for _, _, files in os.walk(dir):
        total += len(files)
    return total


def convert_single_file(tei_path, conllu_path, out_path):
    if not os.path.exists(conllu_path):
        print(f"conllu path does not exist {conllu_path}", file=sys.stderr)
        return
    try:
        xmlstring = tei.merge_tei_with_conllu_layer(conllu_path, tei_path)
        f_out = open(out_path, "wb")  # we are actually writing bytes
        f_out.write(xmlstring)
        f_out.close()
        # We do one extra action here, that is replacing the id's with xml:id's
        # convert_id_to_xmlid(output_path)
    except Exception as e:
        print(f"error with {tei_path}", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)


def convert_files_in_directory_tree(tei_dir, conllu_dir, out_dir):
    """
    Walks through the directory tree and converts each file found.
    """
    # used for progress bar
    total_files = directory_tree_file_count(tei_dir)
    with tqdm(total=total_files) as progress_bar:

        # Walk through the directory tree
        for root, _, files in os.walk(tei_dir):

            # Create the output subdirectory for the current root
            output_subdir = os.path.join(out_dir, os.path.relpath(root, tei_dir))
            os.makedirs(output_subdir, exist_ok=True)

            # Convert each file in the directory
            for file in files:

                # Construct paths
                tei_file = os.path.join(root, file)
                conllu_file = (
                    os.path.join(conllu_dir, os.path.relpath(root, tei_dir), file)
                    + ".conllu"
                )
                out_file = os.path.join(output_subdir, os.path.basename(tei_file))

                # Skip if the output file already exists
                if os.path.exists(out_file):
                    progress_bar.update(1)
                    continue

                # Convert file
                convert_single_file(tei_file, conllu_file, out_file)

                # Update progress bar once done
                progress_bar.update(1)


if __name__ == "__main__":
    # Check if the number of arguments is correct
    if len(sys.argv) != 4:
        print("Usage: python convert-conllu-to-tei.py <TEI_DIR> <CONLLU_DIR> <OUT_DIR>")
        sys.exit(1)

    # Get the arguments
    tei_dir = sys.argv[1]
    conllu_dir = sys.argv[2]
    out_dir = sys.argv[3]

    # Convert the files
    convert_files_in_directory_tree(tei_dir, conllu_dir, out_dir)
