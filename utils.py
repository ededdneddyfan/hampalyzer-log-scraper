from requests.adapters import HTTPAdapter, Retry
import bs4
import requests

# TODO: Put session with retries/backoff in here to reduce code copy pasta
# other stuff that would be reused in here too...