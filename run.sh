#! /usr/bin/bash

files="fadd32_1.v fadd32_2.v fadd32_3.v fadd32_4.v fadd32_5.v fadd32_6.v fadd32_7.v fadd32_8.v fadd32_9.v fadd32_10.v fadd32_11.v fadd32_12.v fadd32_13.v fadd32_14.v fadd32_15.v"
# fadd32_1: roundeed_exp和tiny
# fadd32_9: real_shift_norm和adjusted_exp
# fadd32_12: exp_ext_a和exp_ext_b
faulty_vars="rounded_exp round_up round_up round_up round_up round_up smaller_sticky need_swap real_shift_norm normalized_exp normalized_mantissa exp_ext_a result_sign_opposite result_sign_inf result_mant_nan"
io100="fadd32.io100"
io10000="fadd32.io10000"
source ./env.sh
rm -rf output
# echo "Running to generate first modified files..."
# python main.py --target-files $files --ios $io100 --get-modified-code --modify-type 2
# mv -f ./fadd32_* ./test
modified_files=$(echo $files | sed 's/\.v/_modified.v/g')
# # echo "Running to generate modified files that add intermediate vars..."
# python main.py --target-files $modified_files --ios $io100 --add-variables
# echo "mv all output modified files into test and name it \"1branch\""
# for file in fadd32_*_modified_modified.v; do
#     if [ -f "$file" ]; then
#         # 提取文件名并替换
#         new_name=$(echo "$file" | sed 's/_modified_modified\.v/_1branch.v/')
#         mv "$file" "./test/$new_name"
#     fi
# done
# modified_files_2=$(echo $modified_files | sed 's/_modified\.v/_modified2.v/g')
# nobranch_files=$(echo $modified_files | sed 's/_modified\.v/_nobranch_modified.v/g')
onebranch_files=$(echo $modified_files | sed 's/_modified\.v/_1branch.v/g')
echo "Running final step: evaluate those modified files and check the score"
vars_limit='999999'
python main.py --target-files fadd32_1_1branch0.v $onebranch_files --ios $io10000 --store --faulty-vars n_carry_out $faulty_vars --vars-limit $vars_limit --analyser-type 2 --analyse-output-file "score.txt"
tar -czvf output.tar.gz output