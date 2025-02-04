import os
import cv2
import json
import base64
import camelot
import requests
import pdfplumber
import pandas as pd
from io import StringIO
from pdf2image import convert_from_path

api_key = "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"

def extract_tables_from_pdfs(input_folder, output_folder):
    # Check if the output folder exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            # Initialize a list to store all DataFrames from the PDF
            all_tables_list = []  

            try:

                with pdfplumber.open(pdf_path) as pdf:
                    page = pdf.pages[0]
                    text = page.extract_text()
                    if text:
                        print("PDF is text-based.")
                        # Extract tables from the PDF
                        tables = camelot.read_pdf(pdf_path, pages = 'all', flavor = 'hybrid')

                        # If tables are found, process them
                        if len(tables) > 0:
                            # Combine all tables from different pages into a list of DataFrames
                            for table in tables:
                                all_tables_list.append(table.df)

                            # Concatenate all DataFrames into a single DataFrame
                            all_tables_df = pd.concat(all_tables_list, ignore_index=True)

                            # Create output file path
                            output_file_path = os.path.join(output_folder, f"{filename}.csv")

                            # Save the combined DataFrame to CSV
                            all_tables_df.to_csv(output_file_path, index=False)
                            print(f"All tables from {filename} saved to {output_file_path}")
                            
                            # Save the filename to a text file
                            with open("output_file", "w") as file:
                                file.write(filename)
                        else:
                            print(f"No tables found in {filename}")

                    else:
                        print("PDF is image-based.")
                        convert_pdf_to_images(pdf_path)
                        preprocess_images_in_folder("pdf_to_image")
                        text = call_gpt4_with_images("pdf_to_image")
                        delete_images_in_folder("pdf_to_image")
                        markdown_to_dataframe(text, filename)
                        

                        # Save the filename to a text file
                        with open("output_file", "w") as file:
                            file.write(filename)


            except Exception as e:
                print(f"Failed to process {filename} due to error: {e}")

def convert_pdf_to_images(pdf_path):
    # Ensure the output folder exists
    output_folder = "pdf_to_image"
    os.makedirs(output_folder, exist_ok = True)

    # Extract the base name of the PDF file (without extension)
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

    try:
        # Convert the PDF pages to images
        images = convert_from_path(pdf_path, dpi = 1000 , poppler_path = r"C:\Program Files (x86)\Release-24.08.0-0\poppler-24.08.0\Library\bin")

        # Save each page as an image file
        for i, image in enumerate(images, start=1):
            image_filename = f"{pdf_name}_{i}_page.png"
            image_path = os.path.join(output_folder, image_filename)
            image.save(image_path, "PNG")

        print(f"All pages of '{pdf_name}' have been successfully saved in the '{output_folder}' folder.")
    except Exception as e:
        print(f"Error occurred while converting PDF to images: {e}")

def preprocess_images_in_folder(folder_path):

    # Loop through each file in the folder
    for image_filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_filename)

        # Check if the file is an image (based on extension)
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            try:
                # Read the image in grayscale
                image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

                # Enhance contrast using histogram equalization
                equalized = cv2.equalizeHist(image)

                # Apply adaptive thresholding for better text preservation
                binary = cv2.adaptiveThreshold(
                    image, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    15, 4  # Fine-tune block size and constant
                )

                # Save the processed image back to the folder, overwriting the original file
                cv2.imwrite(image_path, binary)

            except Exception as e:
                print(f"Error processing file {image_filename}: {e}")
    
    print("All images have been preprocessed.")

def encode_image(image_path):
    """Encodes a single image to base64 from the given path."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def call_gpt4_with_images(folder_path):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    final_markdown = ""  # Initialize a string to store all markdown text

    # Loop through each file in the given folder
    for image_filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, image_filename)

        # Check if the file is an image (based on file extension)
        if image_filename.lower().endswith((".png", ".jpg", ".jpeg")):
            base64_image = encode_image(image_path)

            payload = {
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """You are an AI assistant designed to extract tabular information from images of bank statements. Your task is to:

                                1. Convert the table in the image into a markdown table format.
                                2. Ensure the markdown table is complete, with all rows and columns represented.
                                3. Avoid adding any extra text or explanation, only output the markdown table.

                                ### Output Format ###
                                | Column_1 | Column_2 | Column_3 |
                                |----------|----------|----------|
                                |----------|----------|----------|     
                                | value_1  | value_1  | value_1  |
                                | value_2  | value_2  | value_2  |
                                | value_3  | value_3  | value_3  |
                                | value_4  | value_4  | value_4  |
                                
                                ### Instructions ###
                                1. Ensure the table is well-formatted and aligned.
                                2. If a column is shorter than others, fill missing cells with 'Not available'.
                                3. Re-check to ensure no rows or columns are missed.
                                4. Do not include any other information outside the markdown table.
                                5. Avoid adding backticks(```), or any extra characters in the response. Just return the markdown table text.
                                """
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 4096
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = response.json()

            if response.status_code == 200:
                table_data_markdown = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                final_markdown += table_data_markdown + "\n\n"
            else:
                final_markdown += f"# Table from {image_filename}\n\nError: {result.get('error', 'Unknown error occurred')}\n\n"

    return final_markdown

def delete_images_in_folder(folder_path):
    
    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # Check if the file is an image (based on extension)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp')):
            try:
                os.remove(file_path)  # Delete the image file
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")
    
    print("All image files have been deleted.")


def markdown_to_dataframe(markdown_table, filename):

    # Use StringIO to treat the markdown table as CSV
    df = pd.read_csv(StringIO(markdown_table), sep="|", engine="python", skipinitialspace=True)

    # Clean up columns by stripping extra spaces
    df.columns = df.columns.str.strip()

    # Remove columns that have "Unnamed" in their names
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # Save the DataFrame to CSV
    df.to_csv(f"extracted_df/{filename}.csv", index=False)

    print(f"Data Frame save to----> extracted_df/{filename}.csv")

    return df

                
input_folder = "new_pdf"  
output_folder = "extracted_df"  
extract_tables_from_pdfs(input_folder, output_folder)
