# Loop: fld   f0,0(x1)  //f0=array element
#   fadd.d  f4,f0,f2  //add scalar in f2
#   fsd   f4,0(x1)  //store result
#   addi   x1,x1,8   //decrement pointer
#          //8 bytes (per DW)
#   bne   x1,x2,Loop //branch x1 != x2 

from prettytable import PrettyTable
import numpy as np

class table_entry():
    def __init__(self,clk,ir):
        self.clk = clk
        self.ir = ir


class Loop_Execution():
    def __init__(self,instructions):
        self.instructions = instructions
        self.cycle = 0
        self.table = []
        self.wait_cycles = 0
        length = len(instructions)
        self.latency_matrix = np.zeros((length+1,length+1),dtype = np.int32)
        self.distance_matrix = np.ones((length,length),dtype = np.int32)
    
    def is_FP_ALU_Op(self,Ir):
        if(Ir[0][0]=='f'):
            op = Ir[0][1:]
            if(op=='add.d'):
                return True
        return False
    
    def is_Store_double(self,Ir):
        if(Ir[0][0]=='f'):
            op = Ir[0][1:]
            if(op=='sd'):
                return True
        return False
    
    def is_Load_double(self,Ir):
        if(Ir[0][0]=='f'):
            op = Ir[0][1:]
            if(op=='ld'):
                return True
        return False
    
    def is_Integer_Op(self,Ir):
        if(Ir[0][0]!='f'):
            op = Ir[0]
            if op=='add' or op=='addi':
                return True
        return False

    def table_print(self):
        tb = PrettyTable()
        tb.field_names=["clk","ir"]
        for i in range(len(self.table)):
            tb.add_row([self.table[i].clk,self.table[i].ir])
        print(tb)
    
    def run(self):
        for i in range(len(self.instructions)):
            ir1 = self.instructions[i]
            if ir1[0]=="bne" and i==(len(self.instructions)-1) :
                self.latency_matrix[i][i+1]=1
            for j in range(i+1,len(self.instructions)):
                ir2 = self.instructions[j]
                print("ir1:",ir1)
                print("ir2:",ir2)
                if self.is_FP_ALU_Op(ir1):
                    if self.is_FP_ALU_Op(ir2):
                        self.latency_matrix[i][j] = 3
                        print('3')
                    elif self.is_Store_double(ir2):
                        self.latency_matrix[i][j] =2
                        print('2')
                elif self.is_Load_double(ir1):
                    if self.is_FP_ALU_Op(ir2):
                        self.latency_matrix[i][j]=1
                        print('1')
                elif self.is_Integer_Op(ir1):
                    if ir2[0]=="bne":
                        if ir1[1]==ir2[1] or ir1[1] == ir2[2]:
                            self.latency_matrix[i][j]=1
                            print('1')
                
        for i in range(len(self.instructions)):
            distance = 0
            for j in range(i+1,len(self.instructions)):
                distance += (1+self.latency_matrix[j-1][j])
                if distance <= self.latency_matrix[i][j]:
                    self.latency_matrix[i][i+1] += (self.latency_matrix[i][j]-distance+1)
                    distance += (self.latency_matrix[i][j]-distance+1)
        print("latency_matrix:",self.latency_matrix)
        clock = 0
        for i in range(len(self.instructions)):
            ir = self.instructions[i]
            clock += 1
            self.table.append(table_entry(clock,ir))
            for j in range(self.latency_matrix[i,i+1]):
                clock += 1
                self.table.append(table_entry(clock,"stall"))

        self.table_print()
        

        
            


instructions_unscheduled = [["fld","f0","0","x1"],["fadd.d","f4","f0","f2"],
                            ["fsd","f4","0","x1"],["addi","x1","x1","8"],
                            ["bne","x1","x2","Loop"]]
instructions_scheduled = [["fld","f0","0","x1"],["addi","x1","x1","8"],
                        ["fadd.d","f4","f0","f2"],["bne","x1","x2","Loop"],
                            ["fsd","f4","0","x1"]]

# print(instructions_unscheduled)
# print(instructions_scheduled)
loop_execution = Loop_Execution(instructions_unscheduled)
loop_execution.run()