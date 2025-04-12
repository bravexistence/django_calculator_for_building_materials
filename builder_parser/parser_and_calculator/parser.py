import json
import time
import random
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.DEBUG,  # or WARNING
    format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class ProductInfo:
    """
    Class describing a product from the website.
    Fields:
      - name: product name
      - price: price (float or None if parsing fails)
      - url: URL of the product page
    """
    def __init__(self, name: str, price: float | None, url: str):
        self.name = name
        self.price = price
        self.url = url

    def __repr__(self):
        return f"ProductInfo(name='{self.name}', price={self.price}, url='{self.url}')"


class BaseProductParser:
    """
    Base parser class with shared logic for making requests and extracting prices.
    Child classes can handle JSON or ORM integration differently.
    """
    def __init__(self):
        self.session = requests.Session()

    def parse_product(self, name: str, url: str) -> ProductInfo:
        """
        Parses a single page and returns a ProductInfo object.
        If url is empty or request fails, returns price=None.
        """

        if not url:
            logger.warning(f"No URL specified for product '{name}'. Skipping parsing.")
            return None

        domain = urlparse(url).netloc
        verify_ssl = not (domain.endswith("elkom.kz") or domain.endswith("em-c.kz"))

        try:
            logger.debug(f"Requesting URL: {url} (verify_ssl={verify_ssl})")
            response = self.session.get(url, timeout=15, verify=verify_ssl)
        except requests.exceptions.RequestException as e:
            logger.warning(f"Error while requesting {url}: {e}")
            return ProductInfo(name=name, price=None, url=url)

        soup = BeautifulSoup(response.text, "html.parser")
        logger.debug(f"Domain detected: {domain}")

        if "admart.kz" in domain or "reklamag.kz" in domain:
            price_element = soup.select_one('[data-qaid="product_price"]')
        elif "alamet.kz" in domain:
            price_element = soup.select_one("div.white")
        elif "wurth.kz" in domain:
            price_element = soup.select_one(".product_price div div")
        elif "elkom.kz" in domain:
            price_element = soup.select_one(".price_value")
        elif "em-c.kz" in domain:
            price_element = soup.select_one(".price_value")
            if not price_element:
                parent = soup.select_one("div.price.font-bold.font_mxs")
                if parent and parent.has_attr("data-value"):
                    raw_price = parent["data-value"]
                    price_value = self._extract_digits(raw_price)
                    logger.debug(f"Extracted price from data-value: {price_value}")
                    return ProductInfo(name=name, price=price_value, url=url)
        else:
            logger.warning(f"Unknown domain, no parsing rules: {domain}")
            price_element = None

        if price_element:
            raw_price = price_element.get_text(strip=True)
            logger.debug(f"Raw price text: {raw_price}")
            price_value = self._extract_digits(raw_price)
        else:
            logger.debug(f"No price element found for {url}")
            price_value = None

        return ProductInfo(name=name, price=price_value, url=url)

    def _extract_digits(self, text: str) -> float | None:
        digits_only = "".join(ch for ch in text if ch.isdigit())
        logger.debug(f"Extracted digits: {digits_only}")
        return float(digits_only) if digits_only else None


class JSONProductParser(BaseProductParser):
    def __init__(self, json_path: str):
        super().__init__()
        self.json_path = json_path

    def parse_all(self):
        """
        1) Loads the JSON
        2) Iterates over the products
        3) Pauses for 4-6 seconds
        4) Parses each page
        5) Returns a list of ProductInfo objects
        """
        logger.debug(f"Loading products from JSON: {self.json_path}")
        with open(self.json_path, "r", encoding="utf-8") as f:
            products_data = json.load(f)

        results = []
        for idx, item in enumerate(products_data, 1):
            product_name = item["name"]
            product_url = item["url"]

            delay = random.uniform(4, 6)
            logger.debug(f"[{idx}] Sleeping for {delay:.2f}s before parsing {product_name}")
            time.sleep(delay)

            logger.debug(f"[{idx}] Parsing: {product_name} ({product_url})")
            product_info = self.parse_product(product_name, product_url)
            if product_info:
                logger.debug(f"[{idx}] Parsed: {product_info}")
                results.append(product_info)
            else:
                logger.debug(f"[{idx}] Skipped: {product_name} (no valid URL)")

        return results


class ORMProductParser(BaseProductParser):
    def __init__(self):
        super().__init__()

    def parse_queryset_and_save(self, queryset, verbose=False):
        """
        Iterates over Django queryset of Products, parses each URL,
        updates `price` in the DB, and saves the result.
        """
        total = queryset.count()
        for idx, product in enumerate(queryset, 1):
            if verbose:
                print(f"[{idx}/{total}] Обработка: {product.name}")

            time.sleep(random.uniform(4, 6))

            parsed = self.parse_product(product.name, product.url)
            if parsed is None:
                if verbose:
                    print(f"   → Пропущено: пустой или некорректный URL")
                continue

            product.price = parsed.price
            product.save()

            if verbose:
                print(f"   → Цена: {parsed.price}")


if __name__ == "__main__":
    parser = JSONProductParser("../list_of_links.json")
    all_products = parser.parse_all()

    print("Parsing results:")
    for product in all_products:
        print(product)
