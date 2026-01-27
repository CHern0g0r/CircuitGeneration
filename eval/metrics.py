import numpy as np

from Levenshtein import ratio as levenshtein_ratio


def sort_tts(tts):
    return sorted(
        ['_'.join(sorted(tt.split('_'))) for tt in tts]
    )


def validity(is_valid):
    return sum(is_valid) / len(is_valid)


def uniqueness(tts):
    unq = np.unique(tts)
    return len(unq) / len(tts)


def novelty(tts, train_tts):
    unq = set(sort_tts(tts))
    train_tts = set(sort_tts(train_tts))
    novel = [tt for tt in unq if tt not in train_tts]
    return len(novel) / len(unq)


def cond_validity(tts, cond_tts):
    cond_is_valid = [ctt == tt for ctt, tt in zip(cond_tts, tts)]
    return sum(cond_is_valid) / len(cond_is_valid)


def tt_distance(tts, cond_tts):
    res = []
    for tt, cond_tt in zip(tts, cond_tts):
        n_inp = len(tt.split('_'))
        cond_n_inp = len(cond_tt.split('_'))

        if n_inp != cond_n_inp:
            res.append(0)
        else:
            res.append(levenshtein_ratio(tt, cond_tt))
    return sum(res) / len(res)
