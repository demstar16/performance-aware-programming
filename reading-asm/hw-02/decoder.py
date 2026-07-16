import sys

WORD_REGISTERS = {
    "000": "ax",
    "001": "cx",
    "010": "dx",
    "011": "bx",
    "100": "sp",
    "101": "bp",
    "110": "si",
    "111": "di",
}
BYTE_REGISTERS = {
    "000": "al",
    "001": "cl",
    "010": "dl",
    "011": "bl",
    "100": "ah",
    "101": "ch",
    "110": "dh",
    "111": "bh",
}
RM_00 = {
    "000": "bx + si",
    "001": "bx + di",
    "010": "bp + si",
    "011": "bp + di",
    "100": "si",
    "101": "di",
    "110": "bp",
    "111": "bx",
}
RM_01 = {
    "000": "bx + si + disp8",
    "001": "bx + di + disp8",
    "010": "bp + si + disp8",
    "011": "bp + di + disp8",
    "100": "si + disp8",
    "101": "di + disp8",
    "110": "bp + disp8",
    "111": "bx + disp8",
}
RM_10 = {
    "000": "bx + si + disp16",
    "001": "bx + di + disp16",
    "010": "bp + si + disp16",
    "011": "bp + di + disp16",
    "100": "si + disp16",
    "101": "di + disp16",
    "110": "bp + disp16",
    "111": "bx + disp16",
}


def decode_rm(data, pos, mod, rm, w):
    if mod == "00":
        if rm == "110":
            displacement = data[pos + 1] + (data[pos + 2] << 8)
            rmName = f"[{displacement}]"
            consumedBytes = 2
            return rmName, consumedBytes
        else:
            rmName = f"[{RM_00[rm]}]"
            consumedBytes = 0
            return rmName, consumedBytes
    elif mod == "01":
        displacement = data[pos + 1]
        if displacement > 127:
            displacement -= 256
        if displacement == 0 and rm == "110":
            rmName = "[bp]"  # the [bp] special case
        else:
            sign = "+" if displacement >= 0 else "-"
            rmName = f"[{RM_00[rm]} {sign} {abs(displacement)}]"
        return rmName, 1
    elif mod == "10":
        displacement = data[pos + 1] + (data[pos + 2] << 8)
        if displacement > 32767:
            displacement -= 65536
        sign = "+" if displacement >= 0 else "-"
        rmName = f"[{RM_00[rm]} {sign} {abs(displacement)}]"
        return rmName, 2
    elif mod == "11":
        rmName = BYTE_REGISTERS[rm] if w == "0" else WORD_REGISTERS[rm]
        consumedBytes = 0
        return rmName, consumedBytes
    else:
        raise ValueError(f"Invalid mod value at position {pos}: {mod}")


def decode_mov_imm_to_reg(data, pos):
    firstByte = format(data[pos], "08b")
    w = firstByte[4]
    register = firstByte[5:8]
    if w == "0":
        regName = BYTE_REGISTERS[register]
        immediateValue = data[pos + 1]
        return f"mov {regName}, {immediateValue}", 2
    else:
        regName = WORD_REGISTERS[register]
        immediateValue = data[pos + 1] + (data[pos + 2] << 8)
        return f"mov {regName}, {immediateValue}", 3


def decode_mov_imm_to_rm(data, pos):
    firstByte = format(data[pos], "08b")
    w = firstByte[7]
    secondByte = format(data[pos + 1], "08b")
    mod, rm = secondByte[:2], secondByte[5:8]
    rmName, displacementBytes = decode_rm(data, pos + 1, mod, rm, w)
    immediatePos = pos + 2 + displacementBytes

    if w == "0":
        immediateValue = data[immediatePos]
        return f"mov {rmName}, byte {immediateValue}", 2 + displacementBytes + 1
    else:
        immediateValue = data[immediatePos] + (data[immediatePos + 1] << 8)
        return f"mov {rmName}, word {immediateValue}", 2 + displacementBytes + 2


def decode_mov_reg_to_rm(data, pos):
    firstByte = format(data[pos], "08b")
    d, w = firstByte[6], firstByte[7]
    secondByte = format(data[pos + 1], "08b")
    mod, reg, rm = secondByte[:2], secondByte[2:5], secondByte[5:8]

    regName = BYTE_REGISTERS[reg] if w == "0" else WORD_REGISTERS[reg]
    rmName, displacementBytes = decode_rm(data, pos + 1, mod, rm, w)

    if d == "0":
        return f"mov {rmName}, {regName}", 2 + displacementBytes
    else:
        return f"mov {regName}, {rmName}", 2 + displacementBytes


def decode_mov_mem_to_acc(data, pos):
    w = format(data[pos], "08b")[7]
    addr = data[pos + 1] + (data[pos + 2] << 8)
    reg = "al" if w == "0" else "ax"
    return f"mov {reg}, [{addr}]", 3


def decode_mov_acc_to_mem(data, pos):
    w = format(data[pos], "08b")[7]
    addr = data[pos + 1] + (data[pos + 2] << 8)
    reg = "al" if w == "0" else "ax"
    return f"mov [{addr}], {reg}", 3


def decode_instruction(data, pos):
    firstByte = format(data[pos], "08b")
    if firstByte[:7] == "1010000":
        return decode_mov_mem_to_acc(data, pos)
    elif firstByte[:7] == "1010001":
        return decode_mov_acc_to_mem(data, pos)
    elif firstByte[:7] == "1100011":
        return decode_mov_imm_to_rm(data, pos)
    elif firstByte[:6] == "100010":
        return decode_mov_reg_to_rm(data, pos)
    elif firstByte[:4] == "1011":
        return decode_mov_imm_to_reg(data, pos)
    else:
        raise ValueError(f"Unknown instruction at position {pos}: {firstByte}")


def decoder(binary_file):
    with open(binary_file, "rb") as f:
        binary_data = f.read()

    lines = ["bits 16"]
    pos = 0
    while pos < len(binary_data):
        asm, consumed_bytes = decode_instruction(binary_data, pos)
        lines.append(asm)
        pos += consumed_bytes
    return "\n".join(lines)


if __name__ == "__main__":
    print(decoder(sys.argv[1]))
