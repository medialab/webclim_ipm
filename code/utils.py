import os
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def import_data(file_name):

    data_path = os.path.join(".", "data", file_name)
    df = pd.read_csv(data_path, low_memory=False)

    return df


def save_figure(figure_name, dpi=None):

    figure_path = os.path.join('.', 'figure', figure_name + '.png')
    
    plt.savefig(figure_path, dpi=dpi)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def plot_engagement_timeserie(ax, posts_df):
    
    plt.plot(posts_df.groupby(by=["date"])['engagement'].mean(), color="royalblue")

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'),
              np.datetime64('2021-01-01')
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2018-12-31', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2021-01-01', '%Y-%m-%d') + datetime.timedelta(days=4))
    )

    plt.ylabel("Average engagement per post", size='large')
    plt.locator_params(axis='y', nbins=4)
    ax.grid(axis="y")

    ax.set_frame_on(False)