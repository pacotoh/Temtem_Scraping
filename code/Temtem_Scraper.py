# Temtem scraper
from bs4 import BeautifulSoup
import sys
import pandas as pd
import requests
import re
import numpy as np
from selenium import webdriver

# URL GET Request
main_page = 'https://temtem.gamepedia.com'
species = '/Temtem_Species'
http_regex = re.compile('http*')
tier_page = 'https://temtactics.gg/tierlist'
tech_page = 'https://temtactics.gg/db/techniques'

def selenium_get_page(main_page):
    """Open the page and get the html with selenium (Javascript)"""
    driver = webdriver.Firefox()
    driver.get(main_page)
    html = driver.execute_script('return document.documentElement.outerHTML')
    driver.close()
    return html

def get_request(main_page, tail = ''):
    """Returns a bs with the content of the page"""
    rp = requests.get(main_page + tail)
    # BeautifulSoup content generation
    return BeautifulSoup(rp.content, 'html.parser')

def get_header(all_tr):
    """Returns the header of the tr list parameter"""
    stats_list = all_tr[1].findAll('th')    
    name = ['Number','Name']
    header = [i.get_text() for i in stats_list]
    # header modification to clarify the name of the columns
    header[0] = 'Type_1'
    header[1] = 'Type_2'
    header[-1] = 'Total' # The last column is the Sum of the stats
    name.extend(header)
    return name

def get_all_stats(all_tr, header):
    """Returns the stats of the Temtems"""
    lheader = len(header)
    temtems = all_tr[2:]
    dict_tem = {}
    for tm in temtems:
        stats = [i.get_text().rstrip() for i in tm.findAll('td')]
        if len(stats) < lheader:
            stats.insert(3, None)
        dict_tem[str(stats[0])] = stats
    return dict_tem

def get_dataframe(header, dict_temtems):
    """Returns a dataframe with the Temtems data in dict_temtems"""
    df_tm = pd.DataFrame(dict_temtems.values())
    df = df_tm.set_index(df_tm[0])
    df.drop(columns= [0], inplace=True)
    df.columns = header[1:]
    return df

def append_traits(df):
    """Returns the dataframe with the traits lists inserted as a column"""
    name_list = [i.strip() for i in df.Name.to_list()]
    dict_traits = {}
    for name in name_list:
        table = get_request(main_page,  '/' + name).find('table', {'class':'infobox-table'})
        values = table.findAll('a')
        lsval = [v.string for v in values if str(v.string) 
        not in ['None', '⮜', '⮞', 'FreeTem!'] 
        and not http_regex.findall(str(v.string)) 
        and str(v.string) not in name_list]
        dict_traits[name] = lsval
    df['traits'] = list(dict_traits.values())
    return df

def get_tierlist(main_page):
    """Returns a dict with the tiers tags and the Temtems belonging to each tier"""
    html = selenium_get_page(main_page)
    sel_soup = BeautifulSoup(html, 'html.parser')
    tier_lists = sel_soup.findAll('div', {'class': 'tier-list'})[0]
    
    # Get the list of list of h2 elements and select only the content inside
    tiers_category = [i.text for i in tier_lists.findAll('div', {'class': 'tier-category'})]
    ll_tiers = [i.contents[1].findAll('h2') for i in tier_lists.contents]

    # tiers_len is a list of all the temtems included in each tier, ordered by tier [S, A, B, C, D, ?]
    tiers_len = [len(i) for i in ll_tiers]
    all_tems = []

    # Create a list of the temtems inside the tierlists (not all the temtems included. Eg: pre-ev)
    for i in ll_tiers:
        for j in i:
            all_tems.append(j.text)

    # Last step: create a dict with the tier: [list of temtems of the tier]
    dict_tiers = {}
    counter = 0
    index = 0

    for category in tiers_category:
        dict_tiers[category] = all_tems[index:index + tiers_len[counter]]
        index = index + tiers_len[counter]
        counter = counter + 1
    return dict_tiers

def get_techniques(main_page):
    html = selenium_get_page(main_page)
    sel_soup = BeautifulSoup(html, 'html.parser')
    # even and odds are the rows from the table, we can pick both classes into the find
    even_odds = sel_soup.findAll('div', {'class': ['rt-tr -even', 'rt-tr -odd']})
    ls_eo = [[i.contents[0].text, i.contents[1].contents[0].get('alt'), i.contents[3].text, 
    i.contents[4].text, i.contents[5].text,
     i.contents[10].text] for i in even_odds]

    print(even_odds)


############################# Main #############################

#soup = get_request(main_page, species)

# Extracting the table with all Tems from https://temtem.gamepedia.com/Temtem_Species
#temtem_table = soup.findAll('table')[1]
#all_tr = temtem_table.findAll('tr')

# Dataframe creation with header and data
#header = get_header(all_tr)
#dict_temtems = get_all_stats(all_tr, header)
#df_tm = get_dataframe(header, dict_temtems)

# For each Temtem we can append the traits from https://temtem.gamepedia.com/[Temtem name]
#df = append_traits(df_tm)

# Extracting the Tier List from https://temtactics.gg/tierlist  
#tl = get_tierlist(tier_page)

get_techniques(tech_page)
