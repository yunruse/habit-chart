"'sticker chart'-like macOS menubar app for dopamine motivations"

from argparse import ArgumentParser
import datetime
import os
from pathlib import Path

import rumps
import yaml

STAR = '⭐️'
DAY = datetime.timedelta(days=1)

class ChartApp(rumps.App):
    path: Path
    file_last_updated: float = 0
    contents: dict
    day: datetime.date
    today_habits: dict[str, bool]

    def __init__(self, path: Path | None):
        path = path or (Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')) / 'habits.yaml')
        self.path = path.expanduser()
        super().__init__("Habits:", quit_button=None)
        self.reload()
    
    def summary(self):
        summary = ''.join(key for key, done in self.today_habits.items() if done)
        if all(self.today_habits.values()):
            summary += STAR
        return summary
    
    def update_title(self):
        self.title = 'Habits: ' + (self.summary() or f"0 / {len(self.today_habits)}")
    
    @rumps.timer(10)
    def check_edit(self, _):
        "Only reload when necessary"
        # File has been manually changed by user
        time = os.stat(self.path).st_mtime
        if time != self.file_last_updated:
            self.file_last_updated = time
            return self.reload()
        
        # It's a new day!
        if self.today() != self.day:
            return self.reload()
    
    def today(self):
        now = datetime.datetime.now()
        date = now.date()
        hour: int | None = self.contents.get('reset at hour', None)
        if hour is not None and now.hour < hour:
            return date - DAY
        return date

    def reload(self):
        with open(self.path, encoding='utf8') as f:
            self.contents = yaml.load(f, yaml.Loader)
        self.contents.setdefault('log', {})
        
        self.day = self.today()
        
        habits: dict[str, str] = self.contents['habits']
        today_entry = self.contents['log'].get(self.day, '')
        self.today_habits = {
            icon: (icon in today_entry) for icon in habits.keys()}

        N_stars = sum(
            STAR in entry for entry in self.contents['log'].values())

        def callbacker(icon):
            return lambda c: self.check(c, icon)
        
        self.update_title()

        self.menu.clear()
        for icon, name in habits.items():
            item = rumps.MenuItem(
                f'{icon} {name}',
                callbacker(icon))
            item.state = self.today_habits[icon]
            self.menu.add(item)

        self.menu.add(rumps.MenuItem(
            f'Edit habits ({self.day:%d %b}, {STAR}×{N_stars})',
            lambda _: os.system(f'open {str(self.path)!r}')
        ))
        
        self.menu.add(rumps.MenuItem(
            f'Quit Habit Bar',
            rumps.quit_application))
    
    def check(self, caller: rumps.MenuItem, icon: str):
        caller.state = not caller.state
        self.today_habits[icon] = caller.state

        self.update_title()
        self.contents['log'][self.day] = self.summary()

        with open(self.path, 'w', encoding='utf8') as f:
            yaml.dump(self.contents, f, yaml.Dumper, allow_unicode=True, sort_keys=False)

parser = ArgumentParser()
parser.add_argument(
    'file', type=Path, help='Path to .md file', nargs='?', default=None)

if __name__ == '__main__':
    args = parser.parse_args()
    self = ChartApp(args.file)
    self.run()