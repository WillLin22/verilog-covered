from Analyzer import Analyzer
import argparse
import os

def bitwise_or(str1, str2):
    # 确保两个字符串长度相同
    if len(str1) != len(str2):
        raise ValueError("两个字符串长度必须相同")
    
    # 按位或操作
    result = ''.join('1' if s1 == '1' or s2 == '1' else '0' for s1, s2 in zip(str1, str2))
    return result


def bitwise_and(str1, str2):
    # 确保两个字符串长度相同
    if len(str1) != len(str2):
        raise ValueError("两个字符串长度必须相同")
    
    # 按位或操作
    result = ''.join('1' if s1 == '1' and s2 == '1' else '0' for s1, s2 in zip(str1, str2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    code_dir = os.path.dirname(os.path.abspath(__file__)) + "/test/"
    parser.add_argument('--target-file', type=str, default="fadd32_11_modified3.v",  help='Target verilog file')
    parser.add_argument('--iverilog', type=str, default='iverilog', help='iverilog executable')
    parser.add_argument('--get-error-ios', action='store_true', help='Get error IOs')
    parser.add_argument('--get-all-ios', action='store_true', help='Get all IOs')
    parser.add_argument('--get-modified-code', action='store_true', help='Get modified code')
    parser.add_argument('--analyse-result', action='store_true', help='Analyse the result and print the path with highest coverage')
    args = parser.parse_args()
    code_path = code_dir + args.target_file
    # "/home/willlin/miniforge3/envs/veribench/bin/iverilog"
    iverilog = args.iverilog
    analyzer = Analyzer(code_path, "fadd32", iverilog=iverilog)
    ios = analyzer.error_ios if args.get_error_ios else analyzer.ios
    if args.get_error_ios or args.get_all_ios:
        with open("fadd32_ios", "w+") as f:
            for io in ios:
                f.write(f"{io[0][0]} {io[0][1]} {io[0][2]} {io[1]} {io[2]} \t# {io[0][3]} {io[0][4]}\n")
    path_pool = {}
    for index, exec_num in enumerate(analyzer.exec_nums):
        path = ''.join(str(int(i!=0)) for i in exec_num[1:])
        if path in path_pool:
            path_pool[path].append(analyzer.results[index])
        else:
            path_pool[path] = [analyzer.results[index]]
    
    print(len(path_pool))
    path_info = []
    for path in path_pool:
        ionum = len(path_pool[path])
        pathacc = sum(path_pool[path]) / ionum
        path_info.append([path, ionum, pathacc])
    path_info.sort(key=lambda x: x[2], reverse=True)
    result_path = '1'*len(path_info[0][0])
    for path, ionum, pathacc in path_info:
        if pathacc < 1:
            result_path = bitwise_and(result_path, path)
    print(result_path)
    string = analyzer.get_path(path=result_path)
    print(string)
    if args.get_modified_code:
        analyzer.get_modified_code()
    
    print(f'Total IOs: {len(analyzer.results)}')
    print(f'Correct rate: {sum(analyzer.results)} / {len(analyzer.results)} = {sum(analyzer.results)/len(analyzer.results):.4f}')
    
    if args.analyse_result:
        # 对每个ast节点计算正确率，并排序
        ast_info = list()
        ast_info = [((e.name if e.name else 'None', e.op, e.line, e.col), \
            [analyzer.results[i] for i in range(len(analyzer.results)) if analyzer.exec_nums[i][index] != 0]) \
            for index, e in enumerate(analyzer.expressions) if index != 0 ]
        ast_accuracy = [((name, op, line, col) , 1-(sum(results)/len(results)) if len(results) else 0) for (name, op, line, col), results in ast_info]
        ast_accuracy.sort(key=lambda x: x[-1], reverse=True)
        n_ios = len(analyzer.results)
        n_wrong_ios = sum(1 for res in analyzer.results if res == 0)
        ast_number = [((name, op, line, col), sum(1 for res in results if res == 0)/n_wrong_ios if n_wrong_ios != 0 else 0) for (name, op, line, col), results in ast_info]
        ast_number.sort(key=lambda x: x[-1], reverse=True)
        total = 20 # 输出的数量
        def printlist(lst, total):
            cnt = 0
            exist = []
            for (name, op, line, col), val in lst:
                if name == 'None' or name in exist: # or op != 1 or name in exist: # EXP_OP.SIG = 1
                    continue
                exist.append(name)
                print(f"\t{name}:\tline:{line}, col{col}: \t{val:.4f}")
                cnt += 1
                if cnt == total:
                    break
        print('AST node error rate:')    
        printlist(ast_accuracy, total)
        n_cond = 0
        for e in analyzer.expressions[1:]:
            if e.op == 25:
                n_cond += 1
        print(n_cond)
        # print('AST node error number/total error number:')
        # printlist(ast_number, total)


    
    
        