import os

import pandas as pd

from utils import import_data


pd.options.display.max_colwidth = 300
pd.options.display.max_rows = 200


def extract_account_list_from_value_counts_serie(serie, list_name):

    df = pd.DataFrame(columns=["Page or Account URL", "List"])
    df["Page or Account URL"] = serie.index
    df["List"] = list_name

    return df


def export_data(df, file_name):
    csv_path = os.path.join('.', 'data', file_name + '.csv')
    df.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder (this list contains {} accounts).".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2], len(df))
    )


if __name__=="__main__":

    df = import_data(file_name="posts_url_2021-08-16.csv")    
    df = df.drop_duplicates(subset=['url', 'account_id'])
    s = df["account_url"].value_counts()

    # print(s.head(105))

    list_name = "heloise_condor_groups_1"
    top1_df = extract_account_list_from_value_counts_serie(s[s >= 83], list_name)
    export_data(top1_df, list_name)

    list_name = "heloise_condor_groups_2"
    top2_df = extract_account_list_from_value_counts_serie(s[(s >= 64) & (s < 83)], list_name)
    export_data(top2_df, list_name)

    # top6_df = create_template_csv_from_serie(s[s > 23], "heloise_fake_news_pages")
    # print(len(top6_df))