import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from dev import *

class TestGetData(unittest.TestCase):
    def setUp(self):
        self.url = "http://example.com/sample.xml"
        self.get_data = GetData(self.url)

    @patch("requests.get")
    def test_download_xml_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "<xml>Data</xml>"
        result = self.get_data.download_xml()
        self.assertEqual(result, "<xml>Data</xml>")

    @patch("requests.get")
    def test_download_extract_zip_success(self, mock_get):
        mock_zip_data = BytesIO()
        with ZipFile(mock_zip_data, 'w') as mock_zip:
            mock_zip.writestr("file.xml", "<xml>Data</xml>")
        mock_zip_data.seek(0)

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = mock_zip_data.getvalue()

        result = self.get_data.download_extract_zip("http://example.com/file.zip")
        self.assertEqual(result, "file.xml")  

    @patch("xml.etree.ElementTree.iterparse")
    @patch("pandas.DataFrame.to_csv")
    @patch("os.makedirs")
    def test_create_csv_success(self, mock_makedirs, mock_to_csv, mock_iterparse):
        mock_iterparse.return_value = iter([
            ("start", MagicMock(tag="TermntdRcrd", __iter__=lambda x: iter([]))),
        ])

        xml_file = "sample.xml"
        csv_path = "./output/test.csv"

        result = GetData.create_csv(xml_file, csv_path)
        self.assertEqual(result, csv_path) 

    def test_add_columns_success(self):
        df = pd.DataFrame({
            "FinInstrmGnlAttrbts.FullNm": ["Alpha", "Beta", "Gamma", None]
        })
        updated_df = GetData.add_columns(df) 
        self.assertIn('a_count', updated_df.columns)
        self.assertIn('contains_a', updated_df.columns)
        self.assertEqual(updated_df['a_count'].tolist(), [2, 1, 2, 0])
        self.assertEqual(updated_df['contains_a'].tolist(), ['YES', 'YES', 'YES', 'NO'])

    @patch("xmltodict.parse")
    def test_get_DLTINS_file_success(self, mock_xmltodict):
        mock_xmltodict.return_value = {
            'response': {
                'result': {
                    'doc': [
                        {'str': [{'@name': 'file_type', '#text': 'DLTINS'},
                                 {'@name': 'download_link', '#text': 'http://example.com/dltins1.zip'}]},
                        {'str': [{'@name': 'file_type', '#text': 'DLTINS'},
                                 {'@name': 'download_link', '#text': 'http://example.com/dltins2.zip'}]}
                    ]
                }
            }
        }
        result = self.get_data.get_DLTINS_file("<xml>mock data</xml>")
        self.assertEqual(result, "http://example.com/dltins2.zip")


if __name__ == "__main__":
    unittest.main()
