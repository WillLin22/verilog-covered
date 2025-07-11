#! /usr/bin/bash

files="fadd32_1.v fadd32_2.v fadd32_3.v fadd32_4.v fadd32_5.v fadd32_6.v fadd32_7.v fadd32_8.v fadd32_9.v fadd32_10.v fadd32_11.v fadd32_12.v fadd32_13.v fadd32_14.v fadd32_15.v"
faulty_vars=""
io100="fadd32.io100"
io10000="fadd32.io10000"
source ./env.sh
python main.py --target-files $files --ios $io100 --get-modified-code
mv -f ./fadd32_* ./test
modified_files=$(echo $files | sed 's/\.v/_modified.v/g')
python main.py --target-files $files --ios $io100 --add-variables

for file in fadd32_*_modified_modified.v; do
    if [ -f "$file" ]; then
        # 提取文件名并替换
        new_name=$(echo "$file" | sed 's/_modified_modified\.v/_modified2.v/')
        mv "$file" "./test/$new_name"
    fi
done
modified_files_2=$(echo $modified_files | sed 's/_modified\.v/_modified2.v/g')
python main.py --target-files fadd32_1_modified0_2 $modified_files_2 --ios $io10000 --store --analyse-result --faulty-vars $faulty_vars