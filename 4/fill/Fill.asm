// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.




(START)		//initialize counters to 0 after every print cycle
	@SCREEN
	M=0

	@SCREENadd
	M=0

	@count
	M=0


(BLANKSTART)	//initialize SCREENadd pointer to address of SCREEN
	@SCREEN
	D=A
	M=0

	@SCREENadd
	M=D

(BLANK)		//paint screen white
	@SCREENadd
	M=M+1 
	A=M 
	M=0

	@count
	M=M+1 

	//if key is pressed, go to PRINT
	@KBD
	D=M 
	@PRINTSTART
	D;JNE

	//if done printing, go to start
	@8192
	D=A
	@count
	D=D-M 
	@START
	D;JEQ

	@BLANK
	0;JMP



(PRINTSTART)	//initialize SCREENadd pointer to address of SCREEN
	@SCREEN
	D=A
	M=-1

	@SCREENadd
	M=D

(PRINT)		//paint screen black
	@SCREENadd
	M=M+1 
	A=M 
	M=-1

	@count
	M=M+1

	//if key is not pressed, go to BLANK
	@KBD
	D=M 
	@BLANKSTART
	D;JEQ

	//if done printing, go the START
	@8192
	D=A
	@count
	D=D-M 
	@START
	D;JEQ


	@PRINT
	0;JMP



/*PSEUDO CODE:


SCREEN=0	//actual screen address
SCREENadd=0	//pointer that increments to address different screen address

count=0		//counter that counts to last of screen address

until (KBD=!0) 
{
 print nothing
} else {
	print black
	} 
*/ 






