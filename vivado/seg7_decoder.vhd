library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity seg7_decoder is
    Port(
        clk       : in  std_logic;
        rst       : in  std_logic;
        digit_in  : in  std_logic_vector(3 downto 0);
        seven_seg : out std_logic_vector(7 downto 0);
        enable    : out std_logic_vector(3 downto 0)
    );
end seg7_decoder;

architecture Behavioral of seg7_decoder is

    function digit_to_seg(digit : STD_LOGIC_VECTOR(3 downto 0))
        return STD_LOGIC_VECTOR is
    begin
        case digit is
            when "0000" => return "11000000";
            when "0001" => return "11111001";
            when "0010" => return "10100100";
            when "0011" => return "10110000";
            when "0100" => return "10011001";
            when "0101" => return "10010010";
            when "0110" => return "10000010";
            when "0111" => return "11111000";
            when "1000" => return "10000000";
            when "1001" => return "10010000";
            when others => return "10111111";
        end case;
    end function;

begin

    enable <= "1110";

    process(clk, rst)
    begin
        if rst = '1' then
            seven_seg <= (others => '1');
        elsif rising_edge(clk) then
            seven_seg <= digit_to_seg(digit_in);
        end if;
    end process;

end Behavioral;