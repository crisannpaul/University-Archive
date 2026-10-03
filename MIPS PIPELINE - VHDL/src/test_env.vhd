library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity test_env is
    Port ( clk : in STD_LOGIC;
           btn : in STD_LOGIC_VECTOR (4 downto 0);
           sw : in STD_LOGIC_VECTOR (15 downto 0);
           led : out STD_LOGIC_VECTOR (15 downto 0);
           an : out STD_LOGIC_VECTOR (3 downto 0);
           cat : out STD_LOGIC_VECTOR (6 downto 0));
end test_env;

architecture Behavioral of test_env is

signal enable, reset : std_logic;
signal pc_next, instruction_s, temp, imm : std_logic_vector(15 downto 0) := x"0000";
signal read_data1_s, read_data2_s, digits, alu_res_s, data_out, memory_read_data_s : std_logic_vector(15 downto 0);
signal func : std_logic_vector(3 downto 0);
signal  reg_dst, alu_src, jump, branch, mem_write, mem_to_reg, reg_write, zero, pc_src : std_logic;

signal reg1 : std_logic_vector(31 downto 0);
signal reg2 : std_logic_vector(76 downto 0);
signal reg3 : std_logic_vector(36 downto 0);
signal reg4 : std_logic_vector(36 downto 0);

begin

MPG1: entity work.MonoPulse(Behavioral) port map (clk, btn(0), enable);
MPG2: entity work.MonoPulse(Behavioral) port map (clk, btn(1), reset);

process(clk)
begin 
    reg1(31 downto 16) <= pc_next;
    reg1(15 downto 0) <= instruction_s;
    
    
    reg2(0) <= reg_dst;
    reg2(1) <= alu_src;
    reg2(2) <= mem_write;
    reg2(3) <= branch;
    reg2(4) <= mem_to_reg;
    reg2(5) <= reg_write;
    reg2(21 downto 6) <= reg1(31 downto 16);
    reg2(37 downto 22) <= read_data1_s;
    reg2(53 downto 38) <= read_data2_s;
    reg2(69 downto 54) <= imm; 
    reg2(73 downto 70) <= func;
    reg2(76 downto 74) <= reg1(15 downto 13);
    
    reg3(0) <=  reg2(2);
    reg3(1) <=  reg2(3);
    reg3(2) <=  reg2(4);
    reg3(3) <=  reg2(5);
    reg3(4) <= zero;
    reg3(20 downto 5) <= alu_res_s;
    reg3(36 downto 21) <= reg2(53 downto 38);
    
    reg4(0) <= reg3(2);
    reg4(1) <= reg3(3);
    reg4(17 downto 2) <= memory_read_data_s;
    reg4(33 downto 18) <= reg3(20 downto 5);
    
end process;

pc_src <= reg3(1) and reg3(4);

IF1: entity work.InstuctionFetch(Behavioral) port map (
    clk => clk, 
    reset => reset, 
    enable => enable, 
    jump => jump,
    pc_src => pc_src, 
    instruction_addr => pc_next , 
    jump_addr => imm,
    branch_addr =>  imm, 
    pc => pc_next, 
    instruction => instruction_s
);

CU1: entity work.ControlUnit(Behavioral) port map (reg1(15 downto 13),  reg_dst, alu_src, jump, branch, mem_write, mem_to_reg, reg_write);

ID1: entity work.InstructionDecode(Behavioral) port map (clk, enable,  reg1(15 downto 0), reg2(5), reg2(0), data_out, read_data1_s, read_data2_s, imm, temp, func, sw);

EX1: entity work.ExecutionUnit(Behavioral) port map (reg2(37 downto 22), reg2(53 downto 38),  reg2(1), reg2(69 downto 54),  reg2(76 downto 74), reg2(73 downto 70), alu_res_s, zero);

DM1: entity work.DataMemory(Behavioral) port map (clk, enable, reg3(20 downto 5),  reg3(36 downto 21),  reg3(0), memory_read_data_s);

WB1: entity work.WriteBack(Behavioral) port map (reg4(17 downto 2), reg4(33 downto 18), reg4(0), data_out);

SSD1: entity work.Display(Behavioral) port map (clk, digits(3 downto 0), digits(7 downto 4), digits(11 downto 8), digits(15 downto 12), cat, an);


digits <= temp;

--process(sw)
--begin
--    case sw(1 downto 0) is
--        when "00" => digits <= temp1;
--        when "01" => digits <= temp2;
--        when "10" => digits <= temp3;
--        when others => digits <= temp1;
--    end case;
--end process;
led(6) <= reg_dst;
led(5) <= alu_src; 
led(4) <= jump; 
led(3) <= branch;
led(2) <= mem_write;
led(1) <= mem_to_reg;
led(0) <= reg_write;

end Behavioral;
