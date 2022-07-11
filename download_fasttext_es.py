
import os

import fasttext.util


def main():

    SAVE_PATH = "models" # relative to this file

    os.chdir(SAVE_PATH)

    fasttext.util.download_model('es', if_exists='ignore')  # Spanish


if __name__ == '__main__':
    main()
