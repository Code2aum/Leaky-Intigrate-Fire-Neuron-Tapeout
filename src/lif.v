`default_nettype none

module lif (
    input  wire [7:0] current,   // input current
    input  wire       clk,       // IOs: Input path   
    input  wire       rst_n,     // reset_n - low to reset
    output reg [7:0]  state,     // Dedicated outputs
    output wire       spike,     // IOs: Output path
);

    wire[7:0] next_state;
    reg [7:0]  threshold;


    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 0;
            threshold <= 200;
        end else begin
            state <= next_state;
        end
    end

    // next state logic 
    assign next_state = (state >> 1) + current;
    // spike logic
    assign spike = (next_state >= threshold);
    // // reset logic
    // assign state = (spike) ? 0 : next_state;

endmodule
