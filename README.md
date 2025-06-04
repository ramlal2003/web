# Image to SVG Converter

This script converts raster images to vector SVG format using OpenCV for image processing and svgwrite for SVG generation.

## Requirements

- Python 3.7 or higher
- Required Python packages (install using `pip install -r requirements.txt`):
  - Pillow==10.2.0
  - numpy==1.26.4
  - svgwrite==1.4.3
  - opencv-python==4.9.0.80

## Installation

1. Clone this repository or download the files
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python image_to_svg.py input_image.png output.svg
```

Advanced usage with parameters:
```bash
python image_to_svg.py input_image.png output.svg --threshold_block_size 21 --threshold_c 8 --min_contour_len 30 --stroke_width 1.5
```

### Parameters

- `input`: Path to the input image file
- `output`: Path where the SVG file will be saved
- `--min_contour_len`: Minimum length of contours to include in SVG (default: 10)
- `--stroke_color`: Color for the SVG strokes (default: "#FFFFFF" for white)
- `--stroke_width`: Width of the SVG strokes (default: 1.0)
- `--background_color`: Color for the SVG background (default: "#000000" for black)
- `--threshold_block_size`: Neighborhood size for adaptive thresholding (must be odd, default: 11)
- `--threshold_c`: Constant subtracted from weighted mean for adaptive thresholding (default: 2)

## Notes

- The input image will be converted to grayscale before processing
- The quality of the SVG output depends on the input image quality and the parameters used
- For best results, use images with clear edges and good contrast
- The script uses adaptive thresholding for better binarization results 