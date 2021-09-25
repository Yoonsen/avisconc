import dhlab_v2 as d2
import pandas as pd
from random import sample

def sampling(a, b):
    res = a
    if b < len(a):
        res = sample(a, b)
    return res

def sort(df, col = None, up = True):
    if col is None:
        col = df.columns[0]
    return df.sort_values(by = col, ascending = (up == False))
    

def check_words(df, word_parts):
    """ do a df.loc[] on matches for word_parts - a kindof regex search through matches"""
    return pd.concat([df.loc[i] for i in [df[a].index for a in [df.index.str.contains(w) for w in word_parts]]])

def make_subcorpus(actual_titles, corpus):
    """Definer subkorpus basert på titlene"""
    subcorpus = pd.concat([corpus[corpus.urn.str.contains(x)] for x in actual_titles])
    return subcorpus

def collocation(word, before = 20, after = 20, corpus = None, samples = 500000, totals = None):
    """ Collocations from counts - no distance here"""
    coll = d2.urn_collocation(urns = sampling(list(corpus.urn), samples), word = word, before = before, after = after)
    combo = pd.concat([coll.counts, totals.freq], axis = 1)
    combo.freq = combo.freq.fillna(min(combo.freq))
    combo['pmi'] = (combo.counts/combo.counts.sum())/(combo.freq/combo.freq.sum())
    return combo


def coll_dist(word, window = 10, corpus = None, totals = None):
    before = collocation(word = word,before = window, after = 0, corpus = corpus, totals = totals)
    after = collocation(word = word,before = 0, after = window, corpus = corpus, totals = totals)
    before.columns = pd.MultiIndex.from_tuples([('before', x) for x in before.columns], names = ["place", "kind"])
    after.columns = pd.MultiIndex.from_tuples([('after', x) for x in after.columns], names = ["place", "kind"])
    result = pd.concat([before, after], axis = 1)
    return result

def sample_concordances(conc, size = 10):
    r = conc.sample(size)
    r['link'] = r['urn'].apply(lambda c: "<a target='_blank' href = 'https://www.nb.no/items/{x}?searchText={q}'>{display}</a>".format(x = c,display = c.split('_')[2], q = search))
    r['date'] = r['urn'].apply(lambda c: "{display}".format( display = c.split('_')[5]))                   
    return r[['link','date','conc']].sort_values(by = 'date')


def konk(corpus = None, query = None): 
    conc = d2.concordance(urns = list(corpus.urn), words = query, limit = 10000)
    conc['link'] = conc['urn'].apply(lambda c: "<a target='_blank' href = 'https://www.nb.no/items/{x}?searchText={q}'>{display}</a>".format(x = c, display = c.split('_')[2], q = query))
    conc['date'] = conc['urn'].apply(lambda c: "{display}".format( display = c.split('_')[5]))
    return conc[['link','date','conc']].sort_values(by = 'date')

TITLES_NATIONAL = [x.lower() for x in """Aftenposten
Verdensgang
Dagbladet
Dagsavisen
Dagensnaeringsliv
Morgenbladet
Klassekampen
Finansavisen
Vaartland
Nationen 
Aftenpostenjunior""".split()
]