import time
import traceback

import selenium.webdriver as web
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class NbaGraber(object):
    def __init__(self):
        self.browser = web.Chrome()
        self.urls = {
            'player_traditional':'/stats/players/traditional',
            'team_boxscore': '/stats/teams/boxscores',
            'team_advanced_boxscore_traditional' : '/stats/teams/boxscores-traditional',
            'team_advanced_boxscore_advanced' : '/stats/teams/boxscores-advanced',
            'team_advanced_boxscore_fourfactors' : '/stats/teams/boxscores-four-factors',
            'team_advanced_boxscore_misc' : '/stats/teams/boxscores-misc',
            'team_advanced_boxscore_scoring' : '/stats/teams/boxscores-scoring',
            'player_bios' : '/stats/players/bio'

        }
        self.base_url = 'https://www.nba.com'
        self.browser.implicitly_wait(10)
        self.save_out_filename = ''

    def save_df_to_csv(self, df, filename):
        if df is not None:
            df.to_csv(path_or_buf=self.save_out_filename + '-' + filename, index=False)

    def erase_unused_tags(self, soup):
        for tag in soup.find_all(attrs={'hidden': True}):
            tag.decompose()

        for tag in soup.find_all('tr', attrs={'class': 'Crom_colgroup__qYrzI'}):
            tag.decompose()
    def get_current_table_row(self):
        driver = self.browser

        try:
            driver.find_element(By.XPATH, "//select[@class='DropDown_select__4pIg9']/option[@value='-1']").click()
        except Exception as e:
            # print(e)
            print("Error Click button")
            print(driver.current_url)

        page = BeautifulSoup(self.browser.page_source, 'lxml')
        table = page.find('table', class_='Crom_table__p1iZz')
        if table is None:
            return None

        self.erase_unused_tags(table)
        names = [x.text.upper() for x in table.select('th')]
        trs = table.select('tbody tr')
        values = []
        for tr in trs:
            one = [x.get_text(strip=True) for x in tr.find_all('td')]
            values.append(one)
        try:
            df = pd.DataFrame(values, columns=names)
        except Exception as e:
            print("Create table Failed")
            print(names, values)
            print(driver.current_url)
            return None
        return df

    def iterate_all_years(self):
        driver = self.browser

        filter_div = driver.find_element(By.XPATH, '//div[@class="nba-stats-primary-split-block"]/div')
        year_options = filter_div.find_elements(By.TAG_NAME, 'option')

        for year in year_options:
            year.click()
            time.sleep(3)
            df = self.get_current_table_row()
            print(year.text + ' size ' + str(len(df)))
            if df.size == 0:
                print(year)
            filename = year.text + '.csv'
            self.save_df_to_csv(df, filename)


    def main(self):
        urls = self.urls
        driver = self.browser

        for path in urls:
            self.save_out_filename = path
            url = self.base_url + urls[path]
            driver.get(url)
            try:
                print('iterating ' + path)
                self.iterate_all_years()
            except Exception as e:
                print(self.browser.current_url)
                traceback.print_exc()

if __name__ == '__main__':
    players = NbaGraber()
    players.main()
