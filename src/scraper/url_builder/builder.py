BASE_URL = "https://www.therealreal.com"

# this file just helps build urls from therealreal 
# chose a separate file in case they change their structure and so its more dynamic 
def catalog_url(brand: str, sort: str = "newest") -> str:
    return f"{BASE_URL}/products?keywords={brand.replace(' ', '+')}&sort={sort}"
