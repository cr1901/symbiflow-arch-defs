/* XC20XX_CLBCL- The storage section of the CLB. The parameters correspond to
routing MUX config bits of Figure 6 of the XC2064 datasheet. */

`include "../dff/xc20xx_dffsr.sim.v"
`include "../dff/xc20xx_dlatch.sim.v"

module XC20XX_CLBSE(
    A, C, D, // INPUTS
    F, G, // FROM LUT OUTPUTS
    K, // CLK INPUT
    Q // OUTPUT
);
    parameter S_IN = "A"; // A, F, NONE
    parameter CLK_IN = "K"; // K, C, G
    parameter CLK_POL = "POSITIVE"; // POSITIVE, NEGATIVE, NONE
    parameter MODE = "DFF"; // DFF, DLATCH
    parameter R_IN = "D"; // D, F, NONE

    input wire A;
    input wire C;
    input wire D;

    input wire F;
    input wire G;

    input wire K;

    output wire Q;

    wire S_in, Clk_in, R_in, Clk_sig;


    generate
        case(S_IN)
            "A": begin
                assign S_in = A;
            end

            "F": begin
                assign S_in = F;
            end

            "NONE": begin
                assign S_in = 1'b0;
            end

            default: begin
                initial begin
                    $display("ERROR: S_IN must be A, F, or NONE.");
                    $finish;
                end
            end
        endcase
    endgenerate

    generate
        case(CLK_IN)
            "K": begin
                assign Clk_sig = K;
            end

            "C": begin
                assign Clk_sig = C;
            end

            "G": begin
                assign Clk_sig = G;
            end

            default: begin
                initial begin
                    $display("ERROR: CLK_IN must be K, C, or G.");
                    $finish;
                end
            end
        endcase

        case(CLK_POL)
            "POSITIVE": begin
                assign Clk_in = Clk_sig;
            end

            "NEGATIVE": begin
                assign Clk_in = ~Clk_sig;
            end

            "NONE": begin
                assign Clk_in = 1'b0;
            end

            default: begin
                initial begin
                    $display("ERROR: CLK_POL must be POSITIVE, NEGATIVE, or NONE.");
                    $finish;
                end
            end
        endcase
    endgenerate

    generate
        case(R_IN)
            "D": begin
                assign R_in = D;
            end

            "G": begin
                assign R_in = G;
            end

            "NONE": begin
                assign R_in = 1'b0;
            end

            default: begin
                initial begin
                    $display("ERROR: R_IN must be D, G, or NONE.");
                    $finish;
                end
            end
        endcase
    endgenerate

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
