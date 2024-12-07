`timescale 1ns/1ps

module Queue(clk, rst_n, wen, ren, argc, din1, din2, din3, din4, dout, full, empty);
    input clk;
    input rst_n;
    input wen, ren;
    input [1:0] argc;
    input [8-1:0] din1, din2, din3, din4;
    output [8-1:0] dout;
    output full, empty;

    reg [5:0] head, tail;
    reg [6:0] count;
    reg [7:0] mem [0:63];

    assign full = (count == 64) ? 1 : 0;
    assign empty = (count == 0) ? 1 : 0;
    assign dout = mem[tail];

    always @(posedge clk) begin
        if (!rst_n) begin
            head <= 0;
            tail <= 0;
            count <= 0;
        end 
        else begin     
            if (ren && !empty) begin
                tail <= tail + 1;
                count <= count - 1;
            end
            else if (wen && !full) begin
                mem[head] <= din1;
                if (argc >= 2)
                    mem[head + 1] <= din2;
                if (argc >= 3)
                    mem[head + 2] <= din3;
                head <= head + argc;
                count <= count + argc;
            end
        end
    end

endmodule
