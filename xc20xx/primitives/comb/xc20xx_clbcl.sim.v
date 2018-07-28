/* XC20XX_CLBCL- The combinational section of the CLB. The parameters match
config bits of the Combinational Logic sections's inputs/outputs as implemented
in silicon (as well as using a composite of Options 1, 2, and 3 of Figure 5
in the XC2064 datasheet as a guide). */

`include "../lut/xc20xx_lut3.sim.v"

`include "../routing/f0mux/f0mux.sim.v"
`include "../routing/f1mux/f1mux.sim.v"
`include "../routing/f2mux/f2mux.sim.v"
`include "../routing/g0mux/g0mux.sim.v"
`include "../routing/g1mux/g1mux.sim.v"
`include "../routing/g2mux/g2mux.sim.v"

module XC20XX_CLBCL(
    A, B, C, D, // INPUTS
    Q, // FEEDBACK
    F, G // OUTPUTS
);
    parameter [7:0] F_INIT = 0;
    parameter [7:0] G_INIT = 0;
    parameter MUX_FG = 0;

    input wire A;
    input wire B;
    input wire C;
    input wire D;

    input wire Q;

    output wire F;
    output wire G;

    wire F_in0, F_in1, F_in2, G_in0, G_in1, G_in2;
    wire F_out, G_out;


    F0MUX f0mux(
        .A(A), .B(B),
        .F_IN0(F_in0)
    );

    F1MUX f1mux(
        .B(B), .C(C),
        .F_IN1(F_in1)
    );

    F2MUX f2mux(
        .C(C), .D(D), .Q(Q),
        .F_IN2(F_in2)
    );


    G0MUX g0mux(
        .A(A), .B(B),
        .G_IN0(G_in0)
    );

    G1MUX g1mux(
        .B(B), .C(C),
        .G_IN1(G_in1)
    );

    G2MUX g2mux(
        .C(C), .D(D), .Q(Q),
        .G_IN2(G_in2)
    );


    XC20XX_LUT3 #(
        .INIT(F_INIT)
    ) LUT_F (
        F_in0, F_in1, F_in2,
        F_out
    );

    XC20XX_LUT3 #(
        .INIT(G_INIT)
    ) LUT_G (
        G_in0, G_in1, G_in2,
        G_out
    );


    generate if(MUX_FG) begin
        // FIXME: Verify G is in fact the top bits of a "LUT4".
        assign F = B ? G_out : F_out;
        assign G = B ? G_out : F_out;
    end else begin
        assign F = F_out;
        assign G = G_out;
    end endgenerate

endmodule
