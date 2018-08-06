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
    parameter [31:0] S_IN = "A"; // A, F, NONE
    parameter CLK_IN = "K"; // K, C, G
    parameter CLK_POL = "POSITIVE"; // POSITIVE, NEGATIVE, NONE
    parameter [47:0] MODE = "DFF"; // DFF, DLATCH
    parameter [31:0] R_IN = "D"; // D, G, NONE

    input wire A;
    input wire C;
    input wire D;

    input wire F;
    input wire G;

    input wire K;

    output wire Q;

    wire S_in, Clk_in, R_in, Clk_sig;


    function [1:0] sin_bits();
      input reg [31:0] S_IN;

      case(S_IN)
        "A": begin
            sin_bits = 2'h0;
        end

        "F": begin
            sin_bits = 2'h1;
        end

        "NONE": begin
            sin_bits = 2'h2;
        end

        default: begin
            sin_bits = 2'h0;
        end
      endcase
    endfunction

    function [1:0] clkin_bits();
      input reg [7:0] CLK_IN;

      case(CLK_IN)
        "K": begin
            clkin_bits = 2'h0;
        end

        "C": begin
            clkin_bits = 2'h1;
        end

        "G": begin
            clkin_bits = 2'h2;
        end

        default: begin
            clkin_bits = 2'h0;
        end
      endcase
    endfunction

    function [1:0] clkpol_bits();
      input reg [63:0] CLK_POL;

      case(CLK_POL)
        "POSITIVE": begin
            clkpol_bits = 2'h0;
        end

        "NEGATIVE": begin
            clkpol_bits = 2'h1;
        end

        "NONE": begin
            clkpol_bits = 2'h2;
        end

        default: begin
            clkpol_bits = 2'h0;
        end
      endcase
    endfunction

    function [1:0] rin_bits();
      input reg [31:0] R_IN;

      case(R_IN)
        "A": begin
            rin_bits = 2'h0;
        end

        "G": begin
            rin_bits = 2'h1;
        end

        "NONE": begin
            rin_bits = 2'h2;
        end

        default: begin
            rin_bits = 2'h0;
        end
      endcase
    endfunction


    localparam SMUX_BITS = sin_bits(S_IN);
    SMUX #(
        .S(SMUX_BITS)
    ) smux(
        .A(A), .F(F), .GND(1'b0),
        .S_IN(S_in)
    );

    localparam CLKINMUX_BITS = clkin_bits(CLK_IN);
    CLKINMUX #(
        .S(CLKINMUX_BITS)
    ) clkinmux(
        .K(K), .C(C), .G(G),
        .CLK_SIG(Clk_sig)
    );

    localparam CLKPOLMUX_BITS = clkpol_bits(CLK_POL);
    CLKPOLMUX #(
        .S(CLKPOLMUX_BITS)
    ) clkpolmux(
        .CLK(Clk_sig), .CLK_INV(~Clk_sig), .GND(1'b0),
        .CLK_IN(Clk_in)
    );

    localparam RMUX_BITS = rin_bits(R_IN);
    RMUX #(
        .S(RMUX_BITS)
    ) rmux(
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
