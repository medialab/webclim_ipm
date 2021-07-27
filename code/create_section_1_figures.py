import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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


def clean_crowdtangle_url_data(post_url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')
    post_url_df['account_id'] = post_url_df['account_id'].astype(int)

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    return post_url_df


def compute_fake_news_dates(post_url_df, url_df, account_id):

    post_url_group_df = post_url_df[post_url_df["account_id"]==account_id]
    fake_news_dates = []

    for url in post_url_group_df["url"].unique().tolist():
        potential_dates = []

        # We consider the date of the Facebook post or posts:
        potential_dates.append(post_url_group_df[post_url_group_df["url"] == url]["date"].values[0])
        # We consider the date of the fact-check:
        potential_dates.append(url_df[url_df['url']==url]["Date of publication"].values[0])

        potential_dates = [np.datetime64(date) for date in potential_dates]
        date_to_plot = np.max(potential_dates)
        fake_news_dates.append(date_to_plot)
        
    fake_news_dates.sort()

    return fake_news_dates


def compute_repeat_offender_periods(fake_news_dates):

    repeat_offender_periods = []

    if len(fake_news_dates) > 1:
        for index in range(1, len(fake_news_dates)):
            if fake_news_dates[index] - fake_news_dates[index - 1] < np.timedelta64(90, 'D'):

                repeat_offender_periods.append([
                    fake_news_dates[index],
                    fake_news_dates[index - 1] + np.timedelta64(90, 'D')
                ])

    return repeat_offender_periods


def merge_overlapping_periods(overlapping_periods):
    
    if len(overlapping_periods) == 0:
        return []
    
    else:
        overlapping_periods.sort(key=lambda interval: interval[0])
        merged_periods = [overlapping_periods[0]]

        for current in overlapping_periods:
            previous = merged_periods[-1]
            if current[0] <= previous[1]:
                previous[1] = max(previous[1], current[1])
            else:
                merged_periods.append(current)

        return merged_periods


def plot_repeat_example_timeseries_figure(posts_df, posts_url_df, url_df):

    account_name = 'Australian Climate Sceptics Group'

    plt.figure(figsize=(6, 4))
    ax = plt.subplot()
    
    plt.title("'" + account_name + "' Facebook group")

    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    plot_engagement_timeserie(ax, posts_df_group)
    plt.ylim(-15, 150)

    fake_news_dates = compute_fake_news_dates(posts_url_df, url_df, account_id)
    for date in fake_news_dates:
        plt.plot([date, date], [-15, -.5], color='C3')
    plt.text(
        s='Known strikes', color='C3', fontweight='bold',
        x=np.datetime64('2019-09-15'), horizontalalignment='right', 
        y=-3, verticalalignment='top'
    )

    repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
    repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
    for period in repeat_offender_periods:
        plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

    patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
    patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
    plt.legend([patch1, patch2], ["'Repeat offender' periods", "'No strike' periods"],
               loc='upper left', framealpha=1)

    plt.tight_layout()
    save_figure('repeat_example_timeseries')


def keep_repeat_offender_posts(posts_df_group, repeat_offender_periods):
    
    if len(repeat_offender_periods) == 0:
        return pd.DataFrame()

    repeat_offender_df_list = []
    for repeat_offender_period in repeat_offender_periods:
        new_df = posts_df_group[(posts_df_group['date'] >= repeat_offender_period[0]) &
                                (posts_df_group['date'] <= repeat_offender_period[1])]
        if len(new_df) > 0:
            repeat_offender_df_list.append(new_df)
    
    if len(repeat_offender_df_list) > 0:
        return pd.concat(repeat_offender_df_list)
    else:
        return pd.DataFrame()


def keep_free_posts(posts_df_group, repeat_offender_periods):
        
    if len(repeat_offender_periods) == 0:
        return posts_df_group

    free_df_list = []
    for ro_index in range(len(repeat_offender_periods) + 1):
        if ro_index == 0:
            new_df = posts_df_group[posts_df_group['date'] < repeat_offender_periods[0][0]]
        elif ro_index == len(repeat_offender_periods):
            new_df = posts_df_group[posts_df_group['date'] > repeat_offender_periods[-1][1]]
        else:
            new_df = posts_df_group[(posts_df_group['date'] > repeat_offender_periods[ro_index - 1][1]) &
                                    (posts_df_group['date'] < repeat_offender_periods[ro_index][0])]
        if len(new_df) > 0:
            free_df_list.append(new_df)
    
    if len(free_df_list) > 0:
        return pd.concat(free_df_list)
    else:
        return pd.DataFrame()


def calculate_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df):

    sumup_df = pd.DataFrame(columns=[
        'account_name', 
        'engagement_repeat', 
        'engagement_free'
    ])

    for account_id in posts_df['account_id'].unique():

        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        fake_news_dates = compute_fake_news_dates(posts_url_df, url_df, account_id)
        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)

        repeat_offender_df = keep_repeat_offender_posts(posts_df_group, repeat_offender_periods)
        if len(repeat_offender_df) > 0:
            repeat_offender_df = repeat_offender_df[repeat_offender_df['date'] < datetime.datetime.strptime('2020-06-09', '%Y-%m-%d')]

        free_df = keep_free_posts(posts_df_group, repeat_offender_periods)
        if len(free_df) > 0:
            free_df = free_df[free_df['date'] < datetime.datetime.strptime('2020-06-09', '%Y-%m-%d')]

        if (len(repeat_offender_df) > 0) & (len(free_df) > 0):            
            sumup_df = sumup_df.append({
                'account_name': account_name, 
                'engagement_repeat': np.mean(repeat_offender_df['engagement']),
                'engagement_free': np.mean(free_df['engagement']),
            }, ignore_index=True)
            
    sumup_df['percentage_change_engagament'] = ((sumup_df['engagement_repeat'] - sumup_df['engagement_free'])/
                                                sumup_df['engagement_free']) * 100
    return sumup_df


def plot_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df):

    sumup_df = calculate_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df)

    posts_page_df = import_data(file_name="posts_fake_news_2021_page.csv")
    sumup_pages_df = sumup_df[sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    sumup_groups_df = sumup_df[~sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]

    print('\nREPEAT VS FREE PERIODS:')

    print('Australian Climate Sceptics Group percentage change:', 
          sumup_df[sumup_df['account_name']=='Australian Climate Sceptics Group']['percentage_change_engagament'].values[0])

    print('Number of Facebook accounts:', len(sumup_df))
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
    w, p = stats.wilcoxon(sumup_pages_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for pages: w =', w, ', p =', p)

    plt.figure(figsize=(6, 4))
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
    plt.xlabel("Engagement percentage change\nbetween the 'repeat offender' and 'no strike' periods", size='large')

    plt.xlim(-120, 135)
    plt.yticks([])
    plt.ylim(-.2, 1.2)
    ax.set_frame_on(False)

    plt.tight_layout()
    save_figure('repeat_vs_free_percentage_change')


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

    print('\nJUNE DROP:')

    print("Drop for 'Australian Climate Sceptics Group':", sumup_df[sumup_df['account_name']=='Australian Climate Sceptics Group']['percentage_change_engagament'].values[0])

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
    w, p = stats.wilcoxon(sumup_pages_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for pages: w =', w, ', p =', p)
    plt.figure(figsize=(6, 4))
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


if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()

    posts_url_df  = import_data(file_name="posts_url_2021-01-04_.csv")
    posts_url_df = clean_crowdtangle_url_data(posts_url_df)
    url_df = import_data(file_name="appearances_2021-01-04_.csv") 

    plot_repeat_example_timeseries_figure(posts_df, posts_url_df, url_df)
    plot_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df)

    plot_repeat_average_timeseries(posts_df)
    plot_repeat_june_drop_percentage_change(posts_df)
