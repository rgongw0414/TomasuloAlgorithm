## Tomasulo Algorithm (Computer Architecture Lab2)

### Simulator for Tomasulo algorithm
- In this simulator, there are three **adders**, two **multipliers**, two **load buffers**, and two **store buffers**.  <br> 
- The simulator is to execute the six instructions: **L.D、S.D、ADD.D、SUB.D、MUL.D、DIV.D.**  <br> 
- The **execution steps(clock cycles)** of L.D, S.D., ADD.D, SUB.D, MUL.D, and DIV.D are **2, 1, 2, 2, 10, and 40**, respectively.  <br>
- Resources
	- 16 Floating-point register: F0, F2, …, and F30;
	- 32 integer registers: R0, R1, …, and R31;
	- Memory: 8 double-precision floating-point slot (totally 64 Bytes) <br>  <br> 

### How to use: <br>
```bash
python3 project.py xxxxxx.txt
python3 project.py sample.txt
python3 project.py test.txt
...
```

### Input: xxx.txt(which is the instructions) <br> 
- for example, in sample.txt contains the following intructions:
```bash
L.D F2, 8(R1)
L.D F4, 16(R0)
ADD.D F4, F2, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
DIV.D F4, F4, F4
```
### Output: output.txt  <br> 

- sample output:
- (clock by clock status of Register_result_state, Resevation_Station, Load/Store_Buffer and Memory)
```bash
Cycle 1:

Instruction Status: 
						Issue	Complete    Write_Result
		L.D	F2	8	R1	  1	    		 
		L.D	F4	16	R0	  	    		 
		ADD.D	F4	F2	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
-

Resevation Station:
		Time	Name	Busy	Op	Vj	Vk	Qj	Qk
		    	Add_1	No					
		    	Add_2	No					
		    	Add_3	No					
		    	Mult_1	No					
		    	Mult_2	No					

-

Load/Store Buffer:
			Busy	Address		Fu
		Load_1	Yes	8		
		Load_2	No	0		
		Store_1	No	0		
		Store_2	No	0		
-

Register result status:
			F0	F2	F4	F6	F8	F10	F12	F14	F16	F18	F20	F22	F24	F26	F28	F30	
		Qi:		Load_1															
		value:	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	


			R0	R1	R2	R3	R4	R5	R6	R7	R8	R9	R10	R11	R12	R13	R14	R15	R16	R17	R18	R19	R20	R21	R22	R23	R24	R25	R26	R27	R28	R29	R30	R31	
		Qi:																																	
		value:	0	16	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	
-

Memory: 

		 	Mem_1	Mem_2	Mem_3	Mem_4	Mem_5	Mem_6	Mem_7	Mem_8

		Value: 	1	1	1	1	1	1	1	1
-

Cycle 2:

Instruction Status: 
						Issue	Complete    Write_Result
		L.D	F2	8	R1	  1	    		 
		L.D	F4	16	R0	  2	    		 
		ADD.D	F4	F2	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
-

Resevation Station:
		Time	Name	Busy	Op	Vj	Vk	Qj	Qk
		    	Add_1	No					
		    	Add_2	No					
		    	Add_3	No					
		    	Mult_1	No					
		    	Mult_2	No					

-

Load/Store Buffer:
			Busy	Address		Fu
		Load_1	Yes	24		
		Load_2	Yes	16		
		Store_1	No	0		
		Store_2	No	0		
-

Register result status:
			F0	F2	F4	F6	F8	F10	F12	F14	F16	F18	F20	F22	F24	F26	F28	F30	
		Qi:		Load_1	Load_2														
		value:	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	


			R0	R1	R2	R3	R4	R5	R6	R7	R8	R9	R10	R11	R12	R13	R14	R15	R16	R17	R18	R19	R20	R21	R22	R23	R24	R25	R26	R27	R28	R29	R30	R31	
		Qi:																																	
		value:	0	16	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	
-

Memory: 

		 	Mem_1	Mem_2	Mem_3	Mem_4	Mem_5	Mem_6	Mem_7	Mem_8

		Value: 	1	1	1	1	1	1	1	1
-

Cycle 3:

Instruction Status: 
						Issue	Complete    Write_Result
		L.D	F2	8	R1	  1	    3		 
		L.D	F4	16	R0	  2	    		 
		ADD.D	F4	F2	F4	  3	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
-

Resevation Station:
		Time	Name	Busy	Op	Vj	Vk	Qj	Qk
		   2	Add_1	Yes	ADD.D			Load_1	Load_2
		    	Add_2	No					
		    	Add_3	No					
		    	Mult_1	No					
		    	Mult_2	No					

-

Load/Store Buffer:
			Busy	Address		Fu
		Load_1	Yes	24		
		Load_2	Yes	16		
		Store_1	No	0		
		Store_2	No	0		
-

Register result status:
			F0	F2	F4	F6	F8	F10	F12	F14	F16	F18	F20	F22	F24	F26	F28	F30	
		Qi:		Load_1	Add_1														
		value:	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	


			R0	R1	R2	R3	R4	R5	R6	R7	R8	R9	R10	R11	R12	R13	R14	R15	R16	R17	R18	R19	R20	R21	R22	R23	R24	R25	R26	R27	R28	R29	R30	R31	
		Qi:																																	
		value:	0	16	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	
-

Memory: 

		 	Mem_1	Mem_2	Mem_3	Mem_4	Mem_5	Mem_6	Mem_7	Mem_8

		Value: 	1	1	1	1	1	1	1	1
-

Cycle 4:

Instruction Status: 
						Issue	Complete    Write_Result
		L.D	F2	8	R1	  1	    3		 4
		L.D	F4	16	R0	  2	    4		 
		ADD.D	F4	F2	F4	  3	    		 
		DIV.D	F4	F4	F4	  4	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
-

Resevation Station:
		Time	Name	Busy	Op	Vj	Vk	Qj	Qk
		   2	Add_1	Yes	ADD.D	1			Load_2
		    	Add_2	No					
		    	Add_3	No					
		  40	Mult_1	Yes	DIV.D			Add_1	Add_1
		    	Mult_2	No					

-

Load/Store Buffer:
			Busy	Address		Fu
		Load_1	No	0		
		Load_2	Yes	16		
		Store_1	No	0		
		Store_2	No	0		
-

Register result status:
			F0	F2	F4	F6	F8	F10	F12	F14	F16	F18	F20	F22	F24	F26	F28	F30	
		Qi:			Mult_1														
		value:	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	


			R0	R1	R2	R3	R4	R5	R6	R7	R8	R9	R10	R11	R12	R13	R14	R15	R16	R17	R18	R19	R20	R21	R22	R23	R24	R25	R26	R27	R28	R29	R30	R31	
		Qi:																																	
		value:	0	16	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	
-

Memory: 

		 	Mem_1	Mem_2	Mem_3	Mem_4	Mem_5	Mem_6	Mem_7	Mem_8

		Value: 	1	1	1	1	1	1	1	1
-

Cycle 5:

Instruction Status: 
						Issue	Complete    Write_Result
		L.D	F2	8	R1	  1	    3		 4
		L.D	F4	16	R0	  2	    4		 5
		ADD.D	F4	F2	F4	  3	    		 
		DIV.D	F4	F4	F4	  4	    		 
		DIV.D	F4	F4	F4	  5	    		 
		DIV.D	F4	F4	F4	  	    		 
		DIV.D	F4	F4	F4	  	    		 
-

Resevation Station:
		Time	Name	Busy	Op	Vj	Vk	Qj	Qk
		   2	Add_1	Yes	ADD.D	1	1		
		    	Add_2	No					
		    	Add_3	No					
		  40	Mult_1	Yes	DIV.D			Add_1	Add_1
		  40	Mult_2	Yes	DIV.D			Mult_1	Mult_1

-

Load/Store Buffer:
			Busy	Address		Fu
		Load_1	No	0		
		Load_2	No	0		
		Store_1	No	0		
		Store_2	No	0		
-

Register result status:
			F0	F2	F4	F6	F8	F10	F12	F14	F16	F18	F20	F22	F24	F26	F28	F30	
		Qi:			Mult_2														
		value:	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	


			R0	R1	R2	R3	R4	R5	R6	R7	R8	R9	R10	R11	R12	R13	R14	R15	R16	R17	R18	R19	R20	R21	R22	R23	R24	R25	R26	R27	R28	R29	R30	R31	
		Qi:																																	
		value:	0	16	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	0	
-

Memory: 

		 	Mem_1	Mem_2	Mem_3	Mem_4	Mem_5	Mem_6	Mem_7	Mem_8

		Value: 	1	1	1	1	1	1	1	1
```







