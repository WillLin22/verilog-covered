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
    myparser = MyParser()
    code_dir = os.path.dirname(os.path.abspath(__file__)) + "/test/"
    args = myparser.parse_args()
    vars_limit = args.vars_limit
    zero = args.dist_factor_zero
    for i, target_file in enumerate(args.target_files):
        code_path = code_dir + target_file
        # "/home/willlin/miniforge3/envs/veribench/bin/iverilog"
        iverilog = args.iverilog
        start_time = time.time()
        analyzer = Analyzer(code_path, "fadd32", iverilog=iverilog, iofile=args.ios, load_results=args.analyse_only, store_results=args.store)
        end_time = time.time()
        ios = analyzer.error_ios if args.get_error_ios else analyzer.ios
        if args.get_error_ios or args.get_all_ios:
            myparser.output_ios(ios)
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
            analyzer.get_modified_code(target_file)
        if args.add_variables:
            analyzer.add_variables(target_file)
        print(f'Total IOs: {len(analyzer.results)}')
        print(f'Correct rate: {sum(analyzer.results)} / {len(analyzer.results)} = {sum(analyzer.results)/len(analyzer.results):.4f}')
        
        
        if args.analyse_result or args.analyse_only:
            # def dist_factor(x, d):
            #     return x * (1 - d*0.1) if d >= 0 and d < 10 else 0
            def dist_factor(x, d, zero=5 , e=2):
                """
                采用非线性的e次函数，距离为0的时候比例为zero，距离为10的时候比例为0
                """
                return x * (1 - (d / zero) ** e) if d >= 0 and d < zero else 0 
            faulty_var=""           
            if not is_arg_specified('--faulty-vars') or i >= len(args.faulty_vars):
                print(f"Warning: No faulty variable specified, using default: {args.faulty_vars[0]}")
                faulty_var = args.faulty_vars[0]
            else:
                faulty_var = args.faulty_vars[i]
            graph = Assign_Graph()
            dists = graph.run(analyzer.expressions)
            statistics = statistic(analyzer.expressions, analyzer.codes, analyzer.exec_nums, analyzer.results)
            func_list = [tarantula, jaccard, ochiai, D, naish1]
            fault_analyzer = Fault_Locate_Analyzer_Factory().create(dists, vars_limit=vars_limit, dist_factor=lambda x, d: dist_factor(x, d, zero=zero), type=args.analyser_type)
            
            output_file = f"scores_{target_file.split('.')[0]}_{args.ios.split('.')[1]}" if args.analyse_output_file == None else args.analyse_output_file
            output = Output_helper(output_file)
            for func in func_list:
                lst   = statistics.get_var_location_list(func)
                statistics.printlist(target_file , func, 100)
                score = fault_analyzer.analyse(faulty_var, lst)
                print(f"Fault location score for func {func.__name__}: {score:.4f}")
                output.write(f"{score:.4f}\t", "a")
            output.write("\n", "a")

        if args.print_ops:
            ops = list(set([int(e.op) for e in analyzer.expressions[1:]]))
            print(ops)
        


        
        
            
