module XC20XX_DLATCH(
    D, // INPUTS
    EN, // ENABLE
    Q // OUTPUTS
);

    input wire D;
    input wire EN;

    output reg Q;

    // FIXME: What is the default polarity of enable? Does Xilinx XACT
    // officially support S/R when using storage element as a D-Latch? Perhaps
    // split into more accurate XC20XX_DLATCHSR model. For now assume S/R
    // isn't used.
    always @(*) begin
        if(~EN) begin
            Q = D;
        end
    end
endmodule
