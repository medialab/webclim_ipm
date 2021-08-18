from datetime import datetime
import os

import pandas as pd
import ural

from utils import import_data


if __name__=="__main__":

    df_condor = import_data('tpfc-recent.csv')
    print(len(df_condor))

    df_condor = df_condor.dropna(subset=['clean_url'])
    df_condor['uralized_url'] = df_condor['clean_url'].apply(lambda x: ural.normalize_url(x))
    df_condor = df_condor.drop_duplicates(subset=['uralized_url'])
    print(len(df_condor))

    df_condor = df_condor[df_condor['tpfc_rating']=='fact checked as false']
    print(len(df_condor))

    df_condor = df_condor[df_condor['public_shares_top_country'].isin(['CA', 'AU', 'GB', 'US'])]
    print(len(df_condor))

    df_condor['date'] = pd.to_datetime(df_condor['tpfc_first_fact_check'])
    df_condor = df_condor[df_condor['date'] >= datetime.strptime('2019-01-01', '%Y-%m-%d')]
    df_condor = df_condor[df_condor['date'] <= datetime.strptime('2020-12-31', '%Y-%m-%d')]
    print(len(df_condor))

    csv_path = os.path.join('.', 'data', 'tpfc-recent-clean.csv')
    df_condor.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder.".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2])
    )