import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

class HTMLTools:
    def __init__(self, brand: str):
        self.brand = brand
        self.config = self.set_scrape_config(brand)
        self.soup = None

    def set_scrape_config(self, brand: str) -> dict:
        config_path = Path(__file__).parent.parent / "dom_config.json"
        with open(config_path) as f:
            config = json.load(f)

        default = config.get("default", {})
        brand_override = config.get(brand, {})

        merged = {
            "json_ld": {**default.get("json_ld", {}), **brand_override.get("json_ld", {})},
            "dom": {
                **default.get("dom", {}),
                "fields": {
                    **default.get("dom", {}).get("fields", {}),
                    **brand_override.get("dom", {}).get("fields", {}),
                }
            }
        }
        return merged

    def load_html(self, html_path: str):
        self.soup = BeautifulSoup(Path(html_path).read_text(encoding="utf-8"), "lxml")

    def generate_catalog_html(self, brand: str) -> str:
        catalog_url = catalog_url(brand) 
        # helper function to navigate to the url using CDP patchright
        browser = await connect()
        if not browser:
          return
        successful = await fetch_html(catalog_url, browser)
        await browser.close()

        if successful:   
          batch_id = uuid() 
          return batch_id
        # gets url from src/scraper/url_builder function
        # navigates to CDP patchright and downloads to directory
        # returns the batch_id that was used to insert the file

    def check_catalog_html(self, brand: str, batch_id: str) -> bool:
        catalog_dir = Path(__file__).parent.parent.parent.parent / "db" / "html" / "catalog" / brand
        if not catalog_dir.exists():
            return False
        return any(f.stem.endswith(f"_{batch_id}") for f in catalog_dir.iterdir())

     def clean_catalog_html(self, brand: str, batch_id: str) -> list:
        # parse html and return listings
        pass

    ## AGENT TOOLS GO PAST HERE ##

    def get_json_ld(self) -> dict:
        script = self.soup.find("script", {"type": "application/ld+json"})
        if not script:
            return {}
        return json.loads(script.string)

    def get_json_ld_fields(self, path: list[str]) -> any:
        data = self.get_json_ld()
        for key in path:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data.get(key)
            if data is None:
                return None
        return data

    def get_card_testids(self) -> list[str]:
        card = self.soup.find("div", {"data-testid": re.compile(r"^plp-product/\d+$")})
        if not card:
            return []
        return list({
            el["data-testid"]
            for el in card.find_all(attrs={"data-testid": True})
        })

    def get_element_context(self, testid_suffix: str, chars: int = 20, limit: int = 3) -> list[str]:
        card = self.soup.find("div", {"data-testid": re.compile(r"^plp-product/\d+$")})
        if not card:
            return []

        card_html = str(card)
        pattern = re.compile(r'data-testid="[^"]*' + re.escape(testid_suffix) + r'"')
        results = []

        for match in pattern.finditer(card_html):
            start = max(0, match.start() - chars)
            end = min(len(card_html), match.end() + chars)
            results.append(card_html[start:end])
            if len(results) >= limit:
                break

        return results

""" DOM_CONFIG.JSON SHAPE FOR SELECTOR PREFERENCES, where "default" becomes the brand name like "undercover"
 {                                                                                                                
    "default": {                                                                                                   
      "json_ld": {                                                                                                 
        "script_type": "application/ld+json",                                                                      
        "listings_path": ["mainEntity", "itemListElement"],
        "fields": {                                                                                                
          "name": "name",                                                                                          
          "listing_url": "url",
          "image_url": "image"                                                                                     
        }                                                                                                        
      },                                                                                                           
      "dom": {                                                                                                   
        "card_testid": "^plp-product/\\d+$",                                                                       
        "fields": {                           
          "size": "-size",                                                                                         
          "price_original": "-price-original",                                                                   
          "price_final": "-price-final",                                                                           
          "price_callout": "-price-callout"
        }                                                                                                          
      }                                                                                                            
    }
    """