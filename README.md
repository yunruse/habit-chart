# habit-chart

<img src="example.png" alt="Example of the menubar app in use." width="200"/>

A simple macOS menubar habit tracking app. Check off habits done today and earn a star for completing them all!

## Setup and installation

Create a file `~/.config/habits.yaml` with keys like:

```yaml
habits:
  🌳: 15 minutes walk
  🧘: 2 minutes meditation
  📖: Read a book
reset at hour: 7
log:
  2023-09-25: 🌳🧘📖⭐️
  2023-09-26: 🌳🧘
```

Only the `habits` key is necessary; the `log` entry is automatically generated by using the app, and the `reset at hour` (24-hour) can be optionally provided such that habits do not roll over at midnight.

Run as a Python file or use `python setup.py py2app` to create an app which doesn't appear in the Dock. 