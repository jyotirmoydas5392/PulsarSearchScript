import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import subprocess

def convert_ps_to_png_with_rotation(ps_file, png_file):
    """
    Converts a PS file to a PNG file and rotates it if necessary.
    :param ps_file: Path to the input PS file.
    :param png_file: Path to the output PNG file.
    """
    try:
        # Convert PS to PNG using Ghostscript
        subprocess.run(["gs", "-dNOPAUSE", "-sDEVICE=pngalpha", "-r300", 
                        f"-sOutputFile={png_file}", ps_file, "-c", "quit"], check=True)
        print(f"Converted: {ps_file} -> {png_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {ps_file}: {e}")

def batch_convert_ps_to_png(input_dir, output_dir, workers, keyword):
    """
    Batch converts PS files in the input directory to PNG files in the output directory based on the keyword.
    :param input_dir: Directory containing PS files.
    :param output_dir: Directory where PNG files will be saved.
    :param workers: Number of parallel workers for processing.
    :param keyword: Keyword to search for in PS file names.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Prepare list of PS files to process based on the keyword in the file name
    ps_files = [
        (os.path.join(input_dir, filename), os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.png"))
        for filename in os.listdir(input_dir)
        if filename.endswith('.ps') and keyword in filename  # Match the keyword without case conversion
    ]

    if not ps_files:
        print(f"No PS files found containing the keyword '{keyword}' in {input_dir}.")
        return

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor(max_workers=workers) as executor:
        # Submit tasks to the executor
        futures = {executor.submit(convert_ps_to_png_with_rotation, ps_file, png_file): (ps_file, png_file) for ps_file, png_file in ps_files}

        # Process completed tasks
        for future in as_completed(futures):
            ps_file, png_file = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error converting {ps_file}: {e}")

    print("Batch conversion of PS to PNG completed.")

# Example usage
if __name__ == "__main__":
    input_dir = "/path/to/ps/files"
    output_dir = "/path/to/output/png"
    workers = 4  # Number of parallel processes
    keyword = "your_keyword_here"  # Modify with actual keyword

    batch_convert_ps_to_png(input_dir, output_dir, workers, keyword)