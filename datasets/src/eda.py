import numpy as np
import pandas as pd
import networkx as nx

from pathlib import Path
from tqdm import tqdm


type_mapping = {
    0: 'IN',
    1: 'OUT',
    2: 'AND',
}


def get_stats_nx(G):
    stats = {
        'nodes': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
    }
    degree = [d for n, d in G.degree()]
    stats.update({
        'avg_degree': np.mean(degree).item(),
        'max_degree': np.max(degree).item(),
        'min_degree': np.min(degree).item(),
    })
    stats.update({
        'assortativity': nx.degree_assortativity_coefficient(G),
        'avg_clustering': nx.average_clustering(G),
        'transitivity': nx.transitivity(G),
    })
    stats.update({
        'k_core': len(nx.k_core(G)),
        'depth': nx.dag_longest_path_length(G)
    })

    stats.update({
        'AND_count': 0,
        'IN_count': 0,
        'OUT_count': 0
    })

    for n, data in G.nodes(data=True):
        type_key = type_mapping[data['node_type']]
        stats[type_key + '_count'] += 1

    stats.update({
        'inv_edges': 0
    })

    for _, _, data in G.edges(data=True):
        if 'edge_type' in data:
            if data['edge_type'] == 1:
                stats['inv_edges'] += 1
    return stats


def main(df):
    stat_df = pd.DataFrame()

    for i, row in tqdm(df.iterrows(), total=len(df)):
        try:
            if not row['conversion_success'] and pd.isna(row['gml_path']):
                continue
            G = nx.read_graphml(row['gml_path'])
            stats = get_stats_nx(G)
            stats.update({
                'index': row['idx'],
                'name': row['circuit_name'],
                'dataset': row['dataset']
            })
            stat_df = pd.concat(
                [stat_df, pd.DataFrame([stats])],
                ignore_index=True
            )
        except Exception as e:
            print(f"Error processing {row['idx']}: {e}")
            print(row['dataset'], row['circuit_name'], row['gml_path'])
            continue
    return stat_df


if __name__ == '__main__':
    data_path = Path('../data')
    graphml_path = data_path / 'graphml_df.csv'
    cirbo_graphml_path = data_path / 'cirbo_graphml_df.csv'
    df = pd.concat([
        pd.read_csv(graphml_path),
        pd.read_csv(cirbo_graphml_path)
    ], ignore_index=True)

    stat_df = main(df)
    stat_df.to_csv(data_path / 'graph_stats2.csv', index=False)
    print(stat_df.describe().T)
