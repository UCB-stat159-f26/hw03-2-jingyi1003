"""Load singles match data from Tennis Abstract."""

import json
import math
import re
import unicodedata
from datetime import date
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import pandas as pd

_BASE_URL = "https://www.tennisabstract.com"
_DAYS_PER_YEAR = 365.2425
_RESULTS = {"W": "Win", "L": "Loss"}
_UNPLAYED = {"", "W/O", "WO", "DEF", "BYE"}


def get_career_matches(player_name: str) -> pd.DataFrame:
    """Return plot-ready singles matches for a player listed on Tennis Abstract."""
    if not isinstance(player_name, str) or not _name_key(player_name):
        raise ValueError("Enter a player name, such as 'Serena Williams'.")
    name, tour = _find_player(player_name)
    slug = quote(name.replace(" ", ""), safe="")
    profile = _load_profile(slug, tour)
    birthday = _birth_date(profile, name)
    rows = _career_rows(profile, slug)
    return _match_frame(rows, name, birthday)


def _download(path):
    try:
        request = Request(_BASE_URL + path, headers={"User-Agent": "tennis-career/0.1"})
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8-sig")
    except (URLError, TimeoutError, UnicodeError) as error:
        raise RuntimeError(f"Could not read Tennis Abstract data at {path}: {error}") from error


# Normalize names so spaces, case, and accents do not affect player lookup.
def _name_key(name):
    letters = unicodedata.normalize("NFKD", name.casefold())
    return "".join(letter for letter in letters if letter.isalnum())


def _find_player(query):
    entries = _read_array(_download("/mwplayerlist.js"), "playerlist")
    key = _name_key(query)
    matches = {(entry[4:], entry[1]) for entry in entries
               if entry.startswith(("(M) ", "(W) ")) and _name_key(entry[4:]) == key}
    if not matches:
        raise ValueError(f"Player {query!r} was not found on Tennis Abstract.")
    return _choose_player(matches, query)


def _choose_player(matches, query):
    exact = {(name, tour) for name, tour in matches if name.casefold() == query.strip().casefold()}
    candidates = exact or matches
    if len(candidates) != 1:
        raise ValueError(f"Player name {query!r} matches multiple Tennis Abstract profiles.")
    return candidates.pop()


def _array_start(source, variable):
    return re.search(rf"\bvar\s+{variable}\s*=\s*(?=\[)", source)


# Read the array from a JavaScript assignment without running the script.
def _read_array(source, variable):
    start = _array_start(source, variable)
    if start is None:
        raise RuntimeError(f"Tennis Abstract data is missing the {variable} array.")
    try:
        return json.JSONDecoder().raw_decode(source, start.end())[0]
    except ValueError as error:
        raise RuntimeError(f"Could not parse Tennis Abstract's {variable} array.") from error


def _load_profile(slug, tour):
    endpoint = "wplayer-classic" if tour == "W" else "player-classic"
    profile = _download(f"/cgi-bin/{endpoint}.cgi?p={slug}")
    details = f"/jsmatches/{slug}.js"
    if details in profile:
        return _download(details)
    return profile


# Some profiles need an archive to fill in older matches.
def _career_rows(profile, slug):
    current = _read_array(profile, "matchmx") if _array_start(profile, "matchmx") else []
    if current and re.search(r"\bvar\s+careerjs\s*=\s*0\b", profile):
        return current
    archive = _download(f"/jsmatches/{slug}Career.js")
    return current + _read_array(archive, "morematchmx")


def _date(value):
    return date.fromisoformat(f"{value[:4]}-{value[4:6]}-{value[6:]}")


def _birth_date(profile, name):
    match = re.search(r"""\bvar\s+dob\s*=\s*['"]?(\d{8})\b""", profile)
    if match:
        try:
            return _date(match[1])
        except ValueError:
            pass
    raise ValueError(f"No valid birth date is available for {name} on Tennis Abstract.")


def _age_at(event_date, birthday):
    return (event_date - birthday).days / _DAYS_PER_YEAR


# Tennis Abstract stores opponent ages as birth dates or decimal years.
def _opponent_age(value, event_date):
    try:
        if re.fullmatch(r"\d{8}", value):
            age = _age_at(event_date, _date(value))
        else:
            age = float(value)
    except ValueError:
        return None
    return age if math.isfinite(age) and age > 0 else None


def _match_record(row, name, birthday):
    result = _RESULTS.get(row[4])
    if result is None or row[9].strip().upper() in _UNPLAYED:
        return None
    ages = _match_ages(row, birthday)
    if ages is None:
        return None
    return _match_details(row, name, result) | ages


def _match_ages(row, birthday):
    event_date = _date(row[0])
    opponent_age = _opponent_age(str(row[16]), event_date)
    if opponent_age is None:
        return None
    player_age = _age_at(event_date, birthday)
    return {
        "event_date": event_date, "player_age": player_age,
        "opponent_age": opponent_age, "age_difference": player_age - opponent_age,
    }


def _match_details(row, name, result):
    return {
        "player": name, "tournament": row[1], "surface": row[2],
        "round": row[8], "score": row[9], "opponent": row[11], "result": result,
    }


def _match_records(rows, name, birthday):
    for index, row in enumerate(rows, start=1):
        try:
            record = _match_record(row, name, birthday)
        except (TypeError, IndexError, ValueError) as error:
            raise RuntimeError(f"Invalid match record {index} for {name}.") from error
        if record is not None:
            yield record


def _match_frame(rows, name, birthday):
    frame = pd.DataFrame(_match_records(rows, name, birthday))
    if frame.empty:
        raise ValueError(f"No matches with usable opponent ages were found for {name}.")
    keys = ["event_date", "tournament", "round", "score", "opponent", "result"]
    columns = ["player", "event_date", "tournament", "surface", "round", "score",
               "opponent", "result", "player_age", "opponent_age", "age_difference"]
    frame = frame[columns].drop_duplicates(keys)
    return frame.sort_values("event_date", kind="stable", ignore_index=True)


def plot_age_matchups(matches: pd.DataFrame):
    """Return a Matplotlib figure for the matches from get_career_matches."""
    import matplotlib.pyplot as plt

    player = matches["player"].iloc[0]
    figure, axes = plt.subplots(figsize=(10, 6), layout="constrained", facecolor="white")
    for result, color in (("Win", "#40c5e5"), ("Loss", "#953a8c")):
        group = matches.loc[matches["result"].eq(result)]
        axes.scatter(
            group["player_age"], group["age_difference"],
            color=color, label=result, s=18, alpha=0.85, edgecolors="none", zorder=3,
        )
    axes.axhline(0, color="#858585", linewidth=1)
    axes.grid(color="#e7e7e7", linewidth=0.8)
    axes.set_title(f"{player} — Career Singles Matches", weight="bold")
    axes.set_xlabel("Player age (years)")
    axes.set_ylabel("Player age − opponent age (years)")
    axes.spines[["top", "right"]].set_visible(False)
    axes.legend(frameon=False)
    return figure
