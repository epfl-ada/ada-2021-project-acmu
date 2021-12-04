# Whether to create a parsed file from the Quotebank dataset.
PARSE_QUOTEBANK = True

# Colorblind-friendly color palette.
COLORS = ['#377EB8', '#FF7F00', '#4DAF4A', '#F781BF']

# DATA_DIR (root data dir)
BASE_PATH = '/home/albion/code/EPFL/ada/ada-2021-project-acmu/'  # TODO change this on your machine
DATA_DIR = './'
# DATA_DIR = '/content/drive/MyDrive/'
CUSTOM_DATA_DIR = DATA_DIR + 'custom_data/'

# A mapping between a year and the file that contains the input of that year.
QUOTES_BY_YEAR = {year: f"{DATA_DIR}politicians-quotes-{year}-old.json.bz2" for year in range(2015, 2021)}  # TODO remove old

# A mapping between a party and quotes of its members
WIKIDATA_POLITICIANS_PATH = f"{DATA_DIR}wikidata_politicians.csv"

# Path to parquet file used for Wikidata information
WIKIDATA_PATH = f"{DATA_DIR}Quotebank_Wikidata/speaker_attributes.parquet"

# Path to file with mapping between q-codes and labels
WIKIDATA_LABELS_PATH = f"{DATA_DIR}Quotebank_Wikidata/wikidata_labels_descriptions_quotebank.csv.bz2"

# Wikidata columns that are represented by q codes
WIKIDATA_QCODES_COL = ['occupation', 'party']

# The name of the single-value general stats
VALUE_STATS = {'nan_speakers', 'nan_percentage', 'avg_quote_len', 'num_quotes'}

# The name of the counter general stats
COUNTER_STATS = {'quotes_by_date', 'qids_count'}

# The year for which the data will be analyzed
YEAR = 2018