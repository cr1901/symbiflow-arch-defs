module XC20XX_LUT4(
    IN0, IN1, IN2, IN3 // INPUTS
    OUT // OUTPUTS
);

    input wire IN0;
    input wire IN1;
    input wire IN2;
    input wire IN3;

    output wire OUT;

    parameter [15:0] INIT = 0;

    wire [7:0] s3 = IN3 ? INIT[15:8] : INIT[7:0]
    wire [3:0] s2 = IN2 ? s3[7:4] : s3[3:0];
	wire [1:0] s1 = IN1 ? s2[3:2] : s2[1:0];
	assign OUT = IN0 ? s1[1] : s1[0];
endmodule
