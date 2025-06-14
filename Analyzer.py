import os
import tempfile
import subprocess
from joblib import Parallel, delayed
from CDDAnalyzer import CDDAnalyzer
import time


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
    def __init__(self, code_path, function, n_jobs=32, iverilog="iverilog", iofile=None):
        with open(code_path, 'r') as f:
            self.codes = f.read().splitlines()
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
    
    def get_modified_code(self):
        modifier = modify_code(self.expressions, self.codes)
        return modifier.get_modified_code()
    
class statistic():
    """
    处理多样例统计信息，辅助生成节点错误率
    """
    def __init__(self, expressions, exec_nums , results):
        self.expressions = expressions
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
    def printlist(self, function ,total):
        cnt = 0
        exist = []
        lst = [((e.name if e.name != None else 'None', e.op, e.line, e.col), function(self.a_efs[j], self.a_nfs[j], self.a_eps[j], self.a_nps[j])) for j, e in enumerate(self.expressions) if j != 0]
        lst.sort(key=lambda x: x[-1], reverse=True)
        with open(f"results_{function.__name__}.txt", "w+") as f:
            for (name, op, line, col), val in lst:
                if name in exist: # or op != 1 or name in exist: # EXP_OP.SIG = 1
                    continue
                if not name == 'None':
                    exist.append(name)
                print(f"\t{name}:\tline:{line}, col{col}: \t{val:.4f}") 
                f.write(f"\t{name}:\tline:{line}, col{col}: \t{val:.4f}\n") 
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
    def traverse_ast(self, expressions, root, val_list:list[str]):
        """_summary_

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
            if self.get_code_for_sig(expressions, e) in val_list:
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
    def get_code_for_sig(self, expressions, e):
        """Get the code for SIG, SBIT_SEL, MBIT_SEL
        
        Args:
            e (ast): ast node
        
        Returns:
            str: code for the signal
        """
        if e.op == 1:
            return e.name
        elif e.op == 35:  # SBIT_SEL
            e_static = expressions[e.left]
            return e.name + f"[{int(e_static.value.value[0], 16)}]"
        elif e.op == 36:  # MBIT_SEL
            e_left = expressions[e.left]
            e_right = expressions[e.right]
            return e.name + f"[{int(e_left.value.value[0], 16)}:{int(e_right.value.value[0], 16)}]"
            
    
    def get_modified_code(self):
        modified = []
        for idx, e in enumerate(self.expressions[1:]):
            if e.father == None:
                root = e
                sig_list = set()
                stack = [e.right]
                start_line = e.line - 1
                end_line = int()
                if idx == len(self.expressions)-1:
                    end_line = len(self.codes) - 1#不包含endmodule所在行
                else:
                    line = start_line
                    while not self.codes[line].strip().endswith(";"):
                        line += 1
                    end_line = line + 1
                codes = "".join(code.strip() for code in self.codes[start_line:end_line])
                lcodes = codes.split('=', 1)[0]
                rcodes = "(" + codes.split('=', 1)[1].split(';', 1)[0] + ")"
                # SBIT_SEL = 35  # 35:0x23. Specifies single-bit signal select (i.e., [x]).
                # MBIT_SEL = 36  # 36:0x24. Specifies multi-bit signal select (i.e., [x:y]).
                # SIG = 1  # 1:0x01. Specifies signal value.
                while stack:
                    index = stack.pop()
                    if index == 0:
                        continue
                    node = self.expressions[index]
                    if node.op == 1 or node.op == 35 or node.op == 36: 
                        sig_list.add(self.get_code_for_sig(self.expressions, node))
                    stack.append(node.left)
                    stack.append(node.right)
                if len(sig_list) > 4 or len(sig_list) == 0:
                    continue
                sig_list = list(sig_list)
                cond_list = [[f"{sig} == 0", f"{sig} == ~0"] for sig in sig_list]
                import itertools
                cond_list = [list(x) for x in itertools.product(*cond_list)]
                n = len(sig_list)
                val_list = [ [sig_list[i] for i in range(n) if bits[i]] for bits in itertools.product([0,1], repeat=n) ]
                res_rcodes = ""
                for index, cond in enumerate(cond_list):
                    val, width = self.traverse_ast(self.expressions, root.right, val_list[index])
                    codes = f"{width}'h" + f"{abs(val) & ((1 << width) - 1):x}"
                    res_rcodes += "( " + " && ".join(cond) + " )" + " ? " + codes + " : "
                res_rcodes += rcodes
                modified.append([start_line, end_line, lcodes + '=' + res_rcodes + ';\n', 0])
        with open(self.output_path, 'w+') as f:
            for lineno, code in enumerate(self.codes):
                is_modified = [1 if lineno >= r[0] and lineno < r[1] else 0 for r in modified]
                if sum(is_modified) != 0:
                    index = next((i for i, x in enumerate(is_modified) if x == 1), -1)
                    if modified[index][3] == 0:
                        modified[index][3] = 1
                        f.write(modified[index][2])
                else:
                    f.write(code + '\n')
                    
    
            
                    
            
            




if __name__ == "__main__":
    code_path = "/nfs_global/S/jinpengwei/verilog-covered/experiments/gpt-4o-2024-11-20/best/fadd32.v"
    analyzer = Analyzer(code_path, "fadd32")
    breakpoint()
