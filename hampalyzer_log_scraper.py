from match_parser import match_parser
from requests.adapters import HTTPAdapter, Retry
import json
import requests
import time


def main():
    # TODO: Hit API slowly, and nicely
    # There are currently 326 pages. For now I will just hard-code this as a proof of concept
    # but I should be reading in page by page until there's no more next page button
    # MAX_PAGES = 326
    MAX_PAGES = 326
    current_page = 1
    # player keys are their steam_id, aliases are all the names, and they have wins/losses/ties (per server)
    players = {}
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
                is_coaches = 'Coach' in match['parsedlog']
                is_inhouse = 'Inhouse' in match['parsedlog']
                team_a, team_b = match_parser(f"http://app.hampalyzer.com/parsedlogs/{match['parsedlog']}/")
                for player_a, player_b in zip(team_a, team_b):
                    # TODO: this is so lazy, fix later
                    try:
                        players[player_a['steam_id']]['aliases'].add(player_a['name'])
                    except KeyError:
                        players[player_a['steam_id']] = {'aliases': {player_a['name']}}
                    try:
                        players[player_b['steam_id']]['aliases'].add(player_b['name'])
                    except KeyError:
                        players[player_b['steam_id']] = {'aliases': {player_b['name']}}
                    if is_coaches:
                        if player_a['match_result'] == 'win':
                            players[player_a['steam_id']]['coaches wins'] = players[player_a['steam_id']].get('wins', 0) + 1
                        if player_a['match_result'] == 'loss':
                            players[player_a['steam_id']]['coaches losses'] = players[player_a['steam_id']].get('losses', 0) + 1
                        if player_a['match_result'] == 'tie':
                            players[player_a['steam_id']]['coaches ties'] = players[player_a['steam_id']].get('ties', 0) + 1
                        if player_b['match_result'] == 'win':
                            players[player_b['steam_id']]['coaches wins'] = players[player_b['steam_id']].get('wins', 0) + 1
                        if player_b['match_result'] == 'loss':
                            players[player_b['steam_id']]['coaches losses'] = players[player_b['steam_id']].get('losses', 0) + 1
                        if player_b['match_result'] == 'tie':
                            players[player_b['steam_id']]['coaches ties'] = players[player_b['steam_id']].get('ties', 0) + 1
                    if is_inhouse:
                        if player_a['match_result'] == 'win':
                            players[player_a['steam_id']]['inhouse wins'] = players[player_a['steam_id']].get('wins', 0) + 1
                        if player_a['match_result'] == 'loss':
                            players[player_a['steam_id']]['inhouse losses'] = players[player_a['steam_id']].get('losses', 0) + 1
                        if player_a['match_result'] == 'tie':
                            players[player_a['steam_id']]['inhouse ties'] = players[player_a['steam_id']].get('ties', 0) + 1
                        if player_b['match_result'] == 'win':
                            players[player_b['steam_id']]['inhouse wins'] = players[player_b['steam_id']].get('wins', 0) + 1
                        if player_b['match_result'] == 'loss':
                            players[player_b['steam_id']]['inhouse losses'] = players[player_b['steam_id']].get('losses', 0) + 1
                        if player_b['match_result'] == 'tie':
                            players[player_b['steam_id']]['inhouse ties'] = players[player_b['steam_id']].get('ties', 0) + 1
            else:
                continue
        current_page += 1
        time.sleep(1)
    print(players)


if __name__ == "__main__":
    main()
