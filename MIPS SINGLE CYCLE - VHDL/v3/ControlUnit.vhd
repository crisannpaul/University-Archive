----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/09/2022 01:04:24 PM
-- Design Name: 
-- Module Name: CtrlUnit - Behavioral
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

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity ControlUnit is
    Port (  instruction_op_code : in STD_LOGIC_VECTOR (2 downto 0);
           reg_dst : out STD_LOGIC;
           alu_src : out STD_LOGIC;
           jump : out STD_LOGIC;
           branch : out STD_LOGIC;
           mem_write : out STD_LOGIC;
           mem_to_reg : out STD_LOGIC;
           reg_write : out STD_LOGIC);
end ControlUnit;

architecture Behavioral of ControlUnit is

begin

process(instruction_op_code)
begin 
case instruction_op_code is
    --Type R
    when "000" => reg_dst <= '0'; alu_src <= '0'; jump <= '0'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '1';
    
    --add_immediate
    when "001" => reg_dst <= '0'; alu_src <= '1'; jump <= '0'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '1';
    
    --load_word
    when "010" => reg_dst <= '0'; alu_src <= '1'; jump <= '0'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '1'; reg_write <= '1';
    
    --store_word
    when "011" => reg_dst <= '0'; alu_src <= '1'; jump <= '0'; branch <= '0'; mem_write <= '1'; mem_to_reg <= '0'; reg_write <= '0';
    
    --branch_on_equal
    when "100" => reg_dst <= '0'; alu_src <= '0'; jump <= '0'; branch <= '1'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '0';
    
    --and_immediate
    when "101" => reg_dst <= '0'; alu_src <= '1'; jump <= '0'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '1';
    
    --or_immediate
    when "110" => reg_dst <= '0'; alu_src <= '1'; jump <= '0'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '1';
    
    --jump
    when "111" => reg_dst <= '0'; alu_src <= '1'; jump <= '1'; branch <= '0'; mem_write <= '0'; mem_to_reg <= '0'; reg_write <= '0';
end case;
end process;

end Behavioral;
