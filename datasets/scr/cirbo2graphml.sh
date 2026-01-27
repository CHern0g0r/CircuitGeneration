base_path=""
data_path="${base_path}/heap/data/circ/orig/cirbo"
gml_path="${base_path}/heap/data/circ/graphml"
csv_data="${base_path}/workspace/circ/CircuitGeneration/datasets/data/circ_df.csv"
out_csv="${base_path}/workspace/circ/CircuitGeneration/datasets/data/cirbo_df.csv"
dataset="cirbo"

echo "cirbo to graphml"

python -m src.bench2gml \
    --input_dir $data_path \
    --graph_dir $gml_path \
    --csv_data $csv_data \
    --output_csv $out_csv \
    --dataset $dataset
