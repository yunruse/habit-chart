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

HabitChecklist = dict[str, bool]

class ChartApp(rumps.App):
    path: Path
    file_last_updated: float = 0
    contents: dict
    edit_item: rumps.MenuItem

    day: datetime.date
    habits: tuple[HabitChecklist, HabitChecklist]

    def __init__(self, path: Path | None):
        path = path or (Path(os.environ.get('XDG_CONFIG_HOME', '~/.config')) / 'habits.yaml')
        self.path = path.expanduser()
        super().__init__("Habits", quit_button=None)

    # State

    def all_habits_done(self, bonus: bool = False):
        return all(self.habits[bonus].values())

    def summary_line(self):
        habits, bonus = self.habits
        summary = ''.join(positive_keys(habits))
        if self.all_habits_done():
            summary += ALL_DONE
        bonus = list(positive_keys(bonus))
        summary += ''.join(bonus)
        summary += BONUS * len(bonus)
        return summary

    # Title modes

    def title_filled_unicode_stars(self):
        def stars(h: HabitChecklist, empty: str, full: str):
            return ''.join(full if done else empty for done in h.values())

        summary = stars(self.habits[False], '☆', '★')
        summary += stars(self.habits[True], '✧', '✦')
        return summary

    def update_title(self):
        mode: str = self.contents.get('title mode', '').lower().strip()

        if mode == 'stars':
            self.title = self.title_filled_unicode_stars()
        elif mode == 'none':
            self.title = 'Habits'
        else:
            self.title = self.summary_line() or 'Habits'

    def update_summary(self):
        N_all_done = sum(ALL_DONE in e for e in self.contents['log'].values())
        N_bonus = sum(e.count(BONUS) for e in self.contents['log'].values())
        summary = f'{self.day:%a %-d}'
        if N_all_done:
            summary += f', {ALL_DONE}×{N_all_done}'
        if N_bonus:
            summary += f', {BONUS}×{N_bonus}'
        self.edit_item.title = f'Edit habits ({summary})'

    # File checking

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

    # Loading

    def reload(self):
        with open(self.path, encoding='utf8') as f:
            self.contents = yaml.load(f, yaml.Loader)
        self.contents.setdefault('log', {})

        self.day = self.today()
        today_entry = self.contents['log'].get(self.day, '')

        def get(key) -> tuple[dict[str, str], HabitChecklist]:
            self.contents.setdefault(key, {})
            habits: dict[str, str] = self.contents[key]
            return habits, {emoji: (emoji in today_entry) for emoji in habits.keys()}

        habits, habit_checklist = get('habits')
        bonus, bonus_checklist = get('bonus')
        self.habits = habit_checklist, bonus_checklist

        # Build menu
        def callbacker(icon: str, is_bonus=False):
            return lambda c: self.on_check(c, icon, is_bonus)

        def load(h: dict[str, str], is_bonus=False):
            for icon, name in h.items():
                item = rumps.MenuItem(
                    f'{icon}\t{name}',
                    callbacker(icon, is_bonus))
                item.state = self.habits[is_bonus][icon]
                self.menu.add(item)

        self.menu.clear()
        self.menu.add(rumps.MenuItem(f'{ALL_DONE}\tDaily habits'))
        load(habits)
        self.menu.add(rumps.separator)
        if bonus:
            self.menu.add(rumps.MenuItem(f'{BONUS}\tBonus habits'))
            load(bonus, is_bonus=True)
            self.menu.add(rumps.separator)

        self.edit_item = rumps.MenuItem(
            f'Edit habits',
            lambda _: os.system(f'open {str(self.path)!r}'))
        self.menu.add(self.edit_item)
        self.menu.add(rumps.MenuItem(
            f'Quit Habit Bar',
            rumps.quit_application))

        self.update_title()
        self.update_summary()

    def on_check(self, caller: rumps.MenuItem, icon: str, is_bonus):
        # Change state
        caller.state = not caller.state
        self.habits[is_bonus][icon] = caller.state
        self.contents['log'][self.day] = self.summary_line()

        # Update UI
        self.update_title()
        self.update_summary()

        # Update file
        with open(self.path, 'w', encoding='utf8') as f:
            yaml.dump(self.contents, f, yaml.Dumper, allow_unicode=True, sort_keys=False)
        self.file_last_updated = os.stat(self.path).st_mtime

        # SFX
        if self.contents.get('sound', True) and caller.state:
            if self.all_habits_done(is_bonus):
                os.popen('afplay sfx-all.mp3')
            else:
                os.popen('afplay sfx-habit.mp3')


parser = ArgumentParser()
parser.add_argument(
    'file', type=Path, help='Path to .md file', nargs='?', default=None)

if __name__ == '__main__':
    args = parser.parse_args()
    self = ChartApp(args.file)
    self.run()