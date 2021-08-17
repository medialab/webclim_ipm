import os

import pandas as pd

from utils import import_data


pd.options.display.max_colwidth = 300


def extract_account_list_from_value_counts_serie(serie, list_name):

    df = pd.DataFrame(columns=["Page or Account URL", "List"])
    df["Page or Account URL"] = serie.index
    df["List"] = list_name

    return df


def export_data(df, file_name):
    csv_path = os.path.join('.', 'data', file_name + '.csv')
    df.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2])
    )


if __name__=="__main__":

    df = import_data(file_name="posts_url_2021-08-16.csv")    
    df = df.drop_duplicates(subset=['url', 'account_id'])
    s = df["account_url"].value_counts()

    print(s.head(60))

    list_name = "heloise_condor_groups_1"
    top1_df = extract_account_list_from_value_counts_serie(s[s >= 83], list_name)
    print(len(top1_df))
    export_data(top1_df, list_name)


    # top2_df = create_template_csv_from_serie(s[(s <= 45) & (s > 35)], "heloise_fake_news_groups_2")
    # top3_df = create_template_csv_from_serie(s[(s <= 35) & (s > 29)], "heloise_fake_news_groups_3")
    # top4_df = create_template_csv_from_serie(s[(s <= 29) & (s > 26)], "heloise_fake_news_groups_4")
    # top5_df = create_template_csv_from_serie(s[(s <= 26) & (s > 23)], "heloise_fake_news_groups_5")

    # print(len(top2_df))
    # print(len(top3_df))
    # print(len(top4_df))
    # print(len(top5_df))

    # top6_df = create_template_csv_from_serie(s[s > 23], "heloise_fake_news_pages")
    # print(len(top6_df))