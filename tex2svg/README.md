# LaTeX to SVG Converter

This Python application converts LaTeX code snippets into SVG images.

## How it works

1.  **Input**: A LaTeX code snippet (e.g., a tikz diagram).
2.  **Templating**: The snippet is inserted into a `template.tex` file.
3.  **Compilation**: The `.tex` file is compiled into a PDF using `pdflatex`.
4.  **Conversion**: The PDF is converted to an SVG using `pdf2svg`.
5.  **Output**: An SVG file.

## Usage

1.  **Prerequisites**: Make sure you have a LaTeX distribution (like TeX Live `apt install texlive-full`) and `pdf2svg` (`apt install pdf2svg`) installed.
2.  **Run the script**:
    ```bash
    python3 main.py "<latex_snippet>" <output_filename>
    ```
    For example:
    ```bash
    python3 main.py "$\lambda$" the_lambda_image
    ```
3.  **Output**: The script will generate an `<output_filename>.svg` file in the same directory.

## Testing

To run the tests, execute the following command:
```bash
python3 test_main.py
```

## Customization

-   **Template**: You can modify the `template.tex` file to include different LaTeX packages or change the document setup.
