import argparse
import os
import re
import subprocess
import tempfile


def parse_github_repo_url(url: str) -> tuple[str, str]:
    """Extract (owner, repo) from a GitHub repository URL."""
    url = url.strip().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]

    match = re.match(
        r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)",
        url,
    )
    if not match:
        raise ValueError(f"Invalid GitHub repository URL: {url}")

    return match.group(1), match.group(2)


def github_raw_svg_url(
    github_repo_url: str,
    svg_path_in_repo: str,
    branch: str = "master",
) -> str:
    owner, repo = parse_github_repo_url(github_repo_url)
    svg_path_in_repo = svg_path_in_repo.lstrip("/").replace(os.sep, "/")
    return (
        f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{svg_path_in_repo}"
    )


def svg_path_in_repo(svg_filepath: str) -> str:
    """Path of the SVG relative to the git repo root, or basename if not in a repo."""
    svg_filepath = os.path.abspath(svg_filepath)
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.path.dirname(svg_filepath) or ".",
        )
        repo_root = result.stdout.strip()
        return os.path.relpath(svg_filepath, repo_root)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return os.path.basename(svg_filepath)


def build_img_html(raw_svg_url: str, width: str = "50%") -> str:
    return f'<img src="{raw_svg_url}" style="width:{width};"/>'


def copy_to_clipboard(text: str) -> None:
    for cmd in (
        ["wl-copy"],
        ["xclip", "-selection", "clipboard"],
        ["xsel", "--clipboard", "--input"],
    ):
        try:
            subprocess.run(
                cmd,
                input=text,
                text=True,
                check=True,
                capture_output=True,
            )
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise RuntimeError(
        "Could not copy to clipboard (install wl-copy, xclip, or xsel)"
    )


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
    _ = parser.add_argument(
        "--github-repo",
        type=str,
        metavar="URL",
        help=(
            'GitHub repository base URL (e.g. "https://github.com/user/repo"). '
            "On success, copies an <img> tag with a raw.githubusercontent.com src "
            "to the clipboard."
        ),
    )
    _ = parser.add_argument(
        "--github-branch",
        type=str,
        default="master",
        help='Branch for raw URLs (default: "master").',
    )
    _ = parser.add_argument(
        "--img-width",
        type=str,
        default="50%",
        help='Width in the clipboard <img> style (default: "50%%").',
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
        else:
            output = os.path.abspath(output)
        print(f"Successfully generated {output}")

        if args.github_repo:
            raw_url = github_raw_svg_url(
                args.github_repo,
                svg_path_in_repo(output),
                branch=args.github_branch,
            )
            img_html = build_img_html(raw_url, width=args.img_width)
            print(img_html)
            copy_to_clipboard(img_html)
            print(f"Copied to clipboard.")
    except (RuntimeError, FileNotFoundError, ValueError) as e:
        print(f"An error occurred: {e}")