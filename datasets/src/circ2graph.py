import pandas as pd
import subprocess

from pathlib import Path
from hashlib import sha256
from argparse import ArgumentParser

from src.andAIG2Graphml import (
    parseAIGBenchAndCreateNetworkXGraph,
    dumpGMLGraph,
    checkInputPaths
)

from tqdm import tqdm


ABC_COMMAND = "read {input}; strash; write_bench -l {bench_output}"
EXT_SET = {'.aig', '.v', '.blif', '.bench', '.vhdl'}


def single2bench(abc_path: str,
                 input_path: str,
                 bench_output: str):
    res = subprocess.run(
        [
            abc_path,
            '-c',
            ABC_COMMAND.format(
                input=input_path,
                bench_output=bench_output
            )
        ],
        capture_output=True
    )
    output = res.stdout.decode()
    return 'Error:' not in output


def get_raw_files_df(input_dir, bench_dir):
    df = pd.DataFrame(columns=[
        'idx',
        'dataset',
        'circuit_name',
        'orig_path',
        'is_bench',
        'bench_path',
    ])
    for file_path in tqdm(input_dir.glob("**/*"), desc='Collect files'):
        if file_path.is_dir():
            continue
        if file_path.suffix not in EXT_SET:
            continue

        circuit_name = file_path.stem
        circuit_ext = file_path.suffix
        is_bench = (circuit_ext == '.bench')

        relative_path = file_path.relative_to(input_dir)
        idx = str(relative_path.with_suffix(''))
        idx = sha256(idx.encode()).hexdigest()[:16]
        dataset_name = relative_path.parts[0]
        if is_bench:
            bench_path = file_path
        else:
            bench_fname = str(relative_path.with_suffix('.bench')).replace(
                '/', '_').replace('\\', '_')
            bench_path = bench_dir / bench_fname

        df = pd.concat([df, pd.DataFrame([{
            'idx': idx,
            'dataset': dataset_name,
            'circuit_name': circuit_name,
            'orig_path': str(file_path),
            'bench_path': str(bench_path),
            'is_bench': is_bench
        }])], ignore_index=True)

    df.sort_values(by=['idx', 'is_bench'], inplace=True)
    df.drop_duplicates(subset=['idx'], keep='last', inplace=True)

    return df


def convert2bench(input_dir, bench_dir, csv_path, abc_path):
    if not csv_path.exists():
        df = get_raw_files_df(input_dir, bench_dir)
        df.to_csv(csv_path, index=False)
    else:
        df = pd.read_csv(csv_path)

    rcs = []
    for _, row in tqdm(df.iterrows(), desc='abc convert', total=len(df)):
        if row['is_bench']:
            rcs.append(True)
            continue
        rc = single2bench(abc_path, row['orig_path'], row['bench_path'])
        rcs.append(rc)
    df['conversion_success'] = rcs
    df.to_csv(csv_path, index=False)
    return df


def convert2graph(df, graph_dir):
    gml_paths = []
    for _, row in tqdm(df.iterrows(),
                       desc='aig2graph convert',
                       total=len(df)):
        if not row['conversion_success']:
            gml_paths.append(None)
            continue

        bench_path = row['orig_path'] if row['is_bench'] else row['bench_path']
        path_check = checkInputPaths(bench_path, graph_dir)
        if not path_check:
            print(f"Skipping {bench_path}: no such file or dir")
            gml_paths.append(None)
            continue
        try:
            nxGraph = parseAIGBenchAndCreateNetworkXGraph(bench_path)
            if nxGraph is None:
                gml_paths.append(None)
                continue
            gml_path = dumpGMLGraph(nxGraph, bench_path, graph_dir)
        except Exception as e:
            print(f"Error processing {bench_path}: {e}")
            gml_paths.append(None)
            continue
        gml_paths.append(gml_path)
    df['gml_path'] = gml_paths
    return df


def main(args):
    input_dir: Path = args.input_dir
    csv_path: Path = args.csv_data
    bench_dir: Path = args.bench_dir
    graph_dir: Path = args.graph_dir
    abc_path: str = args.abc_path

    if bench_dir and abc_path:
        print('Convert to bench')
        df = convert2bench(input_dir, bench_dir, csv_path, abc_path)
    else:
        df = pd.read_csv(csv_path)

    bench_dfs = []
    if graph_dir:
        print('Convert to graph')
        for dataset in df['dataset'].unique():
            if dataset != 'cirbo':
                continue
            print(f'Processing dataset {dataset}')
            dataset_graph_dir = graph_dir / dataset
            dataset_graph_dir.mkdir(parents=True, exist_ok=True)
            sub_df = df[df['dataset'] == dataset].copy()
            sub_df = convert2graph(sub_df, dataset_graph_dir)
            bench_dfs.append(sub_df)
        df = pd.concat(bench_dfs, ignore_index=True)

    df.to_csv(csv_path.parent / 'cirbo_graphml_df.csv', index=False)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input_dir", type=Path,
                        required=True, help="Input circuit or dir")
    parser.add_argument("--csv_data", type=Path,
                        required=True, help="Output CSV data file")
    parser.add_argument("--bench_dir", type=Path,
                        help="Output bench dir")
    parser.add_argument("--graph_dir", type=Path,
                        help="Output graph dir")
    parser.add_argument('--abc_path', type=str,
                        help='Path to abc binary',
                        default=None)
    args = parser.parse_args()

    # convert2bench(args.abc_path, args.input_dir, args.bench_dir)
    main(args)
