#################################################
#                                               #
#                  chord test                   #
#                                               #
#       Copyright (C) 2022 X Gamer Guide        #
#  https://github.com/X-Gamer-Guide/chord-test  #
#                                               #
#################################################


import os
import random
import signal
import subprocess
import sys

import rtmidi
from colorama import Fore, Style, init
from gtts import gTTS
from playsound import playsound

import utils
from constants import AUDIO_PATH, NOTES, PIANOS, VARIANTS


init()

midiin = rtmidi.RtMidiIn()


def exit_handler(signal, frame):
    utils.clear_console()
    sys.exit()


signal.signal(signal.SIGINT, exit_handler)
signal.signal(signal.SIGTERM, exit_handler)

if not os.path.exists(AUDIO_PATH):
    utils.clear_console()
    # Create the audio directory
    print(f"{Fore.CYAN}Create audio folder ({Style.BRIGHT}{AUDIO_PATH}{Style.NORMAL})...{Fore.RESET}")
    os.mkdir(AUDIO_PATH)
    # Download notes
    for note in NOTES:
        print(f"{Fore.CYAN}Download {Style.BRIGHT}{note}{Style.NORMAL}...{Fore.RESET}")
        tts = gTTS(note.replace("#", " sharp"), lang="en")
        tts.save(os.path.join(AUDIO_PATH, f"{note}.mp3"))
    # Download variants
    for variant in VARIANTS:
        print(f"{Fore.CYAN}Download {Style.BRIGHT}{variant}{Style.NORMAL}...{Fore.RESET}")
        tts = gTTS(variant, lang="en")
        tts.save(os.path.join(AUDIO_PATH, f"{variant}.mp3"))
        for note in NOTES:
            # Merge notes and variants
            print(f"{Fore.CYAN}Create {Style.BRIGHT}{note} {variant}{Style.NORMAL}...{Fore.RESET}")
            subprocess.run(["ffmpeg", "-i", os.path.join(os.path.join(AUDIO_PATH, f"{note}.mp3")), "-i", os.path.join(AUDIO_PATH, f"{variant}.mp3"), "-filter_complex", "[0:0][1:0]concat=n=2:v=0:a=1[out]", "-map", "[out]", "-loglevel", "error", "-hide_banner", "-y", os.path.join(AUDIO_PATH, f"{note}_{variant}.wav")])

utils.clear_console()

while True:
    # Get MIDI ports
    ports = range(midiin.getPortCount())

    if not ports:
        # No MIDI ports found
        print(f"{Fore.RED}{Style.BRIGHT}No MIDI ports found!{Style.RESET_ALL}", file=sys.stderr)
        print("Press enter to check for MIDI ports again...", end="")
        input()
        utils.clear_console()
        continue

    # List available ports
    for port in ports:
        print(f"{Fore.CYAN}{Style.BRIGHT}{port + 1}{Style.RESET_ALL} --> {Fore.YELLOW}{midiin.getPortName(port)}{Fore.RESET}")

    # Ask user to select a port
    print(f"{Fore.RED}{Style.BRIGHT}> {Style.RESET_ALL}", end="")

    inp = input().strip()

    if not inp:
        # Check for ports again
        utils.clear_console()
        continue

    try:
        port = int(inp) - 1
    except ValueError:
        # Invalid input
        utils.clear_console()
        print(f"{Fore.RED}Invalid input, try again!{Fore.RESET}", file=sys.stderr)
        continue

    if port not in ports:
        # Port out of range
        utils.clear_console()
        print(f"{Fore.RED}Port out of range, try again!{Fore.RESET}", file=sys.stderr)
        continue

    break

# Connect to MIDI port
print(f"{Fore.CYAN}Open port to '{Style.BRIGHT}{midiin.getPortName(port)}{Style.NORMAL}' ({Style.BRIGHT}{port}{Style.NORMAL})...{Fore.RESET}")
midiin.openPort(port)

# Clear buffer
print(f"{Fore.CYAN}Clear buffer...{Fore.RESET}")
while True:
    if midiin.getMessage(100) is None:
        break

utils.clear_console()

variants = []
unselected_variants = list(VARIANTS.keys())

while True:

    # List variants
    print(f"{Fore.CYAN}Please select a variant: {Fore.RESET}{Fore.YELLOW}{f'{Fore.RESET}, {Fore.YELLOW}'.join(unselected_variants)}{Fore.RESET}")
    print(f"{Fore.CYAN}Alreay selected: {Fore.YELLOW}{f'{Fore.RESET}, {Fore.YELLOW}'.join(variants)}{Fore.RESET}")
    print(f"{Fore.CYAN}'{Style.BRIGHT}all{Style.NORMAL}' to select all or '{Style.BRIGHT}ready{Style.NORMAL}' if you want to have what you chose!{Fore.RESET}")

    # Ask user to select a variant
    print(f"{Fore.RED}{Style.BRIGHT}> {Style.RESET_ALL}", end="")
    inp = input().strip()

    if inp == "all":
        # Select all variants
        variants = list(VARIANTS.keys())
        break

    if inp == "ready":
        # If user is ready
        if not variants:
            utils.clear_console()
            print(f"{Fore.RED}No variants selected, try again!{Fore.RESET}", file=sys.stderr)
            continue
        break

    if inp not in unselected_variants:
        # Invalid input
        utils.clear_console()
        print(f"{Fore.RED}Invalid input, try again!{Fore.RESET}", file=sys.stderr)
        continue

    unselected_variants.remove(inp)
    variants.append(inp)

    if not unselected_variants:
        break

    utils.clear_console()

utils.clear_console()

while True:
    # List available pianos
    for index, piano in enumerate(PIANOS.keys()):
        print(f"{Fore.CYAN}{Style.BRIGHT}{index + 1}{Style.RESET_ALL} --> {Fore.YELLOW}{piano}{Fore.RESET} ({Fore.GREEN}{PIANOS[piano]['octaves']} octaves{Fore.RESET})")

    # Ask user to select a piano
    print(f"{Fore.RED}{Style.BRIGHT}> {Style.RESET_ALL}", end="")

    try:
        piano_number = int(input()) - 1
    except ValueError:
        # Invalid input
        utils.clear_console()
        print(f"{Fore.RED}Invalid input, try again!{Fore.RESET}", file=sys.stderr)
        continue

    if not 0 <= piano_number < len(PIANOS):
        # Piano index of range
        utils.clear_console()
        print(f"{Fore.RED}Piano out of range, try again!{Fore.RESET}", file=sys.stderr)
        continue

    break

# Select piano
piano = PIANOS[list(PIANOS.keys())[piano_number]]

pressed_keys = []
last_keys = None

while True:
    # Generate random keys
    note_int = random.randint(0, len(NOTES) - 1)
    note = NOTES[note_int]
    variant = random.choice(variants)

    # Skip if keys are the same as last time
    keys = (note_int, variant)
    if keys == last_keys:
        continue
    last_keys = keys

    # Convert keys to actual keys
    keys_to_play = []
    for key in VARIANTS[variant]:
        keys_to_play.append(f"{utils.get_note_str(note_int + key)}{utils.get_octave(note_int + key)}")

    playsound(os.path.join(AUDIO_PATH, f"{note}_{variant}.wav"), False)

    while True:
        utils.clear_console()

        if pressed_keys:
            # Sort pressed keys
            pressed_keys.sort()

            # Get lowest octave
            octave = utils.get_octave(pressed_keys[0])

            # Sort between good and bad keys
            good_keys = []
            bad_keys = []
            for key in pressed_keys:
                key_played = f"{utils.get_note_str(key)}{utils.get_octave(key) - octave + 1}"
                if key_played in keys_to_play:
                    good_keys.append(key_played)
                else:
                    bad_keys.append(key_played)

            utils.render_piano(piano, note, variant, keys_to_play, good_keys, bad_keys)

            # Generate new keys when the current keys are played correctly
            if good_keys == keys_to_play and not bad_keys:
                break

        else:
            utils.render_piano(piano, note, variant, keys_to_play)

        # Get MIDI events
        msg = midiin.getMessage(250)
        if msg:
            if msg.isNoteOn():
                # Key pressed
                pressed_keys.append(msg.getNoteNumber())

            elif msg.isNoteOff():
                # Key released
                key = msg.getNoteNumber()
                if key in pressed_keys:
                    pressed_keys.remove(key)
