import os
from collections import Counter
from itertools import chain

import pandas as pd

from config import VALUE_STATS, COUNTER_STATS, YEAR, QUOTES_BY_YEAR, CUSTOM_DATA_DIR, BASE_PATH


def describe_chunks(df_reader):
    """
    Compute general statistics about the dataset.
    """
    # Initialize single-value stats
    stats = {stat: 0 for stat in VALUE_STATS}
    # Initialize counter stats
    stats = {**stats, **{stat: Counter() for stat in COUNTER_STATS}}
    for chunk in df_reader:
        # Compute stats per chunk
        stats['nan_speakers'] += (chunk['speaker'] == 'None').sum()
        stats['avg_quote_len'] += chunk['quotation'].str.len().sum(axis=0)
        stats['num_quotes'] += len(chunk)
        quotes_by_date = Counter(
            (chunk.groupby(by=chunk["date"].dt.date).count())["quoteID"].T.to_dict()
        )
        stats['quotes_by_date'] += quotes_by_date
        stats['qids_count'] += Counter(chain.from_iterable(chunk['qids']))

    stats['avg_quote_len'] = stats['avg_quote_len'] / stats['num_quotes']
    stats['nan_percentage'] = stats['nan_speakers'] / stats['num_quotes']
    return stats


def create_stats_df():
    # Analyze data chunk by chunk
    df_reader = pd.read_json(QUOTES_BY_YEAR[YEAR], lines=True,
                             compression='bz2', chunksize=10000)
    stats = describe_chunks(df_reader)
    # Print full data stats
    df = pd.DataFrame.from_dict({name: [stats[name]] for name in VALUE_STATS}).style.hide_index().data
    df.to_pickle(os.path.join(CUSTOM_DATA_DIR, 'stats.pkl'))


if __name__ == '__main__':
    os.chdir(BASE_PATH)
    create_stats_df()
