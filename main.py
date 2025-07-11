from Analyzer import Analyzer, statistic
import argparse
import os
import time
import pickle
from tools import *
import sys

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

def tarantula(aef, anf, aep, anp):
    return (aef/(aef + anf) )/(aef/(aef + anf) + aep/(aep + anp)) if aef+anf>0 and aep+anp > 0 and aef+aep > 0 else -1 
def jaccard(aef, anf, aep, anp):
    return aef/(aef + anf + aep) if aef + anf + aep > 0 else -1
def ochiai(aef, anf, aep, anp):
    return aef / ((aef + anf) * (aef + aep)) ** 0.5 if aef + anf > 0 and aef + aep > 0 else -1
def D(aef, anf, aep, anp):
    return aef**2/(anf + aep) if anf + aep > 0 else -1
def naish1(aef, anf, aep, anp):
    return -1 if anf > 0 else anp

def is_arg_specified(arg_name):
    """检查参数是否在命令行中被指定"""
    for arg in sys.argv[1:]:
        if arg == arg_name:
            return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    code_dir = os.path.dirname(os.path.abspath(__file__)) + "/test/"
    parser.add_argument('--target-file', type=str, default="fadd32_11.v",  help='Target verilog file')
    parser.add_argument('--iverilog', type=str, default='iverilog', help='iverilog executable')
    parser.add_argument('--get-error-ios', action='store_true', help='Get error IOs')
    parser.add_argument('--get-all-ios', action='store_true', help='Get all IOs')
    parser.add_argument('--get-modified-code', action='store_true', help='Get modified code')
    parser.add_argument('--add-variables', action='store_true', help='Add middle vars into code')
    parser.add_argument('--analyse-result', action='store_true', help='Run the simulation and analyse the result')
    parser.add_argument('--print-ops', action='store_true', help='Print all operations in the code')
    parser.add_argument('--ios', default=None, type=str, help='IOs file to read')
    parser.add_argument('--get-time', action='store_true', help='Get time of analysis')
    parser.add_argument('--store', action='store_true', help='Store the analyzer object to a pickle file')
    parser.add_argument('--analyse-only', action='store_true', help='Analyse the result only, do not run the simulation. Conflicted with get_all_ios and get_error_ios')
    parser.add_argument('--faulty-var', type=str, default='n_carry_out', help='The faulty variable to analyse')
    parser.add_argument('--analyser-type', type=int, default=2, help='Set the type of analyzer')
    args = parser.parse_args()
    code_path = code_dir + args.target_file
    # "/home/willlin/miniforge3/envs/veribench/bin/iverilog"
    iverilog = args.iverilog
    start_time = time.time()
    analyzer = Analyzer(code_path, "fadd32", iverilog=iverilog, iofile=args.ios, load_results=args.analyse_only, store_results=args.store)
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
        analyzer.get_modified_code(args.target_file)
    if args.add_variables:
        analyzer.add_variables(args.target_file)
    print(f'Total IOs: {len(analyzer.results)}')
    print(f'Correct rate: {sum(analyzer.results)} / {len(analyzer.results)} = {sum(analyzer.results)/len(analyzer.results):.4f}')
    
    
    if args.analyse_result or args.analyse_only:
        # def dist_factor(x, d):
        #     return x * (1 - d*0.1) if d >= 0 and d < 10 else 0
        def dist_factor(x, d, e=2):
            """
            采用非线性的e次函数，距离为0的时候比例为1，距离为10的时候比例为0
            """
            return x * (1 - (d / 10) ** e) if d >= 0 and d < 10 else 0            
        if not is_arg_specified('--faulty-var'):
            print(f"Warning: No faulty variable specified, using default: {args.faulty_var}")
        graph = Assign_Graph()
        dists = graph.run(analyzer.expressions)
        statistics = statistic(analyzer.expressions, analyzer.codes, analyzer.exec_nums, analyzer.results)
        func_list = [tarantula, jaccard, ochiai, D, naish1]
        fault_analyzer = Fault_Locate_Analyzer_Factory().create(dists, vars_limit=10, dist_factor=dist_factor, type=args.analyser_type)
        for func in func_list:
            lst   = statistics.get_var_location_list(func)
            statistics.printlist(args.target_file , func, 100)
            score = fault_analyzer.analyse(args.faulty_var, lst)
            print(f"Fault location score for func {func.__name__}: {score:.4f}")
        
    if args.print_ops:
        ops = list(set([int(e.op) for e in analyzer.expressions[1:]]))
        print(ops)
    


    
    
        
