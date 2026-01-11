import pickle
import logging
import pandas as pd

from argparse import ArgumentParser
from pathlib import Path
from tqdm import tqdm

from cirbo.core import Circuit
from src.utils import cirbo2nx


# logging.basicConfig(level=logging.INFO)


def main(args):
    orig_df = pd.read_csv(args.csv_data)
    if args.dataset is not None:
        orig_df = orig_df[orig_df['dataset'] == args.dataset]

    subdfs = []

    for dataset in orig_df['dataset'].unique():
        logging.info(f'Processing dataset: {dataset}')

        df = orig_df[orig_df['dataset'] == dataset].copy()
        cur_gml_dir = Path(args.graph_dir) / dataset
        cur_gml_dir.mkdir(parents=True, exist_ok=True)
        success = []
        shards = []
        graphs = dict()
        c = 0

        for i, row in tqdm(df.iterrows(),
                           total=len(df),
                           desc=f'Processing dataset {dataset}'):
            bench_path = (
                row['orig_path'] if row['is_bench'] else row['bench_path']
            )
            try:
                circuit = Circuit.from_bench_file(bench_path)
                circ_name = row['circuit_name']
                nx_graph = cirbo2nx(circuit)
                # gml_path = cur_gml_dir / bench_path.split('/')[-1].replace(
                #     '.bench', '.gml'
                # )
                # nx.write_gml(nx_graph, gml_path)

                # gml_path = cur_gml_dir / bench_path.split('/')[-1].replace(
                #     '.bench', '.pkl'
                # )
                # pickle.dump(
                #     nx_graph,
                #     open(gml_path, 'wb')
                # )

                graphs[circ_name] = nx_graph
                success.append(i)
            except Exception as e:
                logging.error(f"Error processing {bench_path}: {e}")
                continue

            if len(graphs) >= args.graph_per_shard:
                gml_path = cur_gml_dir / f'{dataset}_{c}.pkl'
                pickle.dump(
                    graphs,
                    open(gml_path, 'wb')
                )
                shards += [c]*len(graphs)
                graphs = dict()
                c += 1
        else:
            if len(graphs) > 0:
                gml_path = cur_gml_dir / f'{dataset}_{c}.pkl'
                logging.info(f'Saving graphs to {gml_path}')
                pickle.dump(
                    graphs,
                    open(gml_path, 'wb')
                )
                shards += [c]*len(graphs)
                graphs = dict()
                c += 1

        df['shard'] = shards
        df = df.loc[success, ['idx', 'dataset', 'circuit_name', 'shard']]
        subdfs.append(df.loc[success])

    out_df = pd.concat(subdfs, ignore_index=True)
    output_csv_path = Path(args.output_csv)
    out_df.to_csv(output_csv_path, index=False)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Path to input directory with circuits.'
    )
    parser.add_argument(
        '--graph_dir',
        type=str,
        required=True,
        help='Path to output directory with circuits.'
    )
    parser.add_argument(
        '--csv_data',
        type=str,
        required=True,
        help='Path to CSV data file.'
    )
    parser.add_argument(
        '--output_csv',
        type=str,
        required=True,
        help='Path to output CSV file.'
    )
    parser.add_argument(
        '--dataset',
        type=str,
        default=None,
        help='Name of the dataset.'
    )
    parser.add_argument(
        '--log_file',
        type=str,
        default=None
    )
    parser.add_argument(
        '--graph_per_shard',
        type=int,
        default=50000,
        help='Number of graphs per shard file.'
    )

    args = parser.parse_args()

    # if args.log_file is not None:
    #     logging.basicConfig(
    #         filename=args.log_file,
    #         level=logging.INFO,
    #         format='%(asctime)s - %(levelname)s - %(message)s'
    #     )

    main(args)
