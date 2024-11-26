import pandas as pd
import requests
import logging
from typing import Optional
import xmltodict
from zipfile import ZipFile
from io import BytesIO
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

class GetData:
    """
    This class is used to download and process the XML file from the given URL
    """
    def __init__(self, url: str):
        """
        This function is used to initialize the GetData class

        :param url: URL of the XML file
        """
        self.url = url

    def download_xml(self) -> Optional[str]:
        """
        Downloads the XML file from the given URL
        
        :return: content of the XML file as str or None if the download not successful
        """
        try:
            logging.info(f"Downloading XML file from [{self.url}]...")
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()  # for bad HTTP responses
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading XML file: {e}")
            return None

    
    def get_DLTINS_file(self, xml_file:str) -> str:
        """
        This function is used to get the DLTINS file from the XML file
        
        :param xml_file: XML file path

        :return: DLTINS file as string
        """
        try:
            logging.info(f"Processing XML file...")
            data = xmltodict.parse(xml_file)
            docs = data.get('response', {}).get('result', {}).get('doc', [])

            dltins_count = 0
            second_dltins_link = None

            for doc in docs:  
                for item in doc.get('str', []):  # iteration over str fieds in the docs 
                    # if item is file_type and its name is DLTINS, increment the count until 2 (required)
                    if item.get('@name') == 'file_type' and item.get("#text") == "DLTINS":
                        dltins_count += 1
                        if dltins_count == 2:
                            for sub_item in doc.get('str', []):
                                if sub_item.get('@name') == 'download_link':  #in the 2nd DLTINS file, get the download link
                                    second_dltins_link = sub_item.get('#text')
                                    break
                            if second_dltins_link:
                                break
                if second_dltins_link:
                    break

            if second_dltins_link:
                logging.info(f"Second DLTINS file found: {second_dltins_link}")
                return second_dltins_link
            else:
                logging.error("Second DLTINS file not found")
                return ""
            
        except Exception as e:
            logging.error(f"Error processing XML file: {e}")
            return None
        
        except KeyError as e:
            logging.error(f"Missing expected key in the XML structure: {e}")
            return None


    def download_extract_zip(self, url_zip:str) -> Optional[str]:
        """
        Downloads the ZIP file from the URL and extracts the content

        :param url_zip: URL of the ZIP file

        :return: content of the ZIP file as str or None if the download not successful
        """
        try:
            logging.info(f"Downloading ZIP file from [{url_zip}]...")
            response = requests.get(url_zip, timeout=10)
            response.raise_for_status() 

            with ZipFile(BytesIO(response.content)) as z:
                for file_name in z.namelist():  # iterate over the files in the ZIP
                    if file_name.endswith('.xml'):
                        logging.info(f"Extracting -> [{file_name}]")
                        with z.open(file_name) as xml_file:
                            return xml_file.read().decode("utf-8")
            logging.error(f"No XML file found")
            return None
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading ZIP file: {e}")
            return None
        
    
    def create_csv(xml_file, csv_path):

        """Creates CSV from XML File.

        Args:
            xml_file (str): Path of XML file.
            csv_path (str): Path to write the CSV file.

        Returns:
            str: Absolute path of the created CSV file, or None if failed.
        """
        try:
            # Ensure the CSV directory exists
            if not os.path.exists(csv_path):
                logging.info("Creating CSV file path.")
                os.makedirs(csv_path)

            # Extract the CSV file name
            # csv_fname = os.path.basename(xml_file).rsplit(".", 1)[0] + ".csv"
            csv_file = os.path.join(csv_path)

            logging.info("Loading the XML file.")
            xml_iter = ET.iterparse(xml_file, events=("start",))

            csv_columns = [
                "FinInstrmGnlAttrbts.Id",
                "FinInstrmGnlAttrbts.FullNm",
                "FinInstrmGnlAttrbts.ClssfctnTp",
                "FinInstrmGnlAttrbts.CmmdtyDerivInd",
                "FinInstrmGnlAttrbts.NtnlCcy",
                "Issr",
            ]

            extracted_data = []
            logging.info("Parsing the XML file and extracting data.")

            for event, element in xml_iter:
                if event == "start" and "TermntdRcrd" in element.tag:
                    data = {}
                    for elem in element:
                        if "FinInstrmGnlAttrbts" in elem.tag:
                            for child in elem:
                                if "Id" in child.tag:
                                    data[csv_columns[0]] = child.text
                                elif "FullNm" in child.tag:
                                    data[csv_columns[1]] = child.text
                                elif "ClssfctnTp" in child.tag:
                                    data[csv_columns[2]] = child.text
                                elif "CmmdtyDerivInd" in child.tag:
                                    data[csv_columns[3]] = child.text
                                elif "NtnlCcy" in child.tag:
                                    data[csv_columns[4]] = child.text
                        elif "Issr" in elem.tag:
                            data[csv_columns[5]] = elem.text
                    extracted_data.append(data)

            logging.info("All required data extracted. Creating DataFrame.")
            df = pd.DataFrame(extracted_data, columns=csv_columns).dropna()

            logging.info("Writing data to CSV file.")
            logging.info(csv_file)
            df.to_csv(csv_file, index=False)

            logging.info(f"CSV file created successfully at {csv_file}")
            return csv_file

        except ET.ParseError as e:
            logging.error(f"Failed to parse XML file: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

        return None
    
    def add_columns(df:str)->pd.DataFrame:
        """
        Adds a column "a_count" containing the number of times the lower-case character “a” 
        is present in the corresponding column `FinInstrmGnlAttrbts.FullNm` (0 when missing).
        Then add a columns `contains_a`, where for each row, this column is “YES” if `a_count` is
        greater than 0, “NO” if not.

        :param df: DataFrame containing the data

        :returns: pandas dataframe with the added columns

        """
        try: 
            logging.info("Adding columns 'a_count' and 'contains_a'...")

            if 'FinInstrmGnlAttrbts.FullNm' not in df.columns:
                logging.error("'FinInstrmGnlAttrbts.FullNm' column is missing!")
                return None
        
            df['a_count'] = df['FinInstrmGnlAttrbts.FullNm'].apply(
                lambda x: str(x).lower().count('a') if pd.notnull(x) else 0)
            df['contains_a'] = df['a_count'].apply(lambda x: 'YES' if x > 0 else 'NO')

            logging.info("Columns added")

            logging.info("Saving new csv")
            df.to_csv("./output/updated_output.csv", index=False)
            logging.info("New csv saved with all info")

            return df
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None