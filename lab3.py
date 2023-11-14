from prettytable import PrettyTable

# 创建组件状态的数据结构
class unit_status:
    def __init__(self):
        self.Busy = "No"
        self.Op = "Null"
        self.Fi = "Null"
        self.Fj = "Null"
        self.Fk = "Null"
        self.Qj = "Null"
        self.Qk = "Null"
        self.Rj = "Null"
        self.Rk = "Null"
        self.need_ex_cycle = "Null"

    def flush(self):
        self.Busy = "No"
        self.Op = "Null"
        self.Fi = "Null"
        self.Fj = "Null"
        self.Fk = "Null"
        self.Qj = "Null"
        self.Qk = "Null"
        self.Rj = "Null"
        self.Rk = "Null"
        self.need_ex_cycle = "Null"
    def status_print(self):
        print(f"{self.Busy} {self.Op} {self.Fi} {self.Fj} {self.Fk} {self.Qj} {self.Qk} {self.Rj} {self.Rk}")

# 创建指令状态的数据结构
class ir_status:
    def __init__(self, ir, unit):
        self.ir = ir
        self.unit = unit
        self.status = {
            "Issue": -1,
            "Read_Oper": -1,
            "Exec_Comp": -1,
            "Write_Result": -1
        }


class Scoreboard:

    def __init__(self):
        self.units = {"Integer": 1, "Mul": 2, "Add": 1, "Divide": 1}
        self.ex_cycles = {"Integer": 1, "Add": 2, "Mul": 10, "Divide": 40}
        self.instructions = []

        # 如果没有等待发射的指令并且所有组件都是空闲状态，程序就执行完毕
        self.is_all_units_free = True

        # 用来避免发生WAR相关，同时记录发生WAR相关的指令
        self.is_WB_WAR = False
        self.WAR_index = -1

        # 各个组件的空闲状态
        self.units_free = {
            "Integer": True,
            "Mul1": True,
            "Mul2": True,
            "Add": True,
            "Divide": True
        }
        
        # 每种指令需要用到的组件映射
        self.ir_unit = {
            "L.D": "Integer",
            "MUL.D": "Mul",
            "SUB.D": "Add",
            "ADD.D": "Add",
            "DIV.D": "Divide"
        }

        # 每种指令对应的操作码
        self.ir_op = {
            "L.D": "Load",
            "MUL.D": "Mult",
            "SUB.D": "Sub",
            "ADD.D": "Add",
            "DIV.D": "Div"
        }

        # 记录指令状态
        self.ir_status = []

        #记录功能组件状态
        self.units_status = {
            "Integer": unit_status(),
            "Mul1": unit_status(),
            "Mul2": unit_status(),
            "Add": unit_status(),
            "Divide": unit_status()
        }

        #记录寄存器结果状态
        self.reg_status = {}

    #加载指令
    def load_irs(self, instructions):
        for i in range(len(instructions)):
            ir = instructions[i]
            self.instructions.append(ir)

    #判断是否所有组件均处于空闲状态
    def update_all_units_free(self):
        self.is_all_units_free = True
        for key in self.units_free.keys():
            self.is_all_units_free = self.is_all_units_free & self.units_free[
                key]

    #打印三个表格，使用了PrettyTable库
    def print_status(self,clock):
        #print("***************************************************")
        print("\nclock=",clock)
        # print ir status
        print("ir status:")
        tb_ir = PrettyTable()
        tb_ir.field_names=["ir","Issue","Read Oper","Exec Comp","Write Result"]
        for i in range(len(self.ir_status)):
            ir_status = self.ir_status[i]
            # tb_ir.add_row(self.ir_status[i].ir + self.ir_status[i].status)
            ir = ir_status.ir
            issue = ir_status.status["Issue"]
            read_oper = ir_status.status["Read_Oper"]
            exec_comp = ir_status.status["Exec_Comp"]
            write_result = ir_status.status["Write_Result"]
            tb_ir.add_row([ir,issue,read_oper,exec_comp,write_result])
            # print(f"{ir} {issue} {read_oper} {exec_comp} {write_result}")
        print(tb_ir)
        # print unit status
        print("unit status:")
        tb_unit = PrettyTable()
        tb_unit.field_names=["unit","Busy","Op","Fi","Fj","Fk","Qj","Qk","Rj","Rk"]

        unit_status = self.units_status["Integer"]
        tb_unit.add_row(["Integer",unit_status.Busy,unit_status.Op,unit_status.Fi,unit_status.Fj,unit_status.Fk,unit_status.Qj,unit_status.Qk,unit_status.Rj,unit_status.Rk])
        #print("Integer:")
        #unit_status.status_print()
        unit_status = self.units_status["Mul1"]
        tb_unit.add_row(["Mul1",unit_status.Busy,unit_status.Op,unit_status.Fi,unit_status.Fj,unit_status.Fk,unit_status.Qj,unit_status.Qk,unit_status.Rj,unit_status.Rk])
        # unit_status.status_print()
        unit_status = self.units_status["Mul2"]
        tb_unit.add_row(["Mul2",unit_status.Busy,unit_status.Op,unit_status.Fi,unit_status.Fj,unit_status.Fk,unit_status.Qj,unit_status.Qk,unit_status.Rj,unit_status.Rk])
        # print("Mul2:")
        # unit_status.status_print()
        unit_status = self.units_status["Add"]
        tb_unit.add_row(["Add",unit_status.Busy,unit_status.Op,unit_status.Fi,unit_status.Fj,unit_status.Fk,unit_status.Qj,unit_status.Qk,unit_status.Rj,unit_status.Rk])
        # print("Add:")
        # unit_status.status_print()
        unit_status = self.units_status["Divide"]
        tb_unit.add_row(["Divide",unit_status.Busy,unit_status.Op,unit_status.Fi,unit_status.Fj,unit_status.Fk,unit_status.Qj,unit_status.Qk,unit_status.Rj,unit_status.Rk])
        # print("Divide:")
        # unit_status.status_print()
        print(tb_unit)

        # print reg status
        print("reg_status")
        list_index = []
        reg_list = []
        for i in range(32):
            list_index.append("F"+str(i))
            reg_list.append("Null")

        #把字典形式的reg_status转为列表形式
        tb_reg = PrettyTable()
        tb_reg.field_names=list_index
        for key in self.reg_status.keys():
            if self.reg_status[key]!="Null":
                index = int(key[1:])
                #print("index=",index)
                reg_list[index] = self.reg_status[key]
        tb_reg.add_row(reg_list)
        print(tb_reg)
        #print(self.reg_status)

    #得到每个指令状态将要执行的步骤
    def find_next_step(self, ir_status):
        for key in ir_status.status.keys():
            if ir_status.status[key] == -1:
                return key
        return -1

    #每个时钟更新三个表格
    def update_status(self, new_ir, unit, clock):
        #print("update_status")
        #print("new_ir:",new_ir)
        #update old ir status
        #先更新旧的指令、组件和寄存器状态，再发射新的指令并对应更新
        for i in range(len(self.ir_status)):
            old_ir_status = self.ir_status[i]
            next_ir_step = self.find_next_step(old_ir_status)
            old_ir = old_ir_status.ir
            occupy_unit = old_ir_status.unit
            unit_status = self.units_status[occupy_unit]
            #根据每条指令将要执行的步骤更新表格
            if (next_ir_step == "Read_Oper"):
                #check Rj Rk is ready or not
                is_continue = False
                # 判断是否处于阻塞状态
                if unit_status.Rj == "No":
                    if self.reg_status[unit_status.Fj] == "Null":
                        unit_status.Rj = "Yes"
                        is_continue = True
                if unit_status.Rk == "No":
                    if self.reg_status[unit_status.Fk] == "Null":
                        unit_status.Rk = "Yes"
                        is_continue = True
                if is_continue:
                    continue
                # 若不阻塞，更新表格，并初始化EX段需要执行的周期数
                if unit_status.Rj != "No" and unit_status.Rk != "No":
                    #Rj Rk is ready
                    old_ir_status.status[next_ir_step] = clock
                    if occupy_unit=="Mul1" or occupy_unit=="Mul2":
                        unit_status.need_ex_cycle = self.ex_cycles["Mul"]
                    else:
                        unit_status.need_ex_cycle = self.ex_cycles[occupy_unit]

            elif (next_ir_step == "Exec_Comp"):
                # 将Rj和Rk设置为No
                if unit_status.Rj == "Yes":
                    unit_status.Rj = "No"
                if unit_status.Rk == "Yes":
                    unit_status.Rk = "No"

                # 每过一周期，剩余需要执行的周期数-1
                unit_status.need_ex_cycle -= 1
                # 执行结束，更新IR status，记录clock
                if unit_status.need_ex_cycle == 0:
                    old_ir_status.status[next_ir_step] = clock

            elif (next_ir_step == "Write_Result"):
                is_WAR_harzard = False
                #首先判断是否有WAR相关，遍历前面的指令状态表
                #考虑到更新表格是自上往下，为避免发生WAR相关的寄存器同时发生了读和写，需要设置个全局变量is_WB_WAR来延迟写结果段一个周期
                Fi = unit_status.Fi
                for j in range (0,i):
                    forward_ir_status = self.ir_status[j]
                    forward_occupy_unit = forward_ir_status.unit
                    forward_unit_status = self.units_status[forward_occupy_unit]
                    forward_Fj = forward_unit_status.Fj
                    forward_Fk = forward_unit_status.Fk
                    forward_next_ir_step = self.find_next_step(forward_ir_status)
                    #WAR harzard
                    if forward_next_ir_step == "Read_Oper" and (forward_Fj==Fi or forward_Fk==Fi) :
                        is_WAR_harzard = True
                        self.is_WB_WAR = True
                        self.WAR_index = i
                        #print("WAR harzard--------------------------------------------")
                        break
                if not is_WAR_harzard:
                    if self.is_WB_WAR and self.WAR_index==i:
                        self.is_WB_WAR = False
                        self.WAR_index = -1
                    else:
                        self.reg_status[unit_status.Fi] = "Null"
                        old_ir_status.status[next_ir_step] = clock
                        unit_status.flush()
                        self.units_free[occupy_unit] = True


        if (len(new_ir) != 0):
            #通过新的指令，更新三个表格
            self.units_free[unit] = False
            new_ir_status = ir_status(new_ir, unit)
            new_ir_status.status["Issue"] = clock
            self.ir_status.append(new_ir_status)
            
            #print("unit:",unit)
            new_unit_status = self.units_status[unit]
            new_unit_status.Busy = "Yes"
            new_unit_status.Op = self.ir_op[new_ir[0]]
            new_unit_status.Fi = new_ir[1]

            # Fj Rj Qj
            if (new_ir[0] != "L.D"):
                new_unit_status.Fj = new_ir[2]
                if new_ir[2] not in self.reg_status.keys() or self.reg_status[
                        new_ir[2]] == "Null":
                    new_unit_status.Rj = "Yes"
                elif self.reg_status[new_ir[2]] != "Null":
                    new_unit_status.Rj = "No"
                    new_unit_status.Qj = self.reg_status[new_ir[2]]

            # Fk Rk Qk
            new_unit_status.Fk = new_ir[3]
            if new_ir[3] not in self.reg_status.keys() or self.reg_status[
                    new_ir[3]] == "Null":
                new_unit_status.Rk = "Yes"
            elif self.reg_status[new_ir[3]] != "Null":
                new_unit_status.Rk = "No"
                new_unit_status.Qk = self.reg_status[new_ir[3]]

            #Update reg_status
            self.reg_status[new_ir[1]] = self.ir_unit[new_ir[0]]

        #每周期执行结束后，打印三个表格
        self.print_status(clock)

    def run(self):
        index = 0
        clock = 0
        #顺序发射指令，发射前需要判断组件是否被占用
        #如果没有待发射的指令并且所有组件处于空闲状态，就结束程序
        while True:
            clock += 1
            if (index < len(self.instructions)):
                wait_ir = self.instructions[index]
            else:
                wait_ir = []
                
            if (index >= len(self.instructions) and self.is_all_units_free):
                break
            need_unit = "Null"
            if len(wait_ir) == 0:
                self.update_status([], need_unit, clock)
                self.update_all_units_free()
                continue
            #check wait_ir issue
            #print("wait_ir:",wait_ir)
            unit_name = wait_ir[0]
            
            if (unit_name == "MUL.D"):
                if self.units_free["Mul1"]:
                    need_unit = "Mul1"
                elif self.units_free["Mul2"]:
                    need_unit = "Mul2"
            elif self.units_free[self.ir_unit[unit_name]]:
                #print("self.ir_unit[unit_name]",self.ir_unit[unit_name])
                need_unit = self.ir_unit[unit_name]
            #print("need_unit:", need_unit)
            # wait_ir issue
            if (need_unit != "Null"):
                self.update_status(wait_ir, need_unit, clock)
                index += 1
            # wait_ir wait
            else:
                self.update_status([], need_unit, clock)
            self.update_all_units_free()


instructions = [["L.D", "F6", "34", "R2"], ["L.D", "F2", "45", "R3"],
                ["MUL.D", "F0", "F2", "F4"], ["SUB.D", "F8", "F2", "F6"],
                ["DIV.D", "F10", "F0", "F6"], ["ADD.D", "F6", "F8", "F2"]]

Scoreboard = Scoreboard()
Scoreboard.load_irs(instructions)
Scoreboard.run()
