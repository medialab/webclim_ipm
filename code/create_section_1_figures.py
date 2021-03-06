import datetime

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import scipy.stats as stats

from utils import (import_data, save_figure, export_data,
                   timeserie_template, percentage_change_template,
                   calculate_june_drop, calculate_confidence_interval_median)


np.random.seed(0)

def import_crowdtangle_group_data():

    df_list = []
    for file_index in range(5):
        df_list.append(import_data(file_name="posts_fake_news_2021_group_" + str(file_index + 1) + ".csv", folder="section_1_sf"))
    posts_group_df = pd.concat(df_list)

    print("\nThere are {} 'repeat offender' Facebook groups.".format(posts_group_df.account_id.nunique()))

    posts_page_df = import_data(file_name="posts_fake_news_2021_page.csv", folder="section_1_sf")
    print("There are {} 'repeat offender' Facebook pages.".format(posts_page_df.account_id.nunique()))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    list_accounts = posts_df[['account_id', 'account_name']].drop_duplicates()
    list_pages = list_accounts[list_accounts['account_id'].isin(list(posts_page_df["account_id"].unique()))]
    list_pages.insert(2, 'page_or_group', 'page')
    list_groups = list_accounts[~list_accounts['account_id'].isin(list(posts_page_df["account_id"].unique()))]
    list_groups.insert(2, 'page_or_group', 'group')
    list_accounts = pd.concat([list_groups, list_pages])

    return posts_df, posts_page_df, list_accounts


def clean_crowdtangle_url_data(post_url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')
    post_url_df['account_id'] = post_url_df['account_id'].astype(int)

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    return post_url_df


def compute_fake_news_dates(post_url_df, url_df, url_column, date_column, account_id):

    post_url_group_df = post_url_df[post_url_df["account_id"]==account_id]
    fake_news_dates = []

    for url in post_url_group_df["url"].unique().tolist():
        potential_dates = []

        # We consider the date of the Facebook post or posts:
        potential_dates.append(post_url_group_df[post_url_group_df["url"] == url]["date"].values[0])
        # We consider the date of the fact-check:
        potential_dates.append(url_df[url_df[url_column]==url][date_column].values[0])

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

    account_names = ['Australian Climate Sceptics Group', 'A Voice for Choice']
    plt.figure(figsize=(7, 6))

    for i in range(len(account_names)):
        ax = plt.subplot(2, 1, i + 1)
        account_id = posts_df[posts_df['account_name']==account_names[i]].account_id.unique()[0]
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        plt.plot(posts_df_group.groupby(by=["date"])['engagement'].mean(), color="royalblue")
        plt.ylabel("Engagement per post")
        timeserie_template(ax)

        fake_news_dates = compute_fake_news_dates(posts_url_df, url_df, 'url', 'Date of publication', account_id)

        if i == 0:

            plt.title("'" + account_names[i] + "' Facebook group")
            plt.ylim(-10, 150)
            for date in fake_news_dates:
                plt.plot([date, date], [-10, -1], color='C3')

            plt.text(
                s='Known strikes', color='C3', fontweight='bold',
                x=np.datetime64('2019-09-15'), horizontalalignment='right', 
                y=-2, verticalalignment='top'
            )

            patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
            patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
            plt.legend([patch1, patch2], ["'Repeat offender' periods", "'No strike' periods"],
                    loc='upper left', framealpha=1)

            plt.xticks([])

        else:

            plt.title("'" + account_names[i] + "' Facebook page")
            plt.ylim(-23, 350)
            for date in fake_news_dates:
                plt.plot([date, date], [-23, -2.3], color='C3')

            xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
                    np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'),
                    np.datetime64('2021-01-01')
                    ]
            plt.xticks(xticks, rotation=30, ha='right')

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        for period in repeat_offender_periods:
            plt.axvspan(period[0], period[1], ymin=1/16, facecolor='C3', alpha=0.1)

    plt.tight_layout()
    save_figure('sf_examples_timeseries')


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


def calculate_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df, url_column, date_column):

    sumup_df = pd.DataFrame(columns=[
        'account_id',
        'account_name', 
        'engagement_repeat', 
        'engagement_free'
    ])

    for account_id in posts_df['account_id'].unique():

        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        fake_news_dates = compute_fake_news_dates(posts_url_df, url_df, url_column, date_column, account_id)
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
                'account_id': account_id,
                'account_name': account_name, 
                'engagement_repeat': np.mean(repeat_offender_df['engagement']),
                'engagement_free': np.mean(free_df['engagement']),
            }, ignore_index=True)
            
    sumup_df['percentage_change_engagament'] = ((sumup_df['engagement_repeat'] - sumup_df['engagement_free'])/
                                                sumup_df['engagement_free']) * 100
    return sumup_df


def plot_percentage_changes(sumup_groups_df, sumup_pages_df):

    plt.figure(figsize=(7, 4))
    ax = plt.subplot(111)

    plt.plot(sumup_groups_df['percentage_change_engagament'].values, 
             list(np.random.random(len(sumup_groups_df))), 
             'o', markerfacecolor='royalblue', markeredgecolor='blue', alpha=0.6,
             label='Facebook groups')
    low, high = calculate_confidence_interval_median(sumup_groups_df['percentage_change_engagament'].values)
    plt.plot([low, np.median(sumup_groups_df['percentage_change_engagament']), high], 
             [0.5 for x in range(3)], '|-', color='navy', 
             linewidth=2, markersize=12, markeredgewidth=2)

    plt.plot(sumup_pages_df['percentage_change_engagament'].values, 
             list(np.random.random(len(sumup_pages_df))/5 - 0.3), 
             'o', markerfacecolor='skyblue', markeredgecolor='deepskyblue', alpha=0.6,
             label='Facebook pages')
    low, high = calculate_confidence_interval_median(sumup_pages_df['percentage_change_engagament'].values)
    plt.plot([low, np.median(sumup_pages_df['percentage_change_engagament']), high], 
             [-0.2 for x in range(3)], '|-', color='dodgerblue', 
             linewidth=2, markersize=12, markeredgewidth=2)

    percentage_change_template(ax)
    plt.ylim(-.45, 1.35)


def plot_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df, posts_page_df, url_column, date_column, database_name, figure_name, list_accounts):

    sumup_df = calculate_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df, url_column, date_column)

    sumup_pages_df = sumup_df[sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    sumup_groups_df = sumup_df[~sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]

    print('\nREPEAT VS FREE PERIODS:')

    if database_name == 'Science Feedback':
        print('Australian Climate Sceptics Group percentage change:', 
            sumup_df[sumup_df['account_name']=='Australian Climate Sceptics Group']['percentage_change_engagament'].values[0])
        print('A Voice for Choice percentage change:', 
            sumup_df[sumup_df['account_name']=='A Voice for Choice']['percentage_change_engagament'].values[0])

    print('Number of Facebook accounts:', len(sumup_df))
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    
    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)

    print('Median engagement percentage changes for groups:', 
          np.median(sumup_groups_df['percentage_change_engagament']),
          ', n =', len(sumup_groups_df))
    w, p = stats.wilcoxon(sumup_groups_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for groups: w =', w, ', p =', p)

    print('Median engagement percentage changes for pages:', 
          np.median(sumup_pages_df['percentage_change_engagament']),
          ', n =', len(sumup_pages_df))
    w, p = stats.wilcoxon(sumup_pages_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for pages: w =', w, ', p =', p)

    plot_percentage_changes(sumup_groups_df, sumup_pages_df)
    plt.xlabel("Engagement percentage change\nbetween the 'repeat offender' and 'no strike' periods", size='large')
    plt.title("{} 'repeat offender' Facebook accounts ({} data)".format(len(sumup_df), database_name))
    plt.tight_layout()
    save_figure(figure_name)

    sumup_df['repeat_vs_free'] = sumup_df['percentage_change_engagament'].apply(lambda x: str(int(np.round(x))) + '%')
    list_accounts = pd.merge(list_accounts, sumup_df[['account_id', 'repeat_vs_free']], 
                             how='left', on="account_id")

    return list_accounts


def plot_average_timeseries(posts_df, database_name, figure_name):

    drop_date='2020-06-09'
    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'),
              np.datetime64('2021-01-01'), drop_date
             ]

    plt.figure(figsize=(7, 7))

    ax = plt.subplot(3, 1, 1)
    plt.plot(posts_df.groupby(by=["date", "account_id"])['engagement'].sum().groupby(by=['date']).mean(), 
             color="royalblue")
    plt.ylabel("Engagement per day")
    timeserie_template(ax)
    plt.axvline(x=np.datetime64(drop_date), color='C3', linestyle='--')
    plt.title("{} 'repeat offender' Facebook accounts ({} data)".format(
        str(posts_df.account_id.nunique()), database_name))
    if database_name == 'Science Feedback':
        plt.ylim(0, 3200)
    elif database_name == 'Condor':
        plt.ylim(0, 2300)
    plt.xticks(xticks, labels=['' for x in xticks], rotation=30, ha='right')

    ax = plt.subplot(3, 1, 2)
    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(),
             color='grey')
    plt.ylabel("Number of posts per day")
    timeserie_template(ax)
    plt.axvline(x=np.datetime64(drop_date), color='C3', linestyle='--')
    plt.ylim(0, 99)
    plt.xticks(xticks, labels=['' for x in xticks], rotation=30, ha='right')

    ax = plt.subplot(3, 1, 3)
    plt.plot(posts_df.groupby(by=["date"])['engagement'].mean(), 
             color="royalblue")
    plt.ylabel("Engagement per post")
    timeserie_template(ax)
    plt.axvline(x=np.datetime64(drop_date), color='C3', linestyle='--')
    if database_name == 'Science Feedback':
        plt.ylim(0, 60)
    elif database_name == 'Condor':
        plt.ylim(0, 50)
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.tight_layout()
    save_figure(figure_name)


def plot_june_drop_percentage_change(posts_df, posts_page_df, database_name, figure_name, list_accounts):

    sumup_df = calculate_june_drop(posts_df)

    sumup_pages_df = sumup_df[sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    sumup_groups_df = sumup_df[~sumup_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]

    print('\nJUNE DROP:')

    # print("Drop for 'Australian Climate Sceptics Group':", sumup_df[sumup_df['account_name']=='Australian Climate Sceptics Group']['percentage_change_engagament'].values[0])

    print('Number of Facebook account:', len(sumup_df))
    print('Number of Facebook account with a decrease:', len(sumup_df[sumup_df['percentage_change_engagament'] < 0]))
    print('Mean engagement percentage changes:', np.mean(sumup_df['percentage_change_engagament']))
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    
    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)

    print('Median engagement percentage changes for groups:', 
          np.median(sumup_groups_df['percentage_change_engagament']),
          ', n =', len(sumup_groups_df))
    w, p = stats.wilcoxon(sumup_groups_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for groups: w =', w, ', p =', p)

    print('Median engagement percentage changes for pages:', 
          np.median(sumup_pages_df['percentage_change_engagament']),
          ', n =', len(sumup_pages_df))
    w, p = stats.wilcoxon(sumup_pages_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes for pages: w =', w, ', p =', p)

    plot_percentage_changes(sumup_groups_df, sumup_pages_df)
    plt.title("{} 'repeat offender' Facebook accounts ({} data)".format(len(sumup_df), database_name))
    if database_name=='control':
        plt.title("{} 'control' Facebook accounts".format(len(sumup_df)))

    plt.xlabel("Engagement percentage change after June 9, 2020", size='large')
    plt.tight_layout()
    save_figure(figure_name)

    sumup_df['june_drop'] = sumup_df['percentage_change_engagament'].apply(lambda x: str(int(np.round(x))) + '%')
    list_accounts = pd.merge(list_accounts, sumup_df[['account_id', 'june_drop']], 
                             how='left', on="account_id")

    return list_accounts


if __name__=="__main__":

    posts_df, posts_page_df, list_accounts = import_crowdtangle_group_data()

    posts_url_df  = import_data(file_name="posts_url_2021-01-04_.csv", folder="section_1_sf")
    posts_url_df = clean_crowdtangle_url_data(posts_url_df)
    url_df = import_data(file_name="appearances_2021-01-04_.csv", folder="section_1_sf") 

    plot_repeat_example_timeseries_figure(posts_df, posts_url_df, url_df)
    list_accounts = plot_repeat_vs_free_percentage_change(
        posts_df, posts_url_df, url_df, posts_page_df,
        'url', 'Date of publication', 'Science Feedback', 'sf_repeat_vs_free_percentage_change', 
        list_accounts)

    plot_average_timeseries(posts_df, 'Science Feedback', 'sf_average_timeseries')
    list_accounts = plot_june_drop_percentage_change(
        posts_df, posts_page_df, 'Science Feedback', 'sf_june_drop_percentage_change', list_accounts)

    export_data(list_accounts, 'list_accounts_sf', 'section_1_sf')