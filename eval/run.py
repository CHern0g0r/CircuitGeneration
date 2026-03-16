import pickle
import pandas as pd
import torch

from eval.metrics import (
    validity,
    uniqueness,
    novelty,
    tt_distance,
    tt_em
)
from tqdm import tqdm


def main(graphs, df, labels=None):
    cond_tts, graph_list = zip(*graphs)

    circuit_list, is_valid, tts, validity_score = validity(graph_list)
    print(len(tts))

    print('Total', len(graph_list), 'valid', sum(is_valid))
    print(f'Validity: {validity_score:.4f}')
    print(f'Uniqueness: {uniqueness(tts):.4f}')
    print(f'Novelty: {novelty(tts, df["circuit_name"].tolist()):.4f}')
    # print(f'TT average distance: {tt_distance(tts, labels):.4f}')
    # print(f'TTEM: {tt_em(tts, labels):.4f}')


def torch_tt_tostr(tensor):
    tensor = (tensor[tensor.nonzero()].squeeze() + 1) / 2
    tensor = ''.join(str(int(bit)) for bit in tensor.tolist())
    return tensor


if __name__ == "__main__":

    graphs_pth = ''
    labels_pth = ''

    df_pth = ''

    graphs = pickle.load(open(graphs_pth, 'rb'))
    if not isinstance(graphs[0], tuple):
        graphs = [(None, g) for g in graphs]
    df = pd.read_csv(df_pth)

    if labels_pth is not None:
        labels = pickle.load(open(labels_pth, 'rb'))
        if isinstance(labels[0], torch.Tensor):
            labels = list(map(torch_tt_tostr, labels))
        # for lab in labels:
        #     print(lab)

    main(graphs, df, labels)
