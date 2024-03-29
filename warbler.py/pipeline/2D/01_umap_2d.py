"""
UMAP
----

"""

from __future__ import annotations

from datatype.dataset import Dataset
from datatype.spectrogram import flatten
from umap import UMAP


def main() -> None:
    dataset = Dataset('segment')
    dataframe = dataset.load()

    spectrogram = dataframe['filter_array'].tolist()
    flattened = flatten(spectrogram)

    um = UMAP(
        low_memory=True,
        metric='euclidean',
        min_dist=0.0,
        n_neighbors=5,
        n_components=2,
        n_jobs=-1
    )

    embedding = um.fit_transform(flattened)

    column = [
        'umap_x_2d',
        'umap_y_2d'
    ]

    dataframe[column] = embedding

    dataset.save(dataframe)


if __name__ == '__main__':
    main()
