# habit-chart

<img src="example.png" alt="Example of the menubar app in use." width="200"/>

A simple macOS menubar habit tracking app. Check off habits done today and earn a star for completing them all!

## Setup and installation

Create a file `~/.config/habits.yaml` with a `habits` key and, optionally, a `bonus` key:

```yaml
habits:
  🌳: 15 minutes walk
  🧘: 2 minutes meditation
  📖: Read a book
bonus:
  🖊️: Write novel
title mode: star
reset at hour: 7
log:
  2023-09-24: 🌳
  2023-09-25: 🌳🧘📖⭐️
  2023-09-26: 🌳🧘📖⭐️🖊️✨
```

- The `log` key is automatically generated when using the app.
- `habits` and `bonus` are dictionaries with emoji keys and habit-name values. `habits` should be those you always want to do each day; `bonus` are nice extras.
- If you want, `reset at hour` (an integer 0 - 23) can give you some legroom if you use the app after midnight.

Finishing every habit in a day earns you a ⭐️. Likewise, bonus habits earns a ✨.

Run as a Python file or use `python setup.py py2app` to create an app which doesn't appear in the Dock. 
