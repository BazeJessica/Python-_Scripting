from functools import reduce
import pandas as pd

class Clean(object):
    def clean_and_merge(self, dataframes):

        for df in dataframes:
            # strip \xa0 from headers
            df.columns = df.columns.str.replace('\xa0', ' ')
            # conver WL into number
            df['W/L'] = df['W/L'].replace({'W':1, 'L':0})
            # print(df[['MATCH UP', 'GAME DATE']])


        df_merged = reduce(
            lambda  left,right:
            pd.merge(left,right, on=['MATCH UP', 'GAME DATE'], suffixes=('', '_DROP')),
            dataframes
        ).filter(regex='^(?!.*_DROP)')

        if df_merged.size == 0:
            print([x.size for x in dataframes])


        #print(df_merged.head)
        return df_merged

    def main(self):
        # year = [f"20{x:02}-{(x+1):02}" for x in range(3,24)]

        all_merged = pd.DataFrame()
        for year in range(3,24):
            # cconver 23 to 2023-24
            season = f"20{year:02}-{(year+1):02}"

            traditional = pd.read_csv('team_advanced_boxscore_traditional-' + season + '.csv')
            advanced = pd.read_csv('team_advanced_boxscore_advanced-' + season + '.csv')
            fourfactors = pd.read_csv('team_advanced_boxscore_fourfactors-' + season + '.csv')
            misc = pd.read_csv('team_advanced_boxscore_misc-' + season + '.csv')
            scoring = pd.read_csv('team_advanced_boxscore_scoring-' + season + '.csv')

            print('merging ' + season)
            df_merged = self.clean_and_merge([traditional, advanced, fourfactors, misc, scoring])
            #print(season)
            #print(df_merged.head)
            df_merged['season'] = season
            all_merged = pd.concat([df_merged, all_merged], ignore_index=True)
            # df_merged.to_csv('team_box_merged_' + season + '.csv')

        all_merged.to_csv('team_box_all_merged' + '.csv')

if __name__ == '__main__':
    clean = Clean()

    clean.main()