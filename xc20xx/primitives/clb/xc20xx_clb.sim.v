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

    // XC20XX_CLBCL parameters
    parameter [7:0] F_INIT = 0;
    parameter [7:0] G_INIT = 0;
    parameter MUX_FG = 0;

    // XC20XX_CLBSE parameters
    parameter MODE = "DFF"; // DFF, DLATCH


    input wire A;
    input wire B;
    input wire C;
    input wire D;

    output wire X;
    output wire Y;

    input wire K;

    wire F, G, Q;


    XMUX xmux(
        .F(F), .G(G), .Q(Q),
        .X_OUT(X)
    );

    YMUX ymux(
        .F(F), .G(G), .Q(Q),
        .Y_OUT(Y)
    );


    XC20XX_CLBCL #(
        .F_INIT(F_INIT),
        .G_INIT(G_INIT),
        .MUX_FG(MUX_FG)
    ) CL (
        A, B, C, D,
        Q,
        F, G
    );

    XC20XX_CLBSE #(
        .MODE(MODE),
    ) SE (
        A, C, D,
        F, G,
        K,
        Q
    );

endmodule
