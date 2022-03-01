from parameters import BASELINE
from path import DATA
from spectrogram.spectrogram import create_spectrogram


def main():
    path = DATA.joinpath('DgDgY_STE2017/wav/STE01_1_DgDgY2017.wav')
    plt = create_spectrogram(path, BASELINE)

    plt.show()
    plt.close()


if __name__ == '__main__':
    main()
