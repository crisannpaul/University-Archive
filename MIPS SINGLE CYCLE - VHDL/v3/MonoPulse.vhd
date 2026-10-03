----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 02/17/2022 12:14:02 PM
-- Design Name: 
-- Module Name: mip - Behavioral
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
------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity MonoPulse is
    Port ( clk : in STD_LOGIC;
           btn : in STD_LOGIC;
           enable : out STD_LOGIC);
end MonoPulse;

architecture Behavioral of MonoPulse is

signal count : std_logic_vector(31 downto 0) :=x"00000000";
signal Q1 : std_logic;
signal Q2 : std_logic;
signal Q3 : std_logic;

begin

enable <= Q2 AND (NOT Q3);

process(clk)
begin
    if rising_edge(clk) then 
        count <= count + 1;  
    end if;

    if rising_edge(clk) then 
        if count(15 downto 0) = x"FFFF" then 
            Q1 <= btn;
        end if;
    end if;

    if rising_edge(clk) then 
        Q2 <= Q1;
        Q3 <= Q2;
    end if;
end process;

end Behavioral;

