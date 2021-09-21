import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib_venn import venn2, venn3
import scipy.stats as stats
import ural

from utils import (import_data, save_figure, 
                   calculate_june_drop, calculate_confidence_interval_median,
                   percentage_change_template)
from create_section_1_figures import plot_average_timeseries, plot_june_drop_percentage_change

from create_section_1_figures import import_crowdtangle_group_data as import_crowdtangle_group_data_section_1
from create_section_2_figures import import_crowdtangle_group_data_all as import_crowdtangle_group_data_section_2
from create_section_3_figures import import_crowdtangle_group_data as import_crowdtangle_group_data_section_3

def import_crowdtangle_group_data_old():

    posts_group_df = import_data(file_name="posts_main_news_2021_group.csv", folder="supplementary")
    print("There are {} 'mainstream' Facebook groups.".format(posts_group_df.account_id.nunique()))

    posts_page_df = import_data(file_name="posts_main_news_2021_page.csv", folder="supplementary")
    print("There are {} 'mainstream' Facebook pages.".format(posts_page_df.account_id.nunique()))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df, posts_page_df


def import_crowdtangle_group_data():

    posts_df = import_data(file_name="control_groups.csv", folder="supplementary")
    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df


def plot_june_drop_percentage_change_groups(posts_df):

    sumup_df = calculate_june_drop(posts_df)

    print('\nJUNE DROP:')

    print('Number of Facebook account:', len(sumup_df))
    print('Number of Facebook account with a decrease:', len(sumup_df[sumup_df['percentage_change_engagament'] < 0]))
    print('Median engagement percentage changes:', np.median(sumup_df['percentage_change_engagament']))
    
    w, p = stats.wilcoxon(sumup_df['percentage_change_engagament'])
    print('Wilcoxon test against zero for the engagement percentage changes: w =', w, ', p =', p)
    
    plt.figure(figsize=(7, 3.5))
    ax = plt.subplot(111)
    plt.title("{} 'control' Facebook groups".format(len(sumup_df)))

    random_y = list(np.random.random(len(sumup_df)))
    plt.plot(sumup_df['percentage_change_engagament'].values, 
             random_y, 
             'o', markerfacecolor='royalblue', markeredgecolor='blue', alpha=0.6,
             label='Facebook groups')

    low, high = calculate_confidence_interval_median(sumup_df['percentage_change_engagament'].values)
    plt.plot([low, np.median(sumup_df['percentage_change_engagament']), high], 
             [0.5 for x in range(3)], '|-', color='navy', 
             linewidth=2, markersize=12, markeredgewidth=2)

    percentage_change_template(ax)
    plt.ylim(-.2, 1.2)
    plt.xlabel("Engagement percentage change after June 9, 2020", size='large')

    plt.tight_layout()
    save_figure('supplementary_mainstream_june_drop_percentage_change')


def plot_venn_diagram_url():

    df_url_condor = import_data('tpfc-recent-clean.csv', folder="section_2_condor")
    df_url_condor['uralized_url'] = df_url_condor['clean_url'].apply(lambda x: ural.normalize_url(x))
    set_url_condor = set(df_url_condor.uralized_url.unique())

    df_url_sf = import_data('appearances_2021-01-04_.csv', folder="section_1_sf")
    df_url_sf['uralized_url'] = df_url_sf['url'].apply(lambda x: ural.normalize_url(x))
    set_url_sf = set(df_url_sf.uralized_url.unique())

    plt.figure(figsize=(5, 3.5))
    venn2(
        subsets=[set_url_sf, set_url_condor], 
        set_labels=('Science Feedback\nURLs ({})'.format(len(set_url_sf)), 'Condor\nURLs ({})'.format(len(set_url_condor)))
    )
    save_figure('supplementary_venn_urls')


def plot_venn_diagram_group_and_page():

    posts_df_1, posts_page_df_1 = import_crowdtangle_group_data_section_1()
    posts_df_2, posts_page_df_2 = import_crowdtangle_group_data_section_2()
    posts_page_df_3 = import_crowdtangle_group_data_section_3()
    
    plt.figure(figsize=(10, 5))

    plt.subplot(1, 2, 1)
    posts_group_df_1 = posts_df_1[~posts_df_1['account_name'].isin(list(posts_page_df_1["account_name"].unique()))]
    set_group_1 = set(posts_group_df_1.account_id.unique())
    posts_group_df_2 = posts_df_2[~posts_df_2['account_name'].isin(list(posts_page_df_2["account_name"].unique()))]
    set_group_2 = set(posts_group_df_2.account_id.unique())
    venn2(
        subsets=[set_group_1, set_group_2], 
        set_labels=(
            'Science Feedback\nrepeat offenders\ngroups ({})'.format(len(set_group_1)),
            'Condor\nrepeat offenders\ngroups ({})'.format(len(set_group_2))
        )
    )
    plt.tight_layout()

    plt.subplot(1, 2, 2)
    set_page_1 = set(posts_page_df_1.account_id.unique())
    set_page_2 = set(posts_page_df_2.account_id.unique())
    set_page_3 = set(posts_page_df_3.account_id.unique())
    venn3(
        subsets=[set_page_1, set_page_2, set_page_3], 
        set_labels=(
            'Science Feedback\nrepeat offenders\npages ({})'.format(len(set_page_1)),
            'Condor\nrepeat offenders\npages ({})'.format(len(set_page_2)), 
            'Reduced distribution\npages ({})'.format(len(set_page_3))
        )
    )
    plt.tight_layout()

    save_figure('supplementary_venn_groups_and_pages')


if __name__=="__main__":

    # # Old mainstream data
    # posts_df, posts_page_df = import_crowdtangle_group_data_old()
    # plot_average_timeseries(posts_df, 'whatever', 'supplementary_mainstream_average_timeseries', 'control')
    # plot_june_drop_percentage_change(posts_df, posts_page_df, 'control', 'supplementary_mainstream_june_drop_percentage_change')

    # # New mainstream data 
    # posts_df = import_crowdtangle_group_data()
    # plot_average_timeseries(posts_df, 'whatever', 'supplementary_mainstream_average_timeseries', 'control')
    # plot_june_drop_percentage_change_groups(posts_df)

    # Venn diagrams
    plot_venn_diagram_url()
    # plot_venn_diagram_group_and_page()



