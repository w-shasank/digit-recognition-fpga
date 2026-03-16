# Clock 100MHz
set_property -dict { PACKAGE_PIN "H4" IOSTANDARD LVCMOS33 } [get_ports { CLK1 }]
create_clock -period 10.000 -name CLK1 [get_ports CLK1]

# Reset button (S3)
set_property -dict { PACKAGE_PIN "M2" IOSTANDARD LVCMOS33 } [get_ports { RESET }]

# Seven segment segments
set_property -dict { PACKAGE_PIN "P4" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[0] }]
set_property -dict { PACKAGE_PIN "N4" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[1] }]
set_property -dict { PACKAGE_PIN "M3" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[2] }]
set_property -dict { PACKAGE_PIN "M5" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[3] }]
set_property -dict { PACKAGE_PIN "L5" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[4] }]
set_property -dict { PACKAGE_PIN "L6" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[5] }]
set_property -dict { PACKAGE_PIN "M6" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[6] }]
set_property -dict { PACKAGE_PIN "P5" IOSTANDARD LVCMOS33 } [get_ports { seven_seg[7] }]

# Seven segment digit enables (active low)
set_property -dict { PACKAGE_PIN "N3" IOSTANDARD LVCMOS33 } [get_ports { enable[0] }]
set_property -dict { PACKAGE_PIN "R1" IOSTANDARD LVCMOS33 } [get_ports { enable[1] }]
set_property -dict { PACKAGE_PIN "P1" IOSTANDARD LVCMOS33 } [get_ports { enable[2] }]
set_property -dict { PACKAGE_PIN "L4" IOSTANDARD LVCMOS33 } [get_ports { enable[3] }]


# LEDs for debugging result
set_property -dict { PACKAGE_PIN "K17" IOSTANDARD LVCMOS33 } [get_ports { LED[0] }]
set_property -dict { PACKAGE_PIN "J17" IOSTANDARD LVCMOS33 } [get_ports { LED[1] }]
set_property -dict { PACKAGE_PIN "L14" IOSTANDARD LVCMOS33 } [get_ports { LED[2] }]
set_property -dict { PACKAGE_PIN "L15" IOSTANDARD LVCMOS33 } [get_ports { LED[3] }]
