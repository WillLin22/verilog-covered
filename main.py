from Analyzer import Analyzer, statistic
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
    parser.add_argument('--target-file', type=str, default="fadd32_11.v",  help='Target verilog file')
    parser.add_argument('--iverilog', type=str, default='iverilog', help='iverilog executable')
    parser.add_argument('--get-error-ios', action='store_true', help='Get error IOs')
    parser.add_argument('--get-all-ios', action='store_true', help='Get all IOs')
    parser.add_argument('--get-modified-code', action='store_true', help='Get modified code')
    parser.add_argument('--analyse-result', action='store_true')
    parser.add_argument('--print-ops', action='store_true', help='Print all operations in the code')
    parser.add_argument('--ios', default=None, type=str, help='IOs file to read')
    parser.add_argument('--get-time', action='store_true', help='Get time of analysis')
    args = parser.parse_args()
    code_path = code_dir + args.target_file
    # "/home/willlin/miniforge3/envs/veribench/bin/iverilog"
    iverilog = args.iverilog
    import time
    start_time = time.time()
    analyzer = Analyzer(code_path, "fadd32", iverilog=iverilog, iofile=args.ios)
    end_time = time.time()
    ios = analyzer.error_ios if args.get_error_ios else analyzer.ios
    if args.get_error_ios or args.get_all_ios:
        with open("fadd32_ios", "w+") as f:
            for io in ios:
                f.write(f"{io[0][0]} {io[0][1]} {io[0][2]} {io[0][3]} {io[0][4]} \t# {io[1]} {io[2]}\n")
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
    if args.get_time:
        print(f"Analysis time: {end_time - start_time:.4f} seconds")
    if args.get_modified_code:
        analyzer.get_modified_code()
    print(f'Total IOs: {len(analyzer.results)}')
    print(f'Correct rate: {sum(analyzer.results)} / {len(analyzer.results)} = {sum(analyzer.results)/len(analyzer.results):.4f}')
    
    if args.analyse_result:
        statistics = statistic(analyzer.expressions, analyzer.exec_nums, analyzer.results)
        statistics.printlist(statistics.jaccard, 20)
    if args.print_ops:
        ops = list(set([int(e.op) for e in analyzer.expressions[1:]]))
        print(ops)


    
    
        
