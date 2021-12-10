1. Fit party models for all years on random sample of 100k quotes (save these 100k quotes in ADA_data/party_quotes_all_years)
2. Transform the fitted party models on all the quotes. This returns a list of topics and probabilities (save these topics in ADA_data/party_topics_all_years)
3. Remove documents that are not clustered to a topic (-1).
4. Automatic reduction: pass the topics into reduce_topics to return 50 topics per party. This step modifies the model. 
5. Manual reduction: manually define a list of topics -
    - Find bert-topics within the party model related to this list
    - Threshold at 0.6 similarity to keep the most similar topics
    - The topic exists for this party if there are BERT topics are left after the thresholding
    - Plot distribution of topics by number of associated BERT topics
    - TODO graph network (Mihai)?


Topics over time

