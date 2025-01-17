"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame(
        pd.read_csv("data/referendum.csv",
                    sep=";"))
    regions = pd.DataFrame(
        pd.read_csv("data/regions.csv",
                    sep=","))
    departments = pd.DataFrame(
        pd.read_csv("data/departments.csv",
                    sep=","))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    new_df = pd.merge(departments, regions,
                      how='left', left_on=['region_code'],
                      right_on=['code'],
                      suffixes=('_dep', '_reg'))
    keep_col = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    new_df = new_df[keep_col]

    return new_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    exclude = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM',
               'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    referendum = referendum.loc[~referendum['Department code'].isin(exclude)]
    regions_and_departments = regions_and_departments.loc[
        ~regions_and_departments['code_reg'].isin(['COM', '01',
                                                   '02', '03',
                                                   '04', '05', '06'])
        ]

    referendum.loc[:, 'Department code'] = referendum[
        'Department code'].apply(lambda x: x.zfill(2))

    newest_df = pd.merge(referendum, regions_and_departments,
                         how='left', left_on='Department code',
                         right_on='code_dep', suffixes=('', ''))

    return newest_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    keep = ['name_reg', 'Registered', 'Abstentions', 'Null',
            'Choice A', 'Choice B', 'code_reg']
    referendum_and_areas = referendum_and_areas[keep]

    new = referendum_and_areas.groupby(by=['code_reg', 'name_reg']).agg('sum')

    new.reset_index(inplace=True, level=['name_reg'])

    return new


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    gj = gpd.read_file('data/regions.geojson')
    both = pd.merge(gj,
                    referendum_result_by_regions,
                    right_on='code_reg',
                    left_on='code')
    both['ratio'] = both['Choice A']/(both['Choice A'] + both['Choice B'])
    both.plot(column='ratio', legend=True)
    return both


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
