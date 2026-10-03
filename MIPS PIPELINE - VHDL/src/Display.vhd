----------------------------------------------------------------------------------
-- Company:
-- Engineer:
-- 
-- Create Date: 02/22/2022 04:18:37 PM
-- Design Name: 
-- Module Name: ssd - Behavioral
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

entity Display is
    Port ( clk : in STD_LOGIC;
              d0 : in STD_LOGIC_VECTOR (3 downto 0);
              d1 : in STD_LOGIC_VECTOR (3 downto 0);
              d2 : in STD_LOGIC_VECTOR (3 downto 0);
              d3 : in STD_LOGIC_VECTOR (3 downto 0);
              seg7 : out STD_LOGIC_VECTOR (6 downto 0);
              an : out STD_LOGIC_VECTOR (3 downto 0));              
end Display;

architecture Behavioral of Display is

signal counter : STD_LOGIC_VECTOR(15 downto 0) := x"0000";
signal mux1 : STD_LOGIC_VECTOR (3 downto 0) := x"0";
           
begin
           
process(clk)
    begin
    if rising_edge(clk) then 
        counter <= counter+ 1;  
    end if;
end process;

process(clk)
    begin
    if rising_edge(clk) then
        case counter(15 downto 14)  is
            when "00" => mux1 <= d0;
            when "01" => mux1 <= d1;
            when "10" => mux1 <= d2;
            when others => mux1 <= d3;
        end case;
    end if;
end process;

process(clk)
    begin
    if rising_edge(clk) then
        case counter(15 downto 14)  is
            when "00" => an <= "1110";
            when "01" => an <= "1101";
            when "10" => an <= "1011";
            when others => an <= "0111";
        end case;
    end if;
end process;

process(clk)
begin
    if rising_edge(clk) then 
           case mux1 is
            when "0000"=> seg7 <="1000000";  -- '0'
            when "0001"=> seg7 <="1111001";  -- '1'
            when "0010"=> seg7 <="0100100";  -- '2'
            when "0011"=> seg7 <="0110000";  -- '3'
            when "0100"=> seg7 <="0011001";  -- '4' 
            when "0101"=> seg7 <="0010010";  -- '5'
            when "0110"=> seg7 <="0000010";  -- '6'
            when "0111"=> seg7 <="1111000";  -- '7'
            when "1000"=> seg7 <="0000000";  -- '8'
            when "1001"=> seg7 <="0010000";  -- '9'
            when "1010"=> seg7 <="0001000";  -- 'A'
            when "1011"=> seg7 <="0000011";  -- 'B'
            when "1100"=> seg7 <="1000110";  -- 'C'
            when "1101"=> seg7 <="0100001";  -- 'd'
            when "1110"=> seg7 <="0000110";  -- 'E'
            when "1111"=> seg7 <="0001110";  -- 'F'
            when others =>  NULL;
        end case;
    end if;
end process;

end Behavioral;