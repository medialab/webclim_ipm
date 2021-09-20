import pandas as pd
import matplotlib.pyplot as plt

from utils import (import_data, save_figure)
from create_section_1_figures import (
    import_crowdtangle_group_data,
    clean_crowdtangle_url_data,
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

    posts_section_1_df, posts_page_section_1_df = import_crowdtangle_group_data()
    posts_df = posts_df[~posts_df['account_id'].isin(list(posts_section_1_df.account_id.unique()))]
    posts_page_df = posts_page_df[~posts_page_df['account_id'].isin(list(posts_page_section_1_df.account_id.unique()))]
    print("Removing the duplicates from Section 1, there are now {} 'new' Facebook accounts.".format(posts_df.account_id.nunique()))

    return posts_df, posts_page_df


if __name__=="__main__":

    # posts_df, posts_page_df = import_crowdtangle_group_data_all()
    posts_df, posts_page_df = import_crowdtangle_group_data_only_new()

    posts_url_df  = import_data(file_name="posts_url_2021-08-16.csv", folder="section_2_condor")
    posts_url_df = clean_crowdtangle_url_data(posts_url_df)
    url_df = import_data(file_name="tpfc-recent-clean.csv", folder="section_2_condor") 

    plot_repeat_vs_free_percentage_change(posts_df, posts_url_df, url_df, posts_page_df,
                                          'clean_url', 'tpfc_first_fact_check',
                                          'Condor', 'condor_repeat_vs_free_percentage_change')

    plot_average_timeseries(posts_df, 'Condor', 'condor_average_timeseries')

    # posts_df_temp = posts_df[posts_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    # plot_average_timeseries(posts_df_temp, 'Condor', 'condor_average_timeseries_pages')

    # posts_df_temp = posts_df[~posts_df['account_name'].isin(list(posts_page_df["account_name"].unique()))]
    # plot_average_timeseries(posts_df_temp, 'Condor', 'condor_average_timeseries_groups')

    plot_june_drop_percentage_change(posts_df, posts_page_df, 'Condor', 'condor_june_drop_percentage_change')
