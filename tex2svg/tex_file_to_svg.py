import argparse
import os
import subprocess
import tempfile


def tex_file_to_svg(tex_filepath: str, svg_filepath: str | None = None) -> str:
    """
    Compile a TeX file to PDF, convert the PDF to SVG, and discard build artifacts.

    Args:
        tex_filepath: Path to the .tex file to compile.
        svg_filepath: Optional path for the output SVG. Defaults to the same
            basename as the input file, with a .svg extension, in the input
            file's directory.

    Returns:
        The SVG content as a string.
    """
    tex_filepath = os.path.abspath(tex_filepath)
    if not os.path.isfile(tex_filepath):
        raise FileNotFoundError(f"TeX file not found: {tex_filepath}")

    tex_dir = os.path.dirname(tex_filepath)
    base_name = os.path.splitext(os.path.basename(tex_filepath))[0]

    if svg_filepath is None:
        svg_filepath = os.path.join(tex_dir, f"{base_name}.svg")
    else:
        svg_filepath = os.path.abspath(svg_filepath)

    with tempfile.TemporaryDirectory() as tempdir:
        process = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                tempdir,
                tex_filepath,
            ],
            cwd=tex_dir,
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise RuntimeError(
                f"pdflatex failed: {process.stderr}\n{process.stdout}"
            )

        pdf_filepath = os.path.join(tempdir, f"{base_name}.pdf")
        if not os.path.isfile(pdf_filepath):
            raise RuntimeError(f"pdflatex did not produce {pdf_filepath}")

        temp_svg_filepath = os.path.join(tempdir, f"{base_name}.svg")
        process = subprocess.run(
            ["pdf2svg", pdf_filepath, temp_svg_filepath],
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise RuntimeError(f"pdf2svg failed: {process.stderr}")

        with open(temp_svg_filepath, "r") as f:
            svg_content = f.read()

        with open(svg_filepath, "w") as f:
            _ = f.write(svg_content)

    return svg_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compile a TeX file to PDF and convert it to SVG."
    )
    _ = parser.add_argument("tex_filepath", type=str, help="Path to the .tex file.")
    _ = parser.add_argument(
        "output_filepath",
        nargs="?",
        type=str,
        help="Optional output SVG path (defaults to the input basename with .svg).",
    )
    args = parser.parse_args()

    try:
        tex_file_to_svg(args.tex_filepath, args.output_filepath)
        output = args.output_filepath
        if output is None:
            base = os.path.splitext(os.path.basename(args.tex_filepath))[0]
            output = os.path.join(
                os.path.dirname(os.path.abspath(args.tex_filepath)), f"{base}.svg"
            )
        print(f"Successfully generated {output}")
    except (RuntimeError, FileNotFoundError) as e:
        print(f"An error occurred: {e}")
