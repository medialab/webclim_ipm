import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

from utils import import_data, save_figure, plot_engagement_timeserie, calculate_june_drop


def import_crowdtangle_group_data():

    df_list = []
    for file_index in range(5):
        df_list.append(import_data(file_name="posts_fake_news_2021_group_" + str(file_index + 1) + ".csv"))
    posts_group_df = pd.concat(df_list)

    print("\nThere are {} 'repeat offender' Facebook groups.".format(posts_group_df.account_id.nunique()))

    posts_page_df = import_data(file_name="posts_fake_news_2021_page.csv")
    print("There are {} 'repeat offender' Facebook pages.".format(posts_page_df.account_id.nunique()))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df


def plot_repeat_average_timeseries(posts_df):

    drop_date='2020-06-09'

    plt.figure(figsize=(6, 4))
    ax = plt.subplot()

    plt.title("'Repeat offender' Facebook accounts")

    plot_engagement_timeserie(ax, posts_df)

    plt.ylim(0, 60)
    plt.axvline(x=np.datetime64(drop_date), color='C3', linestyle='--')

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'), 
              np.datetime64('2021-01-01'), np.datetime64(drop_date)
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.tight_layout()
    save_figure('repeat_average_timeseries')


def plot_repeat_june_drop_percentage_change(posts_df):

    sumup_df = calculate_june_drop(posts_df)

    posts_page_df = import_data(file_name="posts_fake_news_2021_page.csv")
    sumup_pages_df = sumup_df[sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    sumup_groups_df = sumup_df[~sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]

    plt.figure(figsize=(6, 2.8))
    ax = plt.subplot(111)
    plt.title("'Repeat offender' Facebook accounts")

    plt.plot(sumup_groups_df['percentage_change_engagament'].values, 
             list(np.random.random(len(sumup_groups_df))), 
             'o', markerfacecolor='royalblue', markeredgecolor='blue', alpha=0.4)
    plt.plot(sumup_pages_df['percentage_change_engagament'].values, 
             list(np.random.random(len(sumup_pages_df))), 
             'o', markerfacecolor='royalblue', markeredgecolor='red', alpha=0.4)

    plt.axvline(x=0, color='k', linestyle='--', linewidth=1)
    plt.xticks([-100, 0, 100], 
            ['-100 %', ' 0 %', '+100 %'])
    plt.xlabel("Engagement percentage change after June 9, 2020", size='large')

    plt.xlim(-120, 135)
    plt.yticks([])
    plt.ylim(-.2, 1.2)
    ax.set_frame_on(False)

    plt.tight_layout()
    save_figure('repeat_june_drop_percentage_change')

    print('\nJUNE DROP:')

    print('Number of Facebook account:', len(sumup_df))
    print('Number of Facebook account with a decrease:', len(sumup_df[sumup_df['percentage_change_engagament'] < 0]))
    print('Mean engagement percentage changes:', np.mean(sumup_df['percentage_change_engagament']))
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    
    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)

    print('Median engagement percentage changes for groups:', 
          np.median(sumup_groups_df['percentage_change_engagament']),
          ', n =', len(sumup_groups_df))
    print('Median engagement percentage changes for pages:', 
          np.median(sumup_pages_df['percentage_change_engagament']),
          ', n =', len(sumup_pages_df))


if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()
    # create_repeat_example_timeseries_figure(posts_df)

    plot_repeat_average_timeseries(posts_df)
    plot_repeat_june_drop_percentage_change(posts_df)
