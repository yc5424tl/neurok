import os
from selenium.common.exceptions import NoSuchElementException


class BandcampController:

    def __init__(self, browser):
        self.browser = browser

    def stop_music(self):
        self.browser.close()

    def sign_in(self):
        self.browser.get('https://hellareptilian.bandcamp.com')
        try:
            login_link = self.browser.find_element_by_class_name("login-link")
            login_link.click()
            try:
                username_field = self.browser.find_element_by_id('username-field')
                username_field.send_keys(os.getenv('bandcamp_username'))
                password_field = self.browser.find_element_by_id('password-field')
                password_field.send_keys(os.getenv('bandcamp_password'))
                # submit_button = self.browser.find_element_by_css_selector('input[type="submit"]')
                submit_button = self.browser.find_element_by_xpath('//*[@id="loginform"]/div[3]/button')
                submit_button.click()
                print('signing in to bandcamp...')
                return True
            except NoSuchElementException:
                print('element not found when signing in to bandcamp')
                return False
        except NoSuchElementException:
            print('already signed in to bandcamp')
            return True

    def play_track(self, track_name, track_dialogue, private_album=False):
        if private_album is True:
            print('private album is True, signing in')
            if self.sign_in():
                private_album_link = self.browser.find_element_by_xpath('//a[@href="/album/kinda-songs"]')
                private_album_link.click()
            else:
                print('failed to sign in')
                return False
        elif private_album is False:
            print('private album is false')
            self.browser.get('https://hellareptilian.bandcamp.com')
        try:
            playbutton = self.browser.find_element_by_css_selector(f'[aria-label="Play {track_name}"]')
            playbutton.click()
            return track_dialogue
        except NoSuchElementException:
            return None

    def check_statement(self, statement):

        if 'open bandcamp' in statement:
            self.browser.get('https://hellareptilian.bandcamp.com')
            return "Holy shit balls is this Pumpkin Spice...the saga of the missing spice girl and how things got that way? Fine selection indeed!"

        elif 'open private album' in statement:
            if self.sign_in():
                print('signed in')
                try:
                    self.browser.get('https://hellareptilian.bandcamp.com/album/kinda-songs')
                    return 'Oooooooooohhhh...super secret...or whatever'
                except NoSuchElementException:
                    return None

        elif 'play unicorn e' in statement and 'remix' not in statement:
            return self.play_track(track_name='Unicorny', track_dialogue='One, Two, Three...Unicorny!')

        elif 'play spectre' in statement and 'unplugged' not in statement and 'remix' not in statement:
            return self.play_track(track_name='The Spectacular Spectacle of Spectre Spectating', track_dialogue='vrooom vroom')

        elif 'play hippo crypt' in statement:
            return self.play_track(track_name='Hippocrypt', track_dialogue='look out mon, its a hippo crypt a con')

        elif 'play soho' in statement:
            return self.play_track(track_name='SoHo', track_dialogue='you know soho?')

        elif 'play payphone' in statement:
            return self.play_track(track_name='A Payphone Haunted', track_dialogue='Ring Ring...Ring Ring')

        elif ('play storyline' or 'play fuckin up the storyline' or 'play futs') in statement:
            return self.play_track(track_name='Fuckin Up The Storyline', track_dialogue='They cut Darth Maul in Half, and never, ever, put him back')

        elif 'play beer seeking missile' in statement:
            if self.sign_in():
                print('signed in')
                return self.play_track(track_name='Beer Seeking Missile',
                                       track_dialogue='sights on target, clear to engage',
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif 'play parasites' in statement:
            if self.sign_in():
                print('signed in')
                return self.play_track(track_name='Parasites in Paradise',
                                       track_dialogue="we'll have that criminal's head marched through the streets on a stick",
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif ('play quartet' or 'play no quartet') in statement:
            if self.sign_in():
                print('signed in')
                return self.play_track(track_name='No Quartet',
                                       track_dialogue="okey dokey",
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif 'play spectre unplugged' in statement:
            if self.sign_in():
                print('signed in')
                return self.play_track(track_name="Spectre 'Unplugged'",
                                       track_dialogue="am I in the nineties and watching m t v?",
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif 'play spectre remix' in statement:
            if self.sign_in():
                return self.play_track(track_name="Spectre 2",
                                       track_dialogue="the spectre resurrector",
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif 'play unicorn e remix' in statement:
            if self.sign_in():
                print('signed in')
                return self.play_track(track_name="Unicorny Remix",
                                       track_dialogue="i guess we'll call it bi corny",
                                       private_album=True)
            else:
                print('sign-in failed')
                return "bandcamp sign-in failed"

        elif 'stop bandcamp' in statement:
            self.stop_music()
            return "playback terminated"



