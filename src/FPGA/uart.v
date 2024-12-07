module uart_tx (
    input wire clk,           
    input wire rst_n,         
    input wire [7:0] data,    
    input wire tx_start,      
    output reg tx,            
    output reg tx_done,
    output reg [7:0] output_data
);

    parameter CLK_FREQ = 100_000_000;  
    parameter BAUD_RATE = 9600;        
    parameter BIT_COUNTER_MAX = CLK_FREQ/BAUD_RATE;
    parameter QUEUE_MAX_SIZE = 64;      // 設定佇列最大容量

    reg [3:0] bit_counter;    
    reg [15:0] baud_counter;  
    reg [7:0] tx_data;        
    reg tx_active;            
    
    // 定義有限大小的傳送佇列
    reg wen, ren;
    reg [7:0] din;
    wire [7:0] dout;
    wire full, empty;
    Queue sending_queue (
        .clk(clk),
        .rst_n(rst_n),
        .wen(wen),
        .ren(ren),
        .argc(1),
        .din1(din),        
        .dout(dout),
        .full(full),
        .empty(empty)
    );

    // 處理輸入資料的佇列
    always @(posedge clk) begin
        if (tx_start && !full) begin
            // 將新資料加入佇列
            wen <= 1'b1;
            din <= data;
        end
        else begin
            wen <= 1'b0;
    
        end
    end

    // UART 傳送邏輯
    always @(posedge clk) begin
        if (data != 0)
            output_data <= dout;
        else 
            output_data <= output_data;
        if (!rst_n) begin
            tx <= 1'b1;
            tx_done <= 1'b0;
            bit_counter <= 0;
            baud_counter <= 0;
            tx_active <= 1'b0;
        end 
        else begin
            if (!tx_active && !empty) begin
                tx_active <= 1'b1;
                tx_data <= dout;  // 讀取佇列中的第一筆資料
                ren <= 1'b1;    // 移除已讀取的資料
                bit_counter <= 0;
                baud_counter <= 0;
                tx_done <= 1'b0;
            end
            else begin
                ren <= 1'b0;
            end

            if (tx_active) begin
                if (baud_counter < BIT_COUNTER_MAX) begin
                    baud_counter <= baud_counter + 1;
                end else begin
                    baud_counter <= 0;
                    
                    if (bit_counter == 0)
                        tx <= 1'b0;  
                    else if (bit_counter <= 8)
                        tx <= tx_data[bit_counter-1];  
                    else if (bit_counter == 9)
                        tx <= 1'b1;  
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