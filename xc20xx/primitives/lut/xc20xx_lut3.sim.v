(* blackbox *)
module XC20XX_LUT3(
    IN0, IN1, IN2, // INPUTS
    OUT // OUTPUTS
);

    input wire IN0;
    input wire IN1;
    input wire IN2;

    output wire OUT;

    parameter [7:0] INIT = 0;

    wire [3:0] s2 = IN2 ? INIT[ 7:4] : INIT[3:0];
	wire [1:0] s1 = IN1 ? s2[ 3:2] : s2[1:0];
	assign OUT = IN0 ? s1[1] : s1[0];
endmodule
