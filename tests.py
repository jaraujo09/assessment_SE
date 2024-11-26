from dev import *
from dev import GetData

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", filename="test_logs.log", filemode="w")

def test_get_data():
    url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2021-01-17T00:00:00Z+TO+2021-01-19T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
    
    # Initialize the GetData class
    downloader = GetData(url)
    
    # Step 1: Download XML
    logging.info("Step 1: Downloading XML")
    xml_content = downloader.download_xml()
    if not xml_content:
        logging.error("Failed to download XML")
        return

    logging.info("XML downloaded successfully")

    # Step 2: Get DLTINS file link
    logging.info("Step 2: Extracting DLTINS file link")
    dltins_link = downloader.get_DLTINS_file(xml_content)
    if not dltins_link:
        logging.error("Failed to get DLTINS file link")
        return

    logging.info(f"DLTINS file link: {dltins_link}")

    # Step 3: Download and Extract ZIP
    logging.info("Step 3: Downloading and extracting ZIP")
    extracted_xml_content = downloader.download_extract_zip(dltins_link)
    if not extracted_xml_content:
        logging.error("Failed to download or extract ZIP")
        return

    logging.info(f"Extracted XML content:\n{extracted_xml_content[:500]}")  # showing first 500 characters for brevity
    
def test_converting_xml2csv():
    # Sample XML content (shortened for clarity)
    xml_content = "DLTINS_20210117_01of01.xml"
    test_csv_path = "./output/test_output.csv"
    # download_extract_zip = GetData.download_extract_zip
    GetData.create_csv(xml_file=xml_content, csv_path=test_csv_path)

    
    assert os.path.exists(test_csv_path), "CSV file was not created!"
    df = pd.read_csv(test_csv_path)
    print(df)
    # print(GetData.converting_xml2csv)

def test_add_columns():
    """
    Test the add_columns function by applying it to a sample DataFrame read from a CSV file.

    This function:
    1. Reads a sample CSV file.
    2. Applies the add_columns function to the DataFrame.
    3. Validates the existence of the added columns.
    4. Prints the updated DataFrame for inspection.

    Raises:
        AssertionError: If the required test CSV file does not exist or the columns were not added.
    """

    try:
        test_csv_path = "./output/test_output.csv"

        assert os.path.exists(test_csv_path), f"CSV file '{test_csv_path}' does not exist!"

        df = pd.read_csv(test_csv_path)
        assert not df.empty, "Test CSV file is empty!"
        updated_df = GetData.add_columns(df)

        assert updated_df is not None, "add_columns function returned None!"
        assert 'a_count' in updated_df.columns, "'a_count' column was not added!"
        assert 'contains_a' in updated_df.columns, "'contains_a' column was not added!"

        

    except AssertionError as e:
        logging.error(f"Test failed: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

# Run the test
test_get_data()
test_converting_xml2csv()
test_add_columns()
