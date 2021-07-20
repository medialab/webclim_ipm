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


def rolling_average_per_day(df, column):
    return df.groupby(by=["date"])[column].mean()#.rolling(window=5, win_type='triang', center=True).mean()


def plot_one_group(ax, posts_df, account_id):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), 
            label="Reactions per post", color="C0")

    plt.plot(rolling_average_per_day(posts_df_group, 'share'), 
            label="Shares per post", color="C1")

    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), 
            label="Comments per post", color="C2")

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01')
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2018-12-31', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2021-01-01', '%Y-%m-%d') + datetime.timedelta(days=4))
    )

    plt.locator_params(axis='y', nbins=4)
    ax.grid(axis="y")

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)