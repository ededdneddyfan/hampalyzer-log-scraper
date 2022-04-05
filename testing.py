import bs4
import requests


def team_parser(input_team: bs4.element.Tag) -> dict:
    output_team = []
    list_index = 0
    for index, child in enumerate(input_team.children):
        if isinstance(child, bs4.element.NavigableString):
            raw_name_string = child.string
            # Dumb hacky way of dealing with the inconsistent formatting of values coming from spans
            if index == 0:
                # No leading comma for the first entry
                cleaned_name_string = raw_name_string[:raw_name_string.find('\n')]
            else:
                # Skip ", ", then grab upto newline char
                cleaned_name_string = raw_name_string[2:raw_name_string.find('\n')]
            output_team.append({'name': cleaned_name_string})
        if isinstance(child, bs4.element.Tag):
            raw_tracker_url = child.get('href')
            first_equals_location = raw_tracker_url.find('=') + 1
            output_team[list_index]['steam_id'] = raw_tracker_url.split('&')[0][first_equals_location:]
            list_index += 1
    return output_team


test_url = "http://app.hampalyzer.com/parsedlogs/Coach's-2022-Mar-18-24-51-q332e/"
page = requests.get(test_url)
soup = bs4.BeautifulSoup(page.text, 'html.parser')

final_score_raw = soup.find(class_='list-unstyled').contents[9].contents[1].string
split_raw = final_score_raw.split(' – ')
final_score_team_a = int(split_raw[0].split(' ')[-1])
final_score_team_b = int(split_raw[1].split('\r')[0])

"""<p>
<span class="team-title">Team A</span> —
                    <span class="team-list">massa|2i
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:794334&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, EDEdDNEdDYFaN -z-
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:76483&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, kacchan GIGGLING
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:455990175&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, coachsouz
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:1:2278493&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a></span>
</p>
<p>
<span class="team-title">Team B</span> —
                    <span class="team-list">MightyMouse
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:84622&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, [D.v.S]Demonz
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:3370&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, [OSAFT] BOISY
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:12147350&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a>, transcending
                <a href="https://tracker.thecatacombs.us/index.php?steamid=STEAM_0:0:66094767&amp;name=&amp;ip="><i class="fas fa-user-tag"></i></a></span>
</p>"""
# Parse players for each team (by steam_id)
high_level_group = soup.find_all(class_='team-comparison my-5')[0]
team_spans = high_level_group.find_all('span')
team_a_raw = team_spans[1]
team_b_raw = team_spans[3]
team_a = team_parser(team_a_raw)
team_b = team_parser(team_b_raw)

"""TODO: Upsert to player database, which maps STEAM_ID's to aliases (naive assumption that everyone only has 1 steam id)
One to many relationship"""


# TODO: Add win/loss/tie for each user? simplest implementation is steam_id, main alias, aliases, wins, losses, ties
# I'll also normalize this to have one table for players with steam_id, name, alises
# Another table for matches and you join between the two for match results? Maybe another separate table for results...
# Still thinking about it.
if final_score_team_a > final_score_team_b:
    for index, player in enumerate(team_a):
        team_a[index]['match_result'] = 'win'
    for index, player in enumerate(team_b):
        team_b[index]['match_result'] = 'loss'
elif final_score_team_b > final_score_team_a:
    for index, player in enumerate(team_b):
        team_b[index]['match_result'] = 'win'
    for index, player in enumerate(team_a):
        team_a[index]['match_result'] = 'loss'
elif final_score_team_a == final_score_team_b:
    for index, player in enumerate(team_a):
        team_a[index]['match_result'] = 'tie'
    for index, player in enumerate(team_b):
        team_b[index]['match_result'] = 'tie'

# TODO: Go through each player's stats page from logs and pull data per match. This will be way down the line I think.

# If player not currently in player database, add them with alias from logfile
print(team_a)
print(team_b)