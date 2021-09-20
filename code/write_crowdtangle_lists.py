import os

import pandas as pd

from utils import (import_data, export_data)


pd.options.display.max_colwidth = 300
pd.options.display.max_rows = 200


def extract_account_list_from_value_counts_serie(serie, list_name):

    df = pd.DataFrame(columns=["Page or Account URL", "List"])
    df["Page or Account URL"] = serie.index
    df["List"] = list_name

    print("""\nThe list called '{}' should be created on the CrowdTangle interface, 
and will contain at max {} groups or pages after the batch upload.""".format(list_name, len(df)))

    return df


if __name__=="__main__":

    df = import_data(file_name="posts_url_2021-08-16.csv", folder='section_2_condor')    
    df = df.drop_duplicates(subset=['url', 'account_id'])
    s = df["account_url"].value_counts()

    list_name = "heloise_condor_groups_1"
    top1_df = extract_account_list_from_value_counts_serie(s[s >= 83], list_name)

    list_name = "heloise_condor_groups_2"
    top2_df = extract_account_list_from_value_counts_serie(s[(s >= 64) & (s < 83)], list_name)

    list_name = "heloise_condor_groups_3"
    top3_df = extract_account_list_from_value_counts_serie(s[(s >= 35) & (s < 64)], list_name)

    list_name = "heloise_condor_pages_1"
    top4_df = extract_account_list_from_value_counts_serie(s[s >= 35], list_name)

    list_name = "heloise_condor_groups_4"
    top5_df = extract_account_list_from_value_counts_serie(s[(s >= 24) & (s < 35)], list_name)

    list_name = "heloise_condor_pages_2"
    top6_df = extract_account_list_from_value_counts_serie(s[(s >= 24) & (s < 35)], list_name)

    top_more_than_24 = pd.concat([top1_df, top2_df, top3_df, top4_df, top5_df, top6_df])
    print('\n')
    export_data(top_more_than_24, "condor_lists_for_crowdtangle", folder='section_2_condor')