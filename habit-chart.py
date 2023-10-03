"'sticker chart'-like macOS menubar app for dopamine motivations"

from typing import TypeVar

from argparse import ArgumentParser
import datetime
import os
from pathlib import Path

import rumps
import yaml

ALL_DONE = '⭐️'
BONUS = '✨'
DAY = datetime.timedelta(days=1)

T = TypeVar('T')

def positive_keys(d: dict[T, bool]):
    return (key for key, check in d.items() if check)

class ChartApp(rumps.App):
    path: Path
    file_last_updated: float = 0
    contents: dict
    day: datetime.date
    today_habits: dict[str, bool]
    today_bonus: dict[str, bool]

    def __init__(self, path: Path | None):
        path = path or (Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')) / 'habits.yaml')
        self.path = path.expanduser()
        super().__init__("Habits:", quit_button=None)
        self.reload()
    
    def summary_line(self):
        summary = ''.join(positive_keys(self.today_habits))
        if all(self.today_habits.values()):
            summary += ALL_DONE
        bonus = list(positive_keys(self.today_bonus))
        summary += ''.join(bonus)
        summary += BONUS * len(bonus)
        return summary
    
    # Title modes
    
    def title_filled_unicode_stars(self):
        def stars(h: dict[str, bool], empty: str, full: str):
            return ''.join(full if done else empty for done in h.values())
        
        summary = stars(self.today_habits, '☆', '★')
        summary += stars(self.today_bonus, '✧', '✦')
        return summary

    def update_title(self):
        mode = self.contents.get('title mode', '').lower().strip()

        if mode == 'stars':
            self.title = self.title_filled_unicode_stars()
        elif mode == 'none':
            self.title = 'Habits'
        else:
            self.title = self.summary_line() or 'Habits'
    
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
        today_entry = self.contents['log'].get(self.day, '')
        
        habits: dict[str, str] = self.contents.get('habits', {})
        self.today_habits = {icn: (icn in today_entry) for icn in habits.keys()}
        
        bonus: dict[str, str] = self.contents.get('bonus', {})
        self.today_bonus = {
            icon: (icon in today_entry) for icon in bonus.keys()}
        
        self.update_title()

        # Update menu
        def callbacker(icon: str, is_bonus=False):
            return lambda c: self.check(c, icon, is_bonus)

        def load(h: dict[str, str], is_bonus=False):
            for icon, name in h.items():
                item = rumps.MenuItem(
                    f'{icon} {name}',
                    callbacker(icon, is_bonus))
                item.state =  (self.today_bonus if is_bonus else self.today_habits)[icon]
                self.menu.add(item)
        
        self.menu.clear()
        load(habits)
        self.menu.add(rumps.separator)
        if bonus:
            load(bonus, is_bonus=True)
            self.menu.add(rumps.separator)

        N_all_done = sum(ALL_DONE in e for e in self.contents['log'].values())
        N_bonus = sum(BONUS in e for e in self.contents['log'].values())
        summary = f'{self.day:%d %b}'
        if N_all_done:
            summary += f', {ALL_DONE}×{N_all_done}'
        if N_bonus:
            summary += f', {BONUS}×{N_bonus}'

        self.menu.add(rumps.MenuItem(
            f'Edit habits ({summary})',
            lambda _: os.system(f'open {str(self.path)!r}')
        ))
        
        self.menu.add(rumps.MenuItem(
            f'Quit Habit Bar',
            rumps.quit_application))
    
    def check(self, caller: rumps.MenuItem, icon: str, is_bonus):
        caller.state = not caller.state
        (self.today_bonus if is_bonus else self.today_habits)[icon] = caller.state

        self.update_title()
        self.contents['log'][self.day] = self.summary_line()

        with open(self.path, 'w', encoding='utf8') as f:
            yaml.dump(self.contents, f, yaml.Dumper, allow_unicode=True, sort_keys=False)

parser = ArgumentParser()
parser.add_argument(
    'file', type=Path, help='Path to .md file', nargs='?', default=None)

if __name__ == '__main__':
    args = parser.parse_args()
    self = ChartApp(args.file)
    self.run()