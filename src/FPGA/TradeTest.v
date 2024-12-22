`timescale 1ns / 1ps
`include "AutoTrade.v"

module AutoTrade_top_tb();

    // 定義輸入輸出
    reg clk;
    reg pair;
    reg [8:0] input_data;
    reg input_done;
    wire buy;
    wire sell;
    wire close;
    reg rst_n;

    // 實例化被測試模組
    AutoTrade_top uut (
        .clk(clk),
        .rst_n(rst_n),
        .pair(pair),
        .input_data(input_data),
        .input_done(input_done),
        .buy(buy),
        .sell(sell),
        .close(close)
    );

    // 時鐘生成
    always begin
        #5 clk = ~clk;
    end

    // 測試過程
    initial begin
        $dumpfile("AutoTrade_top_tb.vcd");
        $dumpvars(0, AutoTrade_top_tb);
        // 初始化
        clk = 0;
        pair = 0;
        input_data = 0;
        input_done = 0;
        rst_n = 0;
        #10;
        rst_n = 1;

        // 測試 K 線數據輸入
        input_data = 8'h01;  // 開始信號
        input_done = 1;
        #10 input_done = 0;
        #10;

        // 模擬輸入 5 根 K 線數據
        for (integer i = 0; i < 5; i = i + 1) begin
            for (integer j = 0; j < 11; j = j + 1) begin
                input_data = $random & 8'hFF;  // 隨機數據
                input_done = 1;
                #10 input_done = 0;
                #10;
            end
        end

        // 測試獲利百分比輸入
        input_data = 8'h02;  // 獲利百分比信號
        input_done = 1;
        #10 input_done = 0;
        #10;

        input_data = 8'h00;  // 高位元
        input_done = 1;
        #10 input_done = 0;
        #10;

        input_data = 8'hFF;  // 低位元 (50%)
        input_done = 1;
        #10 input_done = 0;
        #10;

        // 等待處理完成
        #100;

        // 結束模擬
        $finish;
    end

    // 監控輸出
    always @(posedge clk) begin
        if (buy)
            $display("買入信號觸發");
        if (sell)
            $display("賣出信號觸發");
        if (close)
            $display("平倉信號觸發");
    end

endmodule
