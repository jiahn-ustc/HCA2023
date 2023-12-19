'''
两个整形运算ALU，两个浮点运算ALU,二者均是separate的
两个CDB
同时可最多提交两个指令
1 cycle for integer ALU operations
2 cycle for loads
3 cycle for FP add

# LD F0, 0(R1) # 从数组 A 中加载当前元素到寄存器 a0
# ADDD F4, F0, F2 # 将常数 S 加到寄存器 a0 中
# SD F4, 0(R2) # 将结果存回数组 B 中
# DADDUI R1, R1, 1 # 移动到下一个元素的地址，每个元素占 4 字节
# DADDUI R2, R2, 1 # 移动到下一个元素的地址，每个元素占 4 字节
# BNE R1, R3, loop # 如果循环次数不为零，则继续循环
'''
from prettytable import PrettyTable

class reservation_station_item:
    def __init__(self,instruction):
        self.valid = True
        self.occupy_unit = "Null"
        self.Op = instruction[0]
        self.Vj_index = -1
        self.Vk_index = -1
        self.Vj = "Null"
        self.Vk = "Null"
        self.Qj = "Null"
        self.Qk = "Null"
        self.Dest = "Null"

    def flush(self):
        self.valid = False
        self.occupy_unit = "Null"
        self.Op = "Null"
        self.Vj_index = -1
        self.Vk_index = -1
        self.Vj = "Null"
        self.Vk = "Null"
        self.Qj = "Null"
        self.Qk = "Null"
        self.Dest = "Null"
        
    def print_status(self):
        print(f" valid:{self.valid} occupy_unit:{self.occupy_unit} Op:{self.Op} Vj:{self.Vj} Vj_index{self.Vj_index} Vk:{self.Vk} Vk_index{self.Vk_index} Qj:{self.Qj} Qk:{self.Qk} Dest:{self.Dest}")

# class unit_status():
#     def __init__(self):
#         self.status = "free"
#         self.occupy_cycle = -1
    
#     def flush(self):
#         self.status = "free"
#         self.occupy_cycle = -1

class rob_status():
    def __init__(self,instruction):
        self.iters = 0
        self.instruction = instruction
        self.State = "Issue"
        self.is_write_CDB_just_now = False
        if instruction[0] == "SD" or instruction[0] == "BNE":
            self.Destination = "Null"
        else:
            self.Destination = instruction[1]
        self.Value = "Null"
        self.issue_cycle = 0
        self.exec_cycle = 0
        self.mem_cycle = 0
        self.write_CDB_cycle = 0
        # self.commit_cycle = 0
    def print_status(self):
        print(f"{self.instruction} {self.State} {self.Destination} {self.Value}")

class reg_result_status_item():
    def __init__(self,rob_index):
        self.Reorder = rob_index
        self.Busy = True
    def flush(self):
        self.Reorder = -1
        self.Busy = False
    def print_status(self):
        print(f"Reorder:{self.Reorder} Busy:{self.Busy}")

class Tomasulo:
    def __init__(self):
        self.units = {"Integer1": ["free",0], "Integer2": ["free",0],"FP1": ["free",0],"FP2": ["free",0]}
        self.ex_cycles = {"Integer": 1, "FP": 3}
        self.instructions = []
        self.reservation_station=[]
        self.reg_result_status = {}
        self.rob = []
        self.print_table = []
        self.head = 0
        self.tail = -1
        self.clock = 0
        self.iters = 0
    
    def load_irs(self,instructions):
        self.instructions = instructions
    
    def get_reservation_station_item(self,new_ir):
        new_ir_item = reservation_station_item(new_ir)
        #非SD和BNE指令更新reg_result_status
        # if new_ir1[0]!="BNE" and new_ir1[0]!="SD":
        #     self.reg_result_status[new_ir1[1]]=reg_result_status_item(self.tail)
        if new_ir[0]=="SD":
            new_ir_item.Vj = new_ir[1]
            new_ir_item.Vk = new_ir[3]
            if new_ir[1] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[1]].Busy:
                new_ir_item.Qj = "Yes"
            else:
                new_ir_item.Qj = "No"
                new_ir_item.Vj_index = self.reg_result_status[new_ir[1]].Reorder
            if new_ir[3] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[3]].Busy:
                new_ir_item.Qk = "Yes"
            else:
                new_ir_item.Qk = "No"
                new_ir_item.Vk_index = self.reg_result_status[new_ir[3]].Reorder
        elif new_ir[0]=="L.D":
            new_ir_item.Vk = new_ir[3]
            if new_ir[3] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[3]].Busy:
                new_ir_item.Qk = "Yes"
            else:
                new_ir_item.Qk = "No"
                new_ir_item.Vk_index = self.reg_result_status[new_ir[3]].Reorder
            self.reg_result_status[new_ir[1]]=reg_result_status_item(self.tail)
            new_ir_item.Dest = self.reg_result_status[new_ir[1]].Reorder

        elif new_ir[0]=="ADD.D":
            #print('-----------debug----------')
            #self.reg_result_status["F0"].print_status()
            new_ir_item.Vj = new_ir[2]
            new_ir_item.Vk = new_ir[3]
            if new_ir[2] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[2]].Busy:
                new_ir_item.Qj = "Yes"
            else:
                new_ir_item.Qj = "No"
                #print('new_ir[2]:',new_ir[2])
                new_ir_item.Vj_index = self.reg_result_status[new_ir[2]].Reorder
            if new_ir[3] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[3]].Busy:
                new_ir_item.Qk = "Yes"
            else:
                new_ir_item.Qk = "No"
                new_ir_item.Vk_index = self.reg_result_status[new_ir[3]].Reorder
            self.reg_result_status[new_ir[1]]=reg_result_status_item(self.tail)
            new_ir_item.Dest = self.reg_result_status[new_ir[1]].Reorder
        elif new_ir[0]=="DADDUI":
            new_ir_item.Vj = new_ir[2]
            
            if new_ir[2] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[2]].Busy:
                new_ir_item.Qj = "Yes"
            else:
                new_ir_item.Qj = "No"
                new_ir_item.Vj_index = self.reg_result_status[new_ir[2]].Reorder
            self.reg_result_status[new_ir[1]]=reg_result_status_item(self.tail)
            new_ir_item.Dest = self.reg_result_status[new_ir[1]].Reorder
        elif new_ir[0]=="BNE":
            new_ir_item.Vj = new_ir[1]
            new_ir_item.Vk = new_ir[2]

            if new_ir[1] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[1]].Busy:
                new_ir_item.Qj = "Yes"
            else:
                new_ir_item.Qj = "No"
                new_ir_item.Vj_index = self.reg_result_status[new_ir[1]].Reorder
            if new_ir[2] not in self.reg_result_status.keys() or not self.reg_result_status[new_ir[2]].Busy:
                new_ir_item.Qk = "Yes"
            else:
                new_ir_item.Qk = "No"
                new_ir_item.Vk_index = self.reg_result_status[new_ir[2]].Reorder

        return new_ir_item

    def print_status(self):
        print('\n')
        print("clock=", self.clock)
        print("rob:")
        for i in range(len(self.rob)):
            self.rob[i][1].print_status()
        print("reservation station:")
        for i in range(len(self.reservation_station)):
            self.reservation_station[i].print_status()
        print("register result status:")
        for key in self.reg_result_status.keys():
            print("key:",key)
            self.reg_result_status[key].print_status()
        # print('unit status:')
        # print(f"Integer1:{self.units["Integer1"]} Integer2:{self.units["Integer2"]} FP1:{self.units["FP1"]} FP2:{self.units["FP2"]}")
            
            # print("Reorder:",self.reg_result_status[key].Reorder,"Busy:",self.reg_result_status[key].Busy)
        print('\n')
    
    def print_result(self):
        tb_ir = PrettyTable()
        tb_ir.field_names=["ir","Issue","Exec","Mem","Write CDB"]
        max_cycle = 0
        for i in range(len(self.rob)):
            rob_item = self.rob[i][1]
            ir = rob_item.instruction

            Issue = rob_item.issue_cycle
            if Issue>max_cycle:
                max_cycle = Issue
            Exec = rob_item.exec_cycle
            if Exec>max_cycle:
                max_cycle = Exec
            if Exec==0:
                Exec = ''
            Mem = rob_item.mem_cycle
            if Mem>max_cycle:
                max_cycle = Mem
            if Mem==0:
                Mem =''
            Write_CDB = rob_item.write_CDB_cycle
            if Write_CDB>max_cycle:
                max_cycle = Write_CDB
            if Write_CDB==0:
                Write_CDB = ''
            # Commit = rob_item.commit_cycle
            
            tb_ir.add_row([ir,Issue,Exec,Mem,Write_CDB])
        print(tb_ir)

        tb_usage = PrettyTable()
        tb_usage.field_names=["Clock","Integer ALU","FP ALU","Data Cache","CDB"]
        usage_table = []
        for i in range(max_cycle):
            usage_table_item = [i+1,'','','','']
            usage_table.append(usage_table_item)
        for i in range(len(self.rob)):
            rob_item = self.rob[i][1]
            ir = rob_item.instruction
            Issue = rob_item.issue_cycle
            Exec = rob_item.exec_cycle
            iters = rob_item.iters
            if rob_item.instruction[0]=="ADD.D":
                usage_table[Exec-1][2] += str(iters)+"/ADD.D "
                usage_table[Exec][2] += str(iters)+"/ADD.D "
                usage_table[Exec+1][2] += str(iters)+"/ADD.D "
            else:
                usage_table[Exec-1][1] += str(iters)+"/"+ir[0]+" "
            
            Mem = rob_item.mem_cycle
            # print('Mem:',Mem)
            if Mem != 0:
                usage_table[Mem-1][3] += str(iters)+"/"+ir[0]+" "
            
            Write_CDB = rob_item.write_CDB_cycle

            if Write_CDB != 0:
                usage_table[Write_CDB-1][4] += str(iters)+"/"+ir[0]+" "
            # Commit = rob_item.commit_cycle
        for i in range(len(usage_table)):
            tb_usage.add_row(usage_table[i])
            #tb_ir.add_row([ir,Issue,Exec,Mem,Write_CDB])

        print(tb_usage)


    def get_free_int_unit(self):
        if self.units["Integer1"][0]=="free":
            return "Integer1"
        elif self.units["Integer2"][0]=="free":
            return "Integer2"
        return "Null"

    def get_free_fp_unit(self):
        if self.units["FP1"][0]=="free":
            return "FP1"
        elif self.units["FP2"][0]=="free":
            return "FP2"
        return "Null"
    
    def is_all_commit(self):
        for i in range(len(self.rob)):
            rob_item = self.rob[i][1]
            if rob_item.State != "Wait Commit":
                return False
        return True

    def update(self,new_ir1,new_ir2):
        self.clock += 1

        # update old ir status
        for i in range(len(self.reservation_station)):
            rs_item = self.reservation_station[i]
            if not rs_item.valid:
                continue
            rob_item = self.rob[rs_item.Dest]
            #print("rob_item:",rob_item)

            if rob_item[1].State == "Issue":
                if rs_item.Op =="SD" or rs_item.Op =="L.D":
                    if rs_item.Qk == "Yes":
                        int_unit = self.get_free_int_unit()       
                        if int_unit !="Null":
                            self.units[int_unit][0] = "Busy"
                            self.units[int_unit][1] = 1
                            rob_item[1].State="Exec"
                            rob_item[1].exec_cycle=self.clock
                            rs_item.occupy_unit = int_unit
                # elif rs_item.Op =="L.D":
                #     if rs_item.Qk == "Yes":
                #         int_unit = self.get_free_int_unit()
                #         if int_unit !="Null":
                #             self.units[int_unit][0] = "Busy"
                #             self.units[int_unit][1] = 1
                #             rob_item[1].State="Exec"
                elif rs_item.Op == "DADDUI":
                    if rs_item.Qj == "Yes":
                        int_unit = self.get_free_int_unit()
                        if int_unit !="Null":
                            self.units[int_unit][0] = "Busy"
                            self.units[int_unit][1] = 1
                            rob_item[1].State="Exec"
                            rob_item[1].exec_cycle=self.clock
                            rs_item.occupy_unit = int_unit
                elif rs_item.Op == "ADD.D":
                    if rs_item.Qj == "Yes" and rs_item.Qk == "Yes":
                        FP_unit = self.get_free_fp_unit()
                        if FP_unit !="Null":
                            self.units[FP_unit][0] = "Busy"
                            self.units[FP_unit][1] = 3
                            rob_item[1].exec_cycle=self.clock
                            rob_item[1].State="Exec"
                            rs_item.occupy_unit = FP_unit
                elif rs_item.Op == "BNE":
                    if rs_item.Qj == "Yes" and rs_item.Qk == "Yes":
                        int_unit = self.get_free_fp_unit()
                        if int_unit !="Null":
                            self.units[int_unit][0] = "Busy"
                            self.units[int_unit][1] = 1
                            rob_item[1].exec_cycle=self.clock
                            rob_item[1].State="Exec"
                            rs_item.occupy_unit = int_unit
            elif rob_item[1].State == "Exec":
                if rs_item.Op =="L.D":
                    occupy_unit = rs_item.occupy_unit
                    self.units[occupy_unit][1] -= 1
                    if self.units[occupy_unit][1] == 0:
                        self.units[occupy_unit][0] = "free"
                        rs_item.occupy_unit = "Null"
                        rob_item[1].mem_cycle=self.clock
                        rob_item[1].State = "Mem"
                elif rs_item.Op =="SD" :
                    occupy_unit = rs_item.occupy_unit
                    if occupy_unit != "Null":
                        self.units[occupy_unit][1] -= 1
                        if self.units[occupy_unit][1] == 0:
                            rs_item.occupy_unit = "Null"
                            self.units[occupy_unit][0] = "free"
                    elif rs_item.Qj == "Yes":
                        rob_item[1].mem_cycle=self.clock
                        rob_item[1].State = "Mem"
                elif rs_item.Op == "BNE":
                    occupy_unit = rs_item.occupy_unit
                    self.units[occupy_unit][1] -= 1
                    if self.units[occupy_unit][1] == 0:
                        rs_item.occupy_unit = "Null"
                        self.units[occupy_unit][0] = "free"
                        # rob_item[1].commit_cycle=self.clock
                        rob_item[1].State="Wait Commit"
                        rs_item.valid = False
                elif rs_item.Op == "DADDUI" or rs_item.Op == "ADD.D":
                    occupy_unit = rs_item.occupy_unit
                    self.units[occupy_unit][1] -= 1
                    if self.units[occupy_unit][1] == 0:
                        rs_item.occupy_unit = "Null"
                        self.units[occupy_unit][0] = "free"
                        rob_item[1].write_CDB_cycle=self.clock
                        rob_item[1].State="Write CDB"
                        rob_item[1].is_write_CDB_just_now = True
            elif rob_item[1].State == "Mem":
                if rs_item.Op =="SD":
                    rob_item[1].State="Wait Commit"
                    # rob_item[1].commit_cycle=self.clock
                    rs_item.valid = False
                elif rs_item.Op =="L.D":
                    rob_item[1].State="Write CDB"
                    rob_item[1].write_CDB_cycle=self.clock
                    rob_item[1].is_write_CDB_just_now = True
            elif rob_item[1].State == "Write CDB":
                for index in range(len(self.reservation_station)):
                    rs_item = self.reservation_station[index]
                    if not rs_item.valid:
                        continue
                    #rs_item.print_status()
                    #print("rs_item.Dest:",rs_item.Dest)
                    rob_item = self.rob[rs_item.Dest]
                    if rob_item[1].State == "Write CDB":
                        if False:
                            # print('fake write CDB')
                            rob_item[1].print_status()
                            rob_item[1].is_write_CDB_just_now = False
                        else:
                            # print('real write CDB')
                            # rob_item[1].commit_cycle=self.clock
                            rob_item[1].State = "Wait Commit"
                            rs_item.valid = False
                            if self.reg_result_status[rob_item[1].Destination].Reorder == index:
                                self.reg_result_status[rob_item[1].Destination].flush()
                            for j in range(index+1,len(self.reservation_station)):
                                w_rs_item = self.reservation_station[j]
                                if not w_rs_item.valid:
                                    continue
                                w_rob_item = self.rob[w_rs_item.Dest]
                                # print('-----------debug write cdb---------------')
                                if w_rs_item.Vj == rob_item[1].Destination and w_rs_item.Qj=="No" :
                                    # print(f'index:{index} Vj_index:{w_rs_item.Vj_index}')
                                    if w_rs_item.Vj_index == index:
                                        # print('==')
                                        w_rs_item.Qj = "Yes"
                                if w_rs_item.Vk == rob_item[1].Destination and w_rs_item.Qk=="No" :
                                    # print(f'index:{index} Vk_index:{w_rs_item.Vk_index}')
                                    if w_rs_item.Vk_index == index:
                                        w_rs_item.Qk = "Yes"
        if len(new_ir1)>0:
            # issue new_ir1
            self.tail += 1
            # update rob
            self.rob.append([self.tail,rob_status(new_ir1)])
            self.rob[self.tail][1].issue_cycle = self.clock
            self.rob[self.tail][1].iters = self.iters
            # #非SD和BNE指令更新reg_result_status
            # if new_ir1[0]!="BNE" and new_ir1[0]!="SD":
            #     self.reg_result_status[new_ir1[1]]=reg_result_status_item(self.tail)
            
            # update reservation station
            new_ir1_item = self.get_reservation_station_item(new_ir1)
            if new_ir1[0]=="BNE" or new_ir1[0]=="SD":
                new_ir1_item.Dest = self.tail
            self.reservation_station.append(new_ir1_item)

        # issue new_ir2
        if len(new_ir2)>0:
            self.tail += 1
            #update rob
            self.rob.append([self.tail,rob_status(new_ir2)])
            self.rob[self.tail][1].issue_cycle = self.clock
            self.rob[self.tail][1].iters = self.iters
            # if new_ir2[0]!="BNE" and new_ir2[0]!="SD":
            #     #非SD和BNE指令更新reg_result_status
            #     self.reg_result_status[new_ir2[1]]=reg_result_status_item(self.tail)
            
            new_ir2_item = self.get_reservation_station_item(new_ir2)
            if new_ir2[0]=="BNE" or new_ir2[0]=="SD":
                new_ir2_item.Dest = self.tail    
            self.reservation_station.append(new_ir2_item)
        
        # write CDB
        # for i in range(len(self.reservation_station)):
        #     rs_item = self.reservation_station[i]
        #     if not rs_item.valid:
        #         continue
        #     #rs_item.print_status()
        #     #print("rs_item.Dest:",rs_item.Dest)
        #     rob_item = self.rob[rs_item.Dest]
        #     if rob_item[1].State == "Write CDB":
        #         if False:
        #             print('fake write CDB')
        #             rob_item[1].print_status()
        #             rob_item[1].is_write_CDB_just_now = False
        #         else:
        #             print('real write CDB')
        #             rob_item[1].State = "Commit"
        #             rs_item.valid = False
        #             if self.reg_result_status[rob_item[1].Destination].Reorder == i:
        #                 self.reg_result_status[rob_item[1].Destination].flush()
        #             for j in range(i+1,len(self.reservation_station)):
        #                 w_rs_item = self.reservation_station[j]
        #                 if not w_rs_item.valid:
        #                     continue
        #                 w_rob_item = self.rob[w_rs_item.Dest]
        #                 print('-----------debug write cdb---------------')
        #                 if w_rs_item.Vj == rob_item[1].Destination and w_rs_item.Qj=="No" :
        #                     print(f'i:{i} Vj_index:{w_rs_item.Vj_index}')
        #                     if w_rs_item.Vj_index == i:
        #                         print('==')
        #                         w_rs_item.Qj = "Yes"
        #                 if w_rs_item.Vk == rob_item[1].Destination and w_rs_item.Qk=="No" :
        #                     print(f'i:{i} Vk_index:{w_rs_item.Vk_index}')
        #                     if w_rs_item.Vk_index == i:
        #                         w_rs_item.Qk = "Yes"

        #print_status
        self.print_status()                

    def run(self,instructions):
        self.load_irs(instructions)
        for iters in range(1,4):
            self.iters = iters
            i=0
            while True:
                if i>=len(self.instructions):
                    break
                if i+1<len(self.instructions):
                    new_ir1 = self.instructions[i]
                    new_ir2 = self.instructions[i+1]
                else:
                    new_ir1 = self.instructions[i]
                    new_ir2 = []
                self.update(new_ir1,new_ir2)
                i += 2
        while True:
            if self.is_all_commit():
                break
            else:
                self.update([],[])
        self.print_result()
        


instructions = [["L.D", "F0", "0", "R1"], ["ADD.D", "F4", "F0", "F2"],
                ["SD", "F4", "0", "R2"], ["DADDUI", "R1", "R1", "1"],
                ["DADDUI", "R2", "R2", "1"], ["BNE", "R1", "R3", "Loop"]]

Thomas = Tomasulo()
Thomas.run(instructions)