"""
Download audio files from WordReference for a list of words in Spanish and English.

Run with:

nohup python -u download_wordreference_words.py --outdir output/wordreference_words/es --lang es > output/wordreference_words/es.log 2>&1 &
nohup python -u download_wordreference_words.py --outdir output/wordreference_words/en --lang en > output/wordreference_words/en.log 2>&1 &
"""

import os
import re
import logging
from dataclasses import dataclass

import requests
import fire
from tqdm import tqdm


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


@dataclass
class Config:
    outdir: str
    lang: str


class Downloader:

    def __init__(self, config: Config):
        self.config = config

    def run(self):
        logger.info(f"Downloading {self.config.lang} words...")
        words = download_words(self.config.lang)
        logger.info(f"Found {len(words)} words")

        logger.info(f"Downloading audio files in {self.config.outdir}...")
        for i, word in enumerate(tqdm(words)):
            word_outdir = os.path.join(self.config.outdir, word)
            if os.path.exists(word_outdir):
                continue
            download_audios(word, word_outdir, self.config.lang)

        logger.info("Done!")


def main(**kwargs):
    config = Config(**kwargs)
    downloader = Downloader(config)
    downloader.run()


def download_words(lang: str):
    """Download a list of words from the specified language"""
    if lang == "es":
        url = "https://raw.githubusercontent.com/xavier-hernandez/spanish-wordlist/main/text/spanish_words.txt"
    elif lang == "en":
        url = "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words_alpha.txt"
    else:
        raise ValueError(f"Language '{lang}' not supported")
    response = requests.get(url)
    if response.status_code == 200:
        words = response.text.splitlines()
        print(f"Read {len(words)} words. First 10:")
        print(words[:10])
    else:
        raise Exception(f"Failed to fetch words. Status code: {response.status_code}")
    return words


def download_audios(word, outdir, lang):
    """Download all audio files for a given word in url"""
    if lang == "es":
        base_url = "https://www.wordreference.com/definicion"
    elif lang == "en":
        base_url = "https://www.wordreference.com/definition"
    else:
        raise ValueError(f"Language '{lang}' not supported")

    paths = get_audio_paths(word, base_url=base_url)
    # print(paths)
    if not paths:
        # print("No audio files found.")
        return
    os.makedirs(outdir, exist_ok=True)
    for path in paths:
        # e.g. path == '/audio/en/uk/general/en086958.mp3'
        # split into ['', 'audio','en','uk','general','en086958.mp3']
        parts = path.split('/')
        fn = ".".join(parts[1:])
        full_path = os.path.join(outdir, fn)
        url = "https://www.wordreference.com" + path
        # print(f"Downloading {url} → {full_path}")
        resp = requests.get(url)
        resp.raise_for_status()
        with open(full_path, "wb") as f:
            f.write(resp.content)
    # print("Done!")


def get_audio_paths(word, base_url="https://www.wordreference.com/definicion"):
    """Find the paths of audio files in WR url"""
    url = f"{base_url}/{word}"
    r = requests.get(url)
    r.raise_for_status()
    # Regex to grab everything between var audioFiles = [ ... ];
    m = re.search(r"var\s+audioFiles\s*=\s*(\[[^\]]*\])", r.text)
    if not m:
        return []
    # Evaluate the JS array literal into a Python list
    paths = eval(m.group(1))
    return paths


if __name__ == "__main__":
    fire.Fire(main)
