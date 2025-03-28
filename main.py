from Analyzer import Analyzer

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
    # code_path = "/nfs_global/S/jinpengwei/verilog-covered/experiments/gpt-4o-2024-11-20/best/fadd32.v"
    code_path = "/nfs_global/S/jinpengwei/verilog-covered/test/fadd32_11.v"
    analyzer = Analyzer(code_path, "fadd32")
    path_pool = {}
    for index, exec_num in enumerate(analyzer.exec_nums):
        path = ''.join(str(int(i!=0)) for i in exec_num[1:])
        if path in path_pool:
            path_pool[path].append(analyzer.results[index])
        else:
            path_pool[path] = [analyzer.results[index]]
    
    
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