.386
.model flat, stdcall
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;includem biblioteci, si declaram ce functii vrem sa importam
includelib msvcrt.lib
extern exit: proc
extern malloc: proc
extern memset: proc
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
window_title DB "Tapper",0
mat_x DD 0
mat_y DD 0
area_width EQU 500
area_height EQU 500
area DD 0

format_celula DB "%c ", 13, 10, 0 

marime_celula EQU 40
joc_width EQU 9
joc_heigth EQU 9
joc DD 	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
	DD	'M', 'M', 'M', 'M', 'M', 'M', 'M', 'C', 'B'
	DD	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
	DD	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
	DD	'M', 'M', 'M', 'M', 'M', 'M', 'M', 'O', 'B'
	DD	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
	DD	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
	DD	'M', 'M', 'M', 'M', 'M', 'M', 'M', 'O', 'B'
	DD	'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O', 'O'
		

counter DD 0 ; numara evenimentele de tip timer

arg1 EQU 8
arg2 EQU 12
arg3 EQU 16
arg4 EQU 20

symbol_width EQU 10
symbol_height EQU 20
include digits.inc
include letters.inc

.code
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
	jmp desenare_matrice
	
evt_click:
	
	
	
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
	jmp desenare_matrice
	
evt_timer:
	inc counter
	
desenare_matrice:
	push ecx 
	push ebx
	push eax
	
	mov mat_x, 0
	mov mat_y, 0
	
	mov ecx, area_width / marime_celula ; for de la 0 la 9
desenare_celule:
	push ecx
	push eax
	
	vertical_line mat_x, 0, 500, 00h ; desenare linii 
	horizontal_line 0, mat_y, 500, 00h
	
	; mov eax, mat_x
	; add eax, marime_celula
	; mov mat_x, eax 
	
	add mat_x, marime_celula 				; incrementare coordonate
	add mat_y, marime_celula
	 
	pop eax
	pop ecx
	
	loop desenare_celule
	
	pop eax
	pop ebx
	pop ecx

final_draw:
	popa
	mov esp, ebp
	pop ebp
	ret
draw endp

start:
	;alocam memorie pentru zona de desenat
	mov eax, area_width
	mov ebx, area_height
	mul ebx
	shl eax, 2
	push eax
	call malloc
	add esp, 4
	mov area, eax
	
	mov ebx, 0
	mov ecx, joc_width * joc_heigth
loop_print:
	mov eax, ebx
	shl eax, 2
	
	push dword ptr joc[eax]
	push offset format_celula
	call printf
	add esp, 8
	
	inc ebx
	cmp ebx, ecx
	jl loop_print
	
	
	;apelam functia de desenare a ferestrei
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
	push 0
	call exit
end start
