"""
Download audio files from WordReference for a list of words in Spanish and English.

Run with:

nohup python -u download_wordreference_words_v2.py --outdir output/wordreference_words/es --lang es > output/wordreference_words/es.log 2>&1 &
nohup python -u download_wordreference_words_v2.py --outdir output/wordreference_words/en --lang en > output/wordreference_words/en.log 2>&1 &
"""

import os
import logging
import argparse
from dataclasses import dataclass
import time
import random
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
import re

# Configure logging
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    outdir: str
    lang: str
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.85 Safari/537.36"
    )
    timeout: int = 10  # seconds
    retries: int = 3


class Downloader:
    def __init__(self, config: Config):
        self.config = config
        self.session = self._init_session()

    def _init_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": self.config.user_agent,
        })
        retry_strategy = Retry(
            total=self.config.retries,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def run(self):
        logger.info(f"Starting download for language: {self.config.lang}")
        try:
            words = download_search_words(self.session, self.config.lang, self.config.timeout)
        except Exception as e:
            logger.error(f"Failed to download word list: {e}")
            return

        logger.info(f"Total words fetched: {len(words)}")
        os.makedirs(self.config.outdir, exist_ok=True)

        for i, word in enumerate(tqdm(words, desc="Words")):
            # Skip if the word directory already exists:
            word_dir = os.path.join(self.config.outdir, word)
            if os.path.exists(word_dir):
                logger.debug(f"Skipping already processed word: {word}")
                continue
            try:
                download_audios(self.session, word, word_dir, self.config.lang, self.config.timeout)
            except Exception as e:
                logger.warning(f"Error processing '{word}': {e}")
            
            # Sleep randomly:
            time.sleep(random.uniform(0, 2))

            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1} words, sleeping for a moment...")
                time.sleep(10)

        logger.info("All downloads complete.")


def get_audio_paths(session: requests.Session, word: str, lang: str, timeout: int) -> Optional[List[str]]:
    base = {
        "es": "https://www.wordreference.com/definicion/",
        "en": "https://www.wordreference.com/definition/",
    }
    if lang not in base:
        raise ValueError(f"Unsupported language: {lang}")
    url = base[lang] + word
    logger.debug(f"Requesting page: {url}")
    resp = session.get(url, timeout=timeout)
    # Detect Captcha redirect
    if "ShowCaptcha" in resp.url:
        logger.warning(f"Captcha encountered for '{word}' (redirect to {resp.url}), skipping.")
        return None
    resp.raise_for_status()
    text = resp.text
    m = re.search(r"var\s+audioFiles\s*=\s*(\[[^\]]*\])", text)
    if not m:
        return []
    try:
        paths = eval(m.group(1))  # safe JS array literal
    except Exception as e:
        logger.warning(f"Failed to parse audio paths for '{word}': {e}")
        return []
    return paths


def download_audios(session: requests.Session, word: str, outdir: str, lang: str, timeout: int) -> None:
    paths = get_audio_paths(session, word, lang, timeout)
    if paths is None:
        logger.debug(f"Captcha found for '{word}'")
        return
    elif len(paths) == 0:
        logger.debug(f"No audio files found for '{word}'")
        os.makedirs(outdir, exist_ok=True)
        # Write an empty file to indicate no audio files:
        with open(os.path.join(outdir, "NOAUDIO"), "w") as f:
            pass
    else:
        os.makedirs(outdir, exist_ok=True)
        for path in paths:
            # e.g. path == '/audio/en/uk/general/en086958.mp3'
            # split into ['', 'audio','en','uk','general','en086958.mp3']
            parts = path.split('/')
            fn = ".".join(parts[1:])
            full_path = os.path.join(outdir, fn)
            url = "https://www.wordreference.com" + path
            try:
                resp = session.get(url, timeout=timeout)
                resp.raise_for_status()
                with open(full_path, "wb") as f:
                    f.write(resp.content)
            except Exception as e:
                logger.warning(f"Failed download {url}: {e}")


def download_search_words(session: requests.Session, lang: str, timeout: int) -> List[str]:
    sources = {
        "es": "https://raw.githubusercontent.com/xavier-hernandez/spanish-wordlist/main/text/spanish_words.txt",
        "en": "https://raw.githubusercontent.com/dwyl/english-words/refs/heads/master/words_alpha.txt",
    }
    if lang not in sources:
        raise ValueError(f"Unsupported language: {lang}")
    url = sources[lang]
    logger.info(f"Fetching words from {url}")
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    text = resp.text.replace("ń", "ñ").replace("Ń", "Ñ") # fix for ñ error...
    words = [w.strip() for w in text.splitlines() if w.strip()]
    if not words:
        raise RuntimeError("Word list is empty.")
    words = sorted(set(words))  # Remove duplicates and sort
    return words


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download WordReference audio files.")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--lang", required=True, choices=["es","en"] )
    args = parser.parse_args()
    config = Config(outdir=args.outdir, lang=args.lang)
    Downloader(config).run()
