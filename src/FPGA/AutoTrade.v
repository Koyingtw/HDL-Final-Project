module AutoTrade_top(clk, buy, sell, add, sub, pair);
    input clk;
    input buy;
    input sell;
    input add;
    input sub;
    input pair;

    reg [7:0] amount[1:0];

    always @ (posedge clk) begin
        if (add) begin
            amount[pair] <= amount[pair] + 1;
        end
        if (sub) begin
            amount[pair] <= amount[pair] - 1;
        end
    end
endmodule