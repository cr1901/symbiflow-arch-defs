/* XC20XX_LUT- The most-generic LUT implementation. The parameters match
config bits of the LUT's inputs/outputs as implemented in silicon. */

module XC20XX_LUT(
    A, B, C, D, // INPUTS
    Q, // FEEDBACK
    F, G // OUTPUTS
);
    parameter [7:0] F_INIT = 0;
    parameter [7:0] G_INIT = 0;
    parameter F_IN0 = 0; // 0- A, 1- B
    parameter F_IN1 = 0; // 0- B, 1- C
    parameter [1:0] F_IN2 = 2'b0; // 0- C, 1- D, 2- Q, 3- Invalid
    parameter G_IN0 = 0; // 0- A, 1- B
    parameter G_IN1 = 0; // 0- B, 1- C
    parameter [1:0] G_IN2 = 2'b0; // 0- C, 1- D, 2- Q, 3- Invalid
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
        if(F_IN0) begin
            assign F_in0 = B;
        end else begin
            assign F_in0 = A;
        end

        if(F_IN1) begin
            assign F_in1 = C;
        end else begin
            assign F_in1 = B;
        end

        case(F_IN2)
            2'd0: begin
                assign F_in2 = C;
            end

            2'd1: begin
                assign F_in2 = D;
            end

            2'd2: begin
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
        if(G_IN0) begin
            assign G_in0 = B;
        end else begin
            assign G_in0 = A;
        end

        if(G_IN1) begin
            assign G_in1 = C;
        end else begin
            assign G_in1 = B;
        end

        case(G_IN2)
            2'd0: begin
                assign G_in2 = C;
            end

            2'd1: begin
                assign G_in2 = D;
            end

            2'd2: begin
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
