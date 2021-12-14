import pickle
import re
from collections import defaultdict
from datetime import datetime

import pandas as pd
import plotly.express as px
from bertopic import BERTopic

base_data_dir = './'

random_state = 42


def snake_case(s):
    return '_'.join(
        re.sub(r"(\s|_|-)+", " ",
               re.sub(r"[A-Z]{2,}(?=[A-Z][a-z]+[0-9]*|\b)|[A-Z]?[a-z]+[0-9]*|[A-Z]|[0-9]+",
                      lambda mo: ' ' + mo.group(0).lower(), s)).split()
    )


def create_quote_samples_for_party(parties, num_quotes=100000, start_year=2015, end_year=2021):
    """ Only run function once """
    quote_dfs = defaultdict(lambda: pd.DataFrame())

    for party in parties:
        for quote_year in range(start_year, end_year):
            cur_num_quotes = num_quotes // (end_year - start_year)
            if quote_year == end_year - 1:
                cur_num_quotes = num_quotes - (end_year - start_year - 1) * cur_num_quotes
            df = pd.read_csv(f'{base_data_dir}ADA_data/quotebank_one_party-{quote_year}.csv')
            df = df[df['party_one'] == party]
            df = df[['quoteID', 'quotation']]
            print(party, quote_year, cur_num_quotes, len(df))
            df = df.sample(n=cur_num_quotes, random_state=random_state, replace=True)
            quote_dfs[party] = pd.concat([quote_dfs[party], df])

    for party in parties:
        df = quote_dfs[party]
        df = df.sort_values(by=['quoteID'])
        df.to_pickle(f'{base_data_dir}ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')


def get_quotes_sample_df_for_party(party, num_quotes=100000):
    df = pd.read_pickle(f'{base_data_dir}ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')
    assert len(df) == num_quotes
    return df


def get_all_quotes_for_party(party, start_year=2015, end_year=2021, return_quote_ids=False, max_all_quotes=200_000):
    dfs = []
    for quote_year in range(start_year, end_year):
        df = pd.read_csv(f'{base_data_dir}ADA_data/quotebank_one_party-{quote_year}.csv')
        df = df[df['party_one'] == party]
        df = df[['quoteID', 'quotation']]
        dfs.append(df)

    res = pd.concat(dfs)

    if len(res) > max_all_quotes:
        res = res.sample(n=max_all_quotes, random_state=random_state)

    assert len(res) <= max_all_quotes

    if return_quote_ids:
        return res['quotation'].tolist(), res['quoteID'].tolist()
    else:
        return res['quotation'].tolist()


def convert_quoteids_to_timestamps(quoteIDs, bucket_monthly=True):
    def convert_to_month(quoteID):
        return datetime.strptime('-'.join(quoteID.split('-')[:2]), '%Y-%m')

    if bucket_monthly:
        return list(map(convert_to_month, quoteIDs))
    else:
        return quoteIDs


def create_normalised_stacked_topics_chart(topics_over_time_df, top_n_topics=10):
    # Select top 10 topics
    topics_over_time_df = topics_over_time_df[topics_over_time_df['Topic'] < top_n_topics]
    frequency_sums = topics_over_time_df.groupby('Timestamp').sum()['Frequency'].to_frame().rename(
        columns={'Frequency': 'Frequency_Sum'})
    topics_over_time_df = topics_over_time_df.join(frequency_sums, on='Timestamp')
    topics_over_time_df['Frequency_Normalized'] = topics_over_time_df['Frequency'] / topics_over_time_df[
        'Frequency_Sum']
    fig = px.area(topics_over_time_df, x='Timestamp', y='Frequency_Normalized', color='Topic_Names')
    return fig


def per_party_analysis(load_model=True, load_topics=True, load_reduced_model=True, auto_reduction=True,
                       load_topics_over_time=True):
    cur_party = 'Republican Party'
    model_base_path = f'{base_data_dir}ADA_models/{snake_case(cur_party)}'
    sample_quotes_df = get_quotes_sample_df_for_party(cur_party)
    sample_quotes = sample_quotes_df['quotation'].tolist()
    if load_model:
        model = BERTopic(verbose=True).load(f'{model_base_path}_topic_model_1')
    else:
        model = BERTopic(verbose=True).fit(sample_quotes)
        model.save(f'{model_base_path}_topic_model_1')

    # Transform model with all quotes to get topics
    quotes_all, quotes_quoteIDs = get_all_quotes_for_party(cur_party, return_quote_ids=True)

    print(f'Transform on {len(quotes_all)} quotes.')

    if load_topics:
        with open(f'{model_base_path}_all_topics.pkl', 'rb') as topic_file:
            model_topics_all, model_probs_all = pickle.load(topic_file)
    else:
        model_topics_all, model_probs_all = model.transform(quotes_all)
        with open(f'{model_base_path}_all_topics.pkl', 'wb') as topic_file:
            pickle.dump([model_topics_all, model_probs_all], topic_file)

    # Remove quotes which are not clustered into a topic
    quotes_all = [x for i, x in enumerate(quotes_all) if model_topics_all[i] != -1]
    quotes_quoteIDs = [x for i, x in enumerate(quotes_quoteIDs) if model_topics_all[i] != -1]
    model_probs_all = [x for i, x in enumerate(model_probs_all) if
                       model_topics_all[i] != -1] if model_probs_all is not None else model_probs_all
    model_topics_all = [x for x in model_topics_all if x != -1]

    # Automatic reduction
    if auto_reduction:
        if load_reduced_model:
            model = BERTopic(verbose=True).load(f'{model_base_path}_topic_model_reduced')
            with open(f'{model_base_path}_auto_reduced_topics.pkl', 'rb') as topic_file:
                auto_reduced_topics, auto_reduced_probs = pickle.load(topic_file)
        else:
            auto_reduced_topics, auto_reduced_probs = model.reduce_topics(
                quotes_all, model_topics_all, model_probs_all, nr_topics=50
            )
            model.save(f'{model_base_path}_topic_model_reduced')
            with open(f'{model_base_path}_auto_reduced_topics.pkl', 'wb') as topic_file:
                pickle.dump([auto_reduced_topics, auto_reduced_probs], topic_file)

        # Topics over time
        if load_topics_over_time:
            topics_over_time_df = pd.read_pickle(f'{model_base_path}_all_quotes_topics_over_time')
        else:
            topics_over_time_df = model.topics_over_time(
                quotes_all, auto_reduced_topics, convert_quoteids_to_timestamps(quotes_quoteIDs)
            )
            topics_over_time_df.to_pickle(f'{model_base_path}_all_quotes_topics_over_time')

        topics_over_time_df['Topic_Names'] = topics_over_time_df['Topic'].apply(
            lambda topic: " ".join([x[0] for x in model.get_topic(topic)]))
        fig = create_normalised_stacked_topics_chart(topics_over_time_df)
        fig.show()
    else:
        # Manual reduction
        manual_topic_list = [
            'healthcare', 'education', 'military', 'abortion', 'gender',
            'marriage', 'infrastructure', 'religion', 'equality', 'guns',
            'racism', 'masks', 'climate change', 'immigration', 'wildlife',
            'nature', 'transportation', 'government spending', 'energy', 'labour',
            'drugs', 'nato', 'prison'
        ]

        related_topics_dict = {}

        for manual_topic in manual_topic_list:
            related_topics, related_similarities = model.find_topics(manual_topic, top_n=20)
            # threshold topics
            related_topics = [x for i, x in enumerate(related_topics) if related_similarities[i] > 0.6]
            related_topics_dict[manual_topic] = related_topics

        with open(f'{model_base_path}_manual_reduced_topics_dict.pkl', 'wb') as topic_file:
            pickle.dump(related_topics_dict, topic_file)


def main():
    per_party_analysis(load_model=True, load_topics=True, load_reduced_model=True, load_topics_over_time=True)


def pandas_options():
    pd.set_option("display.max_rows", 20)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.width", 300)


if __name__ == '__main__':
    main()
