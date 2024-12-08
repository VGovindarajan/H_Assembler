import sys
from typing import List

def get_initial_symbol_table() ->dict:
    symbol_table = {}

    #Registers
    symbol_table['R0']=0
    symbol_table['R1']=1
    symbol_table['R2']=2
    symbol_table['R3']=3
    symbol_table['R4']=4
    symbol_table['R5']=5
    symbol_table['R6']=6
    symbol_table['R7']=7
    symbol_table['R8'] = 8
    symbol_table['R9'] = 9
    symbol_table['R10'] = 10
    symbol_table['R11'] = 11
    symbol_table['R12'] = 12
    symbol_table['R13'] = 13
    symbol_table['R14'] = 14
    symbol_table['R15'] = 15

    # Other predefined symbols
    symbol_table['SCREEN'] = 16384
    symbol_table['KBD'] = 24576
    symbol_table['SP'] = 0
    symbol_table['LCL'] = 1
    symbol_table['ARG'] = 2
    symbol_table['THIS'] = 3
    symbol_table['THAT'] = 4

    return symbol_table

def get_num_as_str(num:int, str_len:int)->str:
    bin_str = format(num, 'b')
    while len(bin_str) < str_len:
        bin_str = '0' + bin_str
    return bin_str

def get_destination_dict() -> dict:
    #Destinations
    destinations = {}
    destinations[''] = 0b000
    destinations['M'] = 0b001
    destinations['D'] = 0b010
    destinations['A'] = 0b100
    return destinations

def get_destination(destination:str) -> str:
    start = 0b000
    if destination is None or len(destination) == 0:
        return get_num_as_str(start, 3)

    dest_dict = get_destination_dict()
    for ch in destination:
        if ch in dest_dict:
            curr = dest_dict[ch]
            start = start | curr
    return get_num_as_str(start, 3)

def get_jump_dict() -> dict:
    #Jumps
    jumps = {}
    jumps[""] = "000"
    jumps['JGT'] = "001"
    jumps['JEQ'] = "010"
    jumps['JGE'] = "011"
    jumps['JLT'] = "100"
    jumps['JNE'] = "101"
    jumps['JLE'] = "110"
    jumps['JMP'] = "111"
    return jumps

def get_jump(jump:str) ->str:
    jump_dict = get_jump_dict()
    return jump_dict[jump.strip()]

def get_comp_dict() ->dict:
    comp = {}
    comp["0"] = "0101010"
    comp["1"] = "0111111"
    comp["-1"] = "0111010"
    comp["D"] = "0001100"
    comp["A"] = "0110000"
    comp["!D"] = "0001101"
    comp["!A"] = "0110001"
    comp["-D"] = "0001111"
    comp["-A"] = "0110011"
    comp["D+1"] = "0011111"
    comp["A+1"] = "0110111"
    comp["D-1"] = "0001110"
    comp["A-1"] = "0110010"
    comp["D+A"] = "0000010"
    comp["A+D"] = "0000010" #Repeat of D+A
    comp["D-A"] = "0010011"
    comp["A-D"] = "0000111"
    comp["D&A"] = "0000000"
    comp["D|A"] = "0010101"

    comp["M"] = "1110000"
    comp["!M"] = "1110001"
    comp["-M"] = "1110011"
    comp["M+1"] = "1110111"
    comp["M-1"] = "1110010"
    comp["D+M"] = "1000010"
    comp["M+D"] = "1000010" # Repeat of D+M
    comp["D-M"] = "1010011"
    comp["M-D"] = "1000111"
    comp["D&M"] = "1000000"
    comp["D|M"] = "1010101"

    return comp

def get_comp(comp:str) ->str:
    comp_dict = get_comp_dict()
    return comp_dict[comp.strip().upper()]

def print_usage():
    print("Usage : python HackAssembler.py xxx.asm. 'xxx.asm' is your input file and should be in the current directory")

def read_all_lines(file_name:str) -> List[str]:
    lines = []
    try:
        with open(file_name, "r") as f:
            lines = f.readlines()
    except:
        print("File {0} not found", file_name)
        print_usage()

    return lines

def write_all_lines(file_name:str, lines:List[str]) -> bool:
    try:
        with open(file_name, "w+") as f: #we are overwriting the existing file ,if any
            f.write('\n'.join(lines))
            return True
    except Exception as e:
        print(f"Not able to write file {0}. Details {1}", file_name, e)
        print_usage()

    return False

def get_parsed_command(line:str) -> str:
    p = ""
    line = line.strip()
    if len(line) == 0:
        return p
    is_prev_char_comment = False
    for ch in line:
        if ch is None or len(ch) == 0:
            continue
        if ch == '/':
            if is_prev_char_comment:
                return  p
            else:
                is_prev_char_comment = True
        if ch != '/':
            is_prev_char_comment = False
            p = p + ch

    return p

def is_integer(num:str)->bool:
    try:
        int(num)
    except ValueError:
        return False
    return True
def convert_to_a_instruction(location:str, symbol_dict:dict)->str:
    address = location
    if location.startswith('@'):
        address = location[1:]
    selected_address = address
    if is_integer(address):
        selected_address = int(selected_address)
    else:
        if address in symbol_dict:
            selected_address = symbol_dict[address]
        else:
            selected_address = int(selected_address)
    return '0' + get_num_as_str(selected_address, 15)

def convert_to_c_instruction(command:str, symbol_dict:dict) -> str:
    dest_code = ""
    comp_code = ""
    jump_code = ""
    reminder = command
    if '=' in reminder:
        dest_code = reminder[0:reminder.index('=')]
        reminder = reminder[reminder.index('=')+1:]
    if ';' in reminder:
        jump_code = reminder[reminder.index(';')+1:]
        reminder = reminder[:reminder.index(';')]
    comp_code = reminder

    dest = get_destination(dest_code)
    comp = get_comp(comp_code)
    jump = get_jump(jump_code)
    return "111" + comp + dest + jump

def parse_lines(lines:List[str]) -> List[str]:
    symbol_table = get_initial_symbol_table()
    bin_lines = []
    reg_num = 16
    #First pass
    first_pass = []
    for fp in lines:
        parsed_line = get_parsed_command(fp)
        if parsed_line is None or len(parsed_line) == 0:
            continue
        parsed_line = parsed_line.strip()
        if len(parsed_line) > 0:
            if parsed_line.startswith('(') and parsed_line.endswith(')'): #This is a label
                parsed_line = parsed_line[1:-1]
                if parsed_line not in symbol_table:
                    symbol_table[parsed_line] = len(first_pass) #We set the memory location as the next line in first pass
            else:
                first_pass.append(parsed_line)

    #Second pass
    for sp in lines:
        parsed_line = get_parsed_command(sp)
        if parsed_line is None or len(parsed_line) == 0:
            continue
        parsed_line = parsed_line.strip()
        if len(parsed_line) > 0:
            if parsed_line.startswith('(') and parsed_line.endswith(')'):  # This is a label
                continue
        if parsed_line.startswith('@') and (not is_integer(parsed_line[1:])):  # this is an a register
            reg = parsed_line[1:]
            if not reg in symbol_table:
                symbol_table[reg] = reg_num
                reg_num += 1
        #Now convert to A or C instruction
        bin_line = ''
        if parsed_line.startswith('@'):
            bin_line = convert_to_a_instruction(parsed_line, symbol_table)
        else:
            bin_line = convert_to_c_instruction(parsed_line, symbol_table)
        bin_lines.append(bin_line)
    return bin_lines

def generate_output_file_name(input_file_name:str)-> str:
    input_file_name = input_file_name.strip()
    if len(input_file_name) <= 4:
        return "a.hack"
    output_file_name = input_file_name[:-3] + "hack"
    return output_file_name

def run_assembler(input_file_name:str, output_file_name:str)->bool:
    try:
        input_lines = read_all_lines(input_file_name)
        parsed_lines = parse_lines(input_lines)
        write_all_lines(output_file_name, parsed_lines)
        return True
    except Exception as e:
        print("Error : ", e)
    return False


def run_tests():
    adBits = get_destination('AD')
    #print(adBits)
    assert adBits == '110'

    maBits = get_destination('MA')
    #print(maBits)
    assert maBits == '101'

    jmpBits = get_jump("JMP")
    #print(jmpBits)
    assert jmpBits == '111'

    jleBits = get_jump("JLE")
    #print(jleBits)
    assert jleBits == '110'

    dPlus1Bits = get_comp("D+1")
    #print(dPlus1Bits)
    assert dPlus1Bits == '0011111'

    dMinusMBits = get_comp("D-m")
    #print(dMinusMBits)
    assert dMinusMBits == '1010011'


def main():
    l = len(sys.argv)
    if l < 2 :
        print_usage()
        sys.exit(1)

    script_name = sys.argv[0]
    input_file_name = sys.argv[1]
    output_file_name = generate_output_file_name(input_file_name)
    run_assembler(input_file_name, output_file_name)
    print(f"Generated {output_file_name}")

if __name__ == "__main__":
    main()
