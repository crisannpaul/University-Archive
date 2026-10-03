library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.numeric_std.all;


entity InstuctionFetch is
    Port ( clk : in STD_LOGIC;
           reset : in STD_LOGIC;
           enable : in STD_LOGIC;
           jump : in STD_LOGIC;
           pc_src : in STD_LOGIC;
           instruction_addr : in STD_LOGIC_VECTOR (15 downto 0);
           jump_addr : in STD_LOGIC_VECTOR (15 downto 0);
           branch_addr : in STD_LOGIC_VECTOR (15 downto 0);
           pc : out STD_LOGIC_VECTOR (15 downto 0);
           instruction : out STD_LOGIC_VECTOR (15 downto 0));
end InstuctionFetch;

architecture Behavioral of InstuctionFetch is

type mem_rom is array(0 to 15) of std_logic_vector(15 downto 0);

--Creating the instruction memory
--3 types of instructions: type R, type I, type J
--Type R structure : "opcode - 000" & "rs - 3 bits" & "rt - 3 bits" & "rd - 3 bits" & "func - 4 bits" 
--Type I structure : "opcode - 010" & "rs - 3 bits" & "rt - 3 bits" & "address / immediate - 7 bits"
--Type J structure : "opcode - 100" & "jump address - 13 bits"  

--signal instruction_memory : mem_rom := (
--$0 - 000 : $1 - 001 : $2 - 010 : $3 - 011 : $4 - 100

--B"000_000_000_000_0100",--0  --xor $0 $0 $0 
--B"000_001_001_001_0100",--1  --xor $1 $1 $1
--B"000_010_010_010_0100",--2  --xor $2 $2 $2 -- initializing registers
--B"000_011_011_011_0100",--3  --xor $3 $3 $3
--B"000_100_100_100_0100",--4  --xor $4 $4 $4

--B"001_000_100_0000011",--5  --add_immediate $0 $4 (5) ; R[rt] <= R[rs] + Ext(imm) --- n = imm
--B"001_000_001_0000001",--6  --add_immediate $0 $1 (1) ; R[rt] <= R[rs] + Ext(imm) --- for(i = 1; i <= n; i++)
--B"000_001_010_010_0000",--7 --add $1 $2 $2                                                               ---sum = sum + i
--B"100_001_100_0001010",--8  --branch_on_equal $1 $4 $branch_addr ; if(R[rs]==R[rt]) then PC=BranchAddr - IF i !=n BRANCH BACK UP
--B"111_000000000110",--9  --jump $jump_addr ; PC = 6
--B"011_000_000_0000000", --store_word $2 $1 (imm) ; MEM[R[rs] + Ext(imm)] <= R[rd] 
--others => x"0000"   
--);

signal instruction_memory : mem_rom := (

B"000_000_000_000_0100",--0  --xor $0 $0 $0 
B"000_001_001_001_0100",--1  --xor $1 $1 $1
B"000_010_010_010_0100",--2  --xor $2 $2 $2 -- initializing registers
B"000_011_011_011_0100",--3  --xor $3 $3 $3
B"000_100_100_100_0100",--4  --xor $4 $4 $4

B"001_100_000_0000101",--5  --add_immediate $4 $0 (5) ; n = imm
B"001_011_011_0000001",--6  --add_immediate $3 $0 (1) ; i = i + 1
B"000_100_011_100_0000",--7  --add $4 $3 $4 ; sum = sum + i
B"100_100_011_0001010",--8  --beq $4 $3 (10) ; if(i == n) exit loop
B"111_0000000000110",--  --jump (6) ; loop
B"011_011_000_0000001", --store_word $3 $0 (1) ; MEM[R[rs] + Ext(imm)] <= R[rd] 

others => x"0000"   
);

--signal instruction_memory : mem_rom := (

--B"000_000_000_000_0100",--0  --xor $0 $0 $0 
--B"000_001_001_001_0100",--1  --xor $1 $1 $1
--B"000_010_010_010_0100",--2  --xor $2 $2 $2 -- initializing registers
--B"000_011_011_011_0100",--3  --xor $3 $3 $3
--B"000_100_100_100_0100",--4  --xor $4 $4 $4

--B"001_100_000_0000101",--5  --add_immediate $4 $0 (5) ; n = imm
--B"001_100_001_0000111",--5  --add_immediate $4 $1 (5) ; n = imm
--B"000_100_011_100_0101",--6  --mul $0 $1 $0 ;
--B"000_100_011_100_0000",--7  --add $4 $3 $4 ; sum = sum + i
--B"100_100_011_0001010",--8  --beq $4 $3 (10) ; if(i == n) exit loop
--B"111_0000000000110",--  --jump (6) ; loop
--B"011_011_000_0000001", --store_word $3 $0 (1) ; MEM[R[rs] + Ext(imm)] <= R[rd] 

--others => x"0000"   
--);

signal pc_next : STD_LOGIC_VECTOR (15 downto 0);
signal mux : STD_LOGIC_VECTOR (1 downto 0);

begin

process(jump, pc_src)
begin 
    mux <= pc_src & jump;
    case mux is 
        when "00" => pc_next <= instruction_addr + 1;
        when "10" => pc_next <= branch_addr;
        when others => pc_next <= jump_addr;
    end case;
end process;

process(clk)
begin
    if rising_edge(clk) then
        if reset = '1' then 
            pc <= x"0000";
            instruction <= instruction_memory(0);
        else 
        if enable = '1' then
            pc <= pc_next;
            instruction <= instruction_memory(to_integer(unsigned(instruction_addr)));
        end if;
        end if;
    end if;
end process;

end Behavioral;