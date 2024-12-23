module AutoTrade_top(
    input clk,
    input rst_n,
    input pair,
    input mode,  // 模式選擇：0 = 原策略（改良版），1 = 簡單策略
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

    // 控制變數
    reg [3:0] state;
    reg [7:0] cnt;
    
    // 技術指標變數
    reg [31:0] ma5;
    reg [31:0] momentum;
    wire [2:0] index;
    assign index = cnt / 16;

    // 交易狀態變數
    reg in_position;
    reg is_long;
    reg [23:0] entry_price;
    reg [23:0] stop_loss_price;
    reg [23:0] take_profit_price;

    // 模式1相關變數
    wire prev_k_is_up;  // 記錄前一根K棒是否上漲
    reg k_start = 1;       // 標記新的K棒開始
    reg k_end;         // 標記K棒結束
    reg [31:0] counting = 0;
    reg [7:0] seconds = 0;

    assign prev_k_is_up = close_price[1] > open_price[1];

    always @(posedge clk) begin
        if (input_done && state == 1 && cnt == 0 && input_data != timestamp[0]) begin
            counting <= 0;
            seconds <= 0;
        end
        else begin
            if (counting == 100_000_000) begin
                counting <= 0;
                if (seconds + 1 == 60) begin
                    seconds <= 0;
                    k_start <= 0;
                end else begin
                    seconds <= seconds + 1;
                end
            end else begin
                counting <= counting + 1;
            end
        end
    end


    always @(posedge clk) begin
        if (!rst_n) begin
            state <= 4'd0;
            cnt <= 0;
            buy <= 0;
            sell <= 0;
            close <= 0;
            in_position <= 0;
            is_long <= 0;
            entry_price <= 0;
            k_start <= 1;
            k_end <= 0;
            counting <= 0;
            seconds <= 0;
        end
        else if (input_done || state[0] == 0) begin
            case (state)
                // 等待起始信號
                0: begin
                    cnt <= input_done;
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
                        if (cnt == 79) begin
                            state <= 2; 
                            cnt <= 0; 
                        end else begin 
                            cnt <= cnt + 1; 
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
                    end
                end

                // 計算交易訊號
                2: begin
                    if (!mode) begin
                        // 模式0：改良版策略
                        ma5 <= (close_price[0] + close_price[1] + close_price[2] + 
                               close_price[3] + close_price[4]) / 5;
                        momentum <= close_price[0] - close_price[1]; // 動量指標

                        if (!in_position) begin
                            if ((close_price[0] > ma5) + (momentum > 0) +
                                (volume[0] > volume[1] * 11 / 10) + // 成交量增加10%
                                (close_price[0] > high_price[1]) >= 3) begin // 突破高點
                                buy <= 1; sell <= 0; close <= 0;
                                in_position <= 1; is_long <= 1;
                                entry_price <= close_price[0];
                                stop_loss_price <= close_price[0] * 99 / 100; // 止損1%
                                take_profit_price <= close_price[0] * 102 / 100; // 止盈2%
                            end else if ((close_price[0] < ma5) + (momentum < 0) +
                                         (volume[0] > volume[1] * 11 / 10) +
                                         (close_price[0] < low_price[1]) >= 3) begin // 跌破低點
                                buy <= 0; sell <= 1; close <= 0;
                                in_position <= 1; is_long <= 0;
                                entry_price <= close_price[0];
                                stop_loss_price <= close_price[0] * 101 / 100; // 止損1%
                                take_profit_price <= close_price[0] * 98 / 100; // 止盈2%
                            end
                        end 
                        // else begin
                        //     if (is_long) begin
                        //         if (close_price[0] <= stop_loss_price || 
                        //             close_price[0] >= take_profit_price) begin
                        //             buy <= 0; sell <= 0; close <= 1;
                        //             in_position <= 0;
                        //         end
                        //     end else begin
                        //         if (close_price[0] >= stop_loss_price || 
                        //             close_price[0] <= take_profit_price) begin
                        //             buy <= 0; sell <= 0; close <= 1;
                        //             in_position <= 0;
                        //         end
                        //     end
                        // end
                    end 
                    state <= 0; // 回到等待狀態
                end

                // 讀取帳戶資料
                3: begin
                    if (input_done) begin
                        // 將接收到的無符號整數轉換為有符號整數
                        if (input_data > 8'd127) begin
                            profit_percent <= $signed(input_data) - 8'sd256;
                        end else begin
                            profit_percent <= $signed(input_data);
                        end

                        state <= 4;
                        cnt <= 0;
                    end
                end

                // 判斷是否強制平倉
                4: begin
                    if ($signed(profit_percent) <= -8'sd20 || $signed(profit_percent) >= 8'sd20) begin
                        buy <= 0;
                        sell <= 0;
                        close <= 1;
                        in_position <= 0;
                    end
                    state <= 0;
                end
            endcase
        end
    end
endmodule
