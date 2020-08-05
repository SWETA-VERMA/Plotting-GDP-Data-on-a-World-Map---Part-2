"""

Project for Week 4 of "Python Data Visualization".

Unify data via common country codes.



Be sure to read the project description page for further information

about the expected behavior of the program.



@author: sweta

"""

import csv
import math
import pygal


def build_country_code_converter(codeinfo):
    """
    Inputs:
      codeinfo      - A country code information dictionary
    Output:
      A dictionary whose keys are plot country codes and values
      are world bank country codes, where the code fields in the
      code file are specified in codeinfo.
    """

    new_data_dict = {}
    with open(codeinfo['codefile'], 'r') as data_file:
        data = csv.DictReader(data_file, delimiter=codeinfo['separator'],
                              quotechar=codeinfo['quote'])
        for row in data:
            keyid = row[codeinfo['plot_codes']]
            new_data_dict[keyid] = row[codeinfo['data_codes']]

    return new_data_dict



def reconcile_countries_by_code(codeinfo, plot_countries, gdp_countries):
    """
    Inputs:
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary whose keys are plot library country codes
                       and values are the corresponding country name
      gdp_countries  - Dictionary whose keys are country codes used in GDP data
    Output:
      A tuple containing a dictionary and a set.  The dictionary maps
      country codes from plot_countries to country codes from
      gdp_countries.  The set contains the country codes from
      plot_countries that did not have a country with a corresponding
      code in gdp_countries.
      Note that all codes should be compared in a case-insensitive
      way.  However, the returned dictionary and set should include
      the codes with the exact same case as they have in
      plot_countries and gdp_countries.
    """
    pre_plot_dict = build_country_code_converter(codeinfo)
    plot_dict = {}
    plot_set = set()   
    for key, value in plot_countries.items():
        for keycode, valcode in pre_plot_dict.items():
            if key.lower() == keycode.lower() and value != "" and valcode != "":
                for key1, value1 in gdp_countries.items():
                    if key1.lower() == valcode.lower() and value1 != "":
                        plot_dict[key] = key1

    for key, value in plot_countries.items():
        for keycode, valcode in pre_plot_dict.items():
            if key.lower() == keycode.lower() and valcode.upper() not in gdp_countries:
                plot_set.add(key)

    return plot_dict, set(plot_set)

def build_map_dict_by_code(gdpinfo, codeinfo, plot_countries, year):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year for which to create GDP mapping
    Output:
      A tuple containing a dictionary and two sets.  The dictionary
      maps country codes from plot_countries to the log (base 10) of
      the GDP value for that country in the specified year.  The first
      set contains the country codes from plot_countries that were not
      found in the GDP data file.  The second set contains the country
      codes from plot_countries that were found in the GDP data file, but
      have no GDP data for the specified year.
    """
    plot_dict = {}
    plot_dict_1 = {}
    plot_set_1 = set()
    plot_set_2 = set()
    new_data_dict = {}

    with open(gdpinfo['gdpfile'], 'r') as data_file:
        data = csv.DictReader(data_file, delimiter=gdpinfo['separator'],
                              quotechar=gdpinfo['quote'])
        for row in data:
            new_data_dict[row[gdpinfo['country_code']]] = row

    plot_dict, plot_set_1 = reconcile_countries_by_code(codeinfo, plot_countries, new_data_dict)

    plot_set_1.clear()
    val = ""
    for key, value in plot_countries.items():
        for codekey, codeval in plot_dict.items():
            if key in plot_dict:
                if key.lower() == codekey.lower():
                    val = codeval
                else:
                    val = ""
            else:
                plot_set_1.add(key)
        if val != "" and val not in new_data_dict:
            plot_set_1.add(key)


    for key, value in plot_dict.items():
        for key1, val1 in new_data_dict.items():
            if value.lower() == key1.lower():
                if val1[year] != '':
                    plot_dict_1[key] = math.log(float(val1[year]), 10)
                else:
                    plot_set_2.add(key)

    return plot_dict_1, set(plot_set_1), set(plot_set_2)

def render_world_map(gdpinfo, codeinfo, plot_countries, year, map_file):
    """
    Inputs:
      gdpinfo        - A GDP information dictionary
      codeinfo       - A country code information dictionary
      plot_countries - Dictionary mapping plot library country codes to country names
      year           - String year of data
      map_file       - String that is the output map file name
    Output:
      Returns None.
    Action:
      Creates a world map plot of the GDP data in gdp_mapping and outputs
      it to a file named by svg_filename.
    """
    plot_dict_1, plot_set_1, plot_set_2 = build_map_dict_by_code(gdpinfo,
                                                                 codeinfo, plot_countries, year)

    worldmap_chart = pygal.maps.world.World()
    title_map = 'GDP by country for ' + year + ' (log scale), unifiedby common country CODE'
    worldmap_chart.title = title_map
    label_map = 'GDP for ' + year
    worldmap_chart.add(label_map, plot_dict_1)
    worldmap_chart.add('Missing from World Bank Data', plot_set_1)
    worldmap_chart.add('No GDP Data', plot_set_2)
    worldmap_chart.render_in_browser()


def test_render_world_map():
    """
    Test the project code for several years
    """
    gdpinfo = {
        "gdpfile": "isp_gdp.csv",
        "separator": ",",
        "quote": '"',
        "min_year": 1960,
        "max_year": 2015,
        "country_name": "Country Name",
        "country_code": "Country Code"
    }

    codeinfo = {
        "codefile": "isp_country_codes.csv",
        "separator": ",",
        "quote": '"',
        "plot_codes": "ISO3166-1-Alpha-2",
        "data_codes": "ISO3166-1-Alpha-3"
    }

    # Get pygal country code map
    pygal_countries = pygal.maps.world.COUNTRIES

    # 1960
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1960", "isp_gdp_world_code_1960.svg")

    # 1980
    render_world_map(gdpinfo, codeinfo, pygal_countries, "1980", "isp_gdp_world_code_1980.svg")

    # 2000
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2000", "isp_gdp_world_code_2000.svg")

    # 2010
    render_world_map(gdpinfo, codeinfo, pygal_countries, "2010", "isp_gdp_world_code_2010.svg")
