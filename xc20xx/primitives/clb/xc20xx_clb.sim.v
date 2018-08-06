/* XC20XX_CLB- The full CLB of the XC20XX-series. Configuration bits for
routing MUXes are based on Figure 4 of the XC2064 datasheet. The default values
are the topmost inputs to the MUXes. */

`include "../comb/xc20xx_clbcl.sim.v"
`include "../sync/xc20xx_clbse.sim.v"
`include "../routing/xmux/xmux.sim.v"
`include "../routing/ymux/ymux.sim.v"

module XC20XX_CLB(
    A, B, C, D, // INPUTS
    X, Y, // OUTPUTS
    K // CLK
);
    // XC20XX_CLB parameters
    parameter X_OUT = "F"; // F, G, Q
    parameter Y_OUT = "Q"; // F, G, Q

    // XC20XX_CLBCL parameters
    parameter [7:0] F_INIT = 0;
    parameter [7:0] G_INIT = 0;
    parameter F_IN0 = "A"; // A, B
    parameter F_IN1 = "B"; // B, C
    parameter F_IN2 = "C"; // C, D, Q
    parameter G_IN0 = "A"; // A, B
    parameter G_IN1 = "B"; // B, C
    parameter G_IN2 = "C"; // C, D, Q
    parameter MUX_FG = 0;

    // XC20XX_CLBSE parameters
    parameter S_IN = "A"; // A, F, NONE
    parameter CLK_IN = "K"; // K, C, G
    parameter CLK_POL = "POSITIVE"; // POSITIVE, NEGATIVE, NONE
    parameter MODE = "DFF"; // DFF, DLATCH
    parameter R_IN = "D"; // D, G, NONE


    input wire A;
    input wire B;
    input wire C;
    input wire D;

    output wire X;
    output wire Y;

    input wire K;

    wire F, G, Q;


    function [1:0] out_bits();
      input reg [7:0] OUT;

      case(OUT)
        "F": begin
            out_bits = 2'h0;
        end

        "G": begin
            out_bits = 2'h1;
        end

        "Q": begin
            out_bits = 2'h2;
        end

        default: begin
            out_bits = 2'h0;
        end
      endcase
    endfunction


    localparam [1:0] XMUX_BITS = out_bits(X_OUT);
    XMUX #(
        .S(XMUX_BITS)
    ) xmux(
        .F(F), .G(G), .Q(Q),
        .X_OUT(X)
    );

    localparam [1:0] YMUX_BITS = out_bits(Y_OUT);
    YMUX #(
        .S(YMUX_BITS)
    ) ymux(
        .F(F), .G(G), .Q(Q),
        .Y_OUT(Y)
    );


    XC20XX_CLBCL #(
        .F_INIT(F_INIT),
        .G_INIT(G_INIT),
        .F_IN0(F_IN0),
        .F_IN1(F_IN1),
        .F_IN2(F_IN2),
        .G_IN0(G_IN0),
        .G_IN1(G_IN1),
        .G_IN2(G_IN2),
        .MUX_FG(MUX_FG)
    ) CL (
        A, B, C, D,
        Q,
        F, G
    );

    XC20XX_CLBSE #(
        .S_IN(S_IN),
        .CLK_IN(CLK_IN),
        .CLK_POL(CLK_POL),
        .MODE(MODE),
        .R_IN(R_IN)
    ) SE (
        A, C, D,
        F, G,
        K,
        Q
    );

endmodule
