abc_path=""

base_path=""

bench_path="$base_path/bench"
gml_path="$base_path/graphml"

data_path="$base_path/orig"
csv_data="../data/circ_df.csv"

# read_lib Mylib.lib
# abc 03> map
# abc 04> write_bench c432new.bench
# abc 05> write c432new.blif

# $abc_path -c "read $aig_path; strash; write_bench -l $bench_path"

## Convert AIG to BENCH
# python -m src.circ2graph \
#     --input_dir $data_path \
#     --csv_data $csv_data \
#     --bench_dir $bench_path \
#     --abc_path $abc_path \

# Convert BENCH to GraphML
python -m src.circ2graph \
    --input_dir $data_path \
    --csv_data $csv_data \
    --bench_dir $bench_path \
    --graph_dir $gml_path 

## Full pipeline with ABC and converter
# python -m src.circ2graph \
#     --input_dir $data_path \
#     --csv_data $csv_data \
#     --bench_dir $bench_path \
#     --graph_dir $gml_path \
#     --abc_path $abc_path \

