from bs4 import BeautifulSoup
import pathlib
import re
import requests


INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Business_Address': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H'
}


def get_inspection_page(**kwargs):
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    params = INSPECTION_PARAMS.copy()
    for key, val in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = val
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.text


def parse_source(html):
    parsed = BeautifulSoup(html)
    return parsed


def load_inspection_page(name):
    file_path = pathlib.Path(name)
    return file_path.read_text(encoding='utf8')


def restaurant_data_generator(html):
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


if __name__ == '__main__':
    use_params = {
        'Inspection_Start': '1/1/2014',
        'Inspection_End': '1/1/2016',
        'Zip_Code': '98118'
    }
    # html = get_inspection_page(**use_params)
    html = load_inspection_page('inspection_page.html')
    parsed = parse_source(html)
    content_col = parsed.find("td", id="contentcol")
    data_list = restaurant_data_generator(content_col)
    print(data_list[0].prettify())
