module uart_top (
    input wire clk,
    input wire rst,
    input wire send,
    input [7:0] data,
    input wire rx_pin,
    inout wire PS2_DATA,
    inout wire PS2_CLK,
    output wire tx_pin,
    output wire [7:0] rx_data,
    output wire [3:0] an,
    output wire [6:0] seg
);

    wire [7:0] send_data;
    reg send_trigger;
    wire tx_complete;

    wire send_debounced;
    wire send_one_pulse;

    wire rst_debounced;
    wire rst_one_pulse;
    wire rst_n;

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

    // 實例化 UART 發送器
    uart_tx uart_inst (
        .clk(clk),
        .rst_n(rst_n),
        .data(send_data),
        .tx_start(send_trigger),
        .tx(tx_pin),
        .tx_done(tx_complete)
    );

    // keyboard_top keyboard_top_inst (
    //     .PS2_DATA(PS2_DATA),
    //     .PS2_CLK(PS2_CLK),
    //     .rst(rst_n),
    //     .clk(clk),
    //     .ascii_code(rx_data)
    // );

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
        .ascii(send_data)
    );

    assign rx_data = last_change[7:0];

    // 測試資料發送邏輯
    always @(posedge clk) begin
        if (been_ready && key_down[last_change]) begin
            send_trigger <= 1'b1;
        end
        else
            send_trigger <= 1'b0;
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

    // always @(posedge clk) begin
    //     if (test_data != 8'h00)
    //         rx_data <= test_data;
    //     else
    //         rx_data <= 8'hFF;
    //     // if (!rst_n) begin
    //     //     rx_data <= 8'h00;
    //     // end else begin
    //     //     if (rx_done) begin
    //     //         rx_data <= test_data;
    //     //     end
    //     // end
    // end

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