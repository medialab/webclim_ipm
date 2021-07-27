import os
import datetime
import random

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

    print('\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))
    print()


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


def calculate_june_drop(posts_df, period_length=30, drop_date='2020-06-09'):

    drop_date = datetime.datetime.strptime(drop_date, '%Y-%m-%d')

    sumup_df = pd.DataFrame(columns=[
        'account_name', 
        'engagement_before', 
        'engagement_after'
    ])

    for account_id in posts_df['account_id'].unique():

        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        posts_df_group_before = posts_df_group[
            (posts_df_group['date'] >= drop_date - datetime.timedelta(days=period_length)) &
            (posts_df_group['date'] < drop_date)
        ]
        posts_df_group_after = posts_df_group[
            (posts_df_group['date'] > drop_date) &
            (posts_df_group['date'] <= drop_date + datetime.timedelta(days=period_length))
        ]

        if (len(posts_df_group_before) > 0) & (len(posts_df_group_after) > 0) & (np.mean(posts_df_group_before['engagement']) > 0):
            
            sumup_df = sumup_df.append({
                'account_name': account_name, 
                'engagement_before': np.mean(posts_df_group_before['engagement']),
                'engagement_after': np.mean(posts_df_group_after['engagement']),
            }, ignore_index=True)
            
    sumup_df['percentage_change_engagament'] = ((sumup_df['engagement_after'] - sumup_df['engagement_before'])/
                                                sumup_df['engagement_before']) * 100
    return sumup_df


def calculate_confidence_interval_median(sample):

    medians = []
    for bootstrap_index in range(1000):
        resampled_sample = random.choices(sample, k=len(sample))
        medians.append(np.median(resampled_sample))

    return np.percentile(medians, 5), np.percentile(medians, 95)


def percentage_change_template(ax):

    plt.legend(loc='upper right')

    plt.axvline(x=0, color='k', linestyle='--', linewidth=1)
    plt.xticks([-100, -75, -50, -25, 0, 25, 50, 75, 100, 125], 
            ['-100%', '-75%', '-50%', '-25%', ' 0%', '+25%', '+50%', '+75%', '+100%', '+125%'])
    plt.xlim(-120, 135)

    plt.yticks([])
    ax.set_frame_on(False)