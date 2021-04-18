import geocoder
import csv

restaurants_file = "../../menu/menu_data/restaurant_list.tsv";
restaurants_info = []
headers = ['name','menu_link','type','address', 'lon','lat','is_location_valid']
if restaurants_file:
    with open(restaurants_file) as f:
        f_read = list(csv.reader(f, delimiter="\t"))
        restaurants_info= [{headers[0]:r_info[0],
                            headers[1]:r_info[1],
                            headers[2]:r_info[2],
                            headers[3]:r_info[3],
                            headers[4]:0,
                            headers[5]:0,
                            headers[6]:'false'
                            } for r_info in f_read]

for restaurant in restaurants_info:
    is_location_valid = geocoder.osm(restaurant['address']).latlng
    if is_location_valid is not None:
        restaurant['lon'] = is_location_valid[1]
        restaurant['lat'] = is_location_valid[0]
        restaurant['is_location_valid'] = 'true'

with open("updated_restaurant_list.tsv", 'w', newline='', encoding='utf-8') as f:
    d_writer = csv.DictWriter(f, headers, delimiter='\t')
    d_writer.writeheader()
    d_writer.writerows(restaurants_info)



