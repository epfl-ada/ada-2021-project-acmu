import pickle
import random
from collections import defaultdict

import bertopic
import pandas as pd
from bertopic import BERTopic
import re


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
            df = pd.read_csv(f'ADA_data/quotebank_one_party-{quote_year}.csv')
            df = df[df['party_one'] == party]
            df = df[['quoteID', 'quotation']]
            print(party, quote_year, cur_num_quotes, len(df))
            df = df.sample(n=cur_num_quotes, random_state=42, replace=True)
            quote_dfs[party] = pd.concat([quote_dfs[party], df])

    for party in parties:
        df = quote_dfs[party]
        df = df.sort_values(by=['quoteID'])
        df.to_pickle(f'ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')


def get_quotes_sample_df_for_party(party, num_quotes=100000):
    df = pd.read_pickle(f'ADA_data/{snake_case(party)}_{num_quotes}_sample_quotes.pkl')
    assert len(df) == num_quotes
    return df


def get_all_quotes_for_party(party, start_year=2015, end_year=2021, return_quote_ids=False):
    dfs = []
    for quote_year in range(start_year, end_year):
        df = pd.read_csv(f'ADA_data/quotebank_one_party-{quote_year}.csv')
        df = df[df['party_one'] == party]
        df = df[['quoteID', 'quotation']]
        dfs.append(df)

    res = pd.concat(dfs)
    if return_quote_ids:
        return res['quotation'].tolist(), res['quoteID'].tolist()
    else:
        return res['quotation'].tolist()

def per_party_analysis(load_model=True, load_topics=True):
    cur_party = 'Republican Party'
    sample_quotes_df = get_quotes_sample_df_for_party(cur_party)
    sample_quotes = sample_quotes_df['quotation'].tolist()
    if load_model:
        model = BERTopic(verbose=True).load(f'ADA_models/{snake_case(cur_party)}_topic_model_1')
    else:
        model = BERTopic(verbose=True).fit(sample_quotes)
        model.save(f'ADA_models/{snake_case(cur_party)}_topic_model_1')

    # Transform model with all quotes to get topics
    quotes_all = get_all_quotes_for_party(cur_party)

    if load_topics:
        with open(f'ADA_models/{snake_case(cur_party)}_all_topics.pkl', 'rb') as topic_file:
            model_topics_all, model_probs_all = pickle.load(topic_file)
    else:
        model_topics_all, model_probs_all = model.transform(quotes_all)
        with open(f'ADA_models/{snake_case(cur_party)}_all_topics.pkl', 'wb') as topic_file:
            pickle.dump([model_topics_all, model_probs_all], topic_file)

    # Remove quotes which are not clustered into a topic
    quotes_all = [x for i, x in enumerate(quotes_all) if model_topics_all[i] != -1]
    model_probs_all = [x for i, x in enumerate(model_probs_all) if model_topics_all[i] != -1]
    model_topics_all = [x for x in model_topics_all if x != -1]

    # Automatic reduction


    # Manual reduction



def main():

    per_party_analysis()
    # model_file = f'ADA_models/{cur_party}_topic_model'
    #
    # model = BERTopic.load(model_file)
    # model.verbose = True
    #
    # # docs = get_quotes_for_party(cur_party)
    # model_topics, model_probs = model.transform(docs)
    # topics_per_class_df = model.topics_per_class(docs, model_topics,
    #                                              ['guns', 'abortion', 'gender', 'equality', 'republican',
    #                                               'climate change'])
    #
    # print(model)


if __name__ == '__main__':
    main()

"""
    nr_topics = 10
    new_topics, new_probs = model.reduce_topics(docs, model, nr_topics=nr_topics)
    # new_topics.save(f'ADA_models/{cur_party}_reduced_{nr_topics}')


    fig = model.visualize_topics(top_n_topics=20)
    fig.write_html('visual.html')

"""
