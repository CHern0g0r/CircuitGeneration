import numpy as np

from Levenshtein import ratio as levenshtein_ratio
from tqdm import tqdm

from datasets.src.utils import nx2cirbo


def sort_tts(tts):
    return sorted(
        ['_'.join(sorted(tt.split('_'))) for tt in tts]
    )


def nx_valid(nx_digraph):
    pass


def validity(graph_list):
    circuit_list = []
    is_valid = []
    tts = []
    for _, g in enumerate(tqdm(graph_list)):
        try:
            circuit = nx2cirbo(g)
            circuit_list.append(circuit)

            tt = circuit.get_truth_table()
            tt_str = ''.join(
                ''.join(str(int(bit)) for bit in inp)
                for inp in tt
            )
            if not tt_str:
                raise ValueError('Empty truth table')
            is_valid.append(1)
            tts.append(tt_str)
        except Exception as e:
            print(f"graph {_}: {type(e).__name__} {e}")
            circuit_list.append('')
            is_valid.append(0)
            tts.append('')
    validity_score = sum(is_valid) / len(is_valid)
    return circuit_list, is_valid, tts, validity_score


def uniqueness(tts):
    tts = [tt for tt in tts if tt]
    unq = np.unique(tts)
    if not tts:
        return 0
    return len(unq) / len(tts)


def novelty(tts, train_tts):
    unq = set(sort_tts(tts))
    train_tts = set(sort_tts(train_tts))
    novel = [tt for tt in unq if tt not in train_tts]
    if not unq:
        return 0
    return len(novel) / len(unq)


def cond_validity(tts, cond_tts):
    cond_is_valid = [ctt == tt for ctt, tt in zip(cond_tts, tts)]
    return sum(cond_is_valid) / len(cond_is_valid)


def tt_distance(tts, cond_tts):
    res = []
    for tt, cond_tt in zip(tts, cond_tts):
        if not tt:
            continue
        # print(f'{tt} vs {cond_tt}', len(tt), len(cond_tt))
        n_inp = len(tt)
        cond_n_inp = len(cond_tt)

        if n_inp != cond_n_inp:
            res.append(0)
        else:
            res.append(levenshtein_ratio(tt, cond_tt))
    if not res:
        return 0
    return sum(res) / len(res)


def tt_em(tts, cond_tts):
    correct = [1 if tt == cond_tt else 0 for tt, cond_tt in zip(tts, cond_tts)]
    return sum(correct) / len(correct)
