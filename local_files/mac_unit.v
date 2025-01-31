module mac_unit (
    input [3:0] A,          // 4-bit multiplicand
    input [3:0] B,          // 4-bit multiplier
    input [7:0] Acc,        // 8-bit accumulator input
    input clk,              // Clock signal
    input reset,            // Synchronous reset
    output reg [7:0] Result // 8-bit result
);
    // Internal signal for multiplication result
    wire [7:0] Product;

    // Perform multiplication
    assign Product = A * B;

    // MAC logic: Multiply and accumulate
    always @(posedge clk) begin
        if (reset) begin
            Result <= 8'b0; // Reset the result to 0
        end else begin
            Result <= Product + Acc; // Add Product to Accumulator
        end
    end

endmodule
