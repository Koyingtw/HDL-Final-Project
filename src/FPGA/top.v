module top (
    input wire clk,
    input wire rst,
    input wire buy_but,
    input wire sell_but, 
    input wire close_but,
    input wire pair,
    input wire mode,
    input wire enable_trade,
    input [7:0] data,
    input wire rx_pin,
    inout wire PS2_DATA,
    inout wire PS2_CLK,
    output wire tx_pin,
    output reg [7:0] rx_data,
    output wire [3:0] an,
    output wire [6:0] seg
);

    wire [7:0] keyboard_data;
    reg [7:0] send_data;
    reg send_trigger;
    wire tx_complete;
    wire buy, sell, close, rst_n;

    begin // debounce, onepulse
        wire buy_debounced;

        debounce debounce_buy (
            .pb_debounced(buy_debounced),
            .pb(buy_but),
            .clk(clk)
        );

        onepulse onepulse_buy (
            .PB_debounced(buy_debounced),
            .CLK(clk),
            .PB_one_pulse(buy)
        );

        wire sell_debounced;

        debounce debounce_sell (
            .pb_debounced(sell_debounced),
            .pb(sell_but),
            .clk(clk)
        );

        onepulse onepulse_sell (
            .PB_debounced(sell_debounced),
            .CLK(clk),
            .PB_one_pulse(sell)
        );

        wire close_debounced;

        debounce debounce_close (
            .pb_debounced(close_debounced),
            .pb(close_but),
            .clk(clk)
        );

        onepulse onepulse_close (
            .PB_debounced(close_debounced),
            .CLK(clk),
            .PB_one_pulse(close)
        );

        wire rst_debounced;
        wire rst_one_pulse;

        debounce debounce_rst (
            .pb_debounced(rst_debounced),
            .pb(rst),
            .clk(clk)
        );

        onepulse onepulse_rst (
            .PB_debounced(rst_debounced),
            .CLK(clk),
            .PB_one_pulse(rst_one_pulse)
        );

        assign rst_n = ~rst_one_pulse;

        debounce debounce_inst (
            .pb_debounced(send_debounced),
            .pb(send),
            .clk(clk)
        );

        onepulse onepulse_inst (
            .PB_debounced(send_debounced),
            .CLK(clk),
            .PB_one_pulse(send_one_pulse)
        );
        
    end


    wire [511:0] key_down;
    wire [8:0] last_change;
    wire been_ready;

    KeyboardDecoder key_de (
        .key_down(key_down),
        .last_change(last_change),
        .key_valid(been_ready),
        .PS2_DATA(PS2_DATA),
        .PS2_CLK(PS2_CLK),
        .rst(rst),
        .clk(clk)
    );

    // assign rx_data = last_change[7:0];
    key_to_ascii key_to_ascii_inst (
        .clk(clk),
        .key(last_change),
        .ascii(keyboard_data)
    );

    // 實例化 UART 發送器
    uart_tx uart_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data(send_data),
        .tx_start(send_trigger),
        .tx(tx_pin),
        .tx_done(tx_complete)
    );
    // assign rx_data = last_change[7:0];

    reg wen, ren;
    reg [7:0] din1, din2;
    reg [1:0] argc;
    wire [7:0] dout;
    wire full, empty;
    Queue send_queue (
        .clk(clk),
        .rst_n(rst_n),
        .wen(wen),
        .ren(ren),
        .argc(argc),
        .din1(din1),
        .din2(din2),
        .dout(dout),
        .full(full),
        .empty(empty)
    );

    reg [31:0] cnt;
    wire buy_signal, sell_signal, close_signal;


    AutoTrade_top auto_trade_inst (
        .clk(clk),
        .rst_n(rst_n),
        .pair(pair),
        .mode(mode),
        .input_data(recv_data),
        .input_done(rx_done),
        .buy(buy_signal),
        .sell(sell_signal),
        .close(close_signal)
    );
    
    always @(posedge clk) begin
        if (!rst_n) begin
            argc <= 0;
            wen <= 1'b0;
            ren <= 1'b0;
            cnt <= 0;
        end
        if (been_ready && key_down[last_change]) begin
            argc <= 1;
            wen <= 1'b1;
            ren <= 1'b0;
            // din1 <= 8'h01;
            din1 <= keyboard_data;
            // din2 <= 8'h01;
            send_data <= 8'h01;
            send_trigger <= 1'b1;
        end
        else if (buy || sell || close || (enable_trade && (buy_signal || sell_signal || close_signal))) begin
            argc <= 1;
            wen <= 1'b1;
            ren <= 1'b0;
            din1 <= 8'h01 + pair;
            send_data <= 8'h02 * (buy || buy_signal) + 8'h03 * (sell || sell_signal) + 8'h04 * (close || close_signal);
            send_trigger <= 1'b1;
        end
        else if (enable_trade && cnt == 32'd10_000_000) begin
            argc <= 1;
            wen <= 1'b1;
            ren <= 1'b0;
            send_data <= 8'h06;
            din1 <= 8'h01 + pair;
            send_trigger <= 1'b1;
        end
        else if (enable_trade && cnt == 32'd110_000_000) begin
            argc <= 1;
            wen <= 1'b1;
            ren <= 1'b0;
            din1 <= 8'h01 + pair;
            send_data <= 8'h05;
            send_trigger <= 1'b1;
        end
        else if (!empty) begin
            ren <= 1'b1;
            wen <= 1'b0;
            send_trigger <= 1'b1;
            send_data <= dout;
        end
        else begin
            ren <= 1'b0;
            wen <= 1'b0;
            send_trigger <= 1'b0;
        end

        if (cnt == 32'd200_000_000)
            cnt <= 0;
        else
            cnt <= cnt + 1;
    end

    wire [7:0] recv_data;
    wire rx_done;

    uart_rx uart_rx_inst (
        .clk(clk),
        .rst_n(rst_n),
        .rx(rx_pin),
        .data(recv_data),
        .rx_done(rx_done)
    );

    
    reg hold;
    always @(posedge clk) begin
        if (!rst_n) begin
            rx_data <= 8'h00;
            hold <= 0;
        end
        else if (close_signal) begin
            rx_data <= rx_data;
            hold <= 1;
        end
        else if (rx_done && !hold) begin
            rx_data <= recv_data;
        end
    end


    wire [3:0] an;
    wire [6:0] seg;
    wire [3:0] num1, num2;

    assign num1 = data[7:4];
    assign num2 = data[3:0];

    seven_segment(
        .clk(clk),
        .num1(num1),
        .num2(num2),
        .seg(seg),
        .an(an)
    );

endmodule

module debounce (pb_debounced, pb, clk);
    output pb_debounced; // signal of a pushbutton after being debounced
    input pb; // signal from a pushbutton
    input clk;
    reg [3:0] DFF; // use shift_reg to filter pushbutton bounce
    always @(posedge clk)
    begin
    DFF[3:1] <= DFF[2:0];
    DFF[0] <= pb;
    end
    assign pb_debounced = ((DFF == 4'b1111) ? 1'b1 : 1'b0);
endmodule

module onepulse (PB_debounced, CLK, PB_one_pulse);
    input PB_debounced;
    input CLK;
    output PB_one_pulse;
    reg PB_one_pulse;
    reg PB_debounced_delay;
    always @(posedge CLK) begin
    PB_one_pulse <= PB_debounced & (! PB_debounced_delay);
    PB_debounced_delay <= PB_debounced;
    end
endmodule

module seven_segment (
    input clk,
    input wire [3:0] num1,
    input wire [3:0] num2,
    output wire [6:0] seg,
    output wire [3:0] an
);

    reg [31:0] counter;
    always @(posedge clk) begin
        if (counter == 32'd2_000_000)
            counter  <= 0;
        else
            counter <= counter + 1;
    end

    assign an = ~(4'b1 << (counter / 1_000_000));
    wire [15:0] digit, _digit;

    assign digit = (an == 4'b1110) ? (1 << num2) : (1 << num1);

    assign _digit = ~digit;

    SymbolA symbolA (
        .num(digit),
        ._num(_digit),
        .out(seg[0])
    );

    SymbolB symbolB (
        .num(digit),
        ._num(_digit),
        .out(seg[1])
    );

    SymbolC symbolC (
        .num(digit),
        ._num(_digit),
        .out(seg[2])
    );

    SymbolD symbolD (
        .num(digit),
        ._num(_digit),
        .out(seg[3])
    );

    SymbolE symbolE (
        .num(digit),
        ._num(_digit),
        .out(seg[4])
    );

    SymbolF symbolF (
        .num(digit),
        ._num(_digit),
        .out(seg[5])
    );

    SymbolG symbolG (
        .num(digit),
        ._num(_digit),
        .out(seg[6])
    );
endmodule

module SymbolA(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[2], num[3],
            num[5], num[6], num[7], num[8], num[9], num[10],
            num[12] , num[14], num[15]);
endmodule

module SymbolB(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[1], num[2], num[3], num[4],
            num[7], num[8], num[9], num[10],
            num[13]);
endmodule

module SymbolC(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[1], num[3], num[4],
            num[5], num[6], num[7], num[8], num[9], num[10],
            num[11], num[13]);
endmodule

module SymbolD(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[2], num[3], 
            num[5], num[6], num[8],
            num[11], num[12], num[13], num[14]);
endmodule

module SymbolE(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[2],
            num[6], num[8], num[10],
            num[11], num[12], num[13], num[14], num[15]);
endmodule

module SymbolF(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[0], num[4],
            num[5], num[6], num[8], num[9], num[10],
            num[11], num[12], num[14], num[15]);
endmodule

module SymbolG(num, _num, out);
    input [16-1:0] num, _num;
    output out;

    nor and1(out, num[2], num[3], num[4],
            num[5], num[6], num[8], num[9], num[10],
            num[11], num[13], num[14], num[15]);
endmodule
