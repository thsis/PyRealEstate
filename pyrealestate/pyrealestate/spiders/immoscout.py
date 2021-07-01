import scrapy
import re


def get_address(response):
    try:
        address = response.css("span.block.font-nowrap.print-hide::text").get().strip()
    except AttributeError:
        address = ""

    plz = response.css("span.zip-region-and-country::text").get()
    return ' '.join([address, plz])


def get_full_rent(response):
    num_pattern = re.compile(r"\d+")
    try:
        return num_pattern.findall(response.css("div.is24qa-warmmiete-main.is24-value.font-semibold::text").get())[0]
    except TypeError:
        return num_pattern.findall(response.css("div.is24qa-geschaetzte-warmmiete-main.is24-value.font-semibold").get())[0]


class ImmoSpider(scrapy.Spider):
    name = "immospider"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = ["https://www.immobilienscout24.de/Suche/de/baden-wuerttemberg/ludwigsburg-kreis/ludwigsburg/wohnung-mieten"]

    # def start_requests(self):
      #  yield scrapy.Request(self.url)

    def parse(self, response):
        for expose_id in response.css("li.result-list__listing::attr(data-id)").getall():
            link = f"https://www.immobilienscout24.de/expose/{expose_id}#/"
            yield response.follow(link, callback=self.parse_expose, cb_kwargs={"url": link})

    def parse_expose(self, response, url):
        num_pattern = re.compile(r"\d+")
        char_pattern = re.compile(r"[A-Za-z]+")

        yield {"url": url,
               "title": response.css("h1.font-semibold.font-xl.margin-bottom.margin-top-m.palm-font-l.font-line-s::text").get(),
               "expose_id": int(num_pattern.findall(response.css("div.is24-scoutid__content.padding-top-s::text").get())[0]),
               "address": get_address(response),
               "plz": num_pattern.findall(response.css("span.zip-region-and-country::text").get())[0].strip(),
               "city": char_pattern.findall(response.css("span.zip-region-and-country::text").get())[0].strip(),
               "kaltmiete": num_pattern.findall(response.css("div.is24qa-kaltmiete-main.is24-value.font-semibold.is24-preis-value::text").get())[0],
               "warmmiete": num_pattern.findall(response.css("div.is24qa-warmmiete-main.is24-value.font-semibold::text").get())[0],
               "zimmer": num_pattern.findall(response.css("div.is24qa-zi-main.is24-value.font-semibold::text").get())[0],
               "kaution": num_pattern.findall(response.css("div.is24qa-kaution-o-genossenschaftsanteile::text").get())[0],
               "qm": response.css("div.is24qa-flaeche-main.is24-value.font-semibold::text").get().replace("m²", "").strip(),
               "zusatzausstattung": list(set([p.css("span::text").getall() for p in response.css("div.criteriagroup.boolean-listing.padding-top-l")][0])),
               "text": '\n'.join(response.css("pre::text").getall())}
