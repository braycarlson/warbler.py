"""
Sequence2
---------

"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from constant import CWD, PICKLE, PROJECTION, SETTINGS
from datatype.dataset import Dataset
from datatype.imaging import create_image
from datatype.plot import (
    BandwidthSpectrogram,
    SegmentationSpectrogram,
    StandardSpectrogram
)
from datatype.segmentation import DynamicThresholdSegmentation
from datatype.settings import Settings
from datatype.signal import Signal
from datatype.spectrogram import (
    create_spectrogram,
    Linear,
    mel_matrix,
    Spectrogram
)
from io import BytesIO
from PIL import Image as Pillow
from PIL import ImageDraw, ImageFont, ImageOps
from tqdm import tqdm
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy.typing as npt
    import pandas as pd


def create_grid(collection: npt.NDArray, text: str) -> Pillow:
    """Create a grid image from a collection of images.

    Args:
        collection: A numpy array of images.
        text: The text to be displayed on the grid.

    Returns:
        A Pillow image representing the grid.

    """

    column = row = 5

    if all(isinstance(image, bytes) for image in collection):
        collection = [
            np.array(create_image(image), dtype='uint8')
            for image in collection
        ]

    shape = [np.shape(image) for image in collection]

    height, width = max(shape)
    width = np.amax(width)
    height = np.amax(height)

    offset = 20

    grid = Pillow.new(
        'L',
        color=255,
        size=(
            (column * width) + offset,
            (row * height) + offset
        )
    )

    for index, image in enumerate(collection, 0):
        grid.paste(
            create_image(image),
            box=(
                (index % column * width) + offset,
                (index // column * height) + (offset * 2)
            )
        )

    grid = ImageOps.expand(
        grid,
        border=(50, 50),
        fill=(255)
    )

    draw = ImageDraw.Draw(grid)
    font = ImageFont.truetype('fonts/times.ttf', 32)
    text_width = draw.textlength(text, font=font)

    size = (
        (width // 2) + text_width + offset + 50,
        10
    )

    draw.text(
        size,
        text,
        (0),
        font=font
    )

    return grid


def create_signal_page(collection: npt.NDArray, text: str) -> Pillow:
    """Create a signal page image from a collection of images.

    Args:
        collection: A numpy array of images.
        text: The text to be displayed on the signal page.

    Returns:
        A Pillow image representing the signal page.

    """

    padding = y = 800
    length = len(collection)

    if all(isinstance(image, bytes) for image in collection):
        collection = [
            np.array(create_image(image), dtype='uint8')
            for image in collection
        ]

    shape = [np.shape(image) for image in collection]

    height, width, _ = max(shape)
    width = np.amax(width)
    height = np.amax(height)

    height = (height * length) + (padding * length) + y

    if width < 500:
        width = 500

    grid = Pillow.new(
        mode='RGBA',
        color=(255, 255, 255, 255),
        size=(width, height)
    )

    for _, image in enumerate(collection):
        x = int(
            (width - image.width) / 2
        )

        grid.paste(
            image,
            (x, y)
        )

        y = y + image.height + padding

    grid = ImageOps.expand(
        grid,
        border=(50, 300),
        fill=(255, 255, 255, 255)
    )

    draw = ImageDraw.Draw(grid)
    font = ImageFont.truetype('fonts/times.ttf', 300)
    text_width = draw.textlength(text, font=font)

    size = (
        (width + 50 - text_width) // 2,
        50
    )

    draw.text(
        size,
        text,
        (0),
        font=font
    )

    return grid


def get_buffer(row: pd.Series) -> list[BytesIO]:
    """Create a list of image buffers from a row of data.

    Args:
        row: A pandas Series containing the data.

    Returns:
        A list of BytesIO image buffers.

    """

    poster = []

    recording = row.recording
    segmentation = row.segmentation
    # onsets = row.onset
    # offsets = row.offset

    path = CWD.joinpath(recording)
    signal = Signal(path)

    path = CWD.joinpath(segmentation)
    custom = Settings.from_file(path)

    path = SETTINGS.joinpath('dereverberate.json')
    dereverberate = Settings.from_file(path)

    # Original signal
    spectrogram = create_spectrogram(signal, custom)

    plot = StandardSpectrogram()
    plot.signal = signal
    plot.spectrogram = spectrogram
    plot.create()

    plt.title(
        'Original',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    # Pre-Bandpass Filter
    spectrogram = Spectrogram()
    strategy = Linear(signal, custom)
    spectrogram.strategy = strategy

    spectrogram = spectrogram.generate()

    plot = BandwidthSpectrogram()
    plot.settings = custom
    plot.signal = signal
    plot.spectrogram = spectrogram
    plot.create()

    plt.title(
        'Pre-Bandpass Filter',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    # Bandpass filter
    signal.filter(
        custom.butter_lowcut,
        custom.butter_highcut
    )

    spectrogram = create_spectrogram(signal, custom)

    plot = StandardSpectrogram()
    plot.signal = signal
    plot.spectrogram = spectrogram
    plot.create()

    plt.title(
        'Bandpass Filter',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    # Normalize
    signal.normalize()

    spectrogram = create_spectrogram(signal, custom)

    plot = StandardSpectrogram()
    plot.signal = signal
    plot.spectrogram = spectrogram
    plot.create()

    plt.title(
        'Normalize',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    spectrogram = create_spectrogram(signal, custom)

    # Dereverberate
    signal.dereverberate(dereverberate)

    spectrogram = create_spectrogram(signal, custom)

    plot = StandardSpectrogram()
    plot.signal = signal
    plot.spectrogram = spectrogram
    plot.create()

    plt.title(
        'Dereverberate',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    # # Reduce
    # signal.reduce()

    # spectrogram = create_spectrogram(signal, custom)

    # plot = StandardSpectrogram()
    # plot.signal = signal
    # plot.spectrogram = spectrogram
    # plot.create()

    # plt.title(
    #     'Reduce',
    #     fontweight=600,
    #     fontsize=24,
    #     pad=25
    # )

    # buffer = BytesIO()

    # plt.savefig(
    #     buffer,
    #     bbox_inches='tight',
    #     dpi=300,
    #     format='png'
    # )

    # poster.append(buffer)

    # plt.close()

    spectrogram = create_spectrogram(signal, custom)

    # Segmentation
    algorithm = DynamicThresholdSegmentation()
    algorithm.signal = signal
    algorithm.settings = custom
    algorithm.start()

    algorithm.component['spectrogram'] = spectrogram

    plot = SegmentationSpectrogram()
    plot.algorithm = algorithm
    plot.settings = custom
    plot.signal = signal
    plot.create()

    plt.title(
        'Segmentation',
        fontweight=600,
        fontsize=24,
        pad=25
    )

    buffer = BytesIO()

    plt.savefig(
        buffer,
        bbox_inches='tight',
        dpi=300,
        format='png'
    )

    poster.append(buffer)

    plt.close()

    path = SETTINGS.joinpath('spectrogram.json')
    settings = Settings.from_file(path)

    path = PICKLE.joinpath('matrix.npy')

    if path.is_file():
        matrix = np.load(path, allow_pickle=True)
    else:
        matrix = mel_matrix(settings)
        np.save(path, matrix, allow_pickle=True)

    # original = []
    # filtered = []

    # for index, (onset, offset) in enumerate(zip(onsets, offsets), 0):
    #     if index in custom.exclude:
    #         continue

    #     segment = signal.segment(onset, offset)
    #     spectrogram = create_spectrogram(segment, settings)

    #     image = create_image(spectrogram)
    #     o = to_bytes(image)

    #     original.append(o)

    #     image = filter_image(image)
    #     image = to_bytes(image)

    #     filtered.append(image)

    # grid = create_grid(original, 'Original')

    # buffer = BytesIO()

    # grid.save(
    #     buffer,
    #     format='png'
    # )

    # poster.append(buffer)

    # grid = create_grid(filtered, 'Filtered')

    # buffer = BytesIO()

    # grid.save(
    #     buffer,
    #     format='png'
    # )

    # poster.append(buffer)

    return poster


def main() -> None:
    dataset = Dataset('signal')
    dataframe = dataset.load()

    folders = dataframe.folder.unique()

    for folder in folders:
        path = PROJECTION.joinpath(folder)
        path.mkdir(parents=True, exist_ok=True)

    tqdm.pandas(desc='Getting buffer')

    dataframe['buffer'] = (
        dataframe.progress_apply(get_buffer, axis=1)
    )

    folders = dataframe.folder.tolist()
    filenames = dataframe.filename.tolist()
    buffers = dataframe.buffer.tolist()

    for folder, filename, buffer in zip(folders, filenames, buffers):
        print(f"Processing: {filename}")

        images = [
            Pillow.open(b)
            for b in buffer
        ]

        page = create_signal_page(images, filename)

        for b in buffer:
            b.close()

        name = filename + '.png'
        path = PROJECTION.joinpath(folder, name)

        size = (4096, 4096)
        page = ImageOps.contain(page, size)

        page.save(
            path,
            dpi=(72, 72),
            format='png'
        )


if __name__ == '__main__':
    main()
