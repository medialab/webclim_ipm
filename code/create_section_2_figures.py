import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from utils import import_data, save_figure, export_data, timeserie_template
from create_section_1_figures import (
    import_crowdtangle_group_data,
    clean_crowdtangle_url_data,
    compute_fake_news_dates,
    merge_overlapping_periods,
    compute_repeat_offender_periods,
    plot_repeat_vs_free_percentage_change,
    plot_average_timeseries,
    plot_june_drop_percentage_change
)


def import_crowdtangle_group_data_all():

    df_list = []
    for file_index in range(4):
        df_list.append(import_data(file_name="posts_condor_group_" + str(file_index + 1) + ".csv", folder="section_2_condor"))
    posts_group_df = pd.concat(df_list)
    print("\nThere are {} 'repeat offender' Facebook groups.".format(posts_group_df.account_id.nunique()))

    posts_page_df_1 = import_data(file_name="posts_condor_page_1.csv", folder="section_2_condor")
    posts_page_df_2 = import_data(file_name="posts_condor_page_2.csv", folder="section_2_condor")
    posts_page_df = pd.concat([posts_page_df_1, posts_page_df_2])
    print("There are {} 'repeat offender' Facebook pages.".format(posts_page_df.account_id.nunique()))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df, posts_page_df


def import_crowdtangle_group_data_only_new():

    posts_df, posts_page_df = import_crowdtangle_group_data_all()
    print('There are {} Facebook accounts in this section.'.format(posts_df.account_id.nunique()))

    list_accounts_1 = import_crowdtangle_group_data()[2]
    posts_df = posts_df[~posts_df['account_id'].isin(list(list_accounts_1.account_id.unique()))]
    posts_page_df = posts_page_df[~posts_page_df['account_id'].isin(list(list_accounts_1.account_id.unique()))]
    print("Removing the duplicates from Section 1, there are now {} 'new' Facebook accounts.".format(posts_df.account_id.nunique()))

    list_accounts = posts_df[['account_id', 'account_name']].drop_duplicates()
    list_pages = list_accounts[list_accounts['account_id'].isin(list(posts_page_df["account_id"].unique()))]
    list_pages.insert(2, 'page_or_group', 'page')
    list_groups = list_accounts[~list_accounts['account_id'].isin(list(posts_page_df["account_id"].unique()))]
    list_groups.insert(2, 'page_or_group', 'group')
    list_accounts = pd.concat([list_groups, list_pages])

    return posts_df, posts_page_df, list_accounts


def plot_repeat_example_timeseries_figure(posts_df, posts_url_df, url_df):

    account_names = ['Deplorables For Donald Trump', 'Patriots Against Corrupt Government']
    plt.figure(figsize=(7, 6))

    for i in range(len(account_names)):
        ax = plt.subplot(2, 1, i + 1)
        account_id = posts_df[posts_df['account_name']==account_names[i]].account_id.unique()[0]
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        plt.plot(posts_df_group.groupby(by=["date"])['engagement'].mean(), color="royalblue")
        plt.ylabel("Engagement per post")
        timeserie_template(ax)

        fake_news_dates = compute_fake_news_dates(posts_url_df, url_df, 'clean_url', 'tpfc_first_fact_check', account_id)

        if i == 0:

            plt.title("'" + account_names[i] + "' Facebook group")
            plt.ylim(-9, 130)
            for date in fake_news_dates:
                plt.plot([date, date], [-9, -1], color='C3')

            patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
            patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
            plt.legend([patch1, patch2], ["'Repeat offender' periods", "'No strike' periods"],
                    loc='upper right', framealpha=1)

            plt.xticks([])

        else:

            plt.title("'" + account_names[i] + "' Facebook page")
            plt.ylim(-13, 200)
            for date in fake_news_dates:
                plt.plot([date, date], [-13, -1.5], color='C3')

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
    save_figure('condor_examples_timeseries')


if __name__=="__main__":

    # posts_df, posts_page_df = import_crowdtangle_group_data_all()
    posts_df, posts_page_df, list_accounts = import_crowdtangle_group_data_only_new()
    
    posts_url_df  = import_data(file_name="posts_url_2021-08-16.csv", folder="section_2_condor")
    posts_url_df = clean_crowdtangle_url_data(posts_url_df)
    url_df = import_data(file_name="tpfc-recent-clean.csv", folder="section_2_condor") 

    plot_repeat_example_timeseries_figure(posts_df, posts_url_df, url_df)

    list_accounts = plot_repeat_vs_free_percentage_change(
        posts_df, posts_url_df, url_df, posts_page_df, 'clean_url', 'tpfc_first_fact_check',
        'Condor', 'condor_repeat_vs_free_percentage_change', list_accounts)

    plot_average_timeseries(posts_df, 'Condor', 'condor_average_timeseries')
    list_accounts = plot_june_drop_percentage_change(
        posts_df, posts_page_df, 'Condor', 'condor_june_drop_percentage_change', list_accounts)

    export_data(list_accounts, 'list_accounts_condor', 'section_2_condor')