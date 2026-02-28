`default_nettype none

module lif (
    input  wire [7:0] current,   // input current
    input  wire       clk,       // clock
    input  wire       rst_n,     // reset_n - low to reset
    output reg [7:0]  state,     // membrane potential output
    output wire       spike      // spike output (no trailing comma)
);

    localparam [7:0] THRESHOLD = 8'd200;

    wire [7:0] next_state;

    // next state: decay (leak) + integrate incoming current
    assign next_state = (state >> 1) + current;

    // spike fires when potential crosses threshold
    assign spike = (next_state >= THRESHOLD);

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= 8'd0;
        end else begin
            // reset membrane to 0 on spike, otherwise integrate
            state <= spike ? 8'd0 : next_state;
        end
    end

endmodule
