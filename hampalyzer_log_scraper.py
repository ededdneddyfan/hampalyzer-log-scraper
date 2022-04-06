from match_parser import match_parser
from requests.adapters import HTTPAdapter, Retry
import requests
import time


def main():
    # TODO: Hit API slowly, and nicely
    # There are currently 326 pages. For now I will just hard-code this as a proof of concept
    # but I should be reading in page by page until there's no more next page button
    # MAX_PAGES = 326
    MAX_PAGES = 1
    current_page = 1
    while current_page <= MAX_PAGES:
        # Sometimes the hampalyzer is unavailable - give it a chance to load up
        session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        session.mount('http://', HTTPAdapter(max_retries=retries))
        current_url = f"http://app.hampalyzer.com/api/logs/{current_page}"
        api_response = session.get(current_url)
        for match in api_response.json():
            # Don't hammer the site
            time.sleep(1)
            # For now, only parse logs from Coach's or Inhouse
            if 'Coach' in match['parsedlog'] or 'Inhouse' in match['parsedlog']:
                team_a, team_b = match_parser(f"http://app.hampalyzer.com/parsedlogs/{match['parsedlog']}/")
                print(team_a, team_b)
            else:
                continue
        current_page += 1


if __name__ == "__main__":
    main()
