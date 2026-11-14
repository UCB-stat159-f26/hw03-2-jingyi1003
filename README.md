# Tennis Career

This package retrieves singles match data from [Tennis Abstract](https://www.tennisabstract.com/) and plots a player's age against their age difference with each opponent, following the style of the HW2 scatter plot.

## Project files

- [`tennis_career.py`](tennis_career.py) fetches and cleans career match data and creates the scatter plot.
- [`pyproject.toml`](pyproject.toml) defines how the package is installed and lists its dependencies.
- [`tests/`](tests/) contains offline tests and sample Tennis Abstract JavaScript files for Serena Williams and Rafael Nadal.

## Install

Use Python 3.9 or newer.

```sh
python -m pip install git+https://github.com/UCB-stat159-f26/hw03-2-jingyi1003.git
```

## Use

```python
from tennis_career import get_career_matches, plot_age_matchups

serena = get_career_matches("Serena Williams")
figure = plot_age_matchups(serena)
figure.savefig("serena.png", dpi=150)
```

`get_career_matches()` needs an internet connection and returns a pandas DataFrame. It accepts inputs such as `"serena williams"`, `"SerenaWilliams"`, and `"Rafael Nadal"`. An unknown name such as `"GastonSanchez"` raises a `ValueError` with the name in the message.

`plot_age_matchups()` returns a Matplotlib figure. The x-axis is the player's age. The y-axis is the player's age minus the opponent's age, in years. Blue points are wins and purple points are losses.

## Run the tests

From the repository root, use an environment with the project dependencies installed. The tests use the Serena and Nadal JS samples in `tests/fixtures/` and run entirely offline.

```sh
python -B -m unittest discover -s tests -v
```

## Personal reflections

In HW2, I only worked with Serena’s data. Comparing it with Nadal’s sample for HW3 showed me that the same field can mean two different things. For Serena’s opponents, I had to calculate age from a birth date. Nadal’s sample already gave the opponent’s age in years. Using three saved matches for each player made it easy to check the age difference and match results without accessing the website.
