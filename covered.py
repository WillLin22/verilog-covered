from abc import ABC
from constants import EXP_OP
from enum import IntEnum


class BaseClass(ABC):
    def __str__(self):
        fields = []
        for field in self.__dict__:
            value = getattr(self, field)
            if isinstance(value, IntEnum):
                fields.append(f"{field}: {value.name}")
            else:
                fields.append(f"{field}: {value}")
        return f"{{{', '.join(fields)}}}"


    def __repr__(self):
        return self.__str__()




class Esuppl(BaseClass):
    def __init__(self, esuppl):
        # Define the bit positions and masks for each field
        bit_fields = {
            "swapped": (0, 1),
            "root": (1, 1),
            "false": (2, 1),
            "true": (3, 1),
            "left_changed": (4, 1),
            "right_changed": (5, 1),
            "eval_00": (6, 1),
            "eval_01": (7, 1),
            "eval_10": (8, 1),
            "eval_11": (9, 1),
            "lhs": (10, 1),
            "in_func": (11, 1),
            "owns_vec": (12, 1),
            "excluded": (13, 1),
            "type": (14, 3),
            "base": (17, 3),
            "clear_changed": (20, 1),
            "parenthesis": (21, 1),
            "eval": (6, 4),
            # "eval_t": (22, 1),
            # "eval_f": (23, 1),
            # "comb_cntd": (24, 1),
            # "exp_added": (25, 1),
            # "owned": (26, 1),
            # "gen_expr": (27, 1),
            # "prev_called": (28, 1),
            # "for_cntrl": (29, 1),
            # "nba": (30, 1)
        }
        for field, (start_bit, bit_width) in bit_fields.items():
            mask = (1 << bit_width) - 1
            value = (esuppl >> start_bit) & mask
            setattr(self, field, value)




class Vsuppl(BaseClass):
    def __init__(self, vsuppl):
        # Define the bit positions and masks for each field
        bit_fields = {
            "type": (0, 2),
            "data_type": (2, 2),
            "owns_data": (4, 1),
            "is_signed": (5, 1),
            "is_2state": (6, 1),
            # "set": (7, 1)
        }
        for field, (start_bit, bit_width) in bit_fields.items():
            mask = (1 << bit_width) - 1
            value = (vsuppl >> start_bit) & mask
            setattr(self, field, value)




class Vector(BaseClass):
    def __init__(self, line):
        if isinstance(line, str):
            items = line.split()
        elif isinstance(line, list):
            items = line
        else:
            raise TypeError("line must be str or list")
        self._parse(items)


    def _parse(self, items):
        self.width = int(items[0])
        self.suppl = Vsuppl(int(items[1], 16))
        self.value = items[2:]




class DBExpression(BaseClass):
    def __init__(self, line):
        if isinstance(line, str):
            items = line.split()
        elif isinstance(line, list):
            items = line
        else:
            raise TypeError("line must be str or list")
        self._parse(items)


    def _parse(self, items):
        assert int(items[0]) == 2
        self.id = int(items[1])
        self.op = EXP_OP(int(items[2], 16))
        self.line = int(items[3])
        self.col = (int(items[4], 16) >> 16, int(items[4], 16) & 0xFFFF)
        self.exec_num = int(items[5], 16)
        self.suppl = Esuppl(int(items[6], 16))
        self.right = int(items[7])
        self.left = int(items[8])
        self.name = items[-1] if self.op in [EXP_OP.SIG, EXP_OP.SBIT_SEL, EXP_OP.MBIT_SEL] else None
        value = items[9:-1] if self.op in [EXP_OP.SIG, EXP_OP.SBIT_SEL, EXP_OP.MBIT_SEL] else items[9:]
        if self.suppl.owns_vec == 0:
            assert len(value) == 0
            self.value = None
        else:
            self.value = Vector(value)
        self.father = None


