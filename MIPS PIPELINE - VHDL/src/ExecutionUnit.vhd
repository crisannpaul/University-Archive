----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/08/2022 04:54:51 PM
-- Design Name: 
-- Module Name: ExecUnit - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;
use IEEE.numeric_std.all;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity ExecutionUnit is
    Port ( read_data1 : in STD_LOGIC_VECTOR (15 downto 0);
           read_data2 : in STD_LOGIC_VECTOR (15 downto 0);
           alu_src : in STD_LOGIC;
           imm : in STD_LOGIC_VECTOR (15 downto 0);
           alu_op : in STD_LOGIC_VECTOR (2 downto 0);
           func : in STD_LOGIC_VECTOR (3 downto 0);
           alu_res : out STD_LOGIC_VECTOR (15 downto 0);
           zero : out STD_LOGIC);
end ExecutionUnit;

architecture Behavioral of ExecutionUnit is

signal a : STD_LOGIC_VECTOR (15 downto 0);
signal b : STD_LOGIC_VECTOR (15 downto 0);
signal temp : STD_LOGIC_VECTOR(31 downto 0);

begin

process(read_data1, read_data2, alu_src, alu_op, func, imm)
begin

a <= read_data1;
if alu_src = '0' then 
    b <= read_data2;
else 
    b <= imm; 
end if;

case alu_op is
    when "000" =>
       case func is
           when "0000" => alu_res <= a + b;
           when "0001" => alu_res <= a - b;
           when "0010" => alu_res <= a and b;
           when "0011" => alu_res <= a or b;
           when "0100" => alu_res <= a xor b;
           when "0101" => temp <= std_logic_vector(unsigned(a) * unsigned(b)); alu_res <= temp(15 downto 0);
           when "0110" => alu_res <= a(14 downto 0) & "0";
           when "0111" => alu_res <= "0" & a(15 downto 1);
           when others => NULL;
       end case;
    when "001" => alu_res <= a + b;
    when "010" => alu_res <= a + b;
    when "011" => alu_res <= a + b;
    when "100" => if a /= b  then alu_res <= x"0000"; end if;
    when "101" => alu_res <= a and b;
    when "110" => alu_res <= a or b;
    when others => NULL;
end case;

if a = b then 
    zero <= '1';
else
    zero <= '0';
end if;
    
end process;

end Behavioral;
