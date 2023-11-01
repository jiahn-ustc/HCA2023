'''
    IR <= mem[PC];
    PC <= PC+4
    A <= Reg[IR_rs]
    B <= Reg[IR_rs]
    add rd,rs1,rs2 #x[rd] = x[rs1]+x[rs2]
    addi rd,rs1,imm #x[rd]=x[rs1]+sext(imm)
    lw rd,offset(rs1) 
'''


'''
    a[2] = 1
    for(i =0;i<100;i++)
        a[2] = a[2] + 1
'''

'''
main:
0	addi,x1,x0,2            00200093
4	addi x2,x0,100          06400113
8	addi x3,x0,999          3e700193
Loop:
c	blt x3,x0,end           0201c063
10	slli,x4,x3,2            00219213
14	add x5,x4,x2            002202b3
18	lw x6,0(x5)             0002a303
1c	add x6,x6,x1            00130333
20	sw x6,0(x5)             0062a023
24	addi x3,x3,-1           fff18193
28	jal x7, Loop            fe5ff3ef

end:

main:
	addi,x1,x0,2            
	addi x2,x0,100          
	addi x3,x0,999          
Loop:
	blt x3,x0,end           
	slli,x4,x3,4            
	add x5,x4,x2            
	lw x6,0(x5)             
	add x6,x6,x1            
	sw x6,0(x5)             
	addi x3,x3,-1           
	jal Loop                

end:
'''


class CPU:
    def __init__(self, memory_size=5120):
        self.registers = [0]*32  # register cell 4 byte
        self.pc = 0
        self.memory = [0] * memory_size  # memory cell 1 byte
        self.max_num = 0xffffffff
        self.read_register_num = 0
        self.write_register_num = 0
        self.read_memory_num = 0
        self.write_memory_num= 0
        self.cycles = 0
    
    def reset(self):
        self.read_register_num = 0
        self.write_register_num = 0
        self.read_memory_num = 0
        self.write_memory_num= 0
        self.cycles = 0

    def read_register(self, reg_num):
        self.read_register_num += 1
        return self.registers[reg_num]

    def write_register(self, reg_num, value):
        self.write_register_num += 1
        if reg_num != 0:
            self.registers[reg_num] = value

    def read_memory(self, address):
        self.read_memory_num += 1
        result = 0
        result += (self.memory[address] << 24)
        result += (self.memory[address+1] << 16)
        result += (self.memory[address+2] << 8)
        result += self.memory[address+3]
        return result

    def write_memory(self, address, value):
        self.write_memory_num += 1
        self.memory[address] = (value & 0xFF000000) >> 24
        self.memory[address+1] = (value & 0x00FF0000) >> 16
        self.memory[address+2] = (value & 0x0000FF00) >> 8
        self.memory[address+3] = value & 0x000000FF

    def ALU(self, A, B, opcode):
        if(opcode == "add"):
            r = A + B
        elif(opcode == "sub"):
            r = A - B
        elif(opcode == "slli"):
            r = A << B
        elif(opcode == "blt"):
            result = A - B
            r = (result & 0x80000000) >> 31
            if(r == 1):
                return 1
            else:
                return 0
        else:
            r = 0
            print("cant use ALU")
        r = r & self.max_num  # 删除越位
        return r

    def imm_expand(self, imm, opcode):
        imm_12 = (imm & 0x800) >> 11
        if(opcode == "addi" or opcode == "lw" or opcode == "sw"):
            if(imm_12 == 1):
                imm = imm + (0xfffff << 12)
        elif(opcode == "blt"):
            if(imm_12 == 1):
                imm = imm + (0x7ffff << 12)
        elif(opcode == "jal"):
            imm_20 = (imm & 0x80000) >> 19
            if(imm_20 == 1):
                imm = imm + (0x7ff << 20)
        return imm

    def add(self, rd, rs1, rs2):
        A = self.read_register(rs1)
        B = self.read_register(rs2)
        r = self.ALU(
            A, B, "add")
        WB = r
        self.write_register(rd, WB)
        self.pc += 4

    def addi(self, rd, rs1, imm):
        imm = self.imm_expand(imm, "addi")
        A = self.read_register(rs1)
        B = imm
        r = self.ALU(A, B, "add")
        WB = r
        self.write_register(rd,WB)
        self.pc += 4

    def slli(self, rd, rs1, imm):
        #print("execute slli")
        #print("imm=", imm)
        A = self.read_register(rs1)
        B = imm
        r = self.ALU(A, B, "slli")
        WB = r
        self.write_register(rd,WB)
        #print("4*i=", self.registers[rd])
        self.pc += 4

    def blt(self, rs1, rs2, imm):
        imm = self.imm_expand(imm, "blt")
        A = self.read_register(rs1)
        B = self.read_register(rs2)
        r = self.ALU(A, B, "blt")
        if r == 1:
            self.pc += (imm << 1)
        else:
            self.pc += 4

    def lw(self, rd, rs1, imm):
        imm = self.imm_expand(imm, "lw")
        A = self.read_register(rs1)
        B = imm
        r = self.ALU(A, B, "add")
        WB = self.read_memory(r)
        self.write_register(rd,WB)
        #self.registers[rd] = self.read_memory(r)
        self.pc += 4

    def sw(self, rs2, rs1, imm):
        imm = self.imm_expand(imm, "sw")
        A = self.read_register(rs1)
        B = imm
        r = self.ALU(A,B,"add")
        #address = self.registers[rs1]+imm
        #print("address: ", r)
        #WB = self.read_register(rs2)
        self.write_memory(r, self.read_register(rs2))
        self.pc += 4

    def jal(self, rd, imm):
        #print("jal imm0=", hex(imm))
        imm = self.imm_expand(imm, "jal")
        #print("jal imm=", hex(imm))
        self.write_register(rd,self.pc+4)
        #self.registers[rd] = self.pc + 4
        #print("before self.pc=", self.pc)
        #self.pc = self.pc + (imm<<1)
        self.pc = self.ALU(self.pc, imm << 1, "add")
        #print("after self.pc=", self.pc)
    
    def cpu_print(self):
        print("cycles=", self.cycles)
        print("read_memory_num=",self.read_memory_num)
        print("write_memory_num=",self.write_memory_num)
        print("read_register_num=",self.read_register_num)
        print("write_register_num=",self.write_register_num)

    def run(self):
        self.reset()
        while True:
            
            # 取指
            #print("i=", self.registers[3])
            #print("pc=",self.pc)
            ir = self.read_memory(self.pc)
            if (ir == 0):
                break
            #print("ir=", hex(ir))
            self.cycles += 1
            # 译码
            opcode = ir & 0x7f
            if(opcode == 0b0010011):
                # addi
                funct3 = (ir & 0x7000) >> 12
                if(funct3 == 0b000):
                    #print("addi")
                    rd = (ir & 0xf80) >> 7
                    rs1 = (ir & 0xf8000) >> 15
                    imm = (ir & 0xfff00000) >> 20
                    self.addi(rd, rs1, imm)
                elif(funct3 == 0b001):
                    # slli
                    #print("slli")
                    rd = (ir & 0xf80) >> 7
                    rs1 = (ir & 0xf8000) >> 15
                    imm = (ir & 0x1F00000) >> 20
                    self.slli(rd, rs1, imm)
            elif(opcode == 0b0110011):
                #print("add")
                rd = (ir & 0xf80) >> 7
                rs1 = (ir & 0xf8000) >> 15
                rs2 = (ir & 0x01f00000) >> 20
                self.add(rd, rs1, rs2)
            elif(opcode == 0b1100011):
                # blt
                #print("blt")
                rs2 = (ir & 0x1F00000) >> 20
                rs1 = (ir & 0xF8000) >> 15
                imm_12 = (ir & 0x800000000) >> 31
                imm_11 = (ir & 0x80) >> 7
                imm_10_5 = (ir & 0x7E000000) >> 25
                imm_4_1 = (ir & 0xF00) >> 8
                imm = (imm_12 << 11) + (imm_11 << 10) + \
                    (imm_10_5 << 4) + imm_4_1
                self.blt(rs1, rs2, imm)
            elif(opcode == 0b0000011):
                # lw
                #print("lw")
                rd = (ir & 0xf80) >> 7
                rs1 = (ir & 0xF8000) >> 15
                imm = (ir & 0xfff00000) >> 20
                self.lw(rd, rs1, imm)
            elif(opcode == 0b0100011):
                # sw
                #print("sw")
                rs2 = (ir & 0x1F00000) >> 20
                rs1 = (ir & 0xF8000) >> 15
                imm_11_5 = (ir & 0xfe000000) >> 25
                imm_4_0 = (ir & 0xF80) >> 7
                imm = imm_11_5 << 5 + imm_4_0
                self.sw(rs2, rs1, imm)
            elif(opcode == 0b1101111):
                # jal
                #print("jal")
                rd = (ir & 0xf80) >> 7
                imm_20 = (ir & 0x80000000) >> 31
                imm_10_1 = (ir & 0x7FE00000) >> 21
                imm_11 = (ir & 0x100000) >> 20
                imm_19_12 = (ir & 0xFF000) >> 12
                # print("imm_20=",imm_20)
                # print("imm_10_1=",imm_10_1)
                # print("imm_11=",imm_11)
                # print("imm_19_12=",imm_19_12)
                imm = (imm_20 << 19) + (imm_19_12 << 11) + \
                    (imm_11 << 10) + imm_10_1
                #print("decode imm=",hex(imm))
                self.jal(rd, imm)

        # 执行


if __name__ == "__main__":
    instructions = [0x00200093, 0x06400113, 0x3e700193, 0x0201c063, 0x00219213,
                    0x002202b3, 0x0002a303, 0x00130333, 0x0062a023, 0xfff18193, 0xfe5ff3ef]

    print(type(instructions[0]))
    print(instructions[9])
    cpu = CPU()
    for i in range(len(instructions)):
        cpu.write_memory(4*i, instructions[i])
    # print(cpu.memory)
    cpu.run()
    print(cpu.memory)
    # for i in range(100, 100+1000):
    #     print(cpu.memory[i])
    cpu.cpu_print()
