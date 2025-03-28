基于covered获取ast和覆盖率
使用之前先source env.sh

目前只支持部分Verilog语法，后续可以拓展 CDDAnalyzer.py 和 covered.py 来支持更多Verilog语法（上限为covered支持的Verilog语法）

AST每个节点为一个DBExpression类，类成员见covered.py