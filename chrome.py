import webbrowser
import os
import random

CHROME_PATH = os.getenv('chrome_path')


names = ['guy', 'buddy', 'pal', 'champ', 'chief', 'captain', 'dude', 'bro', 'squirt', 'big guy', 'boss', 'man', 'my man', 'bud', 'homie', 'brah', 'bub', 'sparky', 'sport', 'sonny', 'buckaroo', 'lil camper', 'partner', 'homeboy', 'slugger', 'scout', 'scooter', 'sailor', 'sherlok', 'trooper', 'bucko', 'governor', 'gub', 'love', 'darlin', 'slick', 'princess', 'sunshine', 'dawg', 'big slick', 'spunky', 'little guy']


class ChromeController:

    def __init__(self, browser):
        self.browser = browser

    def open_page(self, url):
        # webbrowser.get(self.browser_path).open(url)
        self.browser.get(url)

    def dispatch(self, statement):
        command_dict = {
            'browse reddit': 'https://reddit.com/r/all/top',
            'browse open directories': 'https://reddit.com/r/opendirectories',
            'browse listen to this': 'https://reddit.com/r/listentothis/top/?sort=top&t=twoday',
            'browse plex': 'https://67.220.22.82:32400/web/index.html',
            'browse github': 'https://github.com',
            'browse gmail': 'https://gmail.com',
            'browse google drive': 'https://drive.google.com',
            'browse indeed': 'https://indeed.com',
            'browse linkedin': 'https://linkedin.com',
            'browse amazon': 'https://amazon.com',
        }
        url = command_dict.get(statement)
        if url:
            self.open_page(url)
            condescending_name = random.choice(names)
            return f'how about you {statement}, {condescending_name}'
        else:
            return url
