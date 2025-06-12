from covered import DBExpression
from constants import EXP_OP


class CDDAnalyzer():
    def __init__(self, code_file, cdd_file):
        with open(code_file, 'r') as f:
            codes = f.readlines()
        self.codes = codes

        with open(cdd_file, 'r') as f:
            lines = f.readlines()
        expressions = [None]
        for line in lines:
            if line.startswith('2'):
                e = DBExpression(line)
                expressions.append(e)

        self.expressions = expressions
        self._get_father()



    def analyze(self):
        self._get_real_exec_num()
        self._get_producers()
        self._propagate_exec_num()
        self._get_unexecuted_lines()


    def show_codes(self, show_lineno=True, line=False):
        if line:
            for lineno, code in enumerate(self.codes):
                if show_lineno:
                    print(f"{lineno+1:>3d} ", end='')
                if lineno+1 in self.unexecuted_lines:
                    print('\033[91m' + code + '\033[0m', end='')
                else:
                    print(code, end='')
            return

        unexecuted = [[] for _ in range(len(self.codes))]
        for e in self.expressions[1:]:
            if e.exec_num == 0:
                lineno = e.line - 1
                if unexecuted[lineno]:
                    unexecuted[lineno] = [ min(e.col[0], unexecuted[lineno][0]), max(e.col[1], unexecuted[lineno][1]) ]
                else:
                    unexecuted[lineno] = [e.col[0], e.col[1]]
        for lineno, code in enumerate(self.codes):
            if show_lineno:
                print(f"{lineno+1:>3d} ", end='')
            if unexecuted[lineno]:
                print(code[:unexecuted[lineno][0]] + '\033[91m' + code[unexecuted[lineno][0]:unexecuted[lineno][1]+1] + '\033[0m' + code[unexecuted[lineno][1]+1:], end='')
            else:
                print(code, end='')


    def _get_father(self):
        for e in self.expressions[1:]:
            left_id = e.left
            right_id = e.right
            if left_id != 0:
                self.expressions[left_id].father = e.id
            if right_id != 0:
                self.expressions[right_id].father = e.id


    def _get_real_exec_num(self):
        for e in self.expressions:
            if e is None:
                continue
            match e.op:
                case EXP_OP.SIG: # !
                    self.expressions[e.id].exec_num = 1
                case EXP_OP.COND: # ?:
                    left_id = e.left
                    right_id = e.right
                    left = self.expressions[left_id]
                    right = self.expressions[right_id]
                    if left.suppl.true:
                        self.expressions[right.right].exec_num = 0
                    else:
                        self.expressions[right.left].exec_num = 0
                case EXP_OP.LAND: # &&
                    if e.suppl.eval == 0b0010: # eval_01 == 1
                        self.expressions[e.right].exec_num = 0
                    elif e.suppl.eval == 0b0100: # eval_10 == 1
                        self.expressions[e.left].exec_num = 0
                case EXP_OP.LOR: # ||
                    if e.suppl.eval == 0b0010: # eval_01 == 1
                        self.expressions[e.left].exec_num = 0
                    elif e.suppl.eval == 0b0100: # eval_10 == 1
                        self.expressions[e.right].exec_num = 0

                # case EXP_OP.LAND: # &&
                #     if e.suppl.eval == 0b0010 or e.suppl.eval == 0b0001: # eval_01 == 1
                #         self.expressions[e.right].exec_num = 0
                #     elif e.suppl.eval == 0b0100 or e.suppl.eval == 0b0001: # eval_10 == 1
                #         self.expressions[e.left].exec_num = 0
                # case EXP_OP.LOR: # ||
                #     if e.suppl.eval == 0b0010 or e.suppl.eval == 0b1000: # eval_01 == 1
                #         self.expressions[e.left].exec_num = 0
                #     elif e.suppl.eval == 0b0100 or e.suppl.eval == 0b1000: # eval_10 == 1
                #         self.expressions[e.right].exec_num = 0
                case _: pass


    def _get_producers(self):
        # {name: [{lines:set(), msb:None, lsb:None, exec_num:1}]}
        producers = {}
        
        for e in self.expressions[1:]:
            if e.op in [EXP_OP.ASSIGN, EXP_OP.DASSIGN, EXP_OP.BASSIGN, EXP_OP.NASSIGN] and e.exec_num != 0:
                left_id = e.left
                left = self.expressions[left_id]
                name = left.name
                if left.left == 0 and left.right == 0:
                    msb = left.value.width - 1
                    lsb = 0
                elif left.left != 0 and left.right == 0: # TODO: test
                    # print('To be tested')
                    msb = lsb = int(self.expressions[left.left].value.value[0], 16)
                else: # TODO: test
                    # print('To be tested')
                    msb = int(self.expressions[left.left].value.value[0], 16)
                    lsb = int(self.expressions[left.right].value.value[0], 16)
                stack = [e.id]
                lines = []
                while stack:
                    id = stack.pop()
                    curr_e = self.expressions[id]
                    left_id = curr_e.left
                    right_id = curr_e.right
                    if left_id != 0:
                        stack.append(left_id)
                    if right_id != 0:
                        stack.append(right_id)
                    if curr_e.line != 0:
                        lines.append(curr_e.line)
                if name in producers:
                    producers[name].append({
                        'lines': set(lines), 
                        'msb': msb,
                        'lsb': lsb,
                        'exec_num': 1,
                    })
                else:
                    producers[name] = [{
                        'lines': set(lines),
                        'msb': msb,
                        'lsb': lsb,
                        'exec_num': 1,
                    }]
        self.producers = producers


    def _propagate_exec_num(self):
        # Inline Propagation
        for e in self.expressions[1:]:
            if e.exec_num == 0:
                stack = [e.id]
                while stack:
                    id = stack.pop()
                    curr_e = self.expressions[id]
                    left_id = curr_e.left
                    right_id = curr_e.right
                    if left_id != 0 and self.expressions[left_id] and self.expressions[left_id].exec_num != 0:
                        stack.append(left_id)
                    if right_id != 0 and self.expressions[right_id] and self.expressions[right_id].exec_num != 0:
                        stack.append(right_id)
                    self.expressions[id].exec_num = 0

        # Interline Propagation
        while True:
            old_exec_num = []
            for e in self.expressions[1:]:
                if e.name not in self.producers:
                    continue
                for i in range(len(self.producers[e.name])):
                    old_exec_num.append(self.producers[e.name][i]['exec_num'])
            for e in self.expressions[1:]:
                if e.exec_num == 0:
                    if e.name not in self.producers:
                        continue
                    match e.op:
                        case EXP_OP.SIG:
                            for i in range(len(self.producers[e.name])):
                                self.producers[e.name][i]['exec_num'] = 0
                        case EXP_OP.SBIT_SEL:
                            left_id = e.left
                            left = self.expressions[left_id]
                            msb = lsb = int(left.value.value[0], 16)
                            for i in range(len(self.producers[e.name])):
                                if self.producers[e.name][i]['msb'] <= msb and self.producers[e.name][i]['lsb'] >= lsb:
                                    self.producers[e.name][i]['exec_num'] = 0
                        case EXP_OP.MBIT_SEL:
                            left_id = e.left
                            left = self.expressions[left_id]
                            right_id = e.right
                            right = self.expressions[right_id]
                            msb = int(left.value.value[0], 16)
                            lsb = int(right.value.value[0], 16)
                            for i in range(len(self.producers[e.name])):
                                if self.producers[e.name][i]['msb'] <= msb and self.producers[e.name][i]['lsb'] >= lsb:
                                    self.producers[e.name][i]['exec_num'] = 0
                        case _: pass
            for e in self.expressions[1:]:
                if e.father and self.expressions[e.father].op in [EXP_OP.ASSIGN, EXP_OP.DASSIGN, EXP_OP.BASSIGN, EXP_OP.NASSIGN] and self.expressions[e.father].left == e.id:
                    continue
                if e.exec_num == 1:
                    match e.op:
                        case EXP_OP.SIG:
                            if e.name not in self.producers:
                                continue
                            for i in range(len(self.producers[e.name])):
                                self.producers[e.name][i]['exec_num'] = 1
                        case EXP_OP.SBIT_SEL:
                            left_id = e.left
                            left = self.expressions[left_id]
                            msb = lsb = int(left.value.value[0], 16)
                            if e.name not in self.producers:
                                continue
                            for i in range(len(self.producers[e.name])):
                                if self.producers[e.name][i]['msb'] <= msb and self.producers[e.name][i]['lsb'] >= lsb:
                                    self.producers[e.name][i]['exec_num'] = 1
                        case EXP_OP.MBIT_SEL:
                            left_id = e.left
                            left = self.expressions[left_id]
                            right_id = e.right
                            right = self.expressions[right_id]
                            msb = int(left.value.value[0], 16)
                            lsb = int(right.value.value[0], 16)
                            if e.name not in self.producers:
                                continue
                            for i in range(len(self.producers[e.name])):
                                if self.producers[e.name][i]['msb'] <= msb and self.producers[e.name][i]['lsb'] >= lsb:
                                    self.producers[e.name][i]['exec_num'] = 1
                        case _: pass

            unexecuted_line = []
            for name in self.producers:
                for producer in self.producers[name]:
                    if producer['exec_num'] == 0:
                        unexecuted_line.extend(list(producer['lines']))
            unexecuted_line = list(set(unexecuted_line))
            for e in self.expressions[1:]:
                if e.line in unexecuted_line:
                    e.exec_num = 0

            new_exec_num = []
            for e in self.expressions[1:]:
                if e.name not in self.producers:
                    continue
                for i in range(len(self.producers[e.name])):
                    new_exec_num.append(self.producers[e.name][i]['exec_num'])
            if old_exec_num == new_exec_num:
                break




    def _get_unexecuted_lines(self):
        lines = {}
        for e in self.expressions[1:]:
            if e.line not in lines:
                lines[e.line] = 0
            lines[e.line] |= e.exec_num != 0
        unexecuted_lines = []
        for line in lines:
            if not lines[line]:
                unexecuted_lines.append(line)

        self.unexecuted_lines = unexecuted_lines


    def get_exec_num(self):
        return [None] + [e.exec_num for e in self.expressions[1:]]


    def get_path(self):
        return [int(e.exec_num != 0) for e in self.expressions[1:]]
