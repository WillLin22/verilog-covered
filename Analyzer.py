import os
import tempfile
import subprocess
from joblib import Parallel, delayed
from CDDAnalyzer import CDDAnalyzer
import time
import pickle
from tools import *


def _job(vvp, temp_dir, io, code_path, function, only_parse=False):
    io = io.strip()
    output_filename = function
    match function:
        case "fadd32" | "fadd64":
            rm, a, b, ref_result, ref_fflags = io.split()
            command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}"]
            output_filename += f"_{rm}_{a:>08}_{b:>08}".lower()
        case "fcmp32" | "fcmp64":
            a, b, ref_result, ref_fflags = io.split()
            command = [vvp, f"+a={a}", f"+b={b}"]
        case "fmul32" | "fmul64":
            rm, a, b, ref_result, ref_fflags = io.split()
            command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}"]
        case "fmac32" | "fmac64":
            rm, a, b, c, ref_result, ref_fflags = io.split()
            command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}", f"+c={c}"]
        case "fp2int32" | "fp2int64":
            rm, op, a, ref_result, ref_fflags = io.split()
            command = [vvp, f"+rm={rm}", f"+a={a}", f"+op={op}"]
        case "int2fp32" | "int2fp64":
            rm, sign, a, ref_result, ref_fflags = io.split()
            command = [vvp, f"+rm={rm}", f"+int={a}", f"+sign={sign}"]
        case _:
            print(f"Unknown function: {function}")
            exit()
    # command += [f"2>/dev/null"]
    try:
        sim_ret = subprocess.run(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            cwd=temp_dir
            )
        output = sim_ret.stdout.decode()
    except KeyboardInterrupt:
        exit()
    except:
        if only_parse:
            return None
        return None, 0, 0
    lines = output.split("\n")
    for line in lines:
        if line.startswith("io_result"):
            io_result = line.split()[1]
        if line.startswith("io_fflags"):
            io_fflags = line.split()[1]
    try:
        result = int(int(io_result, 16) == int(ref_result, 16))
    except:
        result = 0
    try:
        fflag = int(int(io_fflags, 16) == int(ref_fflags, 16))
    except:
        fflag = 0


    try:
        # print(f"cd {temp_dir} && covered score -v {code_path} -g 3 -t {function[:-2].upper()} -i testbench.{function[:-2]}_inst  -vcd {temp_dir}/{output_filename}.vcd -p tmp{output_filename} -o {temp_dir}/{output_filename}.cdd > /dev/null 2>&1")
        os.system(f"cd {temp_dir} && covered score -v {code_path} -g 3 -t {function[:-2].upper()} -i testbench.{function[:-2]}_inst  -vcd {temp_dir}/{output_filename}.vcd -p tmp{output_filename} -o {temp_dir}/{output_filename}.cdd > /dev/null 2>&1")
    except:
        print("analyzer cdd wrong")
        breakpoint()

    try:
        analyzer = CDDAnalyzer(code_path, cdd_file=os.path.join(temp_dir, f"{output_filename}.cdd"))
    except Exception as e:
        print(e)
        print("analyzer wrong")
        breakpoint()
    analyzer.analyze()
    os.system(f'rm {temp_dir}/{output_filename}.cdd')
    os.system(f'rm {temp_dir}/{output_filename}.vcd')

    if only_parse:
        return analyzer.expressions
    return analyzer.get_exec_num(), result, fflag ,( io.split(), io_result, io_fflags)


class Analyzer():
    def __init__(self, code_path, function, n_jobs=128, iverilog="iverilog", iofile=None, store_results=True, load_results=False):
        pkl_path = f"./pkl/{code_path.split('/')[-1].split('.')[0]}_{iofile.replace('.', '_')}_analyzer.pkl"
        with open(code_path, 'r') as f:
            self.codes = f.read().splitlines()
        if load_results:
            try:
                with open(pkl_path, 'rb') as f:
                    self.expressions,self.exec_nums, self.results, self.fflags = pickle.load(f)
                self.ios = []
                self.error_ios = []
                return
            except FileNotFoundError:
                print(f"File {pkl_path} not found. Re-running the simulation and store the results.")
                store_results = True
        with tempfile.TemporaryDirectory(dir=f"./temp") as temp_dir:
            os.system(f"cp {code_path} {temp_dir}/")
            os.system(f"cp ./template/{function}_testbench.sv {temp_dir}/")
            # os.system(f"cd {temp_dir} && iverilog -g2012 -o top.vvp -s testbench *v 2>/dev/null 1>/dev/null")
            os.system(f"cd {temp_dir} && {iverilog} -g2012 -o top.vvp -s testbench *v ")
            vvp = os.path.join(temp_dir, "top.vvp")
            if not os.path.exists(vvp):
                print("vvp not exists")
                return None
            if iofile == None:
                iofile = f"{function}.io10000"
            with open("./testdata/" + iofile, 'r') as f:
                ios = f.readlines()
            self.expressions = _job(vvp, temp_dir, ios[0], code_path, function, only_parse=True)
            try:
                rets = Parallel(n_jobs=n_jobs, timeout=100)(delayed(_job)(vvp, temp_dir, io, code_path, function, only_parse=False) for io in ios)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                print(e)
                return None
        self.exec_nums = [ret[0] for ret in rets]
        self.results = [ret[1] for ret in rets]
        self.fflags = [ret[2] for ret in rets]
        self.ios = [ret[3] for ret in rets]
        self.error_ios = [ret[3] for ret in rets if ret[1] == 0]
        if store_results:
            if not os.path.exists("./pkl"):
                os.makedirs("./pkl")
            with open(pkl_path, 'wb') as f:
                pickle.dump((self.expressions, self.exec_nums, self.results, self.fflags), f)


    def get_path(self, index=None, path=None, start_mark="\033[91m", end_mark="\033[0m", reverse=False):
        if path == None:
            path = self.exec_nums[index]
        else:
            if isinstance(path, str):
                path = [None] + [int(i) for i in path]
        path_string = ""
        unexecuted = [[] for _ in range(len(self.codes))]

        for idx, e in enumerate(self.expressions):
            if path[idx] == 0:
                lineno = e.line - 1
                if unexecuted[lineno]:
                    unexecuted[lineno] = [ min(e.col[0], unexecuted[lineno][0]), max(e.col[1], unexecuted[lineno][1]) ]
                else:
                    unexecuted[lineno] = [e.col[0], e.col[1]]
        for lineno, code in enumerate(self.codes):
            if reverse:
                if unexecuted[lineno]:
                    path_string += code[:unexecuted[lineno][0]] + start_mark + code[unexecuted[lineno][0]:unexecuted[lineno][1]+1] + end_mark + code[unexecuted[lineno][1]+1:]
                else:
                    path_string += code
            else:
                if unexecuted[lineno]:
                    path_string += start_mark + code[:unexecuted[lineno][0]] + end_mark + code[unexecuted[lineno][0]:unexecuted[lineno][1]+1] + start_mark + code[unexecuted[lineno][1]+1:] + end_mark
                else:
                    path_string += start_mark + code + end_mark
            path_string += '\n'
        return path_string
    
    def get_modified_code(self, target_file, type):
        modifier = modify_code(self.expressions, self.codes, output_path=f"./{target_file.split('.')[0]}_modified.v")
        return modifier.get_modified_code(type == 1)
    def add_variables(self, target_file):
        modifier = modify_code(self.expressions, self.codes, output_path=f"./{target_file.split('.')[0]}_modified.v")
        return modifier.add_variables()
    
    
def get_code_for_sig(expressions, e):
    """Get the code for SIG, SBIT_SEL, MBIT_SEL
    
    Args:
        e (ast): ast node
    
    Returns:
        str: code for the signal
        width
    """
    width = e.value.width
    if e.op == 1:
        return (e.name, width) 
    elif e.op == 35:  # SBIT_SEL
        e_static = expressions[e.left]
        return (e.name + f"[{int(e_static.value.value[0], 16)}]", width)
    elif e.op == 36:  # MBIT_SEL
        e_left = expressions[e.left]
        e_right = expressions[e.right]
        return (e.name + f"[{int(e_left.value.value[0], 16)}:{int(e_right.value.value[0], 16)}]", width)
    
class statistic():
    """
    处理多样例统计信息，辅助生成节点错误率
    """
    def __init__(self, expressions, codes, exec_nums, results):
        self.expressions = expressions
        self.codes = codes
        n = len(expressions)
        ef = [0] * n
        nf = [0] * n
        ep = [0] * n
        np = [0] * n
        for i in range(len(exec_nums)):
            for j in range(1, n):
                if exec_nums[i][j] != 0 and results[i] == 0:
                    ef[j] += 1
                elif exec_nums[i][j] == 0 and results[i] == 0:
                    nf[j] += 1
                elif exec_nums[i][j] != 0 and results[i] == 1:
                    ep[j] += 1
                elif exec_nums[i][j] == 0 and results[i] == 1:
                    np[j] += 1
        self.a_efs = ef
        self.a_nfs = nf
        self.a_eps = ep
        self.a_nps = np
    def analyze(self, function, info_func):
        lst = [(info_func(e), function(self.a_efs[j], self.a_nfs[j], self.a_eps[j], self.a_nps[j])) for j, e in enumerate(self.expressions) if j != 0 and info_func(e) != None]
        lst.sort(key=lambda x: x[-1], reverse=True)
        return lst
    def get_var_location_list(self, function):
        def info_func(expressions, e):
            while e.father != None:
                e = expressions[e.father]
            return expressions[e.left].name if e.left != 0 else None
        lst = self.analyze(function, info_func=lambda e: info_func(self.expressions, e))
        exist = []
        for (name, weight) in lst:
            if name in exist:
                lst.remove((name, weight))
            else:
                exist.append(name)
        return lst
    def printlist(self, target_file, function ,total):
        def info_func(expressions, e):
            return (get_code_for_sig(expressions, e) if e.name != None else 'None', e.op, e.line, e.col)
        lst = self.analyze(function, info_func=lambda e: info_func(self.expressions, e))
        cnt = 0
        exist = []
        with open(f"results_{target_file.split(".")[0]}_{function.__name__}.txt", "w+") as f:
            for (name, op, line, col), val in lst:
                if name in exist: # or op != 1 or name in exist: # EXP_OP.SIG = 1
                    continue
                if not name == 'None':
                    exist.append(name)
                # print(f"\t{name}:\tline:{line}, col{col}: \t{val:.4f}") 
                # print(f"\t\t{self.codes[line-1][col[0]:col[1] + 1]}")
                f.write(f"\t{name}:\tline:{line}, col{col}: \t{val:.4f}\n") 
                f.write(f"\t\t{self.codes[line-1][col[0]:col[1] + 1]}\n")
                cnt += 1
                if cnt == total:
                    break
        
    
class modify_code():
    """
    目前不支持 带有x和z的代码比较
    使用一个新的.v文件若发现生成问题时，在运行时添加--print-ops获得代码op列表，对下面代码中的case检查是否包含了列表中除了assign类语句的全部op
    """
    def __init__(self, expressions, codes, output_path="./fadd32_11_modified.v"):
        self.expressions = expressions
        self.codes = codes
        self.output_path = output_path
        self.outputs = self._get_output_sigs()
    def traverse_ast(self, expressions, root, val_list:list[str]):
        """
        recursively return the value and width of a ast tree. If val_name appears in the val_list,
        its value is considered to be ~{val_width}'b0 otherwise {val_width}'b0.

        Args:
            expressions (list[ast]): Global ast tree
            root (int): target expression root ast node index
            val_list (list[str]): list of signals that assigns to be all 1

        Returns:
            tuple[int, int]: (value, width)
        """
        if root == 0:
            return 
        e = expressions[root]
        width = e.value.width
        if e.op == 1 or e.op == 35 or e.op == 36:
            if get_code_for_sig(expressions, e) in val_list:
                return (2 ** width - 1, width)
            else:
                return (0, width)
        elif e.op == 0:
            return (int(e.value.value[0], 16), width)
        else:
            v1 = self.traverse_ast(expressions, e.left, val_list)
            v2 = self.traverse_ast(expressions, e.right, val_list)
            return self.update_value(e.op, v1, v2)
    def update_value(self, op, vleft, vright):
        """
        return:
            tuple(int, int): var value and var width
        """
        is_output_bool = False #是否输出为bool值，是的话将width改为1
        single = False # 是否为单目运算符，如果是的话仅使用右值
        others = False # 其他情况
        match op:
            case 2: # XOR
                op = lambda x, y: x ^ y
            case 3: 
                op = lambda x, y: x * y
            case 4:
                op = lambda x, y: x // y
            case 5:
                op = lambda x, y: x % y
            case 6:
                op = lambda x, y: x + y
            case 7:
                op = lambda x, y: x - y
            case 8:
                op = lambda x, y: x & y
            case 9:
                op = lambda x, y: x | y
            case 10:
                op = lambda x, y: ~(x & y)
            case 11:
                op = lambda x, y: ~(x | y)
            case 12:
                op = lambda x, y: ~(x ^ y)
            case 13:
                op = lambda x, y: x < y
                is_output_bool = True
            case 14:
                op = lambda x, y: x > y
                is_output_bool = True
            case 15:
                op = lambda x, y: x << y
                is_output_bool = False
            case 16:
                op = lambda x, y: x >> y
                is_output_bool = False
            case 17:
                op = lambda x, y: x == y
                is_output_bool = True
            case 18:
                op = lambda x, y: x == y
                is_output_bool = True
            case 19:
                op = lambda x, y:  x <= y
                is_output_bool = True
            case 20:
                op = lambda x, y: x >= y
                is_output_bool = True
            case 21:
                op = lambda x, y: x != y
                is_output_bool = True
            case 22:
                op = lambda x, y: x != y
                is_output_bool = True
            case 23:
                op = lambda x, y: x or y
                is_output_bool = True
            case 24:
                op = lambda x, y: x and y
                is_output_bool = True
            case 29:
                op = lambda x: not x
                is_output_bool = True
                single = True
            case 30:
                op = lambda x: x != 0
                is_output_bool = True
                single = True
            case _:
                others = True
        ret = tuple()
        width = int()
        if others:
            match op:
                case 26: # COND_SEL
                    ret = ((vleft[0], vright[0]), max(vleft[1], vright[1]))
                case 25: # COND
                    ret = (vright[0][0] if vleft[0] else vright[0][1], vright[1])
                case 27: # UINV
                    ret = (2**vright[1] - 1 - vright[0], vright[1])
                case 28: # UAND
                    ret = (vright[0] == 2 ** vright[1] - 1, 1)
                case 49: # LIST
                    ret = (vleft[0] * (2** vright[1]) + vright[0], vleft[1] + vright[1])
                case 38: # CONCAT
                    ret = (vright[0], vright[1])
                    
        else:
            if is_output_bool:
                width = 1
            elif single:
                width = vright[1]
            else:
                width = max(vleft[1], vright[1])
            if single:
                ret = (op(vright[0]), width)
            else:
                ret = (op(vleft[0], vright[0]), width) 
        return ret  
            
    def _get_range(self, idx, e):
        """
        Return the range codes[start:end] for a existing assignment
        """
        start_line = e.line - 1
        end_line = int()
        if idx == len(self.expressions)-1:
            end_line = len(self.codes) - 1#不包含endmodule所在行
        else:
            line = start_line
            while not self.codes[line].strip().endswith(";"):
                line += 1
            end_line = line + 1
        return start_line, end_line
    def _get_output_sigs(self):
        outputs = []
        for code in self.codes:
            code = code.strip().split(',')
            for sig in code:
                sig = sig.strip().split(' ')
                if sig[0].strip() == 'output':
                    outputs.append(sig[-1])
        print(f"Debug: outputs: {outputs}")
        return outputs
    def _get_str_from_op(self, op):
        match op:
            case 2: return  lambda x, y, xw, yw: (f"{x} ^ {y}",max(xw, yw))
            case 3: return  lambda x, y, xw, yw: (f"{x} * {y}", xw* yw)
            case 4: return  lambda x, y, xw, yw: (f"{x} / {y}",max(xw, yw))
            case 5: return  lambda x, y, xw, yw: (f"{x} % {y}",max(xw, yw))
            case 6: return  lambda x, y, xw, yw: (f"{x} + {y}",max(xw, yw))
            case 7: return  lambda x, y, xw, yw: (f"{x} - {y}",max(xw, yw))
            case 8: return  lambda x, y, xw, yw: (f"{x} & {y}",max(xw, yw))
            case 9: return  lambda x, y, xw, yw: (f"{x} | {y}",max(xw, yw))
            case 10: return lambda x, y, xw, yw: (f"~({x} & {y})",max(xw, yw))
            case 11: return lambda x, y, xw, yw: (f"~({x} | {y})",max(xw, yw))
            case 12: return lambda x, y, xw, yw: (f"~({x} ^ {y})",max(xw, yw))
            case 13: return lambda x, y, xw, yw: (f"{x} < {y}", 1)
            case 14: return lambda x, y, xw, yw: (f"{x} > {y}", 1)
            case 15: return lambda x, y, xw, yw: (f"{x} << {y}", xw)
            case 16: return lambda x, y, xw, yw: (f"{x} >> {y}", xw)
            case 17: return lambda x, y, xw, yw: (f"{x} == {y}", 1)
            case 18: return lambda x, y, xw, yw: (f"{x} === {y}", 1)
            case 19: return lambda x, y, xw, yw: (f"{x} <= {y}", 1)
            case 20: return lambda x, y, xw, yw: (f"{x} >= {y}", 1)
            case 21: return lambda x, y, xw, yw: (f"{x} != {y}", 1)
            case 22: return lambda x, y, xw, yw: (f"{x} !== {y}", 1)
            case 23: return lambda x, y, xw, yw: (f"{x} || {y}", 1)
            case 24: return lambda x, y, xw, yw: (f"{x} && {y}", 1)
            case 25: return lambda x, y, xw, yw: (f"{x} ? {y}", yw)
            case 26: return lambda x, y, xw, yw: (f"{x} : {y}",max(xw, yw))
            case 27: return lambda x, y, xw, yw: (f"~{y}", yw)
            case 28: return lambda x, y, xw, yw: (f"&{y}", 1)
            case 29: return lambda x, y, xw, yw: (f"!{y}", 1)
            case 30: return lambda x, y, xw, yw: (f"|{y}", 1)
            case 31: return lambda x, y, xw, yw: (f"^{y}", 1)
            case 32: return lambda x, y, xw, yw: (f"~&{y}", 1)
            case 33: return lambda x, y, xw, yw: (f"~|{y}", 1)
            case 34: return lambda x, y, xw, yw: (f"~^{y}", 1)
            case 37: return lambda x, y, xw, yw: ("{" + x + "{" + y + "}"*2, 2 ** xw * yw)
            case 38: return lambda x, y, xw, yw: ("{" + y + "}",yw)
            case 49: return lambda x, y, xw, yw: (f"{x}, {y}", xw + yw)
            case _:
                print(f"_get_str_from_op does not accept op {op}!")
            
            
    def get_modified_code(self, all_expand=True):
        """
        Modify the original code and output to ./{filename}_modified.v
        If all_expand is set, all variables in one assignment will be considered thus an O(2^n) expansion will be made.
        If all_expand is clear, then only when the assignment have no branch will only one branch be added with only one var as condition

        Args:
            all_expand (bool, optional): Whether to expand all variables. Defaults to True.
        """
        def traverse(self, expressions, e, target_ops):
            if e == None:
                return False
            if e.op in target_ops:
                return True
            left = expressions[e.left]
            right = expressions[e.right]
            return traverse(self, expressions, left, target_ops) or traverse(self, expressions, right, target_ops)
        modified = []
        for idx, e in enumerate(self.expressions[1:]):
            if e.father == None:
                root = e
                sig_list = set()
                stack = [e.right]
                start_line, end_line = self._get_range(idx, e)
                codes = "".join(code.strip() for code in self.codes[start_line:end_line])
                lcodes = codes.split('=', 1)[0]
                rcodes = codes.split('=', 1)[1].split(';', 1)[0]
                # SBIT_SEL = 35  # 35:0x23. Specifies single-bit signal select (i.e., [x]).
                # MBIT_SEL = 36  # 36:0x24. Specifies multi-bit signal select (i.e., [x:y]).
                # SIG = 1  # 1:0x01. Specifies signal value.
                while stack:
                    index = stack.pop()
                    if index == 0:
                        continue
                    node = self.expressions[index]
                    if node.op == 1 or node.op == 35 or node.op == 36: 
                        sig_list.add(get_code_for_sig(self.expressions, node))
                    stack.append(node.left)
                    stack.append(node.right)
                if len(sig_list) == 0:
                    continue
                sig_list = list(sig_list)
                res_rcodes = ""
                if all_expand:
                    if len(sig_list) > 4:
                        continue
                    rcodes = '(' + rcodes + ')'
                    cond_list = [[f"{sig} == {w}'b0", f"{sig} == ~{w}'b0"] for sig, w in sig_list]
                    import itertools
                    cond_list = [list(x) for x in itertools.product(*cond_list)]
                    n = len(sig_list)
                    val_list = [ [sig_list[i] for i in range(n) if bits[i]] for bits in itertools.product([0,1], repeat=n) ]
                    for index, cond in enumerate(cond_list):
                        val, width = self.traverse_ast(self.expressions, root.right, val_list[index])
                        codes = f"{width}'h" + f"{abs(val) & ((1 << width) - 1):x}"
                        res_rcodes += "( " + " && ".join(cond) + " )" + " ? " + codes + " : "
                    res_rcodes += rcodes
                    modified.append([start_line, end_line, lcodes + '=' + res_rcodes + ';\n', 0])
                elif not traverse(self, self.expressions, self.expressions[root.right], [25, 26]):
                    sig, width = sig_list[0]
                    cond = f"{sig} == {width}'b0"
                    res_rcodes = cond + ' ? ' + rcodes + ' : ' + rcodes
                    modified.append([start_line, end_line, lcodes + ' = ' + res_rcodes + ';\n', 0])
        self._output_modified_code(modified)
    def _output_modified_code(self, modified, append=False, append_code=None):
        """
        modified: [[start_line, end_line, code, 0], ...]
        append: append append_code to the file
        append_code: if append is set to fault it is not used
        """
        with open(self.output_path, 'w+') as f:
            for lineno, code in enumerate(self.codes):
                if append == True and code.strip().startswith('endmodule'):
                    f.write(append_code)
                is_modified = [1 if lineno >= r[0] and lineno < r[1] else 0 for r in modified]
                if sum(is_modified) != 0:
                    index = next((i for i, x in enumerate(is_modified) if x == 1), -1)
                    if modified[index][3] == 0:
                        modified[index][3] = 1
                        f.write(modified[index][2])
                else:
                    f.write(code + '\n')
            
    def add_variables(self):
        """
        Used to add intermediate variables for expressions
        """
        def last_order_traversal(self, e, cnt, added_var_dict, var_name, var_width):
            """
            return:
                (level, var_cnt, width, code_for_this_part, op)
                level: int, the level of the node in the tree
                var_cnt: int, the number of variables added to the expression
            """
            def add_var_cond(op, fop):
                # return op != 49 and op != 26 and op != 38 # LIST, COND_SEL, CONCAT
                # return op == 25 # COND
                return not is_leaf(op) and fop != 49 and fop != 38 and not (fop == 25 and op == 26) and fop != op
            def is_leaf(op):
                return op == 0 or op == 1 or op == 35 or op == 36
            def need_brackets(op, lop, rop):
                lbrackets = not is_leaf(op) and not is_leaf(lop) and lop != 49 and lop != 26 and lop != 38 and lop != op
                rbrackets = not is_leaf(op) and not is_leaf(rop) and rop != 49 and rop != 26 and rop != 38 and rop != op
                return lbrackets, rbrackets
            if e == None:
                return (0, cnt, 0, "", 0)
            if is_leaf(e.op):
                return (1, cnt, e.value.width, self.codes[e.line - 1][e.col[0]:e.col[1] + 1], e.op)
            op = e.op
            left = self.expressions[e.left] if e.left != 0 else None
            right = self.expressions[e.right] if e.right != 0 else None
            fa = self.expressions[e.father] if e.father != None else None
            faop = fa.op if fa != None else 0
            func = self._get_str_from_op(e.op)
            d1, cnt1, w1, lcode, lop = last_order_traversal(self, left, cnt, added_var_dict, var_name, var_width)
            d2, cnt , w2, rcode, rop = last_order_traversal(self, right, cnt1, added_var_dict, var_name, var_width)
            d = max(d1, d2) + add_var_cond(e.op, faop)
            lbrackets, rbrackets = need_brackets(op, lop, rop)
            if lbrackets:
                lcode = "(" + lcode + ")"
            if rbrackets:
                rcode = "(" + rcode + ")"
            code, width = func(lcode, rcode, w1, w2)
            if d > 1 and add_var_cond(e.op, faop):
                new_var_name = f"{var_name}_{cnt}"
                added_var_dict[new_var_name] = (code, width)
                code = new_var_name
                cnt = cnt + 1
                op = 1
            
            return (d, cnt, width, code, op)
        modified = []
        appeared_vars = set()
        for i, e in enumerate(self.expressions[1:]):
            if e.father == None:
                added_var_dict = {}
                left = self.expressions[e.left]
                right = self.expressions[e.right]
                name = left.name
                width = left.value.width
                start_line, end_line = self._get_range(i, e)
                _, _, _, rcode, _ = last_order_traversal(self, right, 0, added_var_dict, name, width)
                if rcode in added_var_dict:
                    rcode0 = rcode
                    rcode, _ = added_var_dict[rcode]
                    added_var_dict.pop(rcode0)
                code = ""
                sel = lambda width : f"[{width-1}:0]" if width > 1 else ""
                for k, (v, w) in added_var_dict.items():
                    code += f"wire {sel(w)}{k} = {v};\n"
                begin = f"wire {sel(width)}" if name not in appeared_vars and name not in self.outputs else "assign "
                code += f"{begin}{name} = {rcode};\n"
                modified.append([start_line, end_line, code, 0])
        self._output_modified_code(modified)
    def evaluate_every_bit(self):
        """
        Used to add vars to check every existing bit and write it into runnable verilog code
        """
        graph_tool = Assign_Graph()
        vars = graph_tool.get_vars(self.expressions, get_width=True)
        prefix = 'bits_check'
        code = ''
        for vname, vwid in vars:
            if vwid == 1:
                code += f'wire {prefix}_{vname} = {vname};\n'
            else:
                for i in range(vwid):
                    code += f'wire {prefix}_{vname}_{i} = {vname}[{i}];\n'
        self._output_modified_code([], append=True, append_code=code)
                
        
                
                    
    


            




if __name__ == "__main__":
    code_path = "/nfs_global/S/jinpengwei/verilog-covered/experiments/gpt-4o-2024-11-20/best/fadd32.v"
    analyzer = Analyzer(code_path, "fadd32")
    breakpoint()
