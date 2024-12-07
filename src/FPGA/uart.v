module uart_tx (
    input wire clk,           // FPGA 時鐘
    input wire rst_n,         // 重置信號
    input wire [7:0] data,    // 要傳送的資料
    input wire tx_start,      // 開始傳送信號
    output reg tx,            // UART 發送腳位
    output reg tx_done        // 傳送完成信號
);

    parameter CLK_FREQ = 100_000_000;  // 假設 FPGA 時鐘為 100MHz
    parameter BAUD_RATE = 9600;        // 鮑率設定
    parameter BIT_COUNTER_MAX = CLK_FREQ/BAUD_RATE;

    reg [3:0] bit_counter;    // 位元計數器
    reg [15:0] baud_counter;  // 鮑率計數器
    reg [7:0] tx_data;        // 傳送資料暫存
    reg tx_active;            // 傳送狀態

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            tx <= 1'b1;
            tx_done <= 1'b0;
            bit_counter <= 0;
            baud_counter <= 0;
            tx_active <= 1'b0;
        end else begin
            if (tx_start && !tx_active) begin
                tx_active <= 1'b1;
                tx_data <= data;
                bit_counter <= 0;
                baud_counter <= 0;
                tx_done <= 1'b0;
            end

            if (tx_active) begin
                if (baud_counter < BIT_COUNTER_MAX) begin
                    baud_counter <= baud_counter + 1;
                end else begin
                    baud_counter <= 0;
                    
                    if (bit_counter == 0)
                        tx <= 1'b0;  // 起始位
                    else if (bit_counter <= 8)
                        tx <= tx_data[bit_counter-1];  // 資料位
                    else if (bit_counter == 9)
                        tx <= 1'b1;  // 停止位
                    else begin
                        tx_active <= 1'b0;
                        tx_done <= 1'b1;
                    end
                    
                    if (bit_counter <= 9)
                        bit_counter <= bit_counter + 1;
                end
            end
        end
    end
endmodule

module uart_rx (
    input wire clk,           // FPGA 時鐘
    input wire rst_n,         // 重置信號
    input wire rx,            // UART 接收腳位
    output reg [7:0] data,    // 接收到的資料
    output reg rx_done        // 接收完成信號
);

    parameter CLK_FREQ = 100_000_000;  // 100MHz
    parameter BAUD_RATE = 9600;
    parameter BIT_COUNTER_MAX = CLK_FREQ/BAUD_RATE;
    parameter HALF_BIT_COUNTER = BIT_COUNTER_MAX/2;

    reg [3:0] bit_counter;
    reg [15:0] baud_counter;
    reg rx_active;
    reg [7:0] rx_data;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            data <= 8'h00;
            rx_done <= 1'b0;
            bit_counter <= 0;
            baud_counter <= 0;
            rx_active <= 1'b0;
        end else begin
            rx_done <= 1'b0;
            
            if (!rx_active && !rx) begin  // 檢測起始位
                rx_active <= 1'b1;
                baud_counter <= 0;
                bit_counter <= 0;
            end

            if (rx_active) begin
                if (baud_counter < BIT_COUNTER_MAX) begin
                    baud_counter <= baud_counter + 1;
                end else begin
                    baud_counter <= 0;
                    
                    if (bit_counter < 8) begin
                        rx_data[bit_counter] <= rx;
                        bit_counter <= bit_counter + 1;
                    end else begin
                        if (rx) begin  // 檢查停止位
                            data <= rx_data;
                            rx_done <= 1'b1;
                        end
                        rx_active <= 1'b0;
                    end
                end
            end
        end
    end
endmodule