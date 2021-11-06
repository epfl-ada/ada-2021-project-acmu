# [TODO COOL TITLE ABOUT PARTIES & OPINIONS]

## Abstract :memo:
<!---
A 150 word description of the project idea and goals. What’s the motivation behind your project? What story would you like to tell, and why?)
--->
## Research Questions :grey_question:
<!---
A list of research questions you would like to address during the project.
--->
Through our current and future analyses, we aim to answer the following research questions:
* Which are most common subjects tackled by politicians per year? Do these subjects change with time?
* Is there any link between the most common subjects per speaker and their political orientation & party membership?
* Could politicians' quotes be clustered by subject?

<a name="additional-datasets"></a>
## Additional Datasets :fax:

<!---
List the additional dataset(s) you want to use (if any), and some ideas on how you expect to get, manage, process, and enrich it/them.
Show us that you’ve read the docs and some examples, and that you have a clear idea on what to expect. Discuss data size and format if relevant.
It is your responsibility to check that what you propose is feasible.
--->
Given that we are interested in the political orientation of our speakers, we decided to enrich our data with the additional metadata about the
speakers, provided through the `speaker_attributes.parquet` file. 
1. We first have to map the Q-code attributes to their corresponding labels. Initially, we attempted to use the [Wikidata API](https://qwikidata.readthedocs.io/en/stable/readme.html) to aggregate all the aliases and the label for each Q-code.
However, this procedure was slow, so we later decided to use the provided `wikidata_labels_descriptions_quotebank.csv.bz2`
file for the mapping.
2. We merge the Quotebank and the Wikidata entries based on their Q-codes, such that every row would now contain additional labelled information
about the speaker.
3. If a `qid` field in Quotebank does not match with any of the `id` values in Wikidata, we have observered that this happens because the Quotebank
Q-code is not the most recent one. We simply drop all these rows, as they do not have a correspondence in Wikidata.
4. We make use of the speaker's `occupation` present in the Wikidata by selecting only the speakers with _politician_ as one of their occupations.




[TODO] Show what a row looks like before and after.

## Methods :mag:
For the current stage of the project, we decided to analyze the data from 2018. In our final project, we will include all the data throughout the years.
Our research goals are all politically-related. Thus, we use only the subset of quotes belonging to politicians, extracted with the methods described above
in the [Additional Datasets section](#additional-datasets). Furthermore, to ensure a higher confidence that our analysis is based on quotes truly belonging
to politicians, we filtered the rows where the probability of the speaker is higher than 0.6. 
Given the limited in-memory capacity, as well as the large of the files, 

## Proposed timeline :clock10:

## Team Organization :raised_hands:
<!---
A list of internal milestones up until project Milestone 3.
--->
## Questions for TAs
<!---
Add here any questions you have for us related to the proposed project.
--->
