import pickle
import random
from collections import defaultdict

import bertopic
import pandas as pd
from bertopic import BERTopic
import re

base_data_dir = './'


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
            df = df.sample(n=cur_num_quotes, random_state=42, replace=True)
            quote_dfs[party] = pd.concat([quote_dfs[party], df])

    for party in parties:
        df = quote_dfs[party]
        df = df.sort_values(by=['quoteID'])
        df.to_pickle(f'{base_data_dir}ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')


def get_quotes_sample_df_for_party(party, num_quotes=100000):
    df = pd.read_pickle(f'{base_data_dir}ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')
    assert len(df) == num_quotes
    return df


def get_all_quotes_for_party(party, start_year=2015, end_year=2021, return_quote_ids=False):
    dfs = []
    for quote_year in range(start_year, end_year):
        df = pd.read_csv(f'{base_data_dir}ADA_data/quotebank_one_party-{quote_year}.csv')
        df = df[df['party_one'] == party]
        df = df[['quoteID', 'quotation']]
        dfs.append(df)

    res = pd.concat(dfs)
    if return_quote_ids:
        return res['quotation'].tolist(), res['quoteID'].tolist()
    else:
        return res['quotation'].tolist()


def per_party_analysis(load_model=True, load_topics=True, load_reduced_model=True, auto_reduction=True):
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
    quotes_all = get_all_quotes_for_party(cur_party)

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
    model_probs_all = [x for i, x in enumerate(model_probs_all) if model_topics_all[i] != -1]
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

        model.visualize_topics()
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
    per_party_analysis(load_reduced_model=False, load_topics=False)


if __name__ == '__main__':
    main()

"""
    nr_topics = 10
    new_topics, new_probs = model.reduce_topics(docs, model, nr_topics=nr_topics)
    # new_topics.save(f'{base_data_dir}ADA_models/{cur_party}_reduced_{nr_topics}')


    fig = model.visualize_topics(top_n_topics=20)
    fig.write_html('visual.html')

"""
