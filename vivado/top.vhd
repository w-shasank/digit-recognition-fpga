library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity top is
    Port (
        CLK1      : in  STD_LOGIC;
        RESET     : in  STD_LOGIC;
        seven_seg : out STD_LOGIC_VECTOR(7 downto 0);
        enable    : out STD_LOGIC_VECTOR(3 downto 0)
    );
end top;

architecture Behavioral of top is

  -- mlp inference component 
    component mlp_inference is
        port (
            ap_clk           : in  STD_LOGIC;
            ap_rst           : in  STD_LOGIC;
            ap_start         : in  STD_LOGIC;
            ap_done          : out STD_LOGIC;
            ap_idle          : out STD_LOGIC;
            ap_ready         : out STD_LOGIC;
            input_r_address0 : out STD_LOGIC_VECTOR(9 downto 0);
            input_r_ce0      : out STD_LOGIC;
            input_r_q0       : in  STD_LOGIC_VECTOR(7 downto 0);
            result           : out STD_LOGIC_VECTOR(31 downto 0)
        );
    end component;

    component seg7_decoder is
        port (
            clk      : in  STD_LOGIC;
            rst      : in  STD_LOGIC;
            digit_in : in  STD_LOGIC_VECTOR(3 downto 0);
            seven_seg: out STD_LOGIC_VECTOR(7 downto 0);
            enable   : out STD_LOGIC_VECTOR(3 downto 0)
        );
    end component;

    component pixel_rom is
        port (
            clk  : in  STD_LOGIC;
            addr : in  STD_LOGIC_VECTOR(9 downto 0);
            ce   : in  STD_LOGIC;
            data : out STD_LOGIC_VECTOR(7 downto 0)
        );
    end component;

    signal result_sig    : STD_LOGIC_VECTOR(31 downto 0);
    signal addr_sig      : STD_LOGIC_VECTOR(9 downto 0);
    signal ce_sig        : STD_LOGIC;
    signal pixel_data    : STD_LOGIC_VECTOR(7 downto 0);
    signal seven_seg_sig : STD_LOGIC_VECTOR(7 downto 0);
    signal enable_sig    : STD_LOGIC_VECTOR(3 downto 0);

begin

    u_mlp : mlp_inference
        port map (
            ap_clk           => CLK1,
            ap_rst           => RESET,
            ap_start         => '1',
            ap_done          => open,
            ap_idle          => open,
            ap_ready         => open,
            input_r_address0 => addr_sig,
            input_r_ce0      => ce_sig,
            input_r_q0       => pixel_data,
            result           => result_sig
        );

    u_rom : pixel_rom
        port map (
            clk  => CLK1,
            addr => addr_sig,
            ce   => ce_sig,
            data => pixel_data
        );

    u_seg7 : seg7_decoder
        port map (
            clk       => CLK1,
            rst       => RESET,
            digit_in  => result_sig(3 downto 0),
            seven_seg => seven_seg_sig,
            enable    => enable_sig
        );

    seven_seg <= seven_seg_sig;
    enable    <= enable_sig;

end Behavioral;
