import os
from datetime import datetime, timezone

import requests, json



class ChartsAPI:

    def __init__(self):
        self.api_url = "https://charts.ecmwf.int/opencharts-api/v1/"
        self.titlescache = None
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache = {}
        self.get_available_products()

    def get_available_products(self, override=False):
        if not override and os.path.exists(self.script_dir+"/../ProductList.json"):
            print("Opening by file")
            with open(os.path.join(self.script_dir, "../ProductList.json")) as file:
                return json.load(file)
        else:
            print("Requesting")
            request = requests.get(self.api_url+ 'packages/opencharts/products/')

            data = request.json()
            productlist = [product for product in data["products"] if product["opencharts"] == True]
            with open("ProductList.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(productlist, indent=4))
            return productlist
    def search_product(self, search_term):
        if not self.titlescache:
            self.titlescache = [(product["title"], product) for product in self.get_available_products()]
        numresults = 15
        results = []
        print("searching")
        cnt = 0
        for title, product in self.titlescache:
            cnt+=1
            #print(cnt)
            if len(results) == numresults:
                break
            if search_term.lower() in title.lower():
                results.append((title, product))
        return results
    def get_available_area(self, product):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        areas = [i["values"] for i in raw["axis"] if i["name"] in ["area", "projection"]][0]
        return areas
    def get_wide_description(self, product):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        desc = raw["description"]
        return desc
    def get_available_base_times(self, product):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        timeslabels = [time["label"] for time in [axis["values"] for axis in raw["axis"] if axis["name"]=="base_time"][0]]
        timesvalues = [time["value"] for time in [axis["values"] for axis in raw["axis"] if axis["name"]=="base_time"][0]]
        timesparsed = []
        for time in timesvalues:
            dt = datetime.strptime(time, "%Y%m%d%H%M")
            dt = dt.replace(tzinfo=timezone.utc)
            timesparsed.append((dt.strftime('%Y-%m-%dT%H:%M:%SZ'), dt.strftime("%Y%m%d%H%M")))
        return timesparsed
    def get_available_valid_times(self, product, base_time):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        for time in [axis["values"] for axis in raw["axis"] if axis["name"]=="base_time"][0]:
            if base_time == time["value"]:
                linked = time.get("linked_values", None)
                if linked is None: return None
                return [(i["label"], datetime.strptime(i["value"], "%Y%m%d%H%M").strftime('%Y-%m-%dT%H:%M:%SZ'))  for i in linked]
                #return time["linked_values"]
    def get_axis_list(self, product):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        axis = [(ax["name"], ax["title"]) for ax in raw["axis"]]
        return axis
    def get_available_values_random_axis(self, product, axisselected):
        if product not in self.cache.keys():
            raw = requests.get(self.api_url+ 'packages/opencharts/products/' + product )
            self.cache[product] = raw.json()
            raw = raw.json()
        else:
            raw = self.cache[product]
        axisnames = [ax["name"] for ax in raw["axis"]]
        axis = raw["axis"]
        if axisselected in axisnames:
            for i in axis:
                if axisselected == i["name"]:
                    return i










# https://charts.ecmwf.int/opencharts-api/v1/packages/opencharts/products/medium-mslp-wind850/

if __name__ == '__main__':
    api = ChartsAPI()
    validtime = api.get_available_base_times("medium-mslp-wind850")
    print(validtime)






