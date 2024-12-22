module AutoTrade_top(
    input clk,
    input rst_n,
    input pair,
    input [8:0] input_data,
    input input_done,
    output reg buy,
    output reg sell,
    output reg close
);

    // 資料儲存陣列
    reg [7:0] timestamp[4:0];
    reg [23:0] open_price[4:0];
    reg [23:0] close_price[4:0];
    reg [23:0] high_price[4:0];
    reg [23:0] low_price[4:0];
    reg [23:0] volume[4:0];
    reg [7:0] profit_percent;
    reg [255:0] traded;

    // 控制變數
    reg [3:0] state;
    reg [7:0] cnt;
    
    // 技術指標變數
    reg [31:0] ma5;
    reg [31:0] rsi;
    reg [31:0] prev_close;
    wire [2:0] index;
    assign index = cnt / 16;


    always @(posedge clk) begin
        if (!rst_n) begin
            state <= 4'd0;
            cnt <= 0;
            buy <= 0;
            sell <= 0;
            close <= 0;
            traded <= 0;
        end
        else if (input_done || state[0] == 0) begin
            case (state)
                // 等待起始信號
                0: begin
                    cnt <= input_done;
                    buy <= 0;
                    sell <= 0;
                    close <= 0;
                    if (input_data == 8'h01 && input_done) begin
                        state <= 1;
                    end
                    else if (input_data == 8'h02 && input_done) begin
                        state <= 3;
                        cnt <= 0;
                    end
                end

                // 讀取資料
                1: begin
                    if (input_done) begin
                        if (cnt == 0 && input_data != timestamp[0]) begin
                            traded[timestamp[1]] <= 0;
                        end
                        case (cnt % 16)
                            0: timestamp[index] <= input_data;
                            1: open_price[index][23:16] <= input_data;
                            2: open_price[index][15:8] <= input_data;
                            3: open_price[index][7:0] <= input_data;
                            4: high_price[index][23:16] <= input_data;
                            5: high_price[index][15:8] <= input_data;
                            6: high_price[index][7:0] <= input_data;
                            7: low_price[index][23:16] <= input_data;
                            8: low_price[index][15:8] <= input_data;
                            9: low_price[index][7:0] <= input_data;
                            10: close_price[index][23:16] <= input_data;
                            11: close_price[index][15:8] <= input_data;
                            12: close_price[index][7:0] <= input_data;
                            13: volume[index][23:16] <= input_data;
                            14: volume[index][15:8] <= input_data;
                            15: volume[index][7:0] <= input_data;
                        endcase

                        if (cnt == 79) begin
                            state <= 2;
                            cnt <= 0;
                        end
                        else begin
                            cnt <= cnt + 1;
                        end
                    end
                end

                // 計算交易訊號
                2: begin
                    // 計算5分鐘移動平均
                    ma5 <= (close_price[0] + close_price[1] + close_price[2] + 
                           close_price[3] + close_price[4]) / 5;
                    
                    // 交易邏輯
                    if (close_price[0] > ma5 && close_price[0] > open_price[0] &&
                        volume[0] > volume[1] && !traded[timestamp[0]]) begin
                        buy <= 1;
                        sell <= 0;
                        close <= 0;
                        traded[timestamp[0]] <= 1;
                    end
                    else if (close_price[0] < ma5 && close_price[0] < open_price[0] &&
                           volume[0] > volume[1] && traded[timestamp[0]]) begin
                        buy <= 0;
                        sell <= 1;
                        close <= 0;
                        traded[timestamp[0]] <= 1;
                    end
                    else begin
                        buy <= 0;
                        sell <= 0;
                        close <= 0;
                    end
                    
                    state <= 0;  // 回到等待狀態
                end

                // 讀取帳戶資料
                3: begin
                    if (input_done) begin
                        profit_percent <= $signed(input_data);
                        state <= 4;
                        cnt <= 0;
                    end
                end

                // 判斷是否平倉
                4: begin
                    if ($signed(profit_percent) <= -8'sd15 || $signed(profit_percent) >= 8'sd25) begin
                        buy <= 0;
                        sell <= 0;
                        close <= 1;
                    end
                    state <= 0;
                end
            endcase
        end
    end
endmodule
