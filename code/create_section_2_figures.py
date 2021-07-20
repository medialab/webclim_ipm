import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utils import import_data, save_figure, plot_one_group


def import_crowdtangle_group_data():

    posts_wi_date_df = import_data(file_name="posts_self_declared_wi_date.csv")
    print('\nThere are {} Facebook pages with the last strike date visible on the screenshot.'.\
        format(posts_wi_date_df.account_id.nunique()))

    posts_wo_date_df = import_data(file_name="posts_self_declared_wo_date.csv")
    list_wo_name = [
        'Artists For A Free World',
        'Terrence K Williams',
        'Ben Garrison Cartoons',
        'Wendy Bell Radio',
        'New Independence Network',
        'Pruden POD & Post',
        'PR Conservative',
        'Org of Conservative Trump Americans',
        'Con Ciencia Indigena',
        'Republican Party of Lafayette County',
        'The Daily Perspective Podcast',
        'Freedom Memes',
        'White Dragon Society',
        'Robertson Family Values'
    ]
    posts_wo_date_df = posts_wo_date_df[~posts_wo_date_df['account_name'].isin(list_wo_name)]
    print('There are {} Facebook pages without the last strike date visible on the screenshot.'.\
        format(posts_wo_date_df.account_id.nunique()))

    posts_df = pd.concat([posts_wi_date_df, posts_wo_date_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])

    return posts_df


def create_reduce_example_timeseries_figure(posts_df):

    account_name = 'I Love Carbon Dioxide'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    reduced_distribution_date = '2020-04-28'

    plt.figure(figsize=(7, 4))
    ax = plt.subplot()
    
    plt.title("Engagement metrics for the '" + account_name + "' Facebook page")

    plot_one_group(ax, posts_df, account_id)
    plt.ylim(0, 2000)

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-09-01'), np.datetime64('2021-01-01'),
              np.datetime64(reduced_distribution_date)
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.axvline(x=np.datetime64(reduced_distribution_date), 
                color='C3', linestyle='--', linewidth=2)

    plt.legend()
    plt.tight_layout()
    save_figure('reduce_example_timeseries', dpi=100)


if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()
    create_reduce_example_timeseries_figure(posts_df)