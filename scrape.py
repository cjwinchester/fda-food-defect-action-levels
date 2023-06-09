import json
import re

import requests
from bs4 import BeautifulSoup

FILENAME = 'fda-food-defect-levels'


def dl_page():
    ''' Download the HTML page of the handbook '''

    URL = 'https://www.fda.gov/food/ingredients-additives-gras-packaging-guidance-documents-regulatory-information/food-defect-levels-handbook'  # noqa
    
    r = requests.get(URL)
    r.raise_for_status()

    with open(f'{FILENAME}.html', 'w') as outfile:
        outfile.write(r.text)

    print(f'Downloaded {FILENAME}.html')

    return FILENAME


def scrape_data():
    ''' Scrape data from the page '''

    def parse_defect_row(tds):
        ''' Given a pair of tds, parse out the defect info '''
        defect, action = tds

        defect_name_split = [x for x in defect.text.split('\n') if x]
        defect_name = ' '.join(defect_name_split[0].split())

        action_level = ' '.join(action.text.strip().split())

        data = {
            'defect_name': defect_name,
            'action_level': action_level
        }

        if len(defect_name_split) > 1:
            method = ' '.join(defect_name_split[-1].replace('(', '').replace(')', '').split())  # noqa
            data['method'] = method

        method_link = defect.find('a')

        if method_link:
            urlstub = method_link['href']
            link = f'https://www.fda.gov{urlstub}'
            data['method_link'] = link

        return data

    with open(f'{FILENAME}.html', 'r') as infile:
        html = infile.read()

    soup = BeautifulSoup(html, 'html.parser')
    # extract that damn tree nut table, which causes problems
    table = soup.find('table')
    nut_table = table.find('table').extract()

    # and parse the table data into a string for later
    nut_stats = []
    for row in nut_table.find_all('tr')[1:]:
        nut_type, unshelled_pct, shelled_pct = row.find_all('td')

        shelled = shelled_pct.text.strip()
        unshelled = unshelled_pct.text.strip()

        if shelled == '--':
            shelled = None
        else:
            shelled = f'Shelled - {shelled}%'

        if unshelled == '--':
            unshelled = None
        else:
            unshelled = f'Unshelled - {unshelled}%'

        stats = ', '.join([x for x in [shelled, unshelled] if x])

        rowstr = f'- {nut_type.text.strip()}: {stats}'
        nut_stats.append(rowstr)

    tree_nut_str = '\n'.join(nut_stats)

    # main list to hold all the data
    data_out = []

    rows = table.find_all('tr')

    # sentinel dict to hold data as we cruise along
    commodity_data = {}

    for row in rows[1:]:

        # table heads represent a new commodity
        hed = row.find('th')

        if hed:

            # add the completed dict to the tracking list
            if commodity_data:
                data_out.append(commodity_data)

            product = ' '.join(hed.text.strip().split())

            # and start a new one
            commodity_data = {
                'commodity': product,
                'defect_action_levels': []
            }
    
        tds = row.find_all('td')

        # if there's only one td, it's a defect action row
        if len(tds) > 1:
            defect_data = parse_defect_row(tds)
            commodity_data['defect_action_levels'].append(defect_data)

            if commodity_data['commodity'].lower() == 'nuts, tree':
                commodity_data['defect_action_levels'][0]['action_level'] = commodity_data['defect_action_levels'][0]['action_level'] + f'\n{tree_nut_str}'  # noqa
        # otherwise, it's the defect source
        else:
            if not tds[0].text.strip():
                continue
            defect_source, significance = re.split(
                'significance',
                tds[0].text,
                flags=re.IGNORECASE
            )

            defect_source = ' '.join(
                defect_source.replace('DEFECT SOURCE:', '').split()
            )
            significance = ' '.join(significance.lstrip(':').split())

            commodity_data['defect_source'] = defect_source
            commodity_data['significance'] = significance

    with open(f'{FILENAME}.json', 'w') as outfile:
        json.dump(data_out, outfile, indent=4)


if __name__ == '__main__':
    dl_page()
    scrape_data()
