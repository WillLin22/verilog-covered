import os
import tempfile
import subprocess
from joblib import Parallel, delayed
from CDDAnalyzer import CDDAnalyzer


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
    def __init__(self, code_path, function, n_jobs=32, iverilog="iverilog"):
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
            with open(f"./testdata/fadd32.io1000000.modified", 'r') as f:
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
                codes = "".join(self.codes[start_line:end_line])
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
                    if node.op == 1 or node.op == 35 or node.op == 36: # SIG
                        sig_list.add(node.name)
                    stack.append(node.left)
                    stack.append(node.right)
                if len(sig_list) > 8 or len(sig_list) == 0:
                    continue
                sig_list = list(sig_list)
                cond_list = [[f"{sig} == 0", f"{sig} == ~0"] for sig in sig_list]
                import itertools
                cond_list = [list(x) for x in itertools.product(*cond_list)]
                res_rcodes = ""
                for cond in cond_list:
                    res_rcodes += "( " + " && ".join(cond) + " )" + " ? " + rcodes + " : "
                res_rcodes += rcodes
                modified.append([start_line, end_line, lcodes + '=' + res_rcodes + ';\n', 0])
        with open("./fadd32_11_modified3.v", 'w+') as f:
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
