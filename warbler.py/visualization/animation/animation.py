from __future__ import annotations

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

from datatype.builder import Base, Plot
from constant import SETTINGS
from datatype.dataset import Dataset
from datatype.settings import Settings
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Any, Self


class Builder(Base):
    def __init__(self):
        super().__init__()
        self.dataframe = None
        self.unit = {
            'onset': 's',
            'offset': 's',
            'duration': 's',
            'minimum': 'Hz',
            'mean': 'Hz',
            'maximum': 'Hz'
        }

    def ax(self) -> Self:
        figsize = (14, 16)
        figure = plt.figure(figsize=figsize)

        gs = GridSpec(
            3,
            2,
            height_ratios=[1, 3, 2],
            width_ratios=[1, 3]
        )

        # Projection
        ax1 = plt.subplot(gs[1:, :])

        # Spectrogram
        ax2 = plt.subplot(gs[0, 0])

        ax2.set_title(
            'Spectrogram',
            fontsize=20,
            pad=90
        )

        ax2.axis('off')

        # Table
        ax3 = plt.subplot(gs[0, 1])

        plt.subplots_adjust(hspace=1.0)

        self.component['ax'] = ax1
        self.component['ax2'] = ax2
        self.component['ax3'] = ax3
        self.component['figure'] = figure

        return self

    def legend(self) -> Self:
        condition = (
            not self.settings.is_legend or
            not self.settings.is_color
        )

        if condition:
            return self

        ax = self.component.get('ax')
        handles = self.component.get('handles')

        ax.legend(
            handles=handles,
            **self.settings.legend
        )

        return self

    def line(self) -> Self:
        condition = (
            not self.settings.is_legend or
            not self.settings.is_color
        )

        if condition:
            return self

        label = self.component.get('label')

        handles = [
            Line2D(
                [0],
                [0],
                color=color,
                label=label,
                **self.settings.line
            )
            for label, color in label.items()
        ]

        self.component['handles'] = handles

        return self

    def scatter(self) -> Self:
        ax = self.component.get('ax')

        if self.settings.is_color:
            color = self.component.get('color')
            self.settings.scatter['color'] = color

        if self.settings.is_legend:
            label = self.component.get('label')
            self.settings.scatter['label'] = label

        scatter_plot = ax.scatter(
            self.embedding[:, 0],
            self.embedding[:, 1],
            **self.settings.scatter
        )

        ax.set(
            xlabel=None,
            ylabel=None,
            xticklabels=[],
            yticklabels=[]
        )

        ax.tick_params(
            bottom=False,
            left=False
        )

        self.component['scatter_plot'] = scatter_plot

        spectrogram_plot = self.component['ax2'].matshow(
            self.spectrogram[0],
            aspect='auto',
            cmap='Greys'
        )

        self.component['spectrogram_plot'] = spectrogram_plot

        return self

    def table(self, i: int) -> Self:
        ax = self.component.get('ax3')

        ax.cla()

        columns = [
            'folder',
            'filename',
            'sequence',
            'onset',
            'offset',
            'duration',
            'minimum',
            'mean',
            'maximum'
        ]

        copy = self.dataframe.copy()
        features = ['onset', 'offset', 'duration', 'minimum', 'mean', 'maximum']

        copy[features] = copy[features].round(2)

        information = copy.loc[i, columns]

        text = []

        for column, value in zip(columns, information):
            if column in features:
                text.append(
                    (column, str(value) + ' ' + self.unit[column])
                )
            else:
                text.append(
                    (column, value)
                )

        table = ax.table(
            cellLoc='center',
            cellText=text,
            loc='center'
        )

        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 2.0)

        for (row, _), cell in table.get_celld().items():
            if row % 2 == 0:
                cell.set_facecolor('white')
            else:
                cell.set_facecolor(self.settings.row)

        ax.axis('tight')

        ax.set_title(
            'Acoustic Features',
            fontsize=20,
            pad=90
        )

        ax.set(
            xlabel=None,
            ylabel=None,
            xticklabels=[],
            yticklabels=[]
        )

        ax.tick_params(
            bottom=False,
            left=False
        )

        ax.axis('off')

        return self

    def update(self, i: int):
        print(f"Processing: frame {i}")

        embedding = self.embedding[:i]
        spectrogram = self.spectrogram[i]

        self.component['scatter_plot'].set_offsets(embedding)
        self.component['spectrogram_plot'].set_data(spectrogram)

        self.table(i)

        return (
            self.component['scatter_plot'],
            self.component['spectrogram_plot']
        )


    def title(self) -> Self:
        ax = self.component.get('ax')

        name = self.settings.name
        cluster = self.settings.cluster

        title = f"{cluster} Clustering for {name}"

        ax.set_title(
            title,
            fontsize=20,
            pad=25
        )

        return self


class ScatterFCM(Plot):
    def animate(self) -> Any:
        cluster = {'cluster': 'Fuzzy C-Means'}
        self.builder.settings.update(cluster)

        length = len(self.builder.embedding)
        frames = range(length)

        for i in frames:
            plot = (
                self
                .builder
                .ax()
                .title()
                .palette()
                .line()
                .scatter()
                .legend()
                .get()
            )

            figure = plot.get('figure')

            self.builder.update(i)

            plt.subplots_adjust(
                left=0.05,
                right=0.85,
                bottom=0.05
            )

            i = str(i).zfill(2)
            figure.savefig(f"frames/frame_{i}.png")
            plt.close()


def main() -> None:
    dataset = Dataset('segment')
    dataframe = dataset.load()

    drop = [
        'fcm_label_3d',
        'filter_bytes',
        'hdbscan_label_2d',
        'hdbscan_label_3d',
        'original',
        'original_bytes',
        'scale',
        'segment',
        'settings',
        'spectrogram',
        'umap_z_3d'
    ]

    dataframe = dataframe.drop(drop, axis=1)

    order = [1, 0, 8, 3, 10, 5, 7, 2, 6, 4, 9, 13, 11, 12]

    order_dict = {k: i for i, k in enumerate(order)}

    dataframe['fcm_label_2d_order'] = dataframe['fcm_label_2d'].map(order_dict)

    dataframe = dataframe.sort_values(by='fcm_label_2d_order')

    dataframe = dataframe.groupby('fcm_label_2d_order').apply(
        lambda x: x.sort_values('mean')
    ).reset_index(drop=True)

    dataframe = dataframe.drop('fcm_label_2d_order', axis=1)
    dataframe = dataframe.reset_index(drop=True)

    # Load default settings
    path = SETTINGS.joinpath('scatter.json')
    settings = Settings.from_file(path)

    # Change the default to accommodate a larger dataset
    color = 'gainsboro'
    opacity = 0.5
    color = mcolors.to_rgba(color)
    row = color[:3] + (opacity,)

    settings['scatter']['alpha'] = 0.25
    settings['scatter']['s'] = 50
    settings['row'] = row

    unique = dataframe.fcm_label_2d.unique()

    coordinates = [
        dataframe.umap_x_2d,
        dataframe.umap_y_2d
    ]

    embedding = np.column_stack(coordinates)
    label = dataframe.fcm_label_2d.to_numpy()
    spectrogram = dataframe.filter_array.to_numpy()

    scatter = ScatterFCM()

    scatter.builder = Builder()
    scatter.builder.dataframe = dataframe
    scatter.embedding = embedding
    scatter.label = label
    scatter.settings = settings
    scatter.spectrogram = ~spectrogram
    scatter.unique = unique

    scatter.builder.component['color'] = label

    scatter.animate()


if __name__ == '__main__':
    main()
