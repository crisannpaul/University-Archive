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

begin

MPG1: entity work.MonoPulse(Behavioral) port map (clk, btn(0), enable);
MPG2: entity work.MonoPulse(Behavioral) port map (clk, btn(1), reset);

pc_src <= branch and zero;

IF1: entity work.InstuctionFetch(Behavioral) port map (clk, reset, enable, jump, pc_src, pc_next , imm, imm, pc_next, instruction_s);

CU1: entity work.ControlUnit(Behavioral) port map (instruction_s(15 downto 13),  reg_dst, alu_src, jump, branch, mem_write, mem_to_reg, reg_write);

ID1: entity work.InstructionDecode(Behavioral) port map (clk, enable,  instruction_s, reg_write, reg_dst, data_out, read_data1_s, read_data2_s, imm, temp, func, sw);

EX1: entity work.ExecutionUnit(Behavioral) port map (read_data1_s, read_data2_s, alu_src, imm, instruction_s(15 downto 13), func, alu_res_s, zero);

DM1: entity work.DataMemory(Behavioral) port map (clk, enable, alu_res_s,  read_data2_s,  mem_write, memory_read_data_s);

WB1: entity work.WriteBack(Behavioral) port map (memory_read_data_s, alu_res_s, mem_to_reg, data_out);

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
