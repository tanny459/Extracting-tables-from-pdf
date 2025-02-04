# Extracting-tables-from-pdf

PDF Table Extraction and OCR Processing

Overview

This project provides a comprehensive pipeline for extracting tabular data from PDFs, handling both text-based and image-based PDFs. It leverages libraries like camelot and pdfplumber for structured data extraction and integrates OpenAI's GPT-4o model for OCR-based table extraction from images.

Features

Extracts tables from text-based PDFs using camelot and pdfplumber

Converts image-based PDFs to high-resolution images using pdf2image

Applies preprocessing techniques like contrast enhancement and adaptive thresholding using OpenCV

Uses GPT-4o to extract structured tabular data from preprocessed images

Saves extracted tables as CSV files for further analysis

Installation

Prerequisites

Ensure you have the following dependencies installed:

Python 3.x

pip install -r requirements.txt

Required Python Packages

Install dependencies with:
pip install os opencv-python camelot-py requests pdfplumber pandas pdf2image base64

Additionally, ensure you have Poppler installed and configured if running on Windows.

Usage

1. Prepare Input Folder

Place your PDF files inside the new_pdf/ folder.

2. Run the Extraction Script

python extract_tables.py

This script will:

Extract text-based tables and save them as CSV files in extracted_df/

Convert image-based PDFs to images, preprocess them, and extract tables using GPT-4o

3. Output

Extracted tables will be stored as CSV files in extracted_df/.

File Structure
├── new_pdf/                # Folder containing input PDFs
├── extracted_df/           # Folder where extracted tables (CSV) are stored
├── pdf_to_image/           # Temporary folder for storing images from PDFs
├── extract_tables.py       # Main script for processing PDFs
├── requirements.txt        # Required dependencies
├── README.md               # Project documentation

API Key Configuration

Ensure you replace api_key in extract_tables.py with your OpenAI API key for processing image-based PDFs.

Contributions

Feel free to fork and contribute to improving the project!
