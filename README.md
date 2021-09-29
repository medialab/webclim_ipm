This repository corresponds to the draft submitted in 2021 to the Information Processing & Management journal untitled *Investigating Facebook’s interventions against accounts that repeatedly share misinformation* by Héloïse Théro and Emmanuel Vincent.

# Article

Run this to compile the article:
```
pdflatex ipm_after_review
bibtex ipm_after_review
pdflatex ipm_after_review
pdflatex ipm_after_review
```

# Installation

This project was developped on Ubuntu 20.04.3 using Python 3.9.0.

Please install the needed libraries with: `pip install -r requirements.txt`.

To collect data from CrowdTangle, a CrowdTangle token is needed, and you should write it in a `.minetrc` file similar to the `.minetrc.example` file.

# Data collection

### To collect the Facebook repeat offender groups and pages from Condor data (section 2)

Add the Condor data under the name `tpfc-recent.csv` in the `data/section_2_condor` folder, then run:

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
python code/clean_crowdtangle_account_data.py posts_1590764 posts_condor_group_1
python code/clean_crowdtangle_account_data.py posts_1591619 posts_condor_group_2
python code/clean_crowdtangle_account_data.py posts_1592120 posts_condor_page_1
python code/clean_crowdtangle_account_data.py posts_1592111 posts_condor_group_3
python code/clean_crowdtangle_account_data.py posts_1593557 posts_condor_page_2
python code/clean_crowdtangle_account_data.py posts_1593558 posts_condor_group_4
```

### To collect the Facebook repeat offender groups and pages from Science Feedback data (section 1)

First export the following tables in a CSV format from the Science Feedback Airtable database, add the day's date in their name, and put them in the `data/section_1_sf` folder:
* "Appearances-Grid view 2021-01-04.csv"
* "Reviews _ Fact-checks-Grid view 2021-01-04.csv"

Then filter the CSVs with:

```
python code/clean_sciencefeedback_data.py 2021-01-04
```

Then similarly to the previous data collection, we used `collect_crowdtangle_data_by_url.sh`, another adapted `write_crowdtangle_lists.py` then `collect_ct_data_for_accounts.sh` and finally `clean_crowdtangle_account_data.py`.

### To collect the Facebook reduced distribution pages (section 3)

First we looked for the posts sharing a 'reduced distribution' screenshot with the following command:
```
./code/collect_reduced_distribution_posts.sh
```

We then filtered manually thoses posts to keep only the ones matching the criteria described in the article. This created the list of pages described in the `page_list_section_3.csv` file.

Then similarly to the previous data collections, we added those pages in CrowdTangle and used `collect_ct_data_for_accounts.sh` to get all the posts published by these pages in 2019-2020 and finally `clean_crowdtangle_account_data.py`.

### To collect the control groups and pages (supplementary information)

First create the lists of control groups and pages on CrowdTangle, then collect all their posts with `collect_ct_data_for_accounts.sh`.

# Analysis and figures

After collecting the data, run this to generate the different figures integrated in the tex file:
```
python code/create_section_1_figures.py
python code/create_section_2_figures.py
python code/create_section_3_figures.py
python code/create_supplementary_figures.py
```
The PNG files will appear in the `figure` folder.