import json
import re
import sys
import uuid
from datetime import date
from pathlib import Path
from bs4 import BeautifulSoup

# repo root added so CDP_script.py (at root) is importable from here
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from CDP_script import connect, fetch_html
from src.scraper.url_builder.builder import catalog_url as build_catalog_url

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

    async def generate_catalog_html(self, brand: str) -> str:
        url = build_catalog_url(brand)
        browser = await connect()
        if not browser:
            raise RuntimeError("Could not connect to Chrome (port 9222).")
        try:
            html = await fetch_html(url, browser)
        finally:
            await browser.close()

        batch_id = uuid.uuid4().hex[:5]
        date_str = date.today().strftime("%m%d%y")
        out_dir = _REPO_ROOT / "db" / "html" / "catalog" / brand
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{date_str}_{batch_id}.html"
        out_path.write_text(html, encoding="utf-8")
        print(f"[+] Saved {len(html):,} bytes -> {out_path}")
        return batch_id

    def check_catalog_html(self, brand: str, batch_id: str) -> bool:
        catalog_dir = Path(__file__).parent.parent.parent.parent / "db" / "html" / "catalog" / brand
        if not catalog_dir.exists():
            return False
        return any(f.stem.endswith(f"_{batch_id}") for f in catalog_dir.iterdir())

    def get_catalog_html_path(self, brand: str, batch_id: str) -> Path | None:
        catalog_dir = Path(__file__).parent.parent.parent.parent / "db" / "html" / "catalog" / brand
        if not catalog_dir.exists():
            return None
        return next((f for f in catalog_dir.iterdir() if f.stem.endswith(f"_{batch_id}")), None)

    def clean_catalog_html(self, brand: str, batch_id: str) -> list:
        """Parse the saved catalog HTML for this brand+batch_id into a list of listing dicts."""
        path = self.get_catalog_html_path(brand, batch_id)
        if path is None:
            raise FileNotFoundError(f"No catalog HTML for {brand}/{batch_id}")
        self.load_html(str(path))

        cfg = self.config
        json_ld_cfg = cfg["json_ld"]
        raw = self.get_json_ld_fields(json_ld_cfg["listings_path"]) or []
        field_map = json_ld_cfg.get("fields", {})

        card_pattern = re.compile(cfg["dom"]["card_testid"])
        cards = self.soup.find_all("div", {"data-testid": card_pattern})

        # config field name -> output dict key (everything else maps 1:1)
        key_alias = {"price_original": "price", "price_final": "final_price"}

        listings = []
        for i, card in enumerate(cards):
            meta = raw[i] if i < len(raw) else {}
            row = {
                "name": meta.get(field_map.get("name", "name")),
                "brand": brand,
                "listing_url": meta.get(field_map.get("listing_url", "url")),
                "image_url": meta.get(field_map.get("image_url", "image")),
            }
            for cfg_field, testid_suffix in cfg["dom"].get("fields", {}).items():
                el = card.find(attrs={"data-testid": re.compile(testid_suffix + "$")})
                value = el.get_text(strip=True) if el else None
                row[key_alias.get(cfg_field, cfg_field)] = value
            listings.append(row)

        return listings

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