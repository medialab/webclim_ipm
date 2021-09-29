import os
import sys

import pandas as pd
import ural

from utils import (import_data, export_data)


def keep_only_the_urls_considered_fake_by_facebook(url_df):

    url_df = url_df[url_df['Flag as']=='False']

    url_df = url_df[url_df['Fb flagged']=="done"]

    url_df = url_df[~(url_df['Fb correction status'].isin([
        "Corrected to Not Rated",
        "Corrected to True",
        "Corrected to Partly False"
    ]))]

    return url_df


def clean_url_format(url_df):

    url_df['url'] = url_df['url'].transform(lambda x: x.strip())

    url_df['url_cleaned'] = url_df['url']\
        .apply(lambda x: ural.normalize_url(x, 
                                            strip_protocol=False, 
                                            strip_trailing_slash=True))
    url_df['domain_name'] = url_df['url_cleaned'].apply(lambda x: ural.get_domain_name(x))

    # Remove the URLs that are in double in the dataframe, 
    # keeping only the first, i.e. the more recent ocurrence.
    url_df = url_df.drop_duplicates(subset = "url", keep = "first")
    
    return url_df


def add_info_from_fact_check_table(url_df, fact_check_df):

    fact_check_df['scientific_topic'] = fact_check_df['Review url'].str.extract('https://([^/]+)feedback.org')

    url_df = url_df.dropna(subset=['Item reviewed'])
    fact_check_df = fact_check_df.dropna(subset=['Items reviewed'])

    url_df = url_df.merge(fact_check_df[['Items reviewed', 'topic', 'scientific_topic', 'Date of publication']], 
                        left_on='Item reviewed', right_on='Items reviewed', how='left')
    
    url_df.loc[url_df['topic'].isin(["COVID-19", "COVID-19,5G"]), 'scientific_topic'] = 'covid'
    
    url_df = url_df.dropna(subset=['scientific_topic'])

    return url_df


def keep_only_topic_data(url_df, TOPIC):
    if TOPIC in ["climate", "health", "covid"]:
        return url_df[url_df["scientific_topic"] == TOPIC]
    else:
        return url_df
 

if __name__ == "__main__":

    DATE = sys.argv[1]
    TOPIC = sys.argv[2] if len(sys.argv) >= 3 else ""

    url_df = import_data("Appearances-Grid view " + DATE + ".csv", "section_1_sf")
    url_df = keep_only_the_urls_considered_fake_by_facebook(url_df)
    url_df = clean_url_format(url_df)

    fact_check_df = import_data("Reviews _ Fact-checks-Grid view " + DATE + ".csv", "section_1_sf")
    url_df = add_info_from_fact_check_table(url_df, fact_check_df)
    url_df = keep_only_topic_data(url_df, TOPIC)
    url_df = url_df[['url', 'url_cleaned', 'domain_name', 'Item reviewed', 'Date of publication', 'scientific_topic']]
    print("There are {} fake news urls.".format(len(url_df)))

    export_data(url_df, "appearances_" + DATE + "_" + TOPIC, 'section_1_sf')
