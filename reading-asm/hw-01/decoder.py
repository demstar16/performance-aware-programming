import sys

WORD_REGISTERS = {
    "000": "ax",
    "001": "cx",
    "010": "dx",
    "011": "bx",
    "100": "sp",
    "101": "bp",
    "110": "si",
    "111": "di"
}

BYTE_REGISTERS = {
    "000": "al",
    "001": "cl",
    "010": "dl",
    "011": "bl",
    "100": "ah",
    "101": "ch",
    "110": "dh",
    "111": "bh"
}

def decode_instruction(first, second):
    first_byte_bin = format(first, '08b')
    second_byte_bin = format(second, '08b')

    opcode = first_byte_bin[0:6]
    d = first_byte_bin[6]
    w = first_byte_bin[7]
    reg = second_byte_bin[2:5]
    rm = second_byte_bin[5:8]
    
    if(opcode == "100010"):
        mnemonic = "mov"
        
    if d == '0':
        dest, src = rm, reg
    else:
        dest, src = reg, rm

    if w == '0':
        return f"{mnemonic} {BYTE_REGISTERS[dest]}, {BYTE_REGISTERS[src]}"
    else:
        return f"{mnemonic} {WORD_REGISTERS[dest]}, {WORD_REGISTERS[src]}"

def decoder (binary_file):
    with open(binary_file, 'rb') as f:
        binary_data = f.read()

    lines = ["bits 16"]
    for pos in range(0, len(binary_data), 2):
        lines.append(decode_instruction(binary_data[pos], binary_data[pos + 1]))
    return "\n".join(lines)

if __name__ == "__main__":
    print(decoder(sys.argv[1]))