import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from utils import (import_data, save_figure, export_data,
                   timeserie_template, percentage_change_template,
                   calculate_june_drop, calculate_confidence_interval_median)


np.random.seed(2)


def import_crowdtangle_group_data():

    posts_wi_date_df = import_data(file_name="posts_self_declared_wi_date.csv", folder="section_3_self_declared")

    posts_wo_date_df = import_data(file_name="posts_self_declared_wo_date.csv", folder="section_3_self_declared")
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

    posts_df = pd.concat([posts_wi_date_df, posts_wo_date_df])
    print("\nThere are {} 'reduced distribution' Facebook pages.".format(posts_df.account_id.nunique()))

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df


def plot_reduce_example_timeseries(posts_df, pages_df):

    account_name = '100 Percent FED Up'
    reduced_distribution_date = pages_df[pages_df['page_name'] == account_name]['date'].values[0]

    plt.figure(figsize=(7, 3.5))
    ax = plt.subplot()
    
    plt.title("'" + account_name + "' Facebook page")

    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    posts_df_group = posts_df[posts_df["account_id"] == account_id]

    plt.plot(posts_df_group.groupby(by=["date"])['engagement'].mean(), color="royalblue")
    plt.ylabel("Engagement per post")
    timeserie_template(ax)

    plt.ylim(0, 10000)
    plt.axvline(x=np.datetime64(reduced_distribution_date), color='C3', linestyle='--')

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'),
              np.datetime64('2021-01-01'), np.datetime64(reduced_distribution_date)
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.tight_layout()
    save_figure('reduce_example_timeseries')


def calculate_engagement_percentage_change(posts_df, pages_df, period_length=30):

    sumup_df = pd.DataFrame(columns=[
        'account_id',
        'account_name', 
        'engagement_before', 
        'engagement_after'
    ])

    for account_id in posts_df['account_id'].unique():

        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        reduced_distribution_date = pages_df[pages_df['page_name'] == account_name]['date'].values[0]
        reduced_distribution_date = datetime.datetime.strptime(str(reduced_distribution_date)[:10], '%Y-%m-%d')
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        posts_df_group_before = posts_df_group[
            (posts_df_group['date'] >= reduced_distribution_date - datetime.timedelta(days=period_length)) &
            (posts_df_group['date'] < reduced_distribution_date)
        ]
        posts_df_group_after = posts_df_group[
            (posts_df_group['date'] > reduced_distribution_date) &
            (posts_df_group['date'] <= reduced_distribution_date + datetime.timedelta(days=period_length))
        ]

        if (len(posts_df_group_before) > 0) & (len(posts_df_group_after) > 0):
            
            sumup_df = sumup_df.append({
                'account_id': account_id,
                'account_name': account_name, 
                'engagement_before': np.mean(posts_df_group_before['engagement']),
                'engagement_after': np.mean(posts_df_group_after['engagement']),
            }, ignore_index=True)
            
    sumup_df['percentage_change_engagament'] = ((sumup_df['engagement_after'] - sumup_df['engagement_before'])/
                                                sumup_df['engagement_before']) * 100
    return sumup_df


def plot_engagement_percentage_change(posts_df, pages_df, list_accounts):

    sumup_df = calculate_engagement_percentage_change(posts_df, pages_df, period_length=30)

    print('\nREDUCE DROP:')
    print("drop for '100 Percent FED Up':", sumup_df[sumup_df['account_name']=='100 Percent FED Up']['percentage_change_engagament'].values[0])

    print('Number of Facebook pages:', len(sumup_df))
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    
    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)

    plt.figure(figsize=(7, 3.5))
    ax = plt.subplot(111)
    plt.title("{} 'reduced distribution' Facebook pages".format(len(sumup_df)))

    random_y = list(np.random.random(len(sumup_df)))
    plt.plot(sumup_df['percentage_change_engagament'].values, 
             random_y, 
             'o', markerfacecolor='royalblue', markeredgecolor='blue', alpha=0.6,
             label='Facebook pages')

    low, high = calculate_confidence_interval_median(sumup_df['percentage_change_engagament'].values)
    plt.plot([low, np.median(sumup_df['percentage_change_engagament']), high], 
             [0.5 for x in range(3)], '|-', color='navy', 
             linewidth=2, markersize=12, markeredgewidth=2)

    percentage_change_template(ax)
    plt.ylim(-.2, 1.2)
    plt.xlabel("Engagement percentage change\nafter the 'reduced distribution' start date", size='large')

    plt.tight_layout()
    save_figure('reduce_percentage_change')

    sumup_df['after_vs_before_reduce'] = sumup_df['percentage_change_engagament'].apply(lambda x: str(int(np.round(x))) + '%')
    list_accounts = pd.merge(list_accounts, sumup_df[['account_id', 'after_vs_before_reduce']], 
                             how='left', on="account_id")

    return list_accounts


def print_june_drop_stats(posts_df, list_accounts):

    sumup_df = calculate_june_drop(posts_df)

    print('\nJUNE DROP:')
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    print('Number of Facebook pages:', len(sumup_df))

    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)

    sumup_df['june_drop'] = sumup_df['percentage_change_engagament'].apply(lambda x: str(int(np.round(x))) + '%')
    list_accounts = pd.merge(list_accounts, sumup_df[['account_id', 'june_drop']], 
                             how='left', on="account_id")

    return list_accounts

if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()

    # Remove pages already analyzed in section 1 and 2:
    posts_df = posts_df[~posts_df['account_id'].isin([121187761264826, 143745137930, 164620026961366])]
    print("\nThere are {} 'reduced distribution' Facebook pages.".format(posts_df.account_id.nunique()))

    list_accounts = posts_df[['account_id', 'account_name']].drop_duplicates()
    list_accounts.insert(2, 'page_or_group', 'page')

    pages_df = import_data(file_name="page_list_section_3.csv", folder="section_3_self_declared")
    pages_df['date'] = pd.to_datetime(pages_df['reduced_distribution_start_date'])

    plot_reduce_example_timeseries(posts_df, pages_df)
    list_accounts = plot_engagement_percentage_change(posts_df, pages_df, list_accounts)

    list_accounts = print_june_drop_stats(posts_df, list_accounts)
    export_data(list_accounts, 'list_accounts_reduce', 'section_3_self_declared')