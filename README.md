Tomasulo Algorithm
=
Computer Architecture Lab2 project
---
### Implement a simulator for Tomasulo algorithm.  
- In this simulator, there are three adders, two multipliers, two load buffers, and two store buffers.  <br> 
The clock cycles in execution steps of different instructions are according to the slides.  <br> 
The cycles of execution steps of L.D, S.D., ADD.D, SUB.D, MUL.D, and DIV.D are two, one, two, two, 10, and 40, respectively.  <br> 
The simulator is to execute the six instructions: L.D、S.D、ADD.D、SUB.D、MUL.D、DIV.D.  <br> 
(浮點數暫存器有16個，編號為F0、F2、F4、…、F30，初始值為1；整數暫存器有32個，編號為R0、R1、…、R31，除R1的初始值為16外，其餘整數暫存器初始值為0；記憶體為8個雙精準的空間(64 Bytes)，初始值為1) <br> 

input: xxx.txt (which is the instructions) <br> 
output: output.txt (clock by clock status of Register_result_state, Resevation_Station, Load/Store_Buffer and Memory) <br> 

Sample instructions (sample.txt):<br>
```bash
L.D F2, 8(R1)
L.D F4, 16(R0)
ADD.D F4, F2, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
```

How to use: <br>
```bash
python3 project.py xxxxxx.txt
python3 project.py sample.txt
```










