import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import import_data, save_figure, plot_engagement_timeserie


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
        print(posts_df_group_before['date'].nunique(), posts_df_group_after['date'].nunique())

    #     if (len(posts_df_group_before) > 0) & (len(posts_df_group_after) > 0):
            
    #         sumup_df = sumup_df.append({
    #             'account_name': account_name, 
    #             'engagement_before': np.mean(posts_df_group_before['engagement']),
    #             'engagement_after': np.mean(posts_df_group_after['engagement']),
    #         }, ignore_index=True)
            
    # sumup_df['percentage_change_engagament'] = ((sumup_df['engagement_after'] - sumup_df['engagement_before'])/
    #                                             sumup_df['engagement_before']) * 100
    # return sumup_df


if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()
    # create_repeat_example_timeseries_figure(posts_df)

    # plot_repeat_average_timeseries(posts_df)
    calculate_june_drop(posts_df)