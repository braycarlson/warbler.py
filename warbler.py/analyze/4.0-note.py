import matplotlib.pyplot as plt

from dataclass.signal import Signal
from parameters import BASELINE
from pathlib import Path
from spectrogram.plot import plot_segmentations
from vocalseg.dynamic_thresholding import dynamic_threshold_segmentation


def main():
    parameters = BASELINE

    parameters.n_fft = 4096
    parameters.hop_length_ms = 1
    parameters.win_length_ms = 5
    parameters.ref_level_db = 50
    parameters.preemphasis = 0.97
    parameters.min_level_db = -50
    parameters.min_level_db_floor = -20
    parameters.db_delta = 5
    parameters.silence_threshold = 0.01
    parameters.min_silence_for_spec = 0.01
    parameters.max_vocal_for_spec = 1.0
    parameters.min_syllable_length_s = 0.01

    path = Path(
        'E:/code/personal/warbler.py/data/DbWY_STE2017/wav/STE16_DbWY2017.wav'
    )

    signal = Signal(path)

    signal.filter(
        parameters.butter_lowcut,
        parameters.butter_highcut
    )

    results = dynamic_threshold_segmentation(
        signal.data,
        signal.rate,
        n_fft=parameters.n_fft,
        hop_length_ms=parameters.hop_length_ms,
        win_length_ms=parameters.win_length_ms,
        ref_level_db=parameters.ref_level_db,
        pre=parameters.preemphasis,
        min_level_db=parameters.min_level_db,
        silence_threshold=parameters.silence_threshold,
        spectral_range=parameters.spectral_range,
        min_syllable_length_s=parameters.min_syllable_length_s
    )

    plot_segmentations(
        results['spec'],
        results['vocal_envelope'],
        results['onsets'],
        results['offsets'],
        parameters.hop_length_ms,
        signal,
        figsize=(15, 5)
    )

    plt.show()


if __name__ == '__main__':
    main()
