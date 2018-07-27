/* XC20XX_CLBCL- The combinational section of the CLB. The parameters match
config bits of the Combinational Logic sections's inputs/outputs as implemented
in silicon (as well as using a composite of Options 1, 2, and 3 of Figure 5
in the XC2064 datasheet as a guide). */

`include "../lut/xc20xx_lut3.sim.v"

module XC20XX_CLBCL(
    A, B, C, D, // INPUTS
    Q, // FEEDBACK
    F, G // OUTPUTS
);
    parameter [7:0] F_INIT = 0;
    parameter [7:0] G_INIT = 0;
    parameter F_IN0 = "A"; // A, B
    parameter F_IN1 = "B"; // B, C
    parameter F_IN2 = "C"; // C, D, Q
    parameter G_IN0 = "A"; // A, B
    parameter G_IN1 = "B"; // B, C
    parameter G_IN2 = "C"; // C, D, Q
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


    generate
        case(F_IN0)
            "B": begin
                assign F_in0 = B;
            end

            "A": begin
                assign F_in0 = A;
            end

            default: begin
                initial begin
                    $display("ERROR: F_IN0 must use A or B as input.");
                    $finish;
                end
            end
        endcase

        case(F_IN1)
            "C": begin
                assign F_in1 = C;
            end

            "B": begin
                assign F_in1 = B;
            end

            default: begin
                initial begin
                    $display("ERROR: F_IN1 must use C or B as input.");
                    $finish;
                end
            end
        endcase

        case(F_IN2)
            "C": begin
                assign F_in2 = C;
            end

            "D": begin
                assign F_in2 = D;
            end

            "Q": begin
                assign F_in2 = Q;
            end

            default: begin
                initial begin
                    $display("ERROR: F_IN2 must use C, D, or Q as input.");
                    $finish;
                end
            end
        endcase
    endgenerate

    generate
        case(G_IN0)
            "B": begin
                assign G_in0 = B;
            end

            "A": begin
                assign G_in0 = A;
            end

            default: begin
                initial begin
                    $display("ERROR: G_IN0 must use A or B as input.");
                    $finish;
                end
            end
        endcase

        case(G_IN1)
            "C": begin
                assign G_in1 = C;
            end

            "B": begin
                assign G_in1 = B;
            end

            default: begin
                initial begin
                    $display("ERROR: G_IN1 must use C or B as input.");
                    $finish;
                end
            end
        endcase

        case(G_IN2)
            "C": begin
                assign G_in2 = C;
            end

            "D": begin
                assign G_in2 = D;
            end

            "Q": begin
                assign G_in2 = Q;
            end

            default: begin
                initial begin
                    $display("ERROR: G_IN2 must use C, D, or Q as input.");
                    $finish;
                end
            end
        endcase
    endgenerate


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
