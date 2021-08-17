
# Data collection

### To collect the Condor data for Facebook misinformation groups and pages (section 3)

Add the Condor data under the name `tpfc-recent.csv` in the `data` folder, then run:

```
python code/clean_condor_data.py
./code/collect_ct_data_from_urls.sh
python code/write_crowdtangle_lists.py
```

The middle command will run for around 6h.

Create the list of groups and pages on CrowdTangle with the same names as what was printed in the console, and updload the CSV created in the data folder in the CrowdTangle interface. Then run (first do `minet ct lists` to get the correct list ids to ask for):

```
./code/collect_ct_data_for_accounts.sh 1590764
```

Each command will run for around X-X hours.