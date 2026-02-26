import os
import subprocess

def generate_offline_docu():
    # Define the source directory where your .py files are located
    source_dir = ["..\..\..\Platform\Python_Testing_Framework\CommonTestFunctions",
                  "..\..\..\Platform\Python_Testing_Framework\TraceParser"]# Change this to your actual source folder
    output_dir = "..\..\..\Platform\Python_Testing_Framework\docs"

    for source in source_dir:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Run pdoc3 for the entire directory
        subprocess.run(["pdoc", "--html", source, "--output-dir", output_dir, "--force"])

        print(f"Documentation generated in: {output_dir}")
