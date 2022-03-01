import logging

from logger import logger
from path import bootstrap, DATA, DATASET, DIRECTORIES, INDIVIDUALS
from pydub import AudioSegment


log = logging.getLogger(__name__)


@bootstrap
def main():
    aif = [file for file in DATASET.glob('*/*.aif')]
    wav = [file for file in DATA.glob('*/wav/*.wav')]

    a = len(aif)
    w = len(wav)

    # Is each .aif is converted to .wav?
    if a == w:
        log.info(f"{a} .aif files, {w} .wav files")
        return

    for directory in DIRECTORIES:
        for individual in INDIVIDUALS:
            if individual.stem == directory.stem:
                # Note: pydub uses ffmpeg
                for file in directory.glob('*.aif'):
                    wav = individual.joinpath('wav')
                    audio = AudioSegment.from_file(file, format='aiff')

                    filename = file.stem + '.wav'
                    audio.export(wav.joinpath(filename), format='wav')


if __name__ == '__main__':
    with logger():
        main()
