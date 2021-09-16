import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

from utils import (import_data, save_figure, 
                   calculate_june_drop, calculate_confidence_interval_median,
                   percentage_change_template)
from create_section_1_figures import plot_average_timeseries, plot_june_drop_percentage_change


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


if __name__=="__main__":

    # # Old mainstream data
    # posts_df, posts_page_df = import_crowdtangle_group_data_old()
    # plot_average_timeseries(posts_df, 'whatever', 'supplementary_mainstream_average_timeseries', 'established news')
    # plot_june_drop_percentage_change(posts_df, posts_page_df, 'supp', 'supplementary_mainstream_june_drop_percentage_change')

    # New mainstream data 
    posts_df = import_crowdtangle_group_data()
    print(len(posts_df))
    print(posts_df.account_id.nunique())

    plot_average_timeseries(posts_df, 'whatever', 'supplementary_mainstream_average_timeseries', 'control')
    plot_june_drop_percentage_change_groups(posts_df)


