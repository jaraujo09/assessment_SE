import pandas as pd
import requests
import logging
from typing import Optional
import xmltodict


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
            return ""
        
        except KeyError as e:
            logging.error(f"Missing expected key in the XML structure: {e}")
            return ""

        