import pickle
import pandas as pd

from datasets.src.utils import nx2cirbo
from eval.metrics import (
    validity,
    uniqueness,
    novelty
)


def main(graphs, df):
    cond_tts, graph_list = zip(*graphs)
    tts = df['circuit_name'].tolist()

    circuit_list = []
    is_valid = []
    tts = []
    for g in graph_list:
        try:
            circuit = nx2cirbo(g)
            circuit_list.append(circuit)
            is_valid.append(1)

            tt = circuit.get_truth_table()
            tt_str = '_'.join(
                ''.join(str(int(bit)) for bit in inp)
                for inp in tt
            )
            tts.append(tt_str)
        except Exception:
            circuit_list.append('')
            is_valid.append(0)
            tts.append('')

    print(f'Validity: {validity(is_valid):.4f}')
    print(f'Uniqueness: {uniqueness(tts):.4f}')
    print(f'Novelty: {novelty(tts, df["circuit_name"].tolist()):.4f}')


if __name__ == "__main__":
    graphs_pth = 'circ/data/nx_generated.pkl'
    df_path = 'data/circ/pickle/cirbo_small/cirbo_small_df.csv'

    graphs = pickle.load(open(graphs_pth, 'rb'))
    df = pd.read_csv(df_path)
    main(graphs, df)
