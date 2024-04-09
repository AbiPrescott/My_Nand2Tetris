import os
import sys
import numpy as np

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
    ret_count = 0
    full_vmfile, folder = constructorIN()
    lines, count, file_length = write_newvm(full_vmfile, count)
    asmfile = constructorOUT(folder)
    writeinit(asmfile)
    while hasmorecommands(count, file_length) == 1:
        lines, count, file_length = write_newvm(full_vmfile, count)
        current_line = advance(lines)
        print(current_line)
        count += 1

        # ignores comments and whitespace
        if current_line != "comment":
            command_type = commandtype(current_line[0])
        else:
            continue


        if command_type != "c_return":
            # parses argument 1
            arg_1 = arg1(command_type, current_line)

            # this section writes ASM verisons of arithmetic commands. 
            # It also keeps track of the count of each conditional opcode 
            # in order to have different labels (ie. eq1, eq2, etc). 
            # Otherwise, they would share the same label which disrupts the program flow. See 'writearithmetic'
            _, b, c, d = writeArithmetic(
                current_line[0], asmfile, eq_count, gt_count, lt_count
            )
            eq_count = b
            gt_count = c
            lt_count = d
        else:
            writereturn(command_type, asmfile)


        if command_type in ["c_label", "c_goto", "c_if"]:
            writebranch(command_type, arg_1, asmfile)

        elif command_type in ["c_pop", "c_push", "c_function", "c_call"]:
            # parses arguent 2
            arg_2 = arg2(current_line)

            if "c_pop" in command_type or "c_push" in command_type:
                writePushPop(command_type, arg_1, arg_2, asmfile)
            elif "c_function" in command_type:
                writefunction(command_type, arg_1, arg_2, asmfile)
            elif 'c_call' in command_type:
                _, ret_count = writecall(command_type, arg_1, arg_2, ret_count, asmfile)

        else: continue 
    asmfile.close


####################################### PARSER #################################################


# opens input file and transfers lines to 'lines' ready
# to be parsed.

def constructorIN():
    folder = sys.argv[1]
    full_vmfilename = 'full_vmfile.vm'
    full_vmfile = open(full_vmfilename, 'x')
    executed = []

    files = os.listdir(folder)
    vmfiles = []
    
    # filter in all the .vm files in vmfiles
    for file in files:
        if file.endswith('.vm'):
            vmfiles.append(file)

    if 'Sys.vm' in vmfiles:
        index = vmfiles.index('Sys.vm')
        vmfiles[0], vmfiles[index] = vmfiles[index], vmfiles[0]
        # for file in files:
        #     if 'Sys.vm' in file: 
        #         break
        #     elif file.endswith('.vm'):
        #         vmfiles.append(file)

    
    for vmfile in vmfiles:
        vmdir = (folder + '/' + vmfile)
        sys_file = open(vmdir, 'r')
        sys_lines = sys_file.readlines()
        for line in sys_lines:
            full_vmfile.writelines(line)
        executed = vmfile

        if vmfile not in executed:
            vmdir = (folder + '/' + vmfile)
            vm_file = open(vmdir, 'r')
            vm_lines = vm_file.readlines()
            for line in vm_lines:
                full_vmfile.writelines(line)
            executed = executed.append(vmfile)
        else: continue

    return full_vmfilename, folder



def write_newvm(full_vmfilename, count):
    full_vmfile = open(full_vmfilename, 'r')
    lines = full_vmfile.readlines()
    file_length = len(lines)    

    full_vmfile.close()

    return lines[count], count, file_length


# logic to determine whether all lines were sent or not
def hasmorecommands(count, file_length):
    if count < file_length:
        return 1
    else:
        return 0


# holds current line the translator is working on.
# Splits instruction into seperate words
# and returns 'comment' to identify comments so that thay can be ignored
# in main()

#### TRY 'if lines.startwith' 
def advance(lines):
    current_line = lines.split()
    if len(current_line) == 0:
        return "comment"
    if current_line[0].find("/") != -1:
        return "comment"
    else:
        return current_line


# identifies the opcode. Return value determines what
# arguments are needed and for determining what the translation is
def commandtype(current_line):

    if "push" in current_line:
        return "c_push"
    elif "pop" in current_line:
        return "c_pop"

    elif (
        "add" in current_line
        or "sub" in current_line
        or "neg" in current_line
        or "eq" in current_line
        or "gt" in current_line
        or "lt" in current_line
        or "and" in current_line
        or "or" in current_line
        or "not" in current_line
    ): return "c_arithmetic"


    elif "label" in current_line:
        return "c_label"
    elif "if" in current_line:
        return "c_if"
    elif "goto" in current_line:
        return "c_goto"
    elif "function" in current_line:
        return "c_function"
    elif "return" in current_line:
        return "c_return"
    elif "call" in current_line:
        return "c_call"
    else:
        return "syntax error"


# selects argument 1 from instruction
def arg1(command_type, current_line):
    if "c_arithmetic" in command_type:
        return current_line[0]
    else:
        return current_line[1]


# selects argument 2 from instruction
def arg2(current_line):
    return current_line[2]


# creates .asm file
def constructorOUT(vmfile_name):
    asmfile_name = vmfile_name.split(".")[0] + ".asm"
    asmfile = open(asmfile_name, "x")
    return asmfile

####################################### CODE WRITER ############################################

# writes Bootstrap code starting at RAM[0]. (Bootstrap code is code that calls function Sys.init)
# writeinit()
#     SP = 256
#     call sys.init 




# translates arithmetic to ASM
def writeArithmetic(current_line, asmfile, eq_count, gt_count, lt_count):

    if "add" in current_line:
        add_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "A=A-1\n", "M=M+D\n"]
        asmfile.writelines(add_asm)

    if "sub" in current_line:
        sub_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "A=A-1\n", "M=M-D\n"]
        asmfile.writelines(sub_asm)

    if "neg" in current_line:
        neg_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "M=-M\n", "@0\n", "M=M+1\n"]
        asmfile.writelines(neg_asm)

    if "eq" in current_line:
        eq_count = eq_count + 1
        eq_asm = [
            "@0\n",
            "M=M-1\n",
            "A=M\n",
            "D=M\n",
            "A=A-1\n",
            "MD=M-D\n",
            "@TRUEeq{}\n".format(eq_count),
            "D;JEQ\n",
            "@0\n",
            "AM=M-1\n",
            "M=0\n",
            "@ENDeq{}\n".format(eq_count),
            "0;JMP\n",
            "(TRUEeq{})\n".format(eq_count),
            "@0\n",
            "AM=M-1\n",
            "M=-1\n",
            "(ENDeq{})\n".format(eq_count),
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(eq_asm)

    if "gt" in current_line:
        gt_count = gt_count + 1
        gt_asm = [
            "@0\n",
            "M=M-1\n",
            "A=M\n",
            "D=M\n",
            "A=A-1\n",
            "MD=M-D\n",
            "@TRUEgt{}\n".format(gt_count),
            "D;JGT\n",
            "@0\n",
            "AM=M-1\n",
            "M=0\n",
            "@ENDgt{}\n".format(gt_count),
            "0;JMP\n",
            "(TRUEgt{})\n".format(gt_count),
            "@0\n",
            "AM=M-1\n",
            "M=-1\n",
            "(ENDgt{})\n".format(gt_count),
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(gt_asm)

    if "lt" in current_line:
        lt_count = lt_count + 1
        lt_asm = [
            "@0\n",
            "M=M-1\n",
            "A=M\n",
            "D=M\n",
            "A=A-1\n",
            "MD=M-D\n",
            "@TRUElt{}\n".format(lt_count),
            "D;JLT\n",
            "@0\n",
            "AM=M-1\n",
            "M=0\n",
            "@ENDlt{}\n".format(lt_count),
            "0;JMP\n",
            "(TRUElt{})\n".format(lt_count),
            "@0\n",
            "AM=M-1\n",
            "M=-1\n",
            "(ENDlt{})\n".format(lt_count),
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(lt_asm)

    if "and" in current_line:
        and_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "A=A-1\n", "M=M&D\n"]
        asmfile.writelines(and_asm)

    if "or" in current_line:
        or_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "A=A-1\n", "M=M|D\n"]
        asmfile.writelines(or_asm)

    if "not" in current_line:
        not_asm = ["@0\n", "M=M-1\n", "A=M\n", "D=M\n", "M=!D\n", "@0\n", "M=M+1\n"]
        asmfile.writelines(not_asm)

    return asmfile, eq_count, gt_count, lt_count


# translates push/pop to ASM
def writePushPop(commandtype, arg1, arg2, asmfile):
    temp = 5
    ptr = 3
    static = 16

    # PUSH TRANSLATIONS
    if commandtype == "c_push" and arg1 == "constant":
        push_constant = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_constant)

    if commandtype == "c_push" and arg1 == "local":
        push_local = [
            '@1\n',
            "D=M\n",
            '@{}\n'.format(arg2),
            'A=D+A\n',
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_local)

    if commandtype == "c_push" and arg1 == "argument":
        # dest = arg + int(arg2)
        push_argument = [
            '@2\n',
            "D=M\n",
            '@{}\n'.format(arg2),
            'A=D+A\n',
            'D=M\n',
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_argument)

    if commandtype == "c_push" and arg1 == "this":
        push_this = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@R3\n",
            "A=M+D\n",
            "AD=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_this)

    if commandtype == "c_push" and arg1 == "that":
        # dest = that + int(arg2)
        push_that = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@R4\n",
            "A=M+D\n",
            "AD=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_that)

    if commandtype == "c_push" and arg1 == "temp":
        dest = temp + int(arg2)
        push_temp = [
            "@0{}\n".format(dest),
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_temp)

    if commandtype == "c_push" and arg1 == "pointer":
        dest = ptr + int(arg2)
        push_pointer = [
            "@0{}\n".format(dest),
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_pointer)

    if commandtype == "c_push" and arg1 == "static":
        dest = static + int(arg2)
        push_static = [
            "@0{}\n".format(dest),
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_static)

    # POP TRANSLATIONS
    if commandtype == "c_pop" and arg1 == "local":
        #dest = lcl + int(arg2)
        pop_local = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@1\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@1\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg2),
            "D=A\n",
            "@1\n",
            "AM=M-D\n",
            ]
        asmfile.writelines(pop_local)

    if commandtype == "c_pop" and arg1 == "argument":
        #dest = arg + int(arg2)
        pop_argument = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@2\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@2\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg2),
            "D=A\n",
            "@2\n",
            "AM=M-D\n",
            ]
        asmfile.writelines(pop_argument)

    if commandtype == "c_pop" and arg1 == "this":
        # dest = this + int(arg2)
        pop_this = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@R3\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@R3\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg2),
            "D=A\n",
            "@R3\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_this)

    if commandtype == "c_pop" and arg1 == "that":
        # dest = that + int(arg2)
        pop_that = [
            "@{}\n".format(arg2),
            "D=A\n",
            "@R4\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@R4\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg2),
            "D=A\n",
            "@R4\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_that)

    if commandtype == "c_pop" and arg1 == "temp":
        dest = temp + int(arg2)
        pop_temp = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_temp)

    if commandtype == "c_pop" and arg1 == "pointer":
        dest = ptr + int(arg2)
        pop_pointer = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_pointer)

    if commandtype == "c_pop" and arg1 == "static":
        dest = static + int(arg2)
        pop_static = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_static)

    return asmfile


def writebranch(commandtype, arg_1, asmfile):

    if commandtype == 'c_label':
        label_asm = ['({})\n'.format(arg_1)]
        asmfile.writelines(label_asm)
    elif commandtype == 'c_goto':
        goto_asm = ['@{}\n'.format(arg_1), '0;JMP\n']
        asmfile.writelines(goto_asm)
    elif commandtype == 'c_if':
        if_asm = ['@0\n', 'AM=M-1\n', 'D=M\n', '@{}\n'.format(arg_1), 'D;JNE\n']
        asmfile.writelines(if_asm)
    
    return asmfile 
    
def writefunction(command_type, f_name, arg_num, asmfile):
    if 'c_function' in command_type:
        function_asm = [
            '({})\n'.format(f_name), 
            '@{}\n'.format(arg_num), 
            'D=A\n', 
            '@END{}\n'.format(f_name),
            'D;JEQ\n',
            '({}init_0)\n'.format(f_name), 
            '@0\n', 
            'A=M\n', 
            'M=0\n', 
            '@0\n', 
            'M=M+1\n', 
            'D=D-1\n',
            '@{}init_0\n'.format(f_name), 
            'D;JGT\n'
            '(END{})\n'.format(f_name)
            ]
        return asmfile.writelines(function_asm)
    else: return 'invalid syntax'

def writereturn(command_type, asmfile):
    lcl_count = 13
    retaddr_count = 14
    print(lcl_count)
    print(retaddr_count)
    if 'c_return' in command_type:
        return_asm1= np.array([
            # endframe = lcl
            '@1\n',
            'D=M\n',
            '@R{}\n'.format(lcl_count),
            'M=D\n',

            # retaddr = *(endframe - 5)
            '@5\n', 
            'D=A\n',
            '@R{}\n'.format(lcl_count),
            'A=M-D\n', 
            'D=M\n', 
            '@R{}\n'.format(retaddr_count),
            'M=D\n',

            # *arg[0] = pop working stack
            '@0\n',
            'AM=M-1\n', 
            'D=M\n', 
            '@2\n', 
            'A=M\n', 
            'M=D\n', 
            
            # SP = arg + 1
            '@2\n', 
            'D=M+1\n', 
            '@0\n', 
            'M=D\n'
            ])

        # Restore pointers 
        sub_from_count = 1
        ptr_count = 4
        return_asm2 = np.array([])

        while sub_from_count <= 4:
            new_array = np.array([
                '@{}\n'.format(sub_from_count), 
                'D=A\n', 
                '@R{}\n'.format(lcl_count), 
                'A=M-D\n',
                'D=M\n', 
                '@{}\n'.format(ptr_count), 
                'M=D\n'
            ])

            return_asm2 = np.concatenate([return_asm2, new_array])

            sub_from_count += 1
            ptr_count -= 1

        return_asm3 = np.array([
            '@R{}\n'.format(retaddr_count), 
            'A=M\n', 
            '0;JMP\n'
        ])

        # lcl_count += 1
        # retaddr_count += 1

        comment = np.array(['//return//\n'])

        return_total = np.concatenate([comment, return_asm1, return_asm2, return_asm3])

    return asmfile.writelines(return_total)

def writecall(command_type, f, n, ret_count, asmfile):
    if command_type == "c_call":

        call1 = np.array([
            # push return-address
            '@ret{}{}\n'.format(f, ret_count), 
            'D=A\n',
            '@0\n', 
            'A=M\n', 
            'M=D\n', 
            '@0\n', 
            'M=M+1\n'
        ])

        ptr_count = 1
        while ptr_count <= 4:
            push_ptr = np.array([
                '@{}\n'.format(ptr_count),
                'D=M\n', 
                '@0\n', 
                'A=M\n', 
                'M=D\n',
                '@0\n',
                'M=M+1\n'
            ])

            call1 = np.concatenate([call1, push_ptr])
            ptr_count += 1

        call2 = np.array([
            # ARG = SP - n - 5
            '@0\n', 
            'D=M\n', 
            '@{}\n'.format(n), 
            'D=D-A\n', 
            '@5\n', 
            'D=D-A\n', 
            '@2\n', 
            'M=D\n',

            # LCL = SP
            '@0\n', 
            'D=M\n', 
            '@1\n', 
            'M=D\n',

            # goto f 
            '@{}\n'.format(f),
            '0;JMP\n',
            
            # label for return-address
            '(ret{}{})\n'.format(f, ret_count)
        ])

        call_total = np.concatenate([call1, call2])
        ret_count += 1
        return asmfile.writelines(call_total), ret_count

def writeinit(asmfile):
    bootstrap = [
        # SP = 256
        '@256\n', 
        'D=A\n', 
        '@0\n', 
        'M=D\n',
    ]

    # call Sys.init
    call1 = np.array([
            # push return-address
            '@retSys.init\n', 
            'D=A\n',
            '@0\n', 
            'A=M\n', 
            'M=D\n', 
            '@0\n', 
            'M=M+1\n'
        ])

    ptr_count = 1
    while ptr_count <= 4:
        push_ptr = np.array([
            '@{}\n'.format(ptr_count),
            'D=M\n', 
            '@0\n', 
            'A=M\n', 
            'M=D\n',
            '@0\n', 
            'M=M+1\n'
            ])

        call1 = np.concatenate([call1, push_ptr])
        ptr_count += 1

    call2 = np.array([
            # ARG = SP - n - 5
                # '@0\n', 
                # 'D=M\n', 
                # '@0\n', 
                # 'D=D+A\n', 
                # '@5\n', 
                # 'D=D-A\n', 
                # '@2\n', 
                # 'M=D\n',

            # LCL = SP
                # '@0\n', 
                # 'D=M\n', 
                # '@1\n', 
                # 'M=D\n',

            # goto f 
                # '@Sys.init\n',
                # '0;JMP\n',
            
            # label for return-address
            '(retSys.init)\n'
        ])

    call_total = np.concatenate([bootstrap, call1, call2])

    return asmfile.writelines(call_total)
####################################### EXECUTION ##############################################

count = 0
main(count)
