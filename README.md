# Data collection

### To collect the Condor data for Facebook misinformation groups and pages (section 3)

Add the Condor data under the name `tpfc-recent.csv` in the `data` folder, then run:

```
python code/clean_condor_data.py
./code/collect_ct_data_from_urls.sh
python code/write_crowdtangle_lists.py
```

The middle command will run for 6 hours.

Create the list of groups and pages on CrowdTangle with the same names as what was printed in the console, and updload the CSV created in the data folder in the CrowdTangle interface ("settings" at the top right > "batch upload"). 

Then do `minet ct lists` to get the correct list ids to ask for, and run:

```
./code/collect_ct_data_for_accounts.sh 1590764
./code/collect_ct_data_for_accounts.sh 1591619
./code/collect_ct_data_for_accounts.sh 1592120
./code/collect_ct_data_for_accounts.sh 1592111
./code/collect_ct_data_for_accounts.sh 1593557
./code/collect_ct_data_for_accounts.sh 1593558
```

The lenght of each command was respectively:
- 22 hours (49 groups)
- 15 hours (51 groups)
- 1 hour (13 pages)
- 2 days (276 groups)
- 1 hour (22 pages)
- 1.5 days (295 groups)

Finally the obtained files can be reduced by running:
```
python code/clean_crowdtangle_account_data.py posts_condor_1590764 posts_condor_group_1
python code/clean_crowdtangle_account_data.py posts_condor_1591619 posts_condor_group_2
python code/clean_crowdtangle_account_data.py posts_condor_1592120 posts_condor_page_1
python code/clean_crowdtangle_account_data.py posts_condor_1592111 posts_condor_group_3
python code/clean_crowdtangle_account_data.py posts_condor_1593557 posts_condor_page_2
python code/clean_crowdtangle_account_data.py posts_condor_1593558 posts_condor_group_4

```

# Analysis and figures

