# SteelEye Assessment

## Project Overview
This project processes and analyzes financial data from XML files. It downloads a ZIP file from a given URL, extracts XML data, processes it, and generates a structured CSV output. Additionally, it adds computed columns to enhance the analysis. Unit tests are included to verify the core functionality.

### Project Structure

- **dev.py**: Main implementation with the `GetData` class, including methods to:
  - **Download XML/ZIP files.**
  - **Extract and process XML data.**
  - **Generate CSV output.**
  - **Add computed columns.**

- **unittesting.py**: Unit tests for `GetData` methods using the `unittest` framework.

- **tests.py**: Integration tests for the complete workflow.

- **Sample Input Files**: XML/ZIP files for testing.

- **Output Directory**: Processed CSV files are saved in the `./output` directory.

### Requirements

- **Python Version**: 3.7 or higher
  Required packages:
  - `pandas`: For data manipulation.
  - `requests`: For HTTP requests.
  - `xmltodict`: For XML parsing.
  - `unittest`: For testing.
  - `mock`: For mocking in tests.

### Usage

1. **Run the Main Program**:
   - Provide the ZIP file URL containing XML data.
   - Execute `dev.py` to download, process, and generate the CSV.
   ```bash
   python dev.py
   ```
   
2. **Run the UnitTests:**

    - Execute `unittesting.py` to run unit tests.
    ```bash
    python unittesting.py
    ```

3. **Run the integration tests.**
   - Execute `tests.py` to download, process, and generate the CSV.
    ```bash
    python tests.py
    ```


**``GetData`` Methods**
  - **download_xml**: Downloads an XML file from a URL and returns its content as a string.

  - **download_extract_zip**: Downloads and extracts a ZIP file, returning the extracted XML.
  - **create_csv**: Converts XML data into a structured CSV.
  - **add_columns**: Adds two computed columns:
      - **a_count**: Count of "a" occurrences in the FinInstrmGnlAttrbts.FullNm column.
      - **contains_a**: Whether "a" exists in the same column.
  - **get_DLTINS_file**: Extracts and returns the download link for the "DLTINS" file from XML.


**Unit Tests**

Test scenarios include:

  - Successful XML download (test_download_xml_success)
  - ZIP download and extraction (test_download_extract_zip_success)
  - Correct CSV creation (test_create_csv_success)
  - Accurate addition of computed columns (test_add_columns_success)
  - Correct extraction of the "DLTINS" file URL (test_get_DLTINS_file_success)


**Integration Tests**
The ``tests.py`` file tests the complete workflow of the application, including the downloading, processing, and adding computed columns to the data. It includes the following tests:

  - test_get_data: Downloads the XML file, extracts the DLTINS link, and processes the ZIP file.

  - test_converting_xml2csv: Converts XML data to a CSV file and checks its creation.
  
  - test_add_columns: Validates the addition of a_count and contains_a columns in the CSV.

Integration Test Results: Logs are saved in test_logs.log, with each step's success or failure logged for debugging and validation.


