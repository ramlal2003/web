import os
import numpy as np
from PIL import Image
import svgwrite
import cv2 # Import OpenCV
import argparse

def process_image_for_potrace(input_path, threshold_block_size=11, threshold_c=2):
    """
    Process image using OpenCV for better binarization for Potrace.
    Returns a NumPy array of the binary image.
    """
    try:
        img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE) # Read as grayscale
        if img is None:
            print(f"Error: Could not read image from {input_path}")
            return None

        # Apply Gaussian blur to reduce noise
        img_blur = cv2.GaussianBlur(img, (5, 5), 0)

        # Apply adaptive thresholding
        # ADAPTIVE_THRESH_GAUSSIAN_C: threshold is a gaussian-weighted sum of neighborhood values minus the constant C
        # THRESH_BINARY: pixels above threshold are set to max_value (255), below to 0
        img_binary = cv2.adaptiveThreshold(
            img_blur,
            255, # max_value
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            threshold_block_size, # neighborhood size (must be odd)
            threshold_c # constant subtracted from weighted mean
        )
        
        # Invert the binary image if the subject is dark on a lighter background
        # Based on the input image, the subject is dark, so we need to invert
        img_binary = cv2.bitwise_not(img_binary)

        return img_binary

    except Exception as e:
        print(f"Error during image processing with OpenCV: {e}")
        return None

def trace_contours_from_binary(binary_image):
    """
    Trace contours from a binary image (NumPy array).
    Returns a list of contours.
    """
    # Find contours using OpenCV's findContours
    # cv2.RETR_LIST: retrieves all contours
    # cv2.CHAIN_APPROX_SIMPLE: compresses horizontal, vertical, and diagonal segments
    contours, _ = cv2.findContours(binary_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Convert contours to a simpler format (list of points)
    simplified_contours = []
    for contour in contours:
        # Reshape contour from (n, 1, 2) to (n, 2) and convert to list of tuples
        simplified_contour = [tuple(point[0]) for point in contour]
        if len(simplified_contour) > 10: # Minimum contour length
             simplified_contours.append(simplified_contour)
             
    return simplified_contours

def image_to_svg(input_path, output_path, min_contour_len=10, stroke_color="#FFFFFF", stroke_width=1.0, background_color="#000000", threshold_block_size=11, threshold_c=2):
    """
    Convert an image to SVG format using OpenCV for processing and svgwrite for drawing.
    """
    # Process image to get a binary representation
    binary_image_np = process_image_for_potrace(input_path, threshold_block_size, threshold_c)
    if binary_image_np is None:
        return

    # Trace contours from the binary image
    contours = trace_contours_from_binary(binary_image_np)
    
    # Get image dimensions for SVG size
    # Use Pillow just for getting image dimensions reliably
    try:
        img_dim = Image.open(input_path)
        img_width, img_height = img_dim.size
    except Exception as e:
        print(f"Error getting image dimensions: {e}")
        return

    # Create SVG drawing
    dwg = svgwrite.Drawing(output_path, size=(img_width, img_height), profile='full')

    # Add the black background rectangle
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill=background_color))

    # Add contours to SVG as paths (white stroke, no fill)
    for contour in contours:
        if len(contour) > min_contour_len:
            # Format points for SVG path data
            points_str = " ".join([f"{x},{y}" for x, y in contour])
            # Create path data: Move to first point, then Line to subsequent points
            # Use 'L' command for lines between points
            path_data = f"M {contour[0][0]},{contour[0][1]} L {points_str[len(f"{contour[0][0]},{contour[0][1]} "): ]}"
            
            # Use 'Z' to close the path if it seems closed
            # A simple check: if the start and end points are the same or very close
            # This might need refinement depending on the contour tracing output
            # For now, let's assume contours from findContours are often closed loops if they represent shapes
            path_data += " Z"

            dwg.add(dwg.path(d=path_data, fill='none', stroke=stroke_color, stroke_width=stroke_width))

    # Save SVG file
    dwg.save()
    print(f"SVG file has been created at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Convert image to SVG with black background and white outlines using OpenCV for processing.')
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output SVG path')
    parser.add_argument('--min_contour_len', type=int, default=10, help='Minimum length of contours to include in SVG')
    parser.add_argument('--stroke_color', type=str, default="#FFFFFF", help='Color for the SVG strokes (default #FFFFFF for white)')
    parser.add_argument('--stroke_width', type=float, default=1.0, help='Width of the SVG strokes')
    parser.add_argument('--background_color', type=str, default="#000000", help='Color for the SVG background (default #000000 for black)')
    parser.add_argument('--threshold_block_size', type=int, default=11, help='Neighborhood size for adaptive thresholding (must be odd)')
    parser.add_argument('--threshold_c', type=int, default=2, help='Constant subtracted from weighted mean for adaptive thresholding')

    args = parser.parse_args()
    
    image_to_svg(
        args.input,
        args.output,
        args.min_contour_len,
        args.stroke_color,
        args.stroke_width,
        args.background_color,
        args.threshold_block_size,
        args.threshold_c
    )

if __name__ == '__main__':
    main() 