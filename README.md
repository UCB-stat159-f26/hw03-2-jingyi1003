# Tennis Career

This package retrieves singles match data from [Tennis Abstract](https://www.tennisabstract.com/) and plots a player's age against their age difference with each opponent, following the style of the HW2 scatter plot.

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

<!-- Add a short paragraph about what you learned while working on this assignment. For example, describe how the two formats for opponent age affected your code and what the offline tests helped you verify. -->
