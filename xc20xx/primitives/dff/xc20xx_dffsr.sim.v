module XC20XX_DFFSR(
    D, S, R, // INPUTS
    K, // CLK
    Q // OUTPUTS
);

    input wire D;
    input wire S;
    input wire R;
    input wire K;

    output reg Q;

    // Internally the "DFFSR" is implemented as two D-latches back-to-back.
    // S and R are level based on the D-latches, but the back-to-back
    // implementation causes S and R to be edge triggered from Q's
    // point-of-view (as in, "only deasserts on clock edge").
    always @(posedge K, posedge S, posedge R) begin
        if(R) begin
            Q <= 0;
        end else if(S) begin
            Q <= 1;
        end else begin
            Q <= D;
        end
    end
endmodule
