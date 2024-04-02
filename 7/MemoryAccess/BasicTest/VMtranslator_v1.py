
import sys

def main(count):
    a, b, c, d = constructorIN(count)
    asmfile = (constructorOUT(d))
    while hasmorecommands(b,c) == 1:
        count += 1
        a, b, c, d = constructorIN(count)
        current_line = advance(a)
        print(current_line)
        if current_line != 'comment':
            print(commandtype(current_line))
        else: continue 
        if commandtype(current_line) != 'c_return':
            writeArithmetic(current_line, asmfile)
            

        else: continue
        print('B', commandtype(current_line))
        if commandtype(current_line) in ['c_pop' , 'c_push' , 'c_function' , 'c_call']:
            writePushPop(commandtype(current_line),(arg1(commandtype(current_line), current_line)), arg2(current_line), asmfile)
        else: 
            continue






 
####################### PARSER ##############################
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
    if count < file_length - 1 :
        return 1
    else: return 0

# holds current line the translator is working on
def advance(lines):
    current_line = lines.split()
    if len(current_line) == 0: return 'comment'
    if current_line[0].find('/') != -1: return 'comment'
    else: return current_line


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


def arg1(command_type, current_line):
    if 'c_arithmetic' in command_type:
        return current_line[0]
    else: 
        return current_line[1]

def arg2(current_line):
    return current_line[2]


####################### CODE WRITER #######################

def constructorOUT(vmfile_name):
    asmfile_name = vmfile_name.split('.')[0] + '.asm'
    asmfile = open(asmfile_name, 'x')
    return asmfile

def writeArithmetic(current_line, asmfile):
    if current_line == ['add']:
        add_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M+D\n', 'A=A+1\n']
        asmfile.writelines(add_asm)
    return asmfile


def writePushPop(commandtype, arg1, arg2, asmfile):
    if commandtype == 'c_push' and arg1 == 'constant':
        push_constant = ['@', arg2, '\n', 'D=A\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_constant)
    return asmfile



count = 0

main(count)
