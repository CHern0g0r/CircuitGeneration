data_path="/Users/fedor.chernogorskii/heap/data/circ/orig/cirbo"
gml_path="/Users/fedor.chernogorskii/heap/data/circ/graphml"
csv_data="/Users/fedor.chernogorskii/workspace/circ/CircuitGeneration/datasets/data/circ_df.csv"
out_csv="/Users/fedor.chernogorskii/workspace/circ/CircuitGeneration/datasets/data/cirbo_df.csv"
dataset="cirbo"

echo "cirbo to graphml"

python -m src.bench2gml \
    --input_dir $data_path \
    --graph_dir $gml_path \
    --csv_data $csv_data \
    --output_csv $out_csv \
    --dataset $dataset
