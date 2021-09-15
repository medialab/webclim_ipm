import pandas as pd

from utils import import_data
from create_section_1_figures import plot_average_timeseries


def import_crowdtangle_group_data():

    posts_group_df = import_data(file_name="posts_main_news_2021_group.csv", folder="supplementary")
    print("There are {} 'mainstream' Facebook groups.".format(posts_group_df.account_id.nunique()))

    posts_page_df = import_data(file_name="posts_main_news_2021_page.csv", folder="supplementary")
    print("There are {} 'mainstream' Facebook pages.".format(posts_page_df.account_id.nunique()))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df['engagement'] = posts_df[["share", "comment", "reaction"]].sum(axis=1)

    return posts_df


if __name__=="__main__":

    posts_df = import_crowdtangle_group_data()

    plot_average_timeseries(posts_df, 'whathever', 'supplementary_mainstream_average_timeseries', 'established news')
