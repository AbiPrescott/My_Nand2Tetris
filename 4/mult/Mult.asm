// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

/*Pseudo Code

R2 = 0;
count = 0;

for (count=0; count<R0; count++)
{
	R2 = R0 + R1;
} 
*/ 


//R2 = 0
@R2
M=0

//count = 0
@count
M=0

(LOOP)		
	//if count == R0, jump to (END)
	@count
	D=M 
	@R0
	D=D-M

	@END 
	D;JEQ

	// else R1 + R2
	@R2
	D=M 
	@R1
	D=D+M

	//store result in R2 and increment counter
	@R2
	M=D 
	@count
	D=M+1
	@count
	M=D 
	@LOOP
	0;JMP

(END)
	@END
	0;JMP



