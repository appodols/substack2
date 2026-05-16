import os
import email
from email import policy
from bs4 import BeautifulSoup
import argparse
import codecs
import html


def extract_text_from_mhtml(file_path):
    """Extracts text from paragraph, blockquote, and span tags in an MHTML file."""
    with open(file_path, "rb") as file:
        mhtml_message = email.message_from_binary_file(file, policy=policy.default)

    # Extract HTML content from MHTML parts
    html_content = ""
    for part in mhtml_message.walk():
        if part.get_content_type() == "text/html":
            html_content += part.get_content()

    # Decode HTML entities and fix encoding issues
    html_content = html.unescape(html_content)
    html_content = html_content.encode("latin1", "ignore").decode("utf-8", "ignore")

    # Parse the extracted HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract text from relevant tags
    text_elements = soup.find_all(["p", "blockquote", "span"])
    extracted_text = "\n".join([elem.get_text(strip=True) for elem in text_elements])

    # Replace any lingering special characters with proper encoding
    extracted_text = extracted_text.replace("\ufffd", "?")  # Handles unknown characters

    return extracted_text


def process_file(file_path, output_folder):
    """Processes a single MHTML file and saves extracted text as a .txt file."""
    print(f"🔍 Processing file: {file_path}")

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists
    text = extract_text_from_mhtml(file_path)
    output_file = os.path.join(
        output_folder, os.path.basename(file_path).replace(".mhtml", ".txt")
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Extracted text saved to {output_file}")


def process_folder(folder_path, output_folder):
    """Processes all MHTML files in a folder."""
    print(f"🔍 Processing folder: {folder_path}")

    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    os.makedirs(output_folder, exist_ok=True)

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mhtml"):
            file_path = os.path.join(folder_path, file_name)
            process_file(file_path, output_folder)


def main():
    parser = argparse.ArgumentParser(description="Extract text from MHTML files.")
    parser.add_argument(
        "input_path", type=str, help="Path to an MHTML file or folder of MHTML files."
    )
    parser.add_argument(
        "output_folder",
        type=str,
        nargs="?",
        default="extracted_text",
        help="Folder where extracted text files will be saved (default: extracted_text).",
    )
    args = parser.parse_args()

    resolved_path = os.path.abspath(args.input_path)
    print(f"🔍 Checking path: {resolved_path}")
    print(f"🔹 os.path.exists: {os.path.exists(resolved_path)}")
    print(f"🔹 os.path.isfile: {os.path.isfile(resolved_path)}")
    print(f"🔹 os.path.isdir: {os.path.isdir(resolved_path)}")

    if os.path.exists(resolved_path):
        if os.path.isfile(resolved_path):
            process_file(resolved_path, args.output_folder)
        elif os.path.isdir(resolved_path):
            process_folder(resolved_path, args.output_folder)
        else:
            print(f"❌ Path exists but is neither a file nor a folder: {resolved_path}")
    else:
        print(
            f"❌ Invalid path: {resolved_path}. Please provide a valid file or folder."
        )


if __name__ == "__main__":
    main()
