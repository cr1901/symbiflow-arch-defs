/* XC20XX_CLBCL- The storage section of the CLB. The parameters correspond to
routing MUX config bits of Figure 6 of the XC2064 datasheet. */

`include "../dff/xc20xx_dffsr.sim.v"
`include "../dff/xc20xx_dlatch.sim.v"

`include "../routing/smux/smux.sim.v"
`include "../routing/clkinmux/clkinmux.sim.v"
`include "../routing/clkpolmux/clkpolmux.sim.v"
`include "../routing/rmux/rmux.sim.v"

module XC20XX_CLBSE(
    A, C, D, // INPUTS
    F, G, // FROM LUT OUTPUTS
    K, // CLK INPUT
    Q // OUTPUT
);
    parameter MODE = "DFF"; // DFF, DLATCH

    input wire A;
    input wire C;
    input wire D;

    input wire F;
    input wire G;

    input wire K;

    output wire Q;

    wire S_in, Clk_in, R_in, Clk_sig;


    SMUX smux(
        .A(A), .F(F), .GND(1'b0),
        .S_IN(S_in)
    );


    CLKINMUX clkinmux(
        .K(K), .C(C), .G(G),
        .CLK_SIG(Clk_sig)
    );


    CLKPOLMUX clkpolmux(
        .CLK(Clk_sig), .CLK_INV(~Clk_sig), .GND(1'b0),
        .CLK_IN(Clk_in)
    );


    RMUX rmux(
        .D(D), .G(G), .GND(1'b0),
        .R_IN(R_in)
    );


    generate
        case(MODE)
            "DFF": begin
                XC20XX_DFFSR se_dff(
                    F, S_in, R_in,
                    Clk_in,
                    Q
                );
            end

            // FIXME: Possibly use XC20XX_DLATCHSR primitive (to-be-written).
            "DLATCH": begin
                XC20XX_DLATCH se_latch(
                    F,
                    Clk_in,
                    Q
                );
            end

            default: begin
                initial begin
                    $display("ERROR: MODE must be DFF or DLATCH.");
                    $finish;
                end
            end
        endcase
    endgenerate
endmodule
