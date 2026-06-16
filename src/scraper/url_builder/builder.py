BASE_URL = "https://www.therealreal.com"


def catalog_url(brand: str, sort: str = "newest") -> str:
    return f"{BASE_URL}/products?keywords={brand.replace(' ', '+')}&sort={sort}"
