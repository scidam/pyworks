HERBARIUM_SEARCH_URL = 'http://botsad.ru/hitem/json/'

search_parameters = (('country', 'Вьетнам'),
                     ('colstart', '2017-01-01'),
                     ('colend', '2017-12-31')
                    )


try:
    # Python 3.x
    from urllib.parse import quote
    from urllib.request import urlopen
except ImportError:
    # Python 2.x
    from urllib import quote
    from urllib import urlopen
import pandas as pd


search_request_url = HERBARIUM_SEARCH_URL + '?' + '&'.join(map(lambda x: x[0] + '=' + quote(x[1].strip()), search_parameters))



import json
server_response = urlopen(search_request_url)
data = json.loads(server_response.read().decode('utf-8'))
server_response.close()



res = []

for item in data['data']:
    res.append(item['species_fullname'])
    
for item in data['data']:
    for jt in item['additionals']:
        res.append(jt['species_fullname'])    
    
for j in sorted(set(res)):
    print(j)
