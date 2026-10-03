library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity WriteBack is
    Port ( memory_read_data : in STD_LOGIC_VECTOR (15 downto 0);
           alu_res : in STD_LOGIC_VECTOR (15 downto 0);
           mem_to_reg : in STD_LOGIC;
           data_out : out STD_LOGIC_VECTOR (15 downto 0));
end WriteBack;

architecture Behavioral of WriteBack is

begin

process(memory_read_data, alu_res, mem_to_reg)
begin
    case mem_to_reg is
        when '0' => data_out <= alu_res;
        when '1' => data_out <= memory_read_data;
    end case;
end process;

end Behavioral;
