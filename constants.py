from enum import IntEnum

class EXP_OP(IntEnum):
    STATIC = 0  # 0:0x00. Specifies constant value.
    SIG = 1  # 1:0x01. Specifies signal value.
    XOR = 2  # 2:0x02. Specifies '^' operator.
    MULTIPLY = 3  # 3:0x03. Specifies '*' operator.
    DIVIDE = 4  # 4:0x04. Specifies '/' operator.
    MOD = 5  # 5:0x05. Specifies '%' operator.
    ADD = 6  # 6:0x06. Specifies '+' operator.
    SUBTRACT = 7  # 7:0x07. Specifies '-' operator.
    AND = 8  # 8:0x08. Specifies '&' operator.
    OR = 9  # 9:0x09. Specifies '|' operator.
    NAND = 10  # 10:0x0a. Specifies '~&' operator.
    NOR = 11  # 11:0x0b. Specifies '~|' operator.
    NXOR = 12  # 12:0x0c. Specifies '~^' operator.
    LT = 13  # 13:0x0d. Specifies '<' operator.
    GT = 14  # 14:0x0e. Specifies '>' operator.
    LSHIFT = 15  # 15:0x0f. Specifies '<<' operator.
    RSHIFT = 16  # 16:0x10. Specifies '>>' operator.
    EQ = 17  # 17:0x11. Specifies '==' operator.
    CEQ = 18  # 18:0x12. Specifies '===' operator.
    LE = 19  # 19:0x13. Specifies '<=' operator.
    GE = 20  # 20:0x14. Specifies '>=' operator.
    NE = 21  # 21:0x15. Specifies '!=' operator.
    CNE = 22  # 22:0x16. Specifies '!==' operator.
    LOR = 23  # 23:0x17. Specifies '||' operator.
    LAND = 24  # 24:0x18. Specifies '&&' operator.
    COND = 25  # 25:0x19. Specifies '?:' conditional operator.
    COND_SEL = 26  # 26:0x1a. Specifies '?:' conditional select.
    UINV = 27  # 27:0x1b. Specifies '~' unary operator.
    UAND = 28  # 28:0x1c. Specifies '&' unary operator.
    UNOT = 29  # 29:0x1d. Specifies '!' unary operator.
    UOR = 30  # 30:0x1e. Specifies '|' unary operator.
    UXOR = 31  # 31:0x1f. Specifies '^' unary operator.
    UNAND = 32  # 32:0x20. Specifies '~&' unary operator.
    UNOR = 33  # 33:0x21. Specifies '~|' unary operator.
    UNXOR = 34  # 34:0x22. Specifies '~^' unary operator.
    SBIT_SEL = 35  # 35:0x23. Specifies single-bit signal select (i.e., [x]).
    MBIT_SEL = 36  # 36:0x24. Specifies multi-bit signal select (i.e., [x:y]).
    EXPAND = 37  # 37:0x25. Specifies bit expansion operator (i.e., {x{y}}).
    CONCAT = 38  # 38:0x26. Specifies signal concatenation operator (i.e., {x,y}).
    PEDGE = 39  # 39:0x27. Specifies posedge operator (i.e., \@posedge x).
    NEDGE = 40  # 40:0x28. Specifies negedge operator (i.e., \@negedge x).
    AEDGE = 41  # 41:0x29. Specifies anyedge operator (i.e., \@x).
    LAST = 42  # 42:0x2a. Specifies 1-bit holder for parent.
    EOR = 43  # 43:0x2b. Specifies 'or' event operator.
    DELAY = 44  # 44:0x2c. Specifies delay operator (i.e., #(x)).
    CASE = 45  # 45:0x2d. Specifies case equality expression.
    CASEX = 46  # 46:0x2e. Specifies casex equality expression.
    CASEZ = 47  # 47:0x2f. Specifies casez equality expression.
    DEFAULT = 48  # 48:0x30. Specifies case/casex/casez default expression.
    LIST = 49  # 49:0x31. Specifies comma separated expression list.
    PARAM = 50  # 50:0x32. Specifies full parameter.
    PARAM_SBIT = 51  # 51:0x33. Specifies single-bit select parameter.
    PARAM_MBIT = 52  # 52:0x34. Specifies multi-bit select parameter.
    ASSIGN = 53  # 53:0x35. Specifies an assign assignment operator.
    DASSIGN = 54  # 54:0x36. Specifies a wire declaration assignment operator.
    BASSIGN = 55  # 55:0x37. Specifies a blocking assignment operator.
    NASSIGN = 56  # 56:0x38. Specifies a non-blocking assignment operator.
    IF = 57  # 57:0x39. Specifies an if statement operator.
    FUNC_CALL = 58  # 58:0x3a. Specifies a function call.
    TASK_CALL = 59  # 59:0x3b. Specifies a task call (note: this operator MUST be the root of the expression tree)
    TRIGGER = 60  # 60:0x3c. Specifies an event trigger (->).
    NB_CALL = 61  # 61:0x3d. Specifies a "call" to a named block
    FORK = 62  # 62:0x3e. Specifies a fork command
    JOIN = 63  # 63:0x3f. Specifies a join command
    DISABLE = 64  # 64:0x40. Specifies a disable command
    REPEAT = 65  # 65:0x41. Specifies a repeat loop test expression
    WHILE = 66  # 66:0x42. Specifies a while loop test expression
    ALSHIFT = 67  # 67:0x43. Specifies arithmetic left shift (<<<)
    ARSHIFT = 68  # 68:0x44. Specifies arithmetic right shift (>>>)
    SLIST = 69  # 69:0x45. Specifies sensitivity list (*)
    EXPONENT = 70  # 70:0x46. Specifies the exponential operator "**"
    PASSIGN = 71  # 71:0x47. Specifies a port assignment
    RASSIGN = 72  # 72:0x48. Specifies register assignment (reg a = 1'b0)
    MBIT_POS = 73  # 73:0x49. Specifies positive variable multi-bit select (a[b+:3])
    MBIT_NEG = 74  # 74:0x4a. Specifies negative variable multi-bit select (a[b-:3])
    PARAM_MBIT_POS = 75  # 75:0x4b. Specifies positive variable multi-bit parameter select
    PARAM_MBIT_NEG = 76  # 76:0x4c. Specifies negative variable multi-bit parameter select
    NEGATE = 77  # 77:0x4d. Specifies the unary negate operator (-)
    NOOP = 78  # 78:0x4e. Specifies no operation is to be performed (placeholder)
    ALWAYS_COMB = 79  # 79:0x4f. Specifies an always_comb statement (implicit event expression - similar to SLIST)
    ALWAYS_LATCH = 80  # 80:0x50. Specifies an always_latch statement (implicit event expression - similar to SLIST)
    IINC = 81  # 81:0x51. Specifies the immediate increment SystemVerilog operator (++a)
    PINC = 82  # 82:0x52. Specifies the postponed increment SystemVerilog operator (a++)
    IDEC = 83  # 83:0x53. Specifies the immediate decrement SystemVerilog operator (--a)
    PDEC = 84  # 84:0x54. Specifies the postponed decrement SystemVerilog operator (a--)
    DLY_ASSIGN = 85  # 85:0x55. Specifies a delayed assignment (i.e., a = #5 b; or a = @(c) b;)
    DLY_OP = 86  # 86:0x56. Child expression of DLY_ASSIGN, points to the delay expr and the op expr
    RPT_DLY = 87  # 87:0x57. Child expression of DLY_OP, points to the delay expr and the repeat expr
    DIM = 88  # 88:0x58. Specifies a selection dimension (right expression points to a selection expr)
    WAIT = 89  # 89:0x59. Specifies a wait statement
    SFINISH = 90  # 90:0x5a. Specifies a $finish call
    SSTOP = 91  # 91:0x5b. Specifies a $stop call
    ADD_A = 92  # 92:0x5c. Specifies the '+=' operator
    SUB_A = 93  # 93:0x5d. Specifies the '-=' operator
    MLT_A = 94  # 94:0x5e. Specifies the '*=' operator
    DIV_A = 95  # 95:0x5f. Specifies the '/=' operator
    MOD_A = 96  # 96:0x60. Specifies the '%=' operator
    AND_A = 97  # 97:0x61. Specifies the '&=' operator
    OR_A = 98  # 98:0x62. Specifies the '|=' operator
    XOR_A = 99  # 99:0x63. Specifies the '^=' operator
    LS_A = 100  # 100:0x64. Specifies the '<<=' operator
    RS_A = 101  # 101:0x65. Specifies the '>>=' operator
    ALS_A = 102  # 102:0x66. Specifies the '<<<=' operator
    ARS_A = 103  # 103:0x67. Specifies the '>>>=' operator
    FOREVER = 104  # 104:0x68. Specifies the 'forever' statement
    STIME = 105  # 105:0x69. Specifies the $time system call
    SRANDOM = 106  # 106:0x6a. Specifies the $random system call
    PLIST = 107  # 107:0x6b. Task/function port list glue
    SASSIGN = 108  # 108:0x6c. System task port assignment holder
    SSRANDOM = 109  # 109:0x6d. Specifies the $srandom system call
    SURANDOM = 110  # 110:0x6e. Specifies the $urandom system call
    SURAND_RANGE = 111  # 111:0x6f. Specifies the $urandom_range system call
    SR2B = 112  # 112:0x70. Specifies the $realtobits system call
    SB2R = 113  # 113:0x71. Specifies the $bitstoreal system call
    SSR2B = 114  # 114:0x72. Specifies the $shortrealtobits system call
    SB2SR = 115  # 115:0x73. Specifies the $bitstoshortreal system call
    SI2R = 116  # 116:0x74. Specifies the $itor system call
    SR2I = 117  # 117:0x75. Specifies the $rtoi system call
    STESTARGS = 118  # 118:0x76. Specifies the $test$plusargs system call
    SVALARGS = 119  # 119:0x77. Specifies the $value$plusargs system call
    SSIGNED = 120  # 120:0x78. Specifies the $signed system call
    SUNSIGNED = 121  # 121:0x79. Specifies the $unsigned system call
    SCLOG2 = 122  # 122:0x7a. Specifies the $clog2 system call
    SREALTIME = 123  # 123:0x7b. Specifies the $realtime system call
