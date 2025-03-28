import os
import tempfile
import subprocess
from joblib import Parallel, delayed


def test_verilog(code_path, function, n_jobs=64):
    def job(vvp, io, function):
        io = io.strip()
        match function:
            case "fadd32" | "fadd64":
                rm, a, b, ref_result, ref_fflags = io.split()
                command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}", f"2>/dev/null"]
            case "fcmp32" | "fcmp64":
                a, b, ref_result, ref_fflags = io.split()
                command = [vvp, f"+a={a}", f"+b={b}", f"2>/dev/null"]
            case "fmul32" | "fmul64":
                rm, a, b, ref_result, ref_fflags = io.split()
                command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}", f"2>/dev/null"]
            case "fmac32" | "fmac64":
                rm, a, b, c, ref_result, ref_fflags = io.split()
                command = [vvp, f"+rm={rm}", f"+a={a}", f"+b={b}", f"+c={c}", f"2>/dev/null"]
            case "fp2int32" | "fp2int64":
                rm, op, a, ref_result, ref_fflags = io.split()
                command = [vvp, f"+rm={rm}", f"+a={a}", f"+op={op}", f"2>/dev/null"]
            case "int2fp32" | "int2fp64":
                rm, sign, a, ref_result, ref_fflags = io.split()
                command = [vvp, f"+rm={rm}", f"+int={a}", f"+sign={sign}", f"2>/dev/null"]
            case _:
                print(f"Unknown function: {function}")
                exit()
        try:
            sim_ret = subprocess.run(
                command,
                shell=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
                )
            output = sim_ret.stdout.decode()
        except KeyboardInterrupt:
            exit()
        except:
            return 0, 0
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
        return result, fflag


    with tempfile.TemporaryDirectory(dir=f"/run/user/{os.getuid()}") as temp_dir:
        # compile with iverilog
        os.system(f"cp {code_path} {temp_dir}/")
        os.system(f"cp ./template/{function}_testbench.sv {temp_dir}/")
        os.system(f"cd {temp_dir} && iverilog -g2012 -o top.vvp -s testbench *v 2>/dev/null 1>/dev/null")
        vvp = os.path.join(temp_dir, "top.vvp")
        if not os.path.exists(vvp):
            return -1, -1, -1, -1, -1
        # testbench
        with open(f"./testdata/{function}.io10000", 'r') as f:
            ios = f.readlines()
        results = []
        fflags = []
        try:
            ret = Parallel(n_jobs=n_jobs, timeout=5)(delayed(job)(vvp, io, function) for io in ios)
        except KeyboardInterrupt:
            exit()
        except:
            return -1, -1, -1, -1, -1
    results = [i[0] for i in ret]
    fflags = [i[1] for i in ret]
    result_acc = sum(results) / len(results)
    fflag_acc = sum(fflags) / len(fflags)
    all_acc = sum(i and j for i, j in zip(results, fflags)) / len(results)
    return results, fflags, result_acc, fflag_acc, all_acc




if __name__ == "__main__":
    results, fflags, result_acc, fflag_acc, all_acc = test_verilog("codes/op_0_dc_0_docidx_0_codeidx_0.v", "fadd32")


