`ifndef VPR_MUXES_LOGIC_MUX3
`define VPR_MUXES_LOGIC_MUX3

`include "../mux2/mux2.sim.v"

module MUX3(I0, I1, I2, S0, S1, O);
	input wire I0;
	input wire I1;
	input wire I2;
	input wire S0;
	input wire S1;
	output wire O;

	wire m0;
	wire m1;
	wire m2;
	wire m3;

	MUX2 mux0    (.I0(I0), .I1(I1), .S0(S0), .O(m0));
	MUX2 mux1    (.I0(m0), .I1(I2), .S0(S1), .O(O));
endmodule

`endif
