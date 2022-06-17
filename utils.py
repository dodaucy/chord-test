#################################################
#                                               #
#                  chord test                   #
#                                               #
#       Copyright (C) 2022 X Gamer Guide        #
#  https://github.com/X-Gamer-Guide/chord-test  #
#                                               #
#################################################


import textwrap
from typing import Iterable

from colorama import Fore, Style

from constants import CLEAR_SCREEN, NOTES


def clear_console() -> None:
    "Clears the console."
    print(CLEAR_SCREEN, end="", flush=True)


def get_note_str(note: int) -> str:
    "Returns the note as a string."
    return NOTES[note % len(NOTES)]


def get_octave(note: int) -> int:
    "Returns the octave of a note."
    return note // len(NOTES) + 1


def render_piano(current_piano: dict, current_note: str, current_variant: str, keys_to_play: Iterable[str], good_keys: Iterable[str] = [], bad_keys: Iterable[str] = []) -> None:
    "Renders the piano."
    current = current_piano['display_current']['map'].format_map({"note": current_note, "variant": current_variant})
    align = current_piano['display_current']['align']
    size = current_piano['display_current']['size']
    if align == 'left':
        current = current.ljust(size)
    elif align == 'right':
        current = current.rjust(size)
    elif align == 'center':
        current = current.center(size)
    map_keys = {
        "RESET": Style.RESET_ALL,
        "CURRENT": current,
    }
    for octave in range(current_piano['octaves']):
        for note in NOTES:
            map_keys[f"{note}{octave + 1}"] = Style.RESET_ALL
    for key in keys_to_play:
        map_keys[key] = Fore.BLUE + Style.BRIGHT
    for key in good_keys:
        map_keys[key] = Fore.GREEN + Style.BRIGHT
    for key in bad_keys:
        map_keys[key] = Fore.RED + Style.BRIGHT
    clear_console()
    print(textwrap.dedent(current_piano['display']).format_map(map_keys))
