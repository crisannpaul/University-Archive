.386
.model flat, stdcall
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;includem biblioteci, si declaram ce functii vrem sa importam
includelib msvcrt.lib
extern exit: proc
extern malloc: proc
extern memset: proc
extern fread: proc
extern fopen: proc
extern fclose: proc
extern printf: proc

includelib canvas.lib
extern BeginDrawing: proc
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;declaram simbolul start ca public - de acolo incepe executia
public start
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;sectiunile programului, date, respectiv cod
.data
;aici declaram date
window_title DB "Supaplex",0
player_symbol EQU 'S'
wall_symbol EQU 'X'
food_symbol EQU 'F'
ball_symbol EQU 'B'
circuit_symbol EQU 'Z'
empty_symbol EQU 'O'
explosion_symbol EQU 'E'
score DD 0

; ---- PRINT FORMATS ----
format_elem DB "Elem: %c", 13, 10, 0
format_pos DB "Pos: %d", 13, 10, 0
format_wh DB "Width: %d, Height: %d", 13, 10, 0 
format_coords DB "Pos: %d, X: %d, Y: %d", 13, 10, 0
format_button_bounds DB "Right_x < %d | %d < Left_x", 13, 10, 0

; ---- INPUT FILE READING -----
filename db "level.txt", 0
mode_read db "r", 0
format db "%c ", 13, 10, 0
buffer db 0

; ----GRID----
cell_size EQU 40
grid_width EQU 11
grid_height EQU 11
grid DD 0 

; ----AREA----
area_width EQU cell_size * grid_width + 150
area_height EQU cell_size * grid_height
area DD 0

; ----POSITIONS TO REMEMBER----
player_pos DD 0

grid_pos DD 0
grid_x DD 0
grid_y DD 0

area_pos DD 0
area_x DD 0
area_y DD 0

middle_x EQU area_width / 2
middle_y EQU area_height / 2

right_x EQU (area_width*3) / 4
left_x EQU (area_width*1) / 4
up_y EQU (area_height*1) / 4
down_y EQU (area_height*3) / 4

score_x EQU 430
score_y EQU 50

; ----COUNTERS AND FLAGS----
counter DD 0 	; numara evenimentele de tip timer
game_over DD 0 

arg1 EQU 8
arg2 EQU 12
arg3 EQU 16
arg4 EQU 20

symbol_width EQU 10
symbol_height EQU 20
include digits.inc
include letters.inc
; ====GAME ASSETS====
include supaplex.inc
include wall.inc
include ball.inc
include empty.inc
include food.inc
include circuit.inc
include explosion.inc

.code
; ---- MAKE TEXT ----
; procedura make_text afiseaza o litera sau o cifra la coordonatele date
; arg1 - simbolul de afisat (litera sau cifra)
; arg2 - pointer la vectorul de pixeli
; arg3 - pos_x
; arg4 - pos_y
make_text proc
	push ebp
	mov ebp, esp
	pusha
	
	mov eax, [ebp+arg1] ; citim simbolul de afisat
	cmp eax, 'A'
	jl make_digit
	cmp eax, 'Z'
	jg make_digit
	sub eax, 'A'
	lea esi, letters
	jmp draw_text
make_digit:
	cmp eax, '0'
	jl make_space
	cmp eax, '9'
	jg make_space
	sub eax, '0'
	lea esi, digits
	jmp draw_text
make_space:	
	mov eax, 26 ; de la 0 pana la 25 sunt litere, 26 e space
	lea esi, letters
	
draw_text:
	mov ebx, symbol_width
	mul ebx
	mov ebx, symbol_height
	mul ebx
	add esi, eax
	mov ecx, symbol_height
bucla_simbol_linii:
	mov edi, [ebp+arg2] ; pointer la matricea de pixeli
	mov eax, [ebp+arg4] ; pointer la coord y
	add eax, symbol_height
	sub eax, ecx
	mov ebx, area_width
	mul ebx
	add eax, [ebp+arg3] ; pointer la coord x
	shl eax, 2 ; inmultim cu 4, avem un DWORD per pixel
	add edi, eax
	push ecx
	mov ecx, symbol_width
bucla_simbol_coloane:
	cmp byte ptr [esi], 0
	je simbol_pixel_alb
	mov dword ptr [edi], 0
	jmp simbol_pixel_next
simbol_pixel_alb:
	mov dword ptr [edi], 0FFFFFFh
simbol_pixel_next:
	inc esi
	add edi, 4
	loop bucla_simbol_coloane
	pop ecx
	loop bucla_simbol_linii
	popa
	mov esp, ebp
	pop ebp
	ret
make_text endp

; un macro ca sa apelam mai usor desenarea simbolului
make_text_macro macro symbol, drawArea, x, y
	push y
	push x
	push drawArea
	push symbol
	call make_text
	add esp, 16
endm
; ---- END MAKE TEXT ----

; ---- DRAW CELL ----
make_image proc
	push ebp
	mov ebp, esp
	pusha
	
	mov eax, [ebp+arg1]
	
	cmp eax, player_symbol
	je load_player
	cmp eax, wall_symbol
	je load_wall
	cmp eax, food_symbol
	je load_food
	cmp eax, ball_symbol
	je load_ball
	cmp eax, circuit_symbol
	je load_circuit
	cmp eax, empty_symbol
	je load_empty
	cmp eax, explosion_symbol
	je load_explosion
	
	jmp draw_image
	
load_player:
	lea esi, supa
	jmp draw_image
load_wall:
	lea esi, wall
	jmp draw_image
load_food:
	lea esi, food
	jmp draw_image	
load_ball:
	lea esi, ball
	jmp draw_image
load_circuit:
	lea esi, circuit
	jmp draw_image
load_empty:
	lea esi, empty
	jmp draw_image
load_explosion:
	lea esi, explosion
	jmp draw_image
	
draw_image:
	mov ecx, cell_size
loop_draw_lines:
	mov edi, [ebp+arg2] ; pointer to pixel area
	mov eax, [ebp+arg4] ; pointer to coordinate y
	
	add eax, cell_size 
	sub eax, ecx ; current line to draw (total - ecx)
	
	mov ebx, area_width
	mul ebx	; get to current line
	
	add eax, [ebp+arg3] ; get to coordinate x in current line
	shl eax, 2 ; multiply by 4 (DWORD per pixel)
	add edi, eax
	
	push ecx
	mov ecx, cell_size ; store drawing width for drawing loop
	
loop_draw_columns:

	push eax
	mov eax, dword ptr[esi] 
	mov dword ptr [edi], eax ; take data from variable to canvas
	pop eax
	
	add esi, 4
	add edi, 4 ; next dword (4 Bytes)
	
	loop loop_draw_columns
	
	pop ecx
	loop loop_draw_lines
	popa
	
	mov esp, ebp
	pop ebp
	ret
make_image endp

; simple macro to call the procedure easier
draw_cell macro symbol, drawArea, x, y
	push y
	push x
	push drawArea
	push symbol
	call make_image
	add esp, 16
endm
; ---- END DRAW CELL ----

horizontal_line macro x, y, len, color
local line_loop
	mov eax, y 			; EAX = y
	mov ebx, area_width	; EBX = x
	mul ebx 			; EAX = y * width
	add eax, x 			; EAX = y * width + x
	shl eax, 2			; EAX = (y * width + x) * 4
	add eax, area		; EAX = pixel
	
	mov ecx, len		
line_loop:						; while(len > 0)
	mov dword ptr[eax], color   ; draw pixel
	add eax, 4					; move to next one
	loop line_loop
endm

vertical_line macro x, y, len, color
local line_loop
	mov eax, y 			; EAX = y
	mov ebx, area_width	; EBX = x
	mul ebx 			; EAX = y * width
	add eax, x 			; EAX = y * width + x
	shl eax, 2			; EAX = (y * width + x) * 4
	add eax, area		; EAX = pixel
	
	mov ecx, len		
line_loop:						; while(len > 0)
	mov dword ptr[eax], color   ; draw pixel
	add eax, area_width*4		; move to next one
	loop line_loop
endm

; functia de desenare - se apeleaza la fiecare click
; sau la fiecare interval de 200ms in care nu s-a dat click
; arg1 - evt (0 - initializare, 1 - click, 2 - s-a scurs intervalul fara click)
; arg2 - x
; arg3 - y
draw proc
	push ebp
	mov ebp, esp
	pusha
	
	mov eax, [ebp+arg1]
	cmp eax, 1
	jz evt_click
	cmp eax, 2
	jz evt_timer ; nu s-a efectuat click pe nimic
	;mai jos e codul care intializeaza fereastra cu pixeli albi
	mov eax, area_width
	mov ebx, area_height
	mul ebx
	shl eax, 2
	push eax
	push 255
	push area
	call memset
	add esp, 12
	jmp draw_screen
	
evt_click_color:
	mov edi, area
	mov ecx, area_height
	mov ebx, [ebp+arg3]
	and ebx, 7
	inc ebx
bucla_linii:
	mov eax, [ebp+arg2]
	and eax, 0FFh
	; provide a new (random) color
	mul eax
	mul eax
	add eax, ecx
	push ecx
	mov ecx, area_width
bucla_coloane:
	mov [edi], eax
	add edi, 4
	add eax, ebx
	loop bucla_coloane
	pop ecx
	loop bucla_linii
	jmp draw_screen

evt_click:

	push ecx
	push eax				; Save registers
	push edx
	
	mov eax, [ebp+arg2]		; Get x
	
	cmp eax, right_x
	jg move_right			; Click on the right side => move right
	
	cmp eax, left_x			; Click on the left side => move left
	jl move_left
	
	mov eax, [ebp+arg3] 	; Get y
	
	cmp eax, up_y			
	jl move_up				; Click on the upper side => move up
	
	cmp eax, down_y
	jg move_down			; Click on the lower side => move down
	
	jmp no_move

move_up:
	mov eax, grid						; Get grid and player pos
	mov ecx, player_pos
	
	cmp dword ptr [eax+ecx*4-4*grid_width], 'X'	; Can't move if the next cell is X
	je no_move
	cmp dword ptr [eax+ecx*4-4*grid_width], 'B'	; Can't move if the next cell is B
	je no_move
	
	cmp dword ptr [eax+ecx*4-4*grid_width], 'F' ; Increment score if food
	jne no_food_up
	inc score
no_food_up:
	mov dword ptr [eax+ecx*4-4*grid_width], player_symbol	; Move player from pos A -> B
	mov dword ptr [eax+ecx*4], 'O'				; New pos gets player_symbol and the old one gets '0'
	
	sub ecx, grid_width					; Update player pos
	mov player_pos, ecx
	jmp no_move	

move_down:
	mov eax, grid						; Get grid and player pos
	mov ecx, player_pos
	
	cmp dword ptr [eax+ecx*4+4*grid_width], 'X'	; Can't move if the next cell is X
	je no_move
	cmp dword ptr [eax+ecx*4+4*grid_width], 'B'	; Can't move if the next cell is B
	je no_move
	
	
	cmp dword ptr [eax+ecx*4+4*grid_width], 'F' ; Increment score if food
	jne no_food_down
	inc score
no_food_down:
	mov dword ptr [eax+ecx*4+4*grid_width], player_symbol	; Move player from pos A -> B
	mov dword ptr [eax+ecx*4], 'O'				; New pos gets player_symbol and the old one gets '0'
	
	add ecx, grid_width					; Update player pos
	mov player_pos, ecx
	jmp no_move	
	
move_left:
	mov eax, grid						; Get grid and player pos
	mov ecx, player_pos
	
	cmp dword ptr [eax+ecx*4-4], 'X'	; Can't move if the next cell is X
	je no_move
	cmp dword ptr [eax+ecx*4-4], 'B'	; Can't move if the next cell is B
	je no_move
	
	cmp dword ptr [eax+ecx*4-4], 'F' ; Increment score if food
	jne no_food_left
	inc score
no_food_left:
	mov dword ptr [eax+ecx*4-4], player_symbol	; Move player from pos A -> B
	mov dword ptr [eax+ecx*4], 'O'		; New pos gets player_symbol and the old one gets '0'
	
	sub ecx, 1							; Update player pos
	mov player_pos, ecx
	jmp no_move
	
move_right:
	mov eax, grid						; Get grid and player pos
	mov ecx, player_pos
	
	cmp dword ptr [eax+ecx*4+4], 'X'	; Can't move if the next cell is X
	je no_move
	cmp dword ptr [eax+ecx*4+4], 'B'	; Can't move if the next cell is B
	je no_move

	cmp dword ptr [eax+ecx*4+4], 'F' ; Increment score if food
	jne no_food_right
	inc score
no_food_right:
	mov dword ptr [eax+ecx*4+4], player_symbol	; Move player from pos A -> B
	mov dword ptr [eax+ecx*4], 'O'		; New pos gets player_symbol and the old one gets '0'
	
	add ecx, 1							; Update player pos
	mov player_pos, ecx
	jmp no_move
	
no_move:
	pop edx
	pop eax				; Load registers
	pop ecx
	
	jmp draw_screen
	
evt_timer:
	cmp game_over, 1
	jne continue_game	; Wait 3 seconds before termination the program
	inc counter 		; Continue game if it's not over
	cmp counter, 15
	je init_grid
	
continue_game:
	inc counter
	cmp counter, 5		; Balls fall every 3 event timers
	jne draw_screen
	mov counter, 0

	push eax
	push ebx			; Save registers
	push ecx
	
	mov ecx, grid_height * grid_width	
	mov ebx, 0
check_grid:				
	mov eax, ebx
	shl eax, 2
	add eax, grid
	
	cmp dword ptr [eax], ball_symbol	; Check if current cell is ball
	jne skip
	cmp dword ptr [eax+4*grid_width], player_symbol	; Check if the next cell is player
	je ball_hit
	cmp dword ptr [eax+4*grid_width], empty_symbol	; Check if the next cell is empty
	jne skip
	
	mov dword ptr [eax], empty_symbol
	mov dword ptr [eax+4*grid_width], ball_symbol	; If next is empty, drop the ball
	jmp skip
	
ball_hit:
	mov dword ptr [eax], empty_symbol
	mov dword ptr [eax+4*grid_width], explosion_symbol	; Show explosion if ball hit the player
	mov game_over, 1 
	
skip:
	inc ebx				
	cmp ebx, ecx
	jl check_grid	
	
	pop ecx
	pop ebx				; Load registers
	pop eax
	
	jmp draw_screen

draw_screen:
	
	push ecx
	push eax				; Save registers
	push edx
	
	make_text_macro 'S', area, score_x, score_y
	make_text_macro 'C', area, score_x + 10, score_y
	make_text_macro 'O', area, score_x + 20, score_y
	make_text_macro 'R', area, score_x + 30, score_y
	make_text_macro 'E', area, score_x + 40, score_y
	
	mov ebx, 10		; Display score
	mov eax, score
	
	mov edx, 0	
	div ebx			; Unitati
	add edx, '0'
	make_text_macro edx, area, score_x + 30, score_y + 20

	mov edx, 0
	div ebx			; Zeci
	add edx, '0'
	make_text_macro edx, area, score_x + 20, score_y + 20
	
	mov edx, 0
	div ebx			; Sute
	add edx, '0'
	make_text_macro edx, area, score_x + 10, score_y + 20
	
	; ----for(i=0;i<W*H;i++)----
	mov ecx, grid_height * grid_width
	mov ebx, 0		
draw_matrix_loop:
	mov grid_pos, ebx	; Update pos
	push ebx
	push ecx			; Save registers
	
	mov eax, grid_pos
	mov ecx, grid_width
	mov edx, 0
	div ecx
	mov grid_y, eax		; Find y = pos/width
	
	mov eax, grid_pos
	mov ecx, grid_width
	mov edx, 0
	div ecx
	mov grid_x, edx		; Find x = pos%width
	
	mov eax, grid_x
	mov ebx, cell_size
	mul ebx
	mov area_x, eax		; Find area_x = x * cell_size
	
	mov eax, grid_y
	mov ebx, cell_size
	mul ebx
	mov area_y, eax		; Find area_y = y * cell_size
	
	mov eax, grid_pos
	shl eax, 2
	add eax, grid
	mov ebx, [eax]		; Get grid[x][y]
	
	; push ebx
	; push offset format_elem
	; call printf
	; add esp, 8
	
	draw_cell ebx, area, area_x, area_y
	; make_text_macro ebx, area, area_x, area_y	; Draw a cell at the specified cooords

	
	; push area_y
	; push area_x
	; push grid_pos		; Print stuff
	; push offset format_coords
	; call printf
	; add esp, 16
	
	pop ecx				; Load registers
	pop ebx
	inc ebx				
	cmp ebx, ecx
	jl draw_matrix_loop		; if(i <= W*H) loop
	
	vertical_line 0, 0, area_height, 0
	horizontal_line 0, 0, area_height, 0
	vertical_line area_height, 0, area_height, 0
	horizontal_line 0, area_height-1, area_height, 0
	
	
	pop edx
	pop eax				; Load registers
	pop ecx
	
final_draw:
	popa
	mov esp, ebp
	mov esp, ebp
	pop ebp
	ret
draw endp

start:
	; Allocate memory for the drawing area
	mov eax, area_width
	mov ebx, area_height
	mul ebx
	shl eax, 2
	push eax
	call malloc
	add esp, 4
	mov area, eax

init_grid:
	; Allocate memory for the game grid
	mov eax, grid_width
	mov ebx, grid_height
	mul ebx
	shl eax, 2
	push eax
	call malloc
	add esp, 4
	mov grid, eax
	
open_file:
	mov game_over, 0
	mov counter, 0
	push offset mode_read
	push offset filename
	call fopen
	add esp, 8
	mov esi, eax ;salvam pointer-ul la fisier
	
	; ----for(i=0;i<W*H;i++)----
	mov ecx, grid_height * grid_width
	mov ebx, 0
initialize_loop:
	push ecx			; Save registers

read_file:
	push esi 	;stream
	push 1 		;count
	push 1 		;size
	push offset buffer	
	call fread			
	xor eax, eax 		
	mov al, buffer	; Read one element in eax
	add esp, 16
	
	cmp eax, 13 	
	je read_file
	cmp eax, 10		; If (buffer = /n or /r) read again
	je read_file
	
	cmp eax, player_symbol				
	jne not_found			
	mov dword ptr [player_pos], ebx	; Remember player pos
	
not_found:
	mov ecx, grid
	mov dword ptr[ecx+ebx*4], eax	; Grid[x][y] = buffer
	
	pop ecx 			; Load registers
	inc ebx				
	cmp ebx, ecx
	jl initialize_loop	; if(i <= W*H) loop
	
close_file:
	push esi ;stream
	call fclose
	add esp, 4
	
	; apelam functia de desenare a ferestrei
	; typedef void (*DrawFunc)(int evt, int x, int y);
	; void __cdecl BeginDrawing(const char *title, int width, int height, unsigned int *area, DrawFunc draw);
	push offset draw
	push area
	push area_height
	push area_width
	push offset window_title
	call BeginDrawing
	add esp, 20
	
	;terminarea programului
end_program:
	push 0
	call exit
end start
