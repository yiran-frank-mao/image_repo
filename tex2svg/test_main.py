import unittest
from main import latex_to_svg


class TestLatexToSvg(unittest.TestCase):
    def test(self):
        """
        Tests that a simple lambda expression is correctly converted to an SVG.
        """
        latex_snippet = " "
        with open("test_snippet.tex", "r") as f:
            latex_snippet = f.read()

        svg_output = latex_to_svg(latex_snippet)
        self.assertTrue(svg_output.strip().startswith("<?xml"))
        self.assertTrue(svg_output.strip().endswith("</svg>"))
        with open("test_output.svg", "w") as f:
            _ = f.write(svg_output)
        print("Successfully generated test_output")


if __name__ == "__main__":
    unittest.main()
