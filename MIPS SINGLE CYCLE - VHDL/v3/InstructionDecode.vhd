library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.numeric_std.all;

entity InstructionDecode is
    Port ( clk : in STD_LOGIC;
           enable : in STD_LOGIC;
           instruction : in STD_LOGIC_VECTOR (15 downto 0);
           reg_write : in STD_LOGIC;
           reg_dst : in STD_LOGIC;
           write_data : in STD_LOGIC_VECTOR (15 downto 0);
           read_data1 : out STD_LOGIC_VECTOR (15 downto 0);
           read_data2 : out STD_LOGIC_VECTOR (15 downto 0);
           ext_imm : out STD_LOGIC_VECTOR (15 downto 0);
           digits : out STD_LOGIC_VECTOR (15 downto 0);
           func : out STD_LOGIC_VECTOR (3 downto 0);
           sw : in STD_LOGIC_VECTOR (15 downto 0));
end InstructionDecode;

architecture Behavioral of InstructionDecode is

signal read_addr1 : STD_LOGIC_VECTOR (2 downto 0);
signal read_addr2 : STD_LOGIC_VECTOR (2 downto 0);
signal write_addr : STD_LOGIC_VECTOR (2 downto 0);

type mem_ram is array(0 to 15) of std_logic_vector(15 downto 0);
signal register_file : mem_ram := (others => x"0000");

begin

read_addr1 <= instruction(12 downto 10);
read_addr2 <=  instruction(9 downto 7);
func <= instruction(3 downto 0);
ext_imm <= "0000000000" & instruction(5 downto 0); 

process(instruction)
begin
    if reg_dst = '1' then 
        write_addr <= instruction(6 downto 4); 
    else 
        write_addr <= instruction(9 downto 7);  
    end if;
end process;

process(clk, enable)
begin
    if rising_edge(clk) and enable = '1' and reg_write = '1' then
        register_file(to_integer(unsigned(write_addr))) <= write_data;
    end if;
end process;

read_data1 <= register_file(to_integer(unsigned(read_addr1)));
read_data2 <= register_file(to_integer(unsigned(read_addr2)));

process(sw)
begin
    case sw(3 downto 0) is
        when "0000" => digits <= register_file(0);
        when "0001" => digits <= register_file(1);
        when "0010" => digits <= register_file(2);
        when "0011" => digits <= register_file(3);
        when "0100" => digits <= register_file(4);
        when "0101" => digits <= register_file(5);
        when others => digits <= x"FFFF";
    end case;
end process;
end Behavioral;
