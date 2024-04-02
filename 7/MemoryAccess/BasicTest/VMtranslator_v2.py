import sys

# SEQUENCE:
# - open file.vm
# - create file.asm
# - read line[count]
# - unless comment, split instruction into seperate words
# - identify the opcode and 2 arguments
# - write the ASM translation into file.asm
# - increment counter
# - repeat until EOF


def main(count):
    eq_count = 0
    gt_count = 0
    lt_count = 0
    lines, count, file_length, vm_filename = constructorIN(count)
    asmfile = (constructorOUT(vm_filename))
    while hasmorecommands(count, file_length) == 1:
        lines, count, file_length, vm_filename = constructorIN(count)
        current_line = advance(lines)
        count += 1 

        # ignores comments and whitespace
        if current_line != 'comment':
            command_type = commandtype(current_line)
        else: continue

        # parses argument 1
        if command_type != 'c_return':
           arg_1 = arg1(command_type, current_line)
           _, b, c, d = writeArithmetic(current_line, asmfile, eq_count, gt_count, lt_count)
           eq_count = b
           gt_count = c
           lt_count = d
        else: continue
        # parses arguent 2
        if command_type in ['c_pop', 'c_push', 'c_function', 'c_call']:
            arg_2 = arg2(current_line)
            writePushPop(command_type, arg_1, arg_2, asmfile)
        else: continue
    asmfile.close


####################################### PARSER #################################################

# opens input file and transfers lines to 'lines' ready
# to be parsed.
def constructorIN(count):
    vmfile_name = sys.argv[1]
    vmfile = open(vmfile_name, 'r')
    lines = vmfile.readlines()
    file_length = len(lines)
    
    vmfile.close()

    return lines[count], count, file_length, vmfile_name

# logic to determine whether all lines were sent or not
def hasmorecommands(count, file_length):
    if count < file_length:
        return 1
    else: return 0

# holds current line the translator is working on.
# Splits instruction into seperate words 
# and returns 'comment' to identify comments so that thay can be ignored
# in main()
def advance(lines):
    current_line = lines.split()
    if len(current_line) == 0: return 'comment'
    if current_line[0].find('/') != -1: return 'comment'
    else: return current_line

# identifies the opcode. Return value determines what 
# arguments are needed and for determining what the translation is
def commandtype(current_line):
    if 'push' in current_line: return 'c_push'
    elif 'pop' in current_line: return 'c_pop'
    elif 'add' or 'sub' or 'neg' or 'eq' or 'gt' or 'lt' or 'and' or 'or' or 'not' in current_line: return 'c_arithmetic'
    elif 'label' in current_line: return 'c_label'
    elif 'goto' in current_line: return 'c_goto'
    elif 'if-goto' in current_line: return 'c_if'
    elif 'function' in current_line: return 'c_function'
    elif 'return' in current_line: return 'c_return'
    elif 'call' in current_line: return 'c_call'
    else: return 'syntax error'

# selects argument 1 from instruction
def arg1(command_type, current_line):
    if 'c_arithmetic' in command_type:
        return current_line[0]
    else: 
        return current_line[1]

# selects argument 2 from instruction
def arg2(current_line):
    return current_line[2]


####################################### CODE WRITER ############################################

# creates .asm file 
def constructorOUT(vmfile_name):
    asmfile_name = vmfile_name.split('.')[0] + '.asm'
    asmfile = open(asmfile_name, 'x')
    return asmfile

# translates arithmetic to ASM
def writeArithmetic(current_line, asmfile, eq_count, gt_count, lt_count):
    if current_line == ['add']:
        add_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M+D\n']
        asmfile.writelines(add_asm)

    if current_line == ['sub']:
        sub_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M-D\n']
        asmfile.writelines(sub_asm) 

    if current_line == ['neg']:
        neg_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'M=-M\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(neg_asm)

    if current_line == ['eq']:
        eq_count = eq_count + 1
        eq_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'MD=M-D\n', '@TRUEeq{}\n'.format(eq_count), 'D;JEQ\n', '@0\n', 'AM=M-1\n', 'M=0\n', '@ENDeq{}\n'.format(eq_count), '0;JMP\n', '(TRUEeq{})\n'.format(eq_count), '@0\n', 'AM=M-1\n', 'M=-1\n', '(ENDeq{})\n'.format(eq_count), '@0\n', 'M=M+1\n']
        asmfile.writelines(eq_asm)

    if current_line == ['gt']:
        gt_count = gt_count + 1
        gt_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'MD=M-D\n', '@TRUEgt{}\n'.format(gt_count), 'D;JGT\n', '@0\n', 'AM=M-1\n', 'M=0\n', '@ENDgt{}\n'.format(gt_count), '0;JMP\n', '(TRUEgt{})\n'.format(gt_count), '@0\n', 'AM=M-1\n', 'M=-1\n', '(ENDgt{})\n'.format(gt_count), '@0\n', 'M=M+1\n']
        asmfile.writelines(gt_asm)

    if current_line == ['lt']:
        lt_count = lt_count + 1
        lt_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'MD=M-D\n', '@TRUElt{}\n'.format(lt_count), 'D;JLT\n', '@0\n', 'AM=M-1\n', 'M=0\n', '@ENDlt{}\n'.format(lt_count), '0;JMP\n', '(TRUElt{})\n'.format(lt_count), '@0\n', 'AM=M-1\n', 'M=-1\n', '(ENDlt{})\n'.format(lt_count), '@0\n', 'M=M+1\n']
        asmfile.writelines(lt_asm)    

    if current_line == ['and']:
        and_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M&D\n']
        asmfile.writelines(and_asm)

    if current_line == ['or']:
        or_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M|D\n']
        asmfile.writelines(or_asm)

    if current_line == ['not']:
        not_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'M=!D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(not_asm)

    return asmfile, eq_count, gt_count, lt_count

# translates push/pop to ASM
def writePushPop(commandtype, arg1, arg2, asmfile):
    lcl = 300
    arg = 400
    temp = 5
    ptr = 3
    static = 16

    # PUSH TRANSLATIONS
    if commandtype == 'c_push' and arg1 == 'constant':
        push_constant = ['@{}\n'.format(arg2), 'D=A\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_constant)

    if commandtype == 'c_push' and arg1 == 'local':
        dest = lcl + int(arg2)
        push_local = ['@0{}\n'.format(dest), 'D=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_local)

    if commandtype == 'c_push' and arg1 == 'argument':
        dest = arg + int(arg2)
        push_argument = ['@0{}\n'.format(dest), 'D=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_argument)

    if commandtype == 'c_push' and arg1 == 'this':
        push_this = ['@{}\n'.format(arg2), 'D=A\n', '@R3\n', 'A=M+D\n', 'AD=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_this)

    if commandtype == 'c_push' and arg1 == 'that':
        #dest = that + int(arg2)
        push_that = ['@{}\n'.format(arg2), 'D=A\n', '@R4\n', 'A=M+D\n', 'AD=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_that)

    if commandtype == 'c_push' and arg1 == 'temp':
        dest = temp + int(arg2)
        push_temp = ['@0{}\n'.format(dest), 'D=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_temp)

    if commandtype == 'c_push' and arg1 == 'pointer':
        dest = ptr + int(arg2)
        push_pointer = ['@0{}\n'.format(dest), 'D=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n'] 
        asmfile.writelines(push_pointer)

    if commandtype == 'c_push' and arg1 == 'static':
        dest = static + int(arg2)
        push_static = ['@0{}\n'.format(dest), 'D=M\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n'] 
        asmfile.writelines(push_static)


    # POP TRANSLATIONS
    if commandtype == 'c_pop' and arg1 == 'local':
        dest = lcl + int(arg2)
        pop_local = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(dest), 'M=D\n']
        asmfile.writelines(pop_local)

    if commandtype == 'c_pop' and arg1 == 'argument':
        dest = arg + int(arg2)
        pop_argument = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(dest), 'M=D\n']
        asmfile.writelines(pop_argument)

    if commandtype == 'c_pop' and arg1 == 'this':
        #dest = this + int(arg2)
        pop_this = ['@{}\n'.format(arg2), 'D=A\n', '@R3\n', 'AM=M+D\n', '@0\n', 'AM=M-1\n', 'D=M\n', '@R3\n', 'A=M\n', 'M=D\n', '@{}\n'.format(arg2), 'D=A\n', '@R3\n', 'AM=M-D\n']
        asmfile.writelines(pop_this)

    if commandtype == 'c_pop' and arg1 == 'that':
        #dest = that + int(arg2)
        pop_that = ['@{}\n'.format(arg2), 'D=A\n', '@R4\n', 'AM=M+D\n', '@0\n', 'AM=M-1\n', 'D=M\n', '@R4\n', 'A=M\n', 'M=D\n', '@{}\n'.format(arg2), 'D=A\n', '@R4\n', 'AM=M-D\n']
        asmfile.writelines(pop_that)

    if commandtype == 'c_pop' and arg1 == 'temp':
        dest = temp + int(arg2)
        pop_temp = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(dest), 'M=D\n']
        asmfile.writelines(pop_temp)

    if commandtype == 'c_pop' and arg1 == 'pointer':
        dest = ptr + int(arg2)
        pop_pointer = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(dest), 'M=D\n']
        asmfile.writelines(pop_pointer)

    if commandtype == 'c_pop' and arg1 == 'static':
        dest = static + int(arg2)
        pop_static = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(dest), 'M=D\n']
        asmfile.writelines(pop_static)
 
    return asmfile




####################################### EXECUTION ##############################################

count = 0

main(count)

