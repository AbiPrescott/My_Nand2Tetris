import os
import sys
import numpy as np

# SEQUENCE:
# - open folder
# - filter out .vm files
# - make new VM file named folder_name.vm
# - create folder_name.asm
# - write bootsrap code into ASM file
# - read one line at a time (line[count])
# - unless comment, split instruction into seperate words
# - identlify the opcode and 2 arguments
# - write the ASM translation of line into folder_name.asm
# - increment counter
# - repeat until EOF


def main(count):
    # initialise counters needed for functions
    eq_count = 0
    gt_count = 0
    lt_count = 0
    ret_count = 0

    # create new VM file, separate lines in VM file, create ASM file, write bootstrap code
    full_vmfile, folder = constructor_IN()
    lines, count, file_length = write_newvm(full_vmfile, count)
    asmfile = constructor_OUT(folder)
    write_bootstrap(asmfile)

    while hasmorecommands(count, file_length) == 1:
        # called again becuase need to update count after each line, while there are still more commands
        lines, count, file_length = write_newvm(full_vmfile, count)
        current_line = advance(lines)
        count += 1

        # ignores comments and whitespace and indentifies command_type
        if current_line != "comment":
            commandtype = command_type(current_line[0])
        else:
            continue

        # c_return has no arguments so it's exluded
        if commandtype != "c_return":
            # parses argument 1
            arg_1 = arg1(commandtype, current_line)

            # this section write ASM versions of arithmetic commands.
            # It also keeps track of the count of each condional opcode (ie. lt, eq, gt)
            # in order to have different labels (ie. eq1, eq2, etc.)
            # Otherwise, they would share the same label which disrupts the program flow. See 'write_arithmetic'
            _, eq_count, gt_count, lt_count = write_arithmetic(
                current_line[0], asmfile, eq_count, gt_count, lt_count
            )

        else:
            write_return(asmfile)

        # write branching instructions
        if commandtype in ["c_label", "c_goto", "c_if"]:
            write_branch(commandtype, arg_1, asmfile)

        elif commandtype in ["c_pop", "c_push", "c_function", "c_call"]:
            # parses argument 2
            arg_2 = arg2(current_line)

            if "c_pop" in commandtype or "c_push" in commandtype:
                write_pushpop(commandtype, arg_1, arg_2, asmfile)
            elif "c_function" in commandtype:
                write_function(arg_1, arg_2, asmfile)
            elif "c_call" in commandtype:
                _, ret_count = write_call(arg_1, arg_2, ret_count, asmfile)
        else:
            continue

    asmfile.close


############################# PARSER ################################

# - opens input folder
# - selects only the .vm files
# - places them in full_vmfile.vm


def constructor_IN():
    folder = sys.argv[1]
    full_vmfilename = "full_vmfile.vm"
    full_vmfile = open(full_vmfilename, "x")
    executed = []

    files = os.listdir(folder)
    vmfiles = []

    # filter in all the .vm files in vmfiles
    for file in files:
        if file.endswith(".vm"):
            vmfiles.append(file)

    # make sure Sys.vm is the first function in file
    if "Sys.vm" in vmfiles:
        index = vmfiles.index("Sys.vm")
        vmfiles[0], vmfiles[index] = vmfiles[index], vmfiles[0]

    # add lines from each .vm file to full_vmfile.vm
    for vmfile in vmfiles:
        vmdir = folder + "/" + vmfile
        vmfile_opened = open(vmdir, "r")
        vmfile_lines = vmfile_opened.readlines()
        for line in vmfile_lines:
            full_vmfile.writelines(line)

    return full_vmfilename, folder


# - puts lines in full_vmfile.vm into array 'lines' so that it can be indexed
# - returns lenth of full_vmfile.vm to identify EOF
def write_newvm(full_vmfilename, count):
    full_vmfile = open(full_vmfilename, "r")
    lines = full_vmfile.readlines()
    file_length = len(lines)

    full_vmfile.close()

    return lines[count], count, file_length


# creates .asm file
def constructor_OUT(vmfile_name):
    asmfile_name = vmfile_name.split(".")[0] + ".asm"
    asmfile = open(asmfile_name, "x")
    return asmfile


# determines whether has more commands or not
def hasmorecommands(count, file_length):
    if count < file_length:
        return 1
    else:
        return 0


# holds current line the translator is working on.
# Splits instruction into seperate words
# and returns 'comment' to identify comments so that thay can be ignored in main()
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
def command_type(current_line):

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
    ):
        return "c_arithmetic"

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


########################### CODE WRITER #############################

# writes Bootstrap code starting at RAM[0]. (Bootstrap code is code that calls function Sys.init)
#     SP = 256
#     call Sys.init


def write_bootstrap(asmfile):
    bootstrap = [
        "@256\n",
        "D=A\n",
        "@0\n",
        "M=D\n",
    ]

    # call Sys.init
    call1 = np.array(
        [
            # push return-address
            "@retSys.init\n",
            "D=A\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
    )

    # saves pointer into stack so that it can be restored back in when returned from function
    ptr_count = 1
    while ptr_count <= 4:
        push_ptr = np.array(
            [
                "@{}\n".format(ptr_count),
                "D=M\n",
                "@0\n",
                "A=M\n",
                "M=D\n",
                "@0\n",
                "M=M+1\n",
            ]
        )

        call1 = np.concatenate([call1, push_ptr])
        ptr_count += 1

    call2 = np.array(["(retSys.init)\n"])

    call_total = np.concatenate([bootstrap, call1, call2])

    return asmfile.writelines(call_total)


# translates arithmetic to ASM
def write_arithmetic(current_line, asmfile, eq_count, gt_count, lt_count):

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
def write_pushpop(commandtype, arg_1, arg_2, asmfile):
    # these pointers are constants. LCL and ARG can vary, so no declared here
    temp = 5
    ptr = 3
    static = 16

    # PUSH TRANSLATIONS
    if commandtype == "c_push" and arg_1 == "constant":
        push_constant = [
            "@{}\n".format(arg_2),
            "D=A\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_constant)

    elif commandtype == "c_push" and arg_1 == "local":
        push_local = [
            "@1\n",
            "D=M\n",
            "@{}\n".format(arg_2),
            "A=D+A\n",
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_local)

    elif commandtype == "c_push" and arg_1 == "argument":
        push_argument = [
            "@2\n",
            "D=M\n",
            "@{}\n".format(arg_2),
            "A=D+A\n",
            "D=M\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
        asmfile.writelines(push_argument)

    elif commandtype == "c_push" and arg_1 == "this":
        push_this = [
            "@{}\n".format(arg_2),
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

    elif commandtype == "c_push" and arg_1 == "that":
        push_that = [
            "@{}\n".format(arg_2),
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

    elif commandtype == "c_push" and arg_1 == "temp":
        dest = temp + int(arg_2)
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

    elif commandtype == "c_push" and arg_1 == "pointer":
        dest = ptr + int(arg_2)
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

    elif commandtype == "c_push" and arg_1 == "static":
        dest = static + int(arg_2)
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
    elif commandtype == "c_pop" and arg_1 == "local":
        # dest = lcl + int(arg2)
        pop_local = [
            "@{}\n".format(arg_2),
            "D=A\n",
            "@1\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@1\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg_2),
            "D=A\n",
            "@1\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_local)

    elif commandtype == "c_pop" and arg_1 == "argument":
        pop_argument = [
            "@{}\n".format(arg_2),
            "D=A\n",
            "@2\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@2\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg_2),
            "D=A\n",
            "@2\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_argument)

    elif commandtype == "c_pop" and arg_1 == "this":
        pop_this = [
            "@{}\n".format(arg_2),
            "D=A\n",
            "@R3\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@R3\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg_2),
            "D=A\n",
            "@R3\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_this)

    elif commandtype == "c_pop" and arg_1 == "that":
        pop_that = [
            "@{}\n".format(arg_2),
            "D=A\n",
            "@R4\n",
            "AM=M+D\n",
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@R4\n",
            "A=M\n",
            "M=D\n",
            "@{}\n".format(arg_2),
            "D=A\n",
            "@R4\n",
            "AM=M-D\n",
        ]
        asmfile.writelines(pop_that)

    elif commandtype == "c_pop" and arg_1 == "temp":
        dest = temp + int(arg_2)
        pop_temp = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_temp)

    elif commandtype == "c_pop" and arg_1 == "pointer":
        dest = ptr + int(arg2)
        pop_pointer = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_pointer)

    elif commandtype == "c_pop" and arg_1 == "static":
        dest = static + int(arg_2)
        pop_static = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(dest), "M=D\n"]
        asmfile.writelines(pop_static)

    return asmfile


def write_branch(commandtype, arg_1, asmfile):

    if commandtype == "c_label":
        label_asm = ["({})\n".format(arg_1)]
        asmfile.writelines(label_asm)
    elif commandtype == "c_goto":
        goto_asm = ["@{}\n".format(arg_1), "0;JMP\n"]
        asmfile.writelines(goto_asm)
    elif commandtype == "c_if":
        if_asm = ["@0\n", "AM=M-1\n", "D=M\n", "@{}\n".format(arg_1), "D;JNE\n"]
        asmfile.writelines(if_asm)

    return asmfile


def write_function(f_name, arg_num, asmfile):
    function_asm = [
        "({})\n".format(f_name),
        "@{}\n".format(arg_num),
        "D=A\n",
        "@END{}\n".format(f_name),
        "D;JEQ\n",
        "({}init_0)\n".format(f_name),
        "@0\n",
        "A=M\n",
        "M=0\n",
        "@0\n",
        "M=M+1\n",
        "D=D-1\n",
        "@{}init_0\n".format(f_name),
        "D;JGT\n" "(END{})\n".format(f_name),
    ]
    return asmfile.writelines(function_asm)


def write_return(asmfile):
    lcl_count = 13
    retaddr_count = 14

    return_asm1 = np.array(
        [
            # endframe = lcl
            "@1\n",
            "D=M\n",
            "@R{}\n".format(lcl_count),
            "M=D\n",
            # retaddr = *(endframe - 5)
            "@5\n",
            "D=A\n",
            "@R{}\n".format(lcl_count),
            "A=M-D\n",
            "D=M\n",
            "@R{}\n".format(retaddr_count),
            "M=D\n",
            # *arg[0] = pop working stack
            "@0\n",
            "AM=M-1\n",
            "D=M\n",
            "@2\n",
            "A=M\n",
            "M=D\n",
            # SP = arg + 1
            "@2\n",
            "D=M+1\n",
            "@0\n",
            "M=D\n",
        ]
    )

    # Restore pointers
    sub_from_count = 1
    ptr_count = 4
    return_asm2 = np.array([])

    while sub_from_count <= 4:
        new_array = np.array(
            [
                "@{}\n".format(sub_from_count),
                "D=A\n",
                "@R{}\n".format(lcl_count),
                "A=M-D\n",
                "D=M\n",
                "@{}\n".format(ptr_count),
                "M=D\n",
            ]
        )

        return_asm2 = np.concatenate([return_asm2, new_array])

        sub_from_count += 1
        ptr_count -= 1

    return_asm3 = np.array(["@R{}\n".format(retaddr_count), "A=M\n", "0;JMP\n"])

    return_total = np.concatenate([return_asm1, return_asm2, return_asm3])

    return asmfile.writelines(return_total)


def write_call(f, n, ret_count, asmfile):

    call1 = np.array(
        [
            # push return-address
            "@ret{}{}\n".format(f, ret_count),
            "D=A\n",
            "@0\n",
            "A=M\n",
            "M=D\n",
            "@0\n",
            "M=M+1\n",
        ]
    )

    # saves pointer into stack so that it can be restored back in when returned from function
    ptr_count = 1
    while ptr_count <= 4:
        push_ptr = np.array(
            [
                "@{}\n".format(ptr_count),
                "D=M\n",
                "@0\n",
                "A=M\n",
                "M=D\n",
                "@0\n",
                "M=M+1\n",
            ]
        )

        call1 = np.concatenate([call1, push_ptr])
        ptr_count += 1

    call2 = np.array(
        [
            # ARG = SP - n - 5
            "@0\n",
            "D=M\n",
            "@{}\n".format(n),
            "D=D-A\n",
            "@5\n",
            "D=D-A\n",
            "@2\n",
            "M=D\n",
            # LCL = SP
            "@0\n",
            "D=M\n",
            "@1\n",
            "M=D\n",
            # goto f
            "@{}\n".format(f),
            "0;JMP\n",
            # label for return-address
            "(ret{}{})\n".format(f, ret_count),
        ]
    )

    call_total = np.concatenate([call1, call2])
    ret_count += 1
    return asmfile.writelines(call_total), ret_count


####################################### EXECUTION ##############################################

count = 0
main(count)
