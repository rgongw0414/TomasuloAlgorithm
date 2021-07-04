# -*- coding: utf-8 -*-
"""
Implement a simulator for Tomasulo algorithm. 
In this simulator, there are three adders, 
two multipliers, two load buffers, and two store buffers. 
浮點數暫存器有16個，編號為F0、F2、F4、…、F30，初始值為1；
整數暫存器有32個，編號為R0、R1、…、R31，
除R1的初始值為16外，其餘整數暫存器初始值為0；記憶體為8個雙精準的空間(64 Bytes)，初始值為1
"""

import sys

LD = "L.D"   # exe steps: 2
SD = "S.D"   #            1
ADDD = "ADD.D" #          2
SUBD = "SUB.D" #          2
MULD = "MUL.D" #         10
DIVD = "DIV.D" #         40

class Tomasulo:
  def __init__(self, insts, adder_num, multiplier_num, load_buffer_num, store_buffer_num, float_reg_num, int_reg_num, mem_size):
    # 去除指令的逗號，並 initialize instruction status
    i = 0
    for inst in insts:  
      inst_ = ""
      for term in inst.split(" "):
        inst_ = inst_ + term.split(",")[0] + " "
      insts[i] = inst_.split("\n")[0]
      i += 1
    self.instruction_status = [instruction_status(insts[i], i) for i in range(len(insts))]

    self.reservation_station = reservation_station(adder_num, multiplier_num)
    self.load_buffers = [load_buffer(i) for i in range(load_buffer_num)]
    self.store_buffers = [store_buffer(i) for i in range(store_buffer_num)]
    
    self.register_result_status = register_result_status(float_reg_num, int_reg_num)
    self.mem = [mem(i) for i in range(mem_size)]
    self.clock = 1

  def lbIsFull(self): 
    for lb in self.load_buffers: 
      if lb.busy == False: return lb.index # return free buffer's index
    return "True" # indicate Full by returning "True"


  def sbIsFull(self):
    for sb in self.store_buffers: 
      if sb.busy == False: return sb.index # return free buffer's index
    return "True" # indicate Full by returning "True"
  
  def print(self):
    print("Cycle " + str(self.clock) + ":")
    print("\nInstruction Status: ") 
    print("\t\t\t\t\t\t%s\t%s    %s" % ("Issue", "Complete", "Write_Result"))
    for IS in self.instruction_status: IS.print()    
    self.reservation_station.print()
    print("\n-\n")
    print("Load/Store Buffer:")
    print("\t\t\tBusy\tAddress\t\tFu")
    for lb in self.load_buffers: lb.print()    
    for sb in self.store_buffers: sb.print()
    print("-\n")
    self.register_result_status.print()

    print("Memory: \n")
    mem_name = "\t\t "
    mem_value = "\t\tValue: "
    for mem in self.mem: 
      if int(mem.name.split("_")[-1]) % 8 == 0:
        mem_name += ("\tMem_" + str(int(int(mem.name.split("_")[-1]) / 8) + 1))
        mem_value += ("\t" + str(mem.value))        
    print(mem_name + "\n")
    print(mem_value)
    print("-\n")

  def isFinished(self): # check whether the insts are finished
    for IS in self.instruction_status:
      if IS.write == -1: return False
    return True

  def writeResult(self):
    for RS in self.reservation_station.adders:            
      self.broadcast(RS)

    for RS in self.reservation_station.multipliers:      
      self.broadcast(RS)

    for RS in self.load_buffers:
      self.broadcast(RS)
    
    for RS in self.store_buffers:      
      if RS.busy == True and RS.time == 0:                
        if RS.qk != "null":                    
          if RS.qk.split("_")[0] == "Add": fus = self.reservation_station.adders
          elif RS.qk.split("_")[0] == "Mult": fus = self.reservation_station.multipliers
          for fu in fus: # 尋找store buffer所等待的function unit(reservation station)
            #                   ↓必須等buffer所等待的instruction write result之後，再write自己的result
            if RS.qk == fu.name and self.clock == self.instruction_status[fu.inst_index].write + 1: 
              self.mem[RS.address].value = fu.result
              RS.last_time_write = self.clock # 在該station/buffer中紀錄instruction最近一次的write_result時間
              self.instruction_status[RS.inst_index].write = self.clock          
              fu.result = -1 # reset the result
              RS.reset()              
                               
        ###############↓需要針對沒有dependence的狀況修改vk的傳遞路徑
        elif RS.qk == "null": # source register(rt) 無人佔用
          self.mem[RS.address].value = RS.vk
          self.vk_broadcasted_cycle = self.clock
          RS.last_time_write = self.clock # 在該station/buffer中紀錄instruction的write_result時間
          self.instruction_status[RS.inst_index].write = self.clock          
          RS.reset()          

  def broadcast(self, RS):
    if RS.busy == True and RS.time == 0:
      RS.last_time_write = self.clock
      self.instruction_status[RS.inst_index].write = self.clock # write result

      # broadcast to all awaiting reservation stations
      for reg in self.register_result_status.float_regs:
        if reg.qi != "null" and reg.qi == RS.name:            
          reg.value = RS.result
          reg.qi = "null"

      for RSs in self.reservation_station.adders: # search for matched Qj or Qk
        if RSs.busy == True and RSs.qj == RS.name:
          RSs.vj = RS.result
          RSs.vj_broadcasted_cycle = self.clock
          RSs.qj = "null"
        if RSs.busy == True and RSs.qk == RS.name:
          RSs.vk = RS.result
          RSs.vk_broadcasted_cycle = self.clock
          RSs.qk = "null"

      for RSs in self.reservation_station.multipliers: # search for matched Qj or Qk
        if RSs.busy == True and RSs.qj == RS.name:
          RSs.vj = RS.result
          RSs.vj_broadcasted_cycle = self.clock
          RSs.qj = "null"
        if RSs.busy == True and RSs.qk == RS.name:
          RSs.vk = RS.result
          RSs.vk_broadcasted_cycle = self.clock
          RSs.qk = "null"

      for RSs in self.load_buffers: # search for matched Qj
        if RSs.busy == True and RSs.qj == RS.name:
          RSs.vj = RS.result
          RSs.vj_broadcasted_cycle = self.clock
          RSs.qj = "null"          

      """ broadcast給正在等待的reservation station，
      for RSs in self.store_buffers: # search for matched Qk
        if RSs.busy == True and RSs.qk == RS.name:
          RSs.vk = RS.result
          RSs.vk_broadcasted_cycle = self.clock
          RSs.qk = "null"
          """
      RS.reset()
      
  def execute(self):
    for RS in self.reservation_station.adders:      
      if RS.busy == True and RS.vj != "null" and RS.vk != "null" and RS.qj == "null" and RS.qk == "null":
        if RS.vj_broadcasted_cycle == self.clock or RS.vk_broadcasted_cycle == self.clock: continue # 若取得Vj或Vk的時間和execute當下的cycle相同，則略過當下cycle，等到下個cycle再開始執行reservation station內的指令。
        else:
          RS.time = RS.time - 1        
          if RS.time == 0:
            if RS.op == ADDD: RS.result = RS.vj + RS.vk
            elif RS.op == SUBD: RS.result = RS.vj - RS.vk          
            self.instruction_status[RS.inst_index].complete = self.clock

    for RS in self.reservation_station.multipliers: 
      if RS.busy == True and RS.vj != "null" and RS.vk != "null" and RS.qj == "null" and RS.qk == "null":        
        if RS.vj_broadcasted_cycle == self.clock or RS.vk_broadcasted_cycle == self.clock: continue # 若取得Vj或Vk的時間和execute當下的cycle相同，則略過當下cycle，等到下個cycle再開始執行reservation station內的指令。
        else:
          RS.time = RS.time - 1
          if RS.time == 0:
            if RS.op == MULD: RS.result = RS.vj * RS.vk
            elif RS.op == DIVD: RS.result = RS.vj / RS.vk
            self.instruction_status[RS.inst_index].complete = self.clock

    for RS in self.load_buffers:
      if RS.busy == True and RS.vj != "null" and RS.qj == "null": 
        ###### ↓必須考慮load指令取得Vj(base address: rs)的時間是否和execute當下的cycle相同的問題 ######
        if RS.vj_broadcasted_cycle == self.clock: continue # 若取得Vj的時間和execute當下的cycle相同，則略過當下cycle，等到下個cycle再開始執行reservation station內的指令。
        else:
          RS.time = RS.time - 1
          if RS.time == 1:
            RS.address = RS.address + RS.vj
          elif RS.time == 0:
            RS.result = self.mem[RS.address].value
            self.instruction_status[RS.inst_index].complete = self.clock

    for RS in self.store_buffers:      
      #if RS.busy == True and RS.vk != "null"  and RS.qk == "null":

      # 依據測資，不考慮buffer要是load-store queue的第一個。這樣的修改可能使write result階段產生hazard，所以可利用in-order方式去完成load與store指令的write result階段。      
      #if RS.busy == True and RS.vk != "null": 
      if RS.busy == True:
        ###### ↓在正常情況下必須考慮store指令取得Vk(source register: rt)的時間是否和execute當下的cycle相同，但在本專題中由於預設load和store不會存取相同位置，因此不必考慮該問題。 ######
        #if RS.vk_broadcasted_cycle == self.clock: continue
        #else:
        if RS.time != 0: # 若execute階段已經完成，則不再執行該指令，直到dependent的station release其register(rt)後，才能write result，
          RS.time = RS.time - 1
          if RS.time == 0:
            RS.address = RS.address + RS.vj
            self.instruction_status[RS.inst_index].complete = self.clock
  
  def issue(self):
    for inst in self.instruction_status:      
      if inst.issue == -1:  # only issue the unissued instructions
        if inst.name == LD:
          index = self.lbIsFull() # index 為 free load_buffer's index
          #             ↓若該station上個cycle才剛finish write一個instruction的result，且當下的cycle有指令想佔用該station，則拒絕該指令的存取。
          if index != "True" and self.load_buffers[index].last_time_write != self.clock:
            self.load_buffers[index].time = 2
            inst.issue = self.clock
            self.load_buffers[index].inst_index = inst.index # 紀錄該 station 中負責的是哪一個 instruction
            # load or store
            if self.register_result_status.int_regs[inst.rsIndex].qi != "null": # 查看base address register(rs)是否有人佔用
              self.load_buffers[index].qj = self.register_result_status.int_regs[inst.rsIndex].qi
            else:              
              self.load_buffers[index].vj = self.register_result_status.int_regs[inst.rsIndex].value # base address
              self.load_buffers[index].qj = "null"
            self.load_buffers[index].address = inst.offset # save offset(immd. value) to address
            self.load_buffers[index].busy = True

            # load only
            self.register_result_status.float_regs[inst.rtIndex].qi = self.load_buffers[index].name # 將 free load buffer's name 存進 register_result_status's Qi                     

        elif inst.name == SD:
          index = self.sbIsFull() # index 為 free store_buffer's index
          #             ↓若該station上個cycle才剛finish write一個instruction的result，且當下的cycle有指令想佔用該station，則拒絕該指令的存取。
          if index != "True" and self.store_buffers[index].last_time_write != self.clock:
            inst.issue = self.clock
            self.store_buffers[index].time = 1
            self.store_buffers[index].inst_index = inst.index # 紀錄該 station 中負責的是哪一個 instruction            
            # load or store
            if self.register_result_status.int_regs[inst.rsIndex].qi != "null": # 查看base address register(rs)是否有人佔用
              self.store_buffers[index].qj = self.register_result_status.int_regs[inst.rsIndex].qi              
            else:
              self.store_buffers[index].vj = self.register_result_status.int_regs[inst.rsIndex].value # base address
              self.store_buffers[index].qj = "null"              
            self.store_buffers[index].address = inst.offset # save offset(immd. value) to address
            self.store_buffers[index].busy = True

            # store only
            if self.register_result_status.float_regs[inst.rtIndex].qi != "null": # 查看source register(rt)是否有人佔用              
              self.store_buffers[index].qk = self.register_result_status.float_regs[inst.rtIndex].qi              
            else: # 無人佔用該buffer(沒有dependence)
              #                              ↓有可能到時候 source register 不是 float register
              self.store_buffers[index].vk = self.register_result_status.float_regs[inst.rtIndex].value # source register (rt)              
              self.store_buffers[index].qk = "null"
            
        elif inst.name == ADDD or inst.name == SUBD or inst.name == MULD or inst.name == DIVD:        
          if inst.name == ADDD or inst.name == SUBD:             
            index = self.reservation_station.isFull(self.reservation_station.adders)
            #             ↓若該station上個cycle才剛finish write一個instruction的result，且當下的cycle有指令想佔用該station，則拒絕該指令的存取。
            if index != "True" and self.reservation_station.adders[index].last_time_write != self.clock:
              inst.issue = self.clock
              self.reservation_station.adders[index].inst_index = inst.index # 紀錄該 station 中負責的是哪一個 instruction
              if inst.name == ADDD: self.reservation_station.adders[index].op = ADDD
              elif inst.name == SUBD: self.reservation_station.adders[index].op = SUBD              
              self.reservation_station.adders[index].time = 2
              if self.register_result_status.float_regs[inst.rsIndex].qi != "null":
                self.reservation_station.adders[index].qj = self.register_result_status.float_regs[inst.rsIndex].qi
              else:            
                #                                    ↓有可能到時候 source register 不是 float register
                self.reservation_station.adders[index].vj = self.register_result_status.float_regs[inst.rsIndex].value 
                self.reservation_station.adders[index].qj = "null"

              if self.register_result_status.float_regs[inst.rtIndex].qi != "null":
                self.reservation_station.adders[index].qk = self.register_result_status.float_regs[inst.rtIndex].qi                
              else:
                #                                    ↓有可能到時候 source register 不是 float register
                self.reservation_station.adders[index].vk = self.register_result_status.float_regs[inst.rtIndex].value # base address
                self.reservation_station.adders[index].qk = "null"
              self.reservation_station.adders[index].busy = True
              self.register_result_status.float_regs[inst.rdIndex].qi = self.reservation_station.adders[index].name # 將 free adder's name 存進 register_result_status's Qi          

          elif inst.name == MULD or inst.name == DIVD: 
            index = self.reservation_station.isFull(self.reservation_station.multipliers)
            #             ↓若該station上個cycle才剛finish write一個instruction的result，且當下的cycle有指令想佔用該station，則拒絕該指令的存取。
            if index != "True" and self.reservation_station.multipliers[index].last_time_write != self.clock:
              inst.issue = self.clock
              self.reservation_station.multipliers[index].inst_index = inst.index # 紀錄該 station 中負責的是哪一個 instruction
              if inst.name == MULD:
                self.reservation_station.multipliers[index].time = 10
                self.reservation_station.multipliers[index].op = MULD
              elif inst.name == DIVD: 
                self.reservation_station.multipliers[index].time = 40
                self.reservation_station.multipliers[index].op = DIVD

              if self.register_result_status.float_regs[inst.rsIndex].qi != "null":
                self.reservation_station.multipliers[index].qj = self.register_result_status.float_regs[inst.rsIndex].qi
              else:
                #                                       ↓有可能到時候 source register 不是 float register
                self.reservation_station.multipliers[index].vj = self.register_result_status.float_regs[inst.rsIndex].value 
                self.reservation_station.multipliers[index].qj = "null"

              if self.register_result_status.float_regs[inst.rtIndex].qi != "null":
                self.reservation_station.multipliers[index].qk = self.register_result_status.float_regs[inst.rtIndex].qi                
              else:
                #                                       ↓有可能到時候 source register 不是 float register
                self.reservation_station.multipliers[index].vk = self.register_result_status.float_regs[inst.rtIndex].value 
                self.reservation_station.multipliers[index].qk = "null"
              self.reservation_station.multipliers[index].busy = True
              self.register_result_status.float_regs[inst.rdIndex].qi = self.reservation_station.multipliers[index].name # 將 free multiplier's name 存進 register_result_status's Qi          
              
        break # issue one instruction per cycle, so break from for loop anyway


class instruction_status:
  def __init__(self, inst, i):
    inst = inst.split()
    self.name = inst[0]    
    self.issue = self.complete = self.write = self.rs = self.rt = self.rd = self.offset = -1   
    self.index = i # instruction index for reservation_station mapping

    if self.name == LD or self.name == SD: # target address: rt = base(rs) + offset      
      self.offset = int(inst[-1].split("(")[0]) 

      self.rs = inst[-1].split("(")[-1].split(")")[0] # base address
      #                 ↓若到時候測資的 rs 為 float register 則必須修改此處和 self.issue() 的內容
      self.rsIndex = int(self.rs.split('R')[-1])     # rs index for register_result_status mapping

      self.rt = inst[1] # destination register
      #                 ↓若到時候測資的 rt 為 integer register 則必須修改此處和 self.issue() 的內容
      self.rtIndex = int(int(self.rt.split('F')[-1]) / 2)  # rt index for register_result_status mapping; 除以2是因為名稱為F0, F2, F4, ...，而 index 為 0, 1, 2, ...
    else:
      self.rd = inst[1] # destination register
      #                 ↓若到時候測資的 rd 為 integer register 則必須修改此處和 self.issue() 的內容
      self.rdIndex = int(int(self.rd.split('F')[-1]) / 2)  # rd index for register_result_status mapping; 除以2是因為名稱為F0, F2, F4, ...，而 index 為 0, 1, 2, ...

      self.rs = inst[2] # source register 1
      #                 ↓若到時候測資的 rs 為 integer register 則必須修改此處和 self.issue() 的內容
      self.rsIndex = int(int(self.rs.split('F')[-1]) / 2)  # rs index for register_result_status mapping; 除以2是因為名稱為F0, F2, F4, ...，而 index 為 0, 1, 2, ...

      self.rt = inst[3] # source register 2
      #                 ↓若到時候測資的 rt 為 integer register 則必須修改此處和 self.issue() 的內容
      self.rtIndex = int(int(self.rt.split('F')[-1]) / 2)  # rt index for register_result_status mapping; 除以2是因為名稱為F0, F2, F4, ...，而 index 為 0, 1, 2, ...

  def print(self):
    if self.issue == -1: issue = ""
    else: issue = self.issue
    if self.complete == -1: complete = ""
    else: complete = self.complete
    if self.write == -1: write = ""
    else: write = self.write

    if self.name == LD or self.name == SD:      
      print("\t\t%s\t%s\t%s\t%s\t  %s\t    %s\t\t %s" % (self.name, self.rt, self.offset, self.rs, issue, complete, write))
    else:
      print("\t\t%s\t%s\t%s\t%s\t  %s\t    %s\t\t %s" % (self.name, self.rd, self.rs, self.rt, issue, complete, write))


class reservation_station:
  def __init__(self, adder_num, multiplier_num):
    self.adders = [adder(i) for i in range(adder_num)]
    self.multipliers = [multiplier(i) for i in range(multiplier_num)]
  
  def isFull(self, RS):
    for rs in RS:
      if rs.busy == False: return rs.index
    return "True"

  def print(self):
    print("-\n\nResevation Station:")
    print("\t\tTime\tName\tBusy\tOp\tVj\tVk\tQj\tQk")
    for adder in self.adders: self.print_RS(adder)
    for multiplier in self.multipliers: self.print_RS(multiplier)

  def print_RS(self, RS):
    if RS.time == -1: time = ""
    else: time = RS.time
    if RS.busy == False: busy = "No"
    else: busy = "Yes"
    if RS.op == "null": op = ""
    else: op = RS.op
    if RS.vj == "null": vj = ""
    else: vj = RS.vj
    if RS.vk == "null": vk = ""
    else: vk = RS.vk
    if RS.qj == "null": qj = ""
    else: qj = qj = RS.qj.split("_")[0] + "_" + str(int(RS.qj.split("_")[-1]) + 1)      
    if RS.qk == "null": qk = ""
    else: qk = RS.qk.split("_")[0] + "_" + str(int(RS.qk.split("_")[-1]) + 1)
    name = RS.name.split("_")[0] + "_" + str(int(RS.name.split("_")[-1]) + 1)    
    print("\t\t%4s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (time, name, busy, op, vj, vk, qj, qk))
  
  def adderIsFull(self, RS):
    for adder in self.adders:
      if adder.busy == False: return False
    return True

  def multiplierIsFull(self, RS):
    for multiplier in self.multipliers:
      if multiplier.busy == False: return False
    return True

class adder:
  def __init__(self, i):
    self.index = i
    self.name = "Add_" + str(i)
    self.time = -1
    self.busy = False
    self.op = "null"
    self.vj = "null"
    self.vk = "null"
    self.qj = "null"
    self.qk = "null"
    self.result = 0
    self.inst_index = -1 # 紀錄該 reservation_station 處理的是哪一個 instruction
    self.vj_broadcasted_cycle = -1 # 為了不讓RS在broadcast的cycle就開始執行，因此必須在RS記錄得到broadcast的時間(cycle)
    self.vk_broadcasted_cycle = -1
    self.last_time_write = -1 # 為了禁止在write result之後的下個cycle解放station後，馬上被新的指令issue並放入該station中，
                   # 因此紀錄該 station 上個指令的 write result 時間，讓下個指令必須隔兩個cycle才能issue。
  
  def reset(self):    
    self.time = -1
    self.busy = False
    self.op = "null"
    self.vj = "null"
    self.vk = "null"
    self.qj = "null"
    self.qk = "null"
    #self.result = 0
    #self.inst_index = -1
    self.vj_broadcasted_cycle = -1
    self.vk_broadcasted_cycle = -1

class multiplier:
  def __init__(self, i):
    self.index = i
    self.name = "Mult_" + str(i)
    self.time = -1
    self.busy = False
    self.op = "null"
    self.vj = "null"
    self.vk = "null"
    self.qj = "null"
    self.qk = "null"
    self.result = 0
    self.inst_index = -1 # 紀錄該 reservation_station 處理的是哪一個 instruction
    self.vj_broadcasted_cycle = -1 # 為了不讓RS在broadcast的cycle就開始執行，因此必須在RS記錄得到broadcast的時間(cycle)
    self.vk_broadcasted_cycle = -1
    self.last_time_write = -1 # 為了禁止在write result之後的下個cycle解放station後，馬上被新的指令issue並放入該station中，
                   # 因此紀錄該 station 上個指令的 write result 時間，讓下個指令必須隔兩個cycle才能issue。

  def reset(self):    
    self.time = -1
    self.busy = False
    self.op = "null"
    self.vj = "null"
    self.vk = "null"
    self.qj = "null"
    self.qk = "null"
    #self.result = 0
    #self.inst_index = -1
    self.vj_broadcasted_cycle = -1
    self.vk_broadcasted_cycle = -1

class load_buffer:
  def __init__(self, i):
    self.index = i  # index for register_result_status mapping
    self.name = "Load_" + str(i)
    self.time = -1
    self.busy = False
    self.vj = "null" # base address
    self.qj = "null" # the function unit which is processing base address
    self.address = 0 
    self.result = 0
    self.inst_index = -1 # 紀錄該 reservation_station 處理的是哪一個 instruction
    self.vj_broadcasted_cycle = -1  # 為了不讓RS在broadcast的cycle就開始執行，因此必須在RS記錄得到broadcast的時間(cycle)
    self.last_time_write = -1 # 為了禁止在write result之後的下個cycle解放station後，馬上被新的指令issue並放入該station中，
                   # 因此紀錄該 station 上個指令的 write result 時間，讓下個指令必須隔兩個cycle才能issue。

  def reset(self):    
    self.time = -1
    self.busy = False
    self.vj = "null"
    self.qj = "null"
    self.address = 0     
    #self.result = 0
    #self.inst_index = -1
    self.vj_broadcasted_cycle = -1 

  def print(self):
    if self.busy == False: busy = "No"
    else: busy = "Yes"
    if self.qj == "null": qj = ""
    else: qj = self.qj.split("_")[0] + "_" + str(int(self.qj.split("_")[-1]) + 1)          
    name = self.name.split("_")[0] + "_" + str(int(self.name.split("_")[-1]) + 1)
    print("\t\t%s\t%s\t%s\t\t%s" % (name, busy, self.address, qj))    


class store_buffer:
  # mem[rs + immd.(offset)] = rt
  def __init__(self, i):
    self.index = i  # index for register_result_status mapping    
    self.name = "Store_" + str(i)
    self.time = -1
    self.busy = False
    self.vj = "null" # base address register(rs)
    self.vk = "null" # source register (rt)
    self.qj = "null" 
    self.qk = "null" # the function unit which is processing base address
    self.address = 0
    self.result = 0
    self.inst_index = -1 # 紀錄該 reservation_station 處理的是哪一個 instruction
    self.vk_broadcasted_cycle = -1 # 為了不讓RS在broadcast的cycle就開始執行，因此必須在RS記錄得到broadcast的時間(cycle)
    self.last_time_write = -1 # 為了禁止在write result之後的下個cycle解放station後，馬上被新的指令issue並放入該station中，
                   # 因此紀錄該 station 上個指令的 write result 時間，讓下個指令必須隔兩個cycle才能issue。    

  def reset(self):    
    self.time = -1
    self.busy = False
    self.vj = "null"
    self.vk = "null"
    self.qj = "null"
    self.qk = "null"
    self.address = 0     
    #self.result = 0
    #self.inst_index = -1
    self.vk_broadcasted_cycle = -1

  def print(self):
    if self.busy == False: busy = "No"
    else: busy = "Yes"
    if self.qk == "null": qk = ""
    else: qk = self.qk.split("_")[0] + "_" + str(int(self.qk.split("_")[-1]) + 1)          
    name = self.name.split("_")[0] + "_" + str(int(self.name.split("_")[-1]) + 1)    
    print("\t\t%s\t%s\t%s\t\t%s" % (name, busy, self.address, qk))    


class mem:  # 記憶體為8個雙精準(64-bit)的空間(64-Bytes)，初始值為1
  def __init__(self, i):
    self.name = "Mem_" + str(i)
    if i % 8 == 0: self.value = 1
    else: self.value = 0

class register_result_status:
  def __init__(self, float_reg_num, int_reg_num):
    self.float_regs = [float_reg(i) for i in range(float_reg_num)] # 浮點數暫存器有16個，編號為F0、F2、F4、…、F30，初始值為1；
    self.int_regs = [int_reg(i) for i in range(int_reg_num)]    # 整數暫存器有32個，編號為R0、R1、…、R31
    self.int_regs[1].value = 16    

  def print(self):    
    print("Register result status:")
    a = ""
    for fr in self.float_regs: a += fr.name + "\t"
    print("\t\t\t" + a)

    a = ""
    for fr in self.float_regs: 
      if fr.qi == "null": qi = ""
      else: qi = fr.qi.split("_")[0] + "_" + str(int(fr.qi.split("_")[-1]) + 1)      
      a += str(qi) + "\t"
    print("\t\tQi:\t" + a)

    a = ""
    for fr in self.float_regs: a += str(fr.value) + "\t"
    print("\t\tvalue:\t" + a)
    print("\n")
    
    a = ""
    for ir in self.int_regs:  a += ir.name + "\t"
    print("\t\t\t" + a)

    a = ""
    for ir in self.int_regs:
      if ir.qi == "null": qi = ""
      else: qi = ir.qi.split("_")[0] + "_" + str(int(ir.qi.split("_")[-1]) + 1)
      a += str(qi) + "\t"
    print("\t\tQi:\t" + a)

    a = ""
    for ir in self.int_regs: a += str(ir.value) + "\t"
    print("\t\tvalue:\t" + a)
    print("-\n")    


class float_reg:
  def __init__(self, i):
    self.name = "F" + str(i * 2)
    self.value = 1
    self.qi = "null" # 正在等待的 function unit
  
  def print(self):
    print("reg %s, value: %d" % (self.name, self.value))


class int_reg:
  def __init__(self, i):
    self.name = "R" + str(i)
    self.value = 0
    self.qi = "null" # 正在等待的 function unit

  def print(self):
    print("reg %s, value: %d" % (self.name, self.value))

def __main__():
  # read argument from command lind
  #input_argv = str(sys.argv[1])
  #f = open(input_argv, 'r')
  #insts = f.readlines()   # read instructions from text file

  # read input from pwd
  f = open("sample4.txt", 'r')
  insts = f.readlines()   # read instructions from text file
  f.close()

  adder_num = 3
  multiplier_num = load_buffer_num = store_buffer_num = 2  
  float_reg_num = 16  # 16 floating-point register, from F0, F2, F4, …, to F30, 初始值為1； 
  int_reg_num = 32   # 32 integer register, from R0, R1, …, to R31
  mem_size = 64     # 64-byte memory(8 double-precision space)
  tomasulo = Tomasulo(insts, adder_num, multiplier_num, load_buffer_num, store_buffer_num, 
						float_reg_num, int_reg_num, mem_size)
  
  original_stdout = sys.stdout 
  sys.stdout = open("output.txt", "w")    
  while (True):
    #ipdb.set_trace()        
    tomasulo.writeResult()  # 執行已完成Execution步驟的指令    
    tomasulo.execute() # 執行已完成Issue步驟的指令，並在維護每個正在本步驟的指令    
    tomasulo.issue()  # issue下一個未被issue的指令        
    
    tomasulo.print()    
    tomasulo.clock += 1 # steps one clock cycle
    
    if tomasulo.isFinished(): break
    #if tomasulo.clock > 71: break
  sys.stdout = original_stdout  

if __name__ == "__main__":
  __main__()