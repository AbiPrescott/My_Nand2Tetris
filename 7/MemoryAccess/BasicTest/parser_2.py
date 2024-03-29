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



# NEXT TASK
# - complete the arithemtic and push/pop module 





def main(count):
    lines, count, file_length, vm_filename = constructorIN(count)
    asmfile = (constructorOUT(vm_filename))
    while hasmorecommands(count, file_length) == 1:
        count += 1 
        lines, count, file_length, vm_filename = constructorIN(count)
        current_line = advance(lines)

        # ignores comments and whitespace
        if current_line != 'comment':
            command_type = commandtype(current_line)
        else: continue

        # parses argument 1
        if command_type != 'c_return':
           arg_1 = arg1(command_type, current_line)
           writeArithmetic(current_line, asmfile)
        else: continue

        # parses arguent 2
        if command_type in ['c_pop', 'c_push', 'c_function', 'c_call']:
            arg_2 = arg2(current_line)
            writePushPop(command_type, arg_1, arg_2, asmfile)
        else: continue


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
    if count < file_length - 1 :
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
def writeArithmetic(current_line, asmfile):
    if current_line == ['add']:
        add_asm = ['@0\n', 'M=M-1\n', 'A=M\n', 'D=M\n', 'A=A-1\n', 'M=M+D\n', 'A=A+1\n']
        asmfile.writelines(add_asm)
    return asmfile

# translates push/pop to ASM
def writePushPop(commandtype, arg1, arg2, asmfile):
    if commandtype == 'c_push' and arg1 == 'constant':
        push_constant = ['@', arg2, '\n', 'D=A\n', '@0\n', 'A=M\n', 'M=D\n', '@0\n', 'M=M+1\n']
        asmfile.writelines(push_constant)
    return asmfile




####################################### EXECUTION ##############################################

count = 0

main(count)

