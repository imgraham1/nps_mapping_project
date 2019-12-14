import sys
import json
import requests
import numpy as np
from secrets import *
from bs4 import BeautifulSoup
from itertools import compress
import plotly.graph_objs as go

class NationalSite():
    def __init__(self, type, name, desc, address_street = None, address_city = None, address_state = None, address_zip = None, url=None):
        self.url = url
        self.name = name
        self.type = type
        self.desc = desc
        self.address_zip = address_zip
        self.address_city = address_city
        self.address_state = address_state
        self.address_street = address_street

    def __str__(self):
        site_info = str(self.name) + " (" + str(self.type) + "): " + str(self.address_street) + ", " + str(self.address_city) + ", " + str(self.address_state) + " " + str(self.address_zip)
        return site_info

class NearbyPlace():
    def __init__(self, name, latitude, longitude):
        self.name = name
        self. latitude = latitude
        self.longitude = longitude

CACHE_FNAME = 'Cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}

def get_unique_key(catalog_url):
  return catalog_url

def make_request_using_cache(catalog_url):
    unique_ident = get_unique_key(catalog_url)

    if unique_ident in CACHE_DICTION:
        return CACHE_DICTION[unique_ident]

    else:
        resp = requests.get(catalog_url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]

def get_sites_for_state(state_abbr):

    state_abbr = state_abbr.lower()
    global sites
    sites = []
    places = []
    types = []
    locations = []
    descriptions = []
    links = []
    addresses = []
    towns = []
    states = []
    zips = []

    baseurl = "https://www.nps.gov/state/"

    catalog_url = baseurl + state_abbr + "/index.htm"
    page_text = make_request_using_cache(catalog_url)
    # page_text = requests.get(baseurl).text
    page_soup = BeautifulSoup(page_text, 'html.parser')
    page_info = page_soup.find_all('li', class_ = 'clearfix')

    make_request_using_cache(catalog_url)

    for x in page_info:
        h3 = x.find('h3')
        if h3 == None:
            pass
        else:
            place = h3.text
        places.append(place)

        h2 = x.find('h2')
        if h2 == None:
            pass
        else:
            type = h2.text
        types.append(type)

        h4 = x.find('h4')
        if h4 == None:
            pass
        else:
            location = h4.text
        locations.append(location)

        for x in page_info:
            p = x.find('p')
            if p == None:
                pass
            else:
                description = p.text
            descriptions.append(description)

    for x in page_info:
        z = x.find('a')['href']
        links.append(z)
    del links[-1]

    for x in links:

        baseurl = "https://www.nps.gov" + x + "planyourvisit/basicinfo.htm"
        page_text = requests.get(baseurl).text
        page_soup = BeautifulSoup(page_text, 'html.parser')
        try:
            address_info = page_soup.find('span', itemprop="streetAddress").text
            address_info = address_info.replace("\n", "")
            addresses.append(address_info)
        except:
            addresses.append("No address given")

        town = page_soup.find('span', itemprop="addressLocality").text
        town = town.replace("\n", "")
        towns.append(town)

        state = page_soup.find('span', itemprop="addressRegion").text
        state = state.replace("\n", "")
        states.append(state)

        zip = page_soup.find('span', itemprop="postalCode").text
        zip = zip.replace("     ", "")
        zip = zip.replace("\n", "")
        zips.append(zip)

    del places[-1]
    del types[-1]
    del locations[-1]
    del descriptions[-1]

    i = 0
    for x in places:
        instance = NationalSite(types[i], x, descriptions[i], addresses[i], towns[i],states[i], zips[i])
        sites.append(instance)
        i+=1
    return sites

CACHE_FNAME1 = 'Cache.json'
try:
    cache_file = open(CACHE_FNAME1, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION1 = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION1 = {}

def params_unique_combination1(coordurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return coordurl + "_" + "_".join(res)

def make_request_using_cache1(coordurl, params):
    global unique_ident
    unique_ident = params_unique_combination1(coordurl, params)

    if unique_ident in CACHE_DICTION1:
        global result1
        result1 = CACHE_DICTION1[unique_ident]
        return result1
    else:
        resp = requests.get(coordurl, params)
        CACHE_DICTION1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        # global result1
        result1 = CACHE_DICTION1[unique_ident]
        return result1

def params_unique_combination2(sitesurl, params2):
    alphabetized_keys = sorted(params2.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params2[k]))
    return sitesurl + "_" + "_".join(res)

def make_request_using_cache2(sitesurl, params2):
    global unique_ident
    unique_ident = params_unique_combination2(sitesurl, params2)

    if unique_ident in CACHE_DICTION1:
        global siteresult1
        siteresult1 = CACHE_DICTION1[unique_ident]
        return siteresult1
    else:
        resp = requests.get(sitesurl, params2)
        CACHE_DICTION1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        siteresult1 = CACHE_DICTION1[unique_ident]
        return siteresult1

def get_nearby_places_for_site(national_site):

    global nearby
    nearby = []
    global nearbylat
    nearbylat = []
    global nearbylng
    nearbylng = []
    global nearby_sites
    nearby_sites = []

    coordurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"

    params = {}
    params['fields'] = 'geometry'
    params['inputtype'] = 'textquery'
    params['input'] = national_site.name + ' ' + national_site.type
    params['key'] = google_places_key

    nearby_data = make_request_using_cache1(coordurl, params)

    if nearby_data['status'] != 'OK':
        return []

    else:

        lat = nearby_data['candidates'][0]['geometry']['location']['lat']
        lng = nearby_data['candidates'][0]['geometry']['location']['lng']

        sitesurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="  + str(lat) + "," + str(lng)
        params2 = {}
        params2['radius'] = '10000'
        params2['key'] = google_places_key

        nearby_data1 = make_request_using_cache2(sitesurl, params2)
        for x in nearby_data1['results']:

            place = NearbyPlace(x['name'], x['geometry']['location']['lat'], x['geometry']['location']['lng'])
            nearby_sites.append(place)
            nearby.append(x['name'])

        return nearby_sites

def params_unique_combination3(graph_coordurl, params3):
    alphabetized_keys = sorted(params3.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params3[k]))
    return graph_coordurl + "_" + "_".join(res)

def make_request_using_cache3(graph_coordurl, params3):
    global unique_ident
    unique_ident = params_unique_combination3(graph_coordurl, params3)

    if unique_ident in CACHE_DICTION1:
        global result1
        result1 = CACHE_DICTION1[unique_ident]
        return result1
    else:
        resp = requests.get(graph_coordurl, params3)
        CACHE_DICTION1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        result1 = CACHE_DICTION1[unique_ident]
        return result1

def plot_sites_for_state(state_abbr):
    get_sites_for_state(state_abbr)

    names = []
    graph_lat = []
    graph_lng = []

    i = 0
    for x in sites:
        names.append(x.name)

        x.name.replace(" ", "+")

        graph_coordurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

        params3 = {}
        params3['query'] = x.name
        params3['type'] = 'park'
        params3['key'] = google_places_key

        make_request_using_cache3(graph_coordurl, params3)
        if result1['status'] == "ZERO_RESULTS":
            graph_lat.append("no lat")
            graph_lng.append("no lng")
        else:
            graph_lat.append(result1['results'][0]['geometry']['location']['lat'])
            graph_lng.append(result1['results'][0]['geometry']['location']['lng'])


    bools = []
    for x in graph_lat:
        if type(x) == str:
            bools.append(False)
        else:
            bools.append(True)

    names = list(compress(names, bools))
    graph_lat = list(compress(graph_lat, bools))
    graph_lng = list(compress(graph_lng, bools))

    min_lat = float(min(graph_lat))
    max_lat = float(max(graph_lat))
    min_lon = float(min(graph_lng))
    max_lon = float(max(graph_lng))

    lat_axis = [min_lat -1, max_lat + 1]
    lon_axis = [max_lon + 1, min_lon -1]

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    trace = dict(
        type = 'scattermapbox',
        lon = graph_lng,
        lat = graph_lat,
        text = names,
        hoverinfo = 'text',
        mode = 'markers',
        marker = dict(
            size = 12,
            symbol = 'star',
            color = 'blue'
        ))

    data = [trace]

    fig = go.Figure(data=data)

    fig.update_layout(
        title = 'National Parks',
        geo_scope='usa',
        )

    layout = dict(
        title = 'National Parks',
        autosize=True,
        showlegend = False,
        mapbox=dict(
            accesstoken=MAPBOX_TOKEN,
            bearing=0,
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            pitch=0,
            zoom=5,
          )
    )
    fig.update_layout(layout)
    fig.show()

def params_unique_combination4(graph_coordurl, params4):
    alphabetized_keys = sorted(params4.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params4[k]))
    return graph_coordurl + "_" + "_".join(res)

def make_request_using_cache4(graph_coordurl, params4):
    global unique_ident
    unique_ident = params_unique_combination4(graph_coordurl, params4)

    if unique_ident in CACHE_DICTION1:
        global result1
        result1 = CACHE_DICTION1[unique_ident]
        return result1
    else:
        resp = requests.get(graph_coordurl, params4)
        CACHE_DICTION1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        result1 = CACHE_DICTION1[unique_ident]
        return result1

def params_unique_combination5(sitesurl, params5):
    alphabetized_keys = sorted(params5.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params5[k]))
    return sitesurl + "_" + "_".join(res)

def make_request_using_cache5(sitesurl, params5):
    global unique_ident
    unique_ident = params_unique_combination5(sitesurl, params5)

    if unique_ident in CACHE_DICTION1:
        global siteresult1
        siteresult1 = CACHE_DICTION1[unique_ident]
        return siteresult1
    else:
        resp = requests.get(sitesurl, params5)
        CACHE_DICTION1[unique_ident] = json.loads(resp.text)
        dumped_json_cache = json.dumps(CACHE_DICTION1)
        fw = open(CACHE_FNAME1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        siteresult1 = CACHE_DICTION1[unique_ident]
        return siteresult1

def plot_nearby_for_site(site_object):

    nearbylat = []
    nearbylng = []
    nearby_sites = []

    names = []
    graph_lat = []
    graph_lng = []

    names.append(site_object.name)
    site_object.name.replace(" ", "+")
    graph_coordurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"

    params4 = {}
    params4['fields'] = 'geometry'
    params4['inputtype'] = 'textquery'
    params4['input'] = site_object.name + ' ' + site_object.type
    params4['key'] = google_places_key

    make_request_using_cache4(graph_coordurl, params4)

    if result1['status'] != 'OK':
        graph_lat.append("no lat")
        graph_lng.append("no lng")
    else:
        graph_lat.append(result1['candidates'][0]['geometry']['location']['lat'])
        graph_lng.append(result1['candidates'][0]['geometry']['location']['lng'])

        bools = []
        for x in graph_lat:
            if type(x) == str:
                bools.append(False)
            else:
                bools.append(True)
                names = list(compress(names, bools))
                graph_lat = list(compress(graph_lat, bools))
                graph_lng = list(compress(graph_lng, bools))

    if not names:
        print('There was no result for your search')
        sys.exit()

    lat = result1['candidates'][0]['geometry']['location']['lat']
    lng = result1['candidates'][0]['geometry']['location']['lng']

    sitesurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="  + str(lat) + "," + str(lng)
    params5 = {}
    params5['radius'] = '10000'
    params5['key'] = google_places_key
    make_request_using_cache5(sitesurl, params5)
    for x in siteresult1['results']:
        nearby_sites.append(x['name'])
        nearbylat.append(x['geometry']['location']['lat'])
        nearbylng.append(x['geometry']['location']['lng'])

    min_lat = float(min(nearbylat))
    max_lat = float(max(nearbylat))
    min_lon = float(min(nearbylng))
    max_lon = float(max(nearbylng))

    lat_axis = [min_lat -1, max_lat + 1]
    lon_axis = [max_lon + 1, min_lon -1]

    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2

    trace = dict(
        type = 'scattermapbox',
        # locationmode = 'USA-states',
        lon = graph_lng,
        lat = graph_lat,
        text = names,
        hoverinfo = 'text',
        mode = 'markers',
        marker = dict(
            size = 12,
            symbol = 'star',
            color = 'blue'
        ))

    trace2 = dict(
        type = 'scattermapbox',
        lon = nearbylng,
        lat = nearbylat,
        text = nearby_sites,
        hoverinfo = 'text',
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'circle',
            color = 'red'
        ))

    data = [trace, trace2]

    fig = go.Figure(data=data)

    layout = dict(
        title = 'National Parks',
        geo_scope='usa',
        autosize=True,
        showlegend = False,
        mapbox=dict(
            accesstoken=MAPBOX_TOKEN,
            bearing=0,
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            pitch=0,
            zoom=11,
          )
    )
    fig.update_layout(layout)
    fig.show()


commands = "\n List of acceptable commands: \n\n\t List <stateabbr>\n \t\t --available anytime \n \t\t --lists all National Sites in a state \n \t\t --valid inputs: a two-letter state abbreviation \n\t Nearby <result_number> \n\t\t --available only if there is an active result set \n\t\t --lists all Places near a given result \n\t\t --valid input for <result number>: an integer 1 to len(result_set_size) \n\t Map \n\t\t --available only if there is an active result set \n\t\t --displays the current results on a map\n\t Exit \n\t\t --exits the program \n\t Help \n\t\t --lists available commands (these instructions)\n"




state_abbr = ['al', 'ak', 'az', 'ar', 'ca' , 'co', 'ct', 'de', 'fl', 'ga', 'hi', 'id', 'il', 'in', 'ia', 'ks', 'ky', 'la', 'me', 'md', 'ma', 'mi', 'mn', 'ms', 'mo', 'mt', 'ne', 'nv', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'oh', 'ok', 'or', 'pa', 'ri', 'sc', 'sd', 'tn', 'ut', 'vt', 'va', 'wa', 'wv', 'wi', 'wy', 'tx']

states = {'al' : 'Alabama', 'ak' : 'Alaska', 'az' : 'Arizona', 'ar' : 'Arkansas', 'ca' : 'California', 'co' : 'Colorado', 'ct' : 'Connecticut', 'de' : 'Deleware', 'fl' : 'Florida', 'ga': 'Georgia', 'hi' : 'Hawaii', 'id' : 'Idaho', 'il' : 'Illinois', 'in' : 'Indiana', 'ia' : 'Iowa', 'ks' : 'Kansas', 'ky' : 'Kentucky', 'la' : 'Louisiana', 'me' : 'Maine', 'md' : 'Maryland', 'ma' : 'Massachusettes', 'mi' : 'Michigan', 'mn' : 'Minnesota', 'ms' : 'Mississippi', 'mo' : 'Missouri', 'mt' : 'Montana', 'ne' : 'Nebraska', 'nv' : 'Nevada', 'nh' : 'New Hampshire', 'nj' : 'New Jersey', 'nm' : 'New Mexico', 'ny' : 'New York', 'nc' : 'North Carolina', 'nd' : 'North Dakota', 'oh' : 'Ohio', 'ok' : 'Oklahoma', 'or' : 'Oregon', 'pa' : 'Pennsylvania', 'ri' : 'Rhode Island', 'sc' : 'South Carolina', 'sd' : 'South Dakota', 'tn' : 'Tennessee', 'ut' : 'Utah', 'vt' : 'Vermont', 'va' : 'Virginia', 'wa' : 'Washington', 'wv' : 'West Virginia', 'wi' : 'Wisconsin', 'wy' :'Wyoming', 'tx' : 'Texas'}



if __name__ == '__main__':
    print(commands)
    while True:
        print('\n')
        z = input('Enter command (or "help" for options): ')
        print('\n')
        z.lower()
        z = z.split()

        if z[0] == 'list':
            abbr = z[1]
            if z[1] in state_abbr:
                print("\n National sites in " + states[abbr])
                # state = input('Enter state abbreviation you would like to search: ')
                get_sites_for_state(z[1])

            else:
                print('Please enter a valid state abbreviation')
                print('\n')

            num = 1
            for x in sites:
                print('['+str(num)+'] ' +" "+ str(x))

                num+=1
                listed = True
                last = "parks"

            print('\n Type "nearby <result number>” to search for places near one of the national sites above, “map” to map the list of national sites, or ‘list <state>” to do a search for another state \n')

        elif z[0] == 'nearby':
            if 'listed' not in vars():
                print("List national sites for a state first!")

            elif listed == True:
                try:
                    which = int(z[1]) - 1
                    print("\n Places nearby " + sites[which].name + "\n")
                    get_nearby_places_for_site(sites[which])



                    last = "nearby"
                    num = 1
                    for x in nearby:
                        print('['+str(num)+'] '+ x)
                        num+=1
                    if nearby:
                        print('\n Type “map” to map the nearby sites, or ‘list <state>” to do a search for another state \n')
                    if not nearby:
                        print('No nearby places!')
                except IndexError:
                    print('Please enter a valid number')


        elif z[0] == 'map':
            if 'listed' not in vars():
                print('\n')
                print("List national sites for a state first!")
                print('\n')
            if last == "parks":
                plot_sites_for_state(abbr)
            elif last == "nearby":
                plot_nearby_for_site(sites[which])

        elif z[0] == 'exit':
            print('\n')
            print("Thank you!")
            print('\n')
            sys.exit()

        elif z[0] == 'help':
            print(commands)

        elif z[0] != 'list' or 'nearby' or 'map' or 'exit' or 'help':
            print('Please enter a valid command! For a list of acceptable inputs type "help"')
    #end
