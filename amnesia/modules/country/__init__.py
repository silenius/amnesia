from .model import Country
from .resources import CountryEntity
from .resources import CountryResource
from .validation import CountrySchema

def includeme(config):
    config.include('.mapper')
    config.include('.views')
