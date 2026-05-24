import subprocess
import tempfile
import os
import argparse


def latex_to_svg(latex_snippet: str):
    """
    Converts a LaTeX snippet to an SVG image.

    Args:
        latex_snippet: The LaTeX code to be converted.

    Returns:
        The SVG content as a string.
    """
    latex_snippet = latex_snippet.replace("\\n", " ").strip()
    with open("template.tex", "r") as f:
        template = f.read()

    latex_code = template.replace("%{INPUTS}", latex_snippet)

    with tempfile.TemporaryDirectory() as tempdir:
        tex_filepath = os.path.join(tempdir, "input.tex")
        with open(tex_filepath, "w") as f:
            _ = f.write(latex_code)

        # Compile LaTeX to PDF
        process = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                tempdir,
                tex_filepath,
            ],
            capture_output=True,
            text=True,
        )

        if process.returncode != 0:
            raise RuntimeError(f"pdflatex failed: {process.stderr}\\n{process.stdout}")

        pdf_filepath = os.path.join(tempdir, "input.pdf")
        svg_filepath = os.path.join(tempdir, "output.svg")

        # Convert PDF to SVG
        process = subprocess.run(
            ["pdf2svg", pdf_filepath, svg_filepath], capture_output=True, text=True
        )

        if process.returncode != 0:
            raise RuntimeError(f"pdf2svg failed: {process.stderr}")

        with open(svg_filepath, "r") as f:
            svg_content = f.read()

    return svg_content


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a LaTeX snippet to an SVG file."
    )
    _ = parser.add_argument(
        "latex_snippet", type=str, help="The LaTeX snippet to convert."
    )
    _ = parser.add_argument(
        "output_filename",
        type=str,
        help="The name of the output SVG file (without extension).",
    )
    args = parser.parse_args()

    try:
        svg_output = latex_to_svg(args.latex_snippet)
        output_filepath = f"{args.output_filename}.svg"
        with open(output_filepath, "w") as f:
            _ = f.write(svg_output)
        print(f"Successfully generated {output_filepath}")
    except RuntimeError as e:
        print(f"An error occurred: {e}")
