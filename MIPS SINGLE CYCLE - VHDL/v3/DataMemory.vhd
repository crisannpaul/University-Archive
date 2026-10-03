library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.numeric_std.all;

entity DataMemory is
    Port ( clk : in STD_LOGIC;
           enable : in STD_LOGIC;
           alu_res : in STD_LOGIC_VECTOR (15 downto 0);
           read_data2 : in STD_LOGIC_VECTOR (15 downto 0);
           mem_write : in STD_LOGIC;
           memory_read_data : out STD_LOGIC_VECTOR (15 downto 0));
end DataMemory;

architecture Behavioral of DataMemory is

type mem_rom is array(0 to 255) of std_logic_vector(15 downto 0);
signal data_memory : mem_rom;

signal adress : STD_LOGIC_VECTOR (15 downto 0);
signal write_data : STD_LOGIC_VECTOR (15 downto 0);
signal read_data : STD_LOGIC_VECTOR (15 downto 0);

begin

adress <= alu_res;
write_data <= read_data2;
memory_read_data <= data_memory(to_integer(unsigned(adress)));

process(clk, enable)
begin
if rising_edge(clk) and mem_write = '1' then
    data_memory(to_integer(unsigned(adress)))  <= read_data2 ;
end if;
end process;

end Behavioral;
