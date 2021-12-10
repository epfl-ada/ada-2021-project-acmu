import pickle
import random
from collections import defaultdict

import bertopic
import pandas as pd
from bertopic import BERTopic

random.seed(42)


def get_quotes_for_party(party, num_quotes=100000, save_list=True):
    quotes = defaultdict(list)

    for quote_year in range(2015, 2021):
        df = pd.read_csv(f'ADA_data/quotebank_one_party-{quote_year}.csv')
        quotes[party].extend(df[df['party_one'] == party]['quotation'].tolist())

    cur_quotes = random.sample(quotes[party], num_quotes)

    if save_list:
        with open(f'{party}_quotes.txt', 'wb') as file:
            pickle.dump(cur_quotes, file)

    return cur_quotes


def main():
    cur_party = 'Republican Party'
    model_file = f'ADA_models/{cur_party}_topic_model'

    model = BERTopic.load(model_file)
    model.verbose = True

    docs = get_quotes_for_party(cur_party)
    model_topics, model_probs = model.transform(docs)
    topics_per_class_df = model.topics_per_class(docs, model_topics, ['guns', 'abortion', 'gender', 'equality', 'republican', 'climate change'])

    print(model)


if __name__ == '__main__':
    main()


"""
    nr_topics = 10
    new_topics, new_probs = model.reduce_topics(docs, model, nr_topics=nr_topics)
    # new_topics.save(f'ADA_models/{cur_party}_reduced_{nr_topics}')


    fig = model.visualize_topics(top_n_topics=20)
    fig.write_html('visual.html')

"""