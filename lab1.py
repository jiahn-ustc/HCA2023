class Registers:
    def __init__(self,n,size):
        self.nums = n
        self.size = size
        self.files = []
        for i in range(self.nums):
            self.files.append(0)
        
    def read(self,i):
        if(i<0 or i>=self.nums):
            print("i is not valid")
        else:
            return hex(self.files[i])
    def write(self,i,data):
        if(data>=0 and data <= 2**32-1):
            self.files[i]=data

class Memory:
    def __init__(self,n,size):
        self.files = {}
        self.address_size = n
        self.cell_size = size
        for i in range(10):
            self.files[i]=i
    def read(self,address):
        if address in self.files.keys():
            return hex(self.files[address])
        else:
            return 0
    def write(self,address,data):
        if (data>=0 and data<=2**8-1):
            self.files[address]=data

class Simulator:
    def __init__(self,registers,memory):
        self.registers = registers
        self.memory = memory
    def load(self,reg_index,memory_index):
        # 使用小端存储
        result = 0
        for i in range(4):
            result += self.memory.files[memory_index+i]*(2**(8*(3-i)))
        self.registers.files[reg_index]=result
    def add(self,reg_dest,reg_src1,reg_src2):
        result = self.registers.files[reg_src1] + self.registers.files[reg_src2]
        if result>= 2**self.registers.size:
            self.registers.files[reg_dest] = result - 2**self.registers.size
        else:
            self.registers.files[reg_dest] = result
    def save(self,reg_src,mem_dest):
        result = self.registers.files[reg_src]
        self.memory.files[mem_dest] = (result & 0xFF000000) >> 24
        self.memory.files[mem_dest+1] = (result & 0x00FF0000 )>> 16
        self.memory.files[mem_dest+2] = (result & 0x0000FF00) >> 8
        self.memory.files[mem_dest+3] = result & 0x000000FF
    def run(self,instructions):
        print("Memory:",self.memory.files,"other data of any address is 0")
        for instruction in instructions:
            operation = instruction.strip().split(' ')[0]
            args = instruction.strip().split(' ')[1]
            print(f"\nExecute:{instruction}")
            print("Before:")
            if operation =="Load":
                print("Registers:",self.registers.files)
                reg_index = int(args.split(',')[0][1:])
                memory_index = int(args.split(',')[1][1:])
                self.load(reg_index,memory_index)
                print("After:")
                print("Registers:",self.registers.files)
            elif operation == "Add":
                print("Registers:",self.registers.files)
                reg_dest= int(args.split(',')[0][1:])
                reg_src1=int(args.split(',')[1][1:])
                reg_src2 = int(args.split(',')[2][1:])
                self.add(reg_dest,reg_src1,reg_src2)
                print("After:")
                print("Registers:",self.registers.files)
            elif operation == "Store":
                print("Memory:",self.memory.files,"other data of any address is 0")
                reg_src=int(args.split(',')[0][1:])
                mem_dest = int(args.split(',')[1][1:])
                self.save(reg_src,mem_dest)
                print("After:")
                print("Memory:",self.memory.files,"other data of any address is 0")
            else:
                print(f"Unsupported operation: {operation}")


instructions= ["Load r1,#0","Load r2,#1","Add r3,r1,r2","Store r3,#3"]


memory = Memory(32,8)
registers = Registers(32,32)
sim = Simulator(registers,memory)
sim.run(instructions)


