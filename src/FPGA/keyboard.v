module keyboard_top(
    inout wire PS2_DATA,
    inout wire PS2_CLK,
    input wire rst,
    input wire clk,
    output wire [7:0] ascii_code
    );

    wire [7:0] ASCII[8:0];
    
    parameter [8:0] LEFT_SHIFT_CODES  = 9'b0_0001_0010;
    parameter [8:0] RIGHT_SHIFT_CODES = 9'b0_0101_1001;
    parameter [8:0] KEY_CODES_00 = 9'b0_0100_0101; // 0 => 45
    parameter [8:0] KEY_CODES_01 = 9'b0_0001_0110; // 1 => 16
    parameter [8:0] KEY_CODES_02 = 9'b0_0001_1110; // 2 => 1E
    parameter [8:0] KEY_CODES_03 = 9'b0_0010_0110; // 3 => 26
    parameter [8:0] KEY_CODES_04 = 9'b0_0010_0101; // 4 => 25
    parameter [8:0] KEY_CODES_05 = 9'b0_0010_1110; // 5 => 2E
    parameter [8:0] KEY_CODES_06 = 9'b0_0011_0110; // 6 => 36
    parameter [8:0] KEY_CODES_07 = 9'b0_0011_1101; // 7 => 3D
    parameter [8:0] KEY_CODES_08 = 9'b0_0011_1110; // 8 => 3E
    parameter [8:0] KEY_CODES_09 = 9'b0_0100_0110; // 9 => 46
        
    parameter [8:0] KEY_CODES_10 = 9'b0_0111_0000; // right_0 => 70
    parameter [8:0] KEY_CODES_11 = 9'b0_0110_1001; // right_1 => 69
    parameter [8:0] KEY_CODES_12 = 9'b0_0111_0010; // right_2 => 72
    parameter [8:0] KEY_CODES_13 = 9'b0_0111_1010; // right_3 => 7A
    parameter [8:0] KEY_CODES_14 = 9'b0_0110_1011; // right_4 => 6B
    parameter [8:0] KEY_CODES_15 = 9'b0_0111_0011; // right_5 => 73
    parameter [8:0] KEY_CODES_16 = 9'b0_0111_0100; // right_6 => 74
    parameter [8:0] KEY_CODES_17 = 9'b0_0110_1100; // right_7 => 6C
    parameter [8:0] KEY_CODES_18 = 9'b0_0111_0101; // right_8 => 75
    parameter [8:0] KEY_CODES_19 = 9'b0_0111_1101; // right_9 => 7D

    parameter [8:0] KEY_CODES_Q = 9'h15;
    parameter [8:0] KEY_CODES_W = 9'h1D;
    parameter [8:0] KEY_CODES_E = 9'h24;
    parameter [8:0] KEY_CODES_R = 9'h2D;
    parameter [8:0] KEY_CODES_T = 9'h2C;
    parameter [8:0] KEY_CODES_Y = 9'h35;
    parameter [8:0] KEY_CODES_U = 9'h3C;
    parameter [8:0] KEY_CODES_I = 9'h43;
    parameter [8:0] KEY_CODES_O = 9'h44;
    parameter [8:0] KEY_CODES_P = 9'h4D;
    parameter [8:0] KEY_CODES_A = 9'h1C;
    parameter [8:0] KEY_CODES_S = 9'h1B;
    parameter [8:0] KEY_CODES_D = 9'h23;
    parameter [8:0] KEY_CODES_F = 9'h2B;
    parameter [8:0] KEY_CODES_G = 9'h34;
    parameter [8:0] KEY_CODES_H = 9'h33;
    parameter [8:0] KEY_CODES_J = 9'h3B;
    parameter [8:0] KEY_CODES_K = 9'h42;
    parameter [8:0] KEY_CODES_L = 9'h4B;
    parameter [8:0] KEY_CODES_Z = 9'h1A;
    parameter [8:0] KEY_CODES_X = 9'h22;
    parameter [8:0] KEY_CODES_C = 9'h21;
    parameter [8:0] KEY_CODES_V = 9'h2A;
    parameter [8:0] KEY_CODES_B = 9'h32;
    parameter [8:0] KEY_CODES_N = 9'h31;
    parameter [8:0] KEY_CODES_M = 9'h3A;
    parameter [8:0] KEY_CODES_SPACE = 9'h29;

    assign ASCII[9'h1C] = 8'h41; // A
    assign ASCII[9'h32] = 8'h42; // B
    assign ASCII[9'h21] = 8'h43; // C
    assign ASCII[9'h23] = 8'h44; // D
    assign ASCII[9'h24] = 8'h45; // E
    assign ASCII[9'h2B] = 8'h46; // F
    assign ASCII[9'h34] = 8'h47; // G
    assign ASCII[9'h33] = 8'h48; // H
    assign ASCII[9'h43] = 8'h49; // I
    assign ASCII[9'h3B] = 8'h4A; // J
    assign ASCII[9'h42] = 8'h4B; // K
    assign ASCII[9'h4B] = 8'h4C; // L
    assign ASCII[9'h3A] = 8'h4D; // M
    assign ASCII[9'h31] = 8'h4E; // N
    assign ASCII[9'h44] = 8'h4F; // O
    assign ASCII[9'h4D] = 8'h50; // P
    assign ASCII[9'h15] = 8'h51; // Q
    assign ASCII[9'h2D] = 8'h52; // R
    assign ASCII[9'h1B] = 8'h53; // S
    assign ASCII[9'h2C] = 8'h54; // T
    assign ASCII[9'h3C] = 8'h55; // U
    assign ASCII[9'h2A] = 8'h56; // V
    assign ASCII[9'h1D] = 8'h57; // W
    assign ASCII[9'h22] = 8'h58; // X
    assign ASCII[9'h35] = 8'h59; // Y
    assign ASCII[9'h1A] = 8'h5A; // Z

    assign ASCII[9'h29] = 8'h20; // SPACE

    assign ASCII[9'h45] = 8'h30; // 0
    assign ASCII[9'h16] = 8'h31; // 1
    assign ASCII[9'h1E] = 8'h32; // 2
    assign ASCII[9'h26] = 8'h33; // 3
    assign ASCII[9'h25] = 8'h34; // 4
    assign ASCII[9'h2E] = 8'h35; // 5
    assign ASCII[9'h36] = 8'h36; // 6
    assign ASCII[9'h3D] = 8'h37; // 7
    assign ASCII[9'h3E] = 8'h38; // 8
    assign ASCII[9'h46] = 8'h39; // 9

    
    reg [15:0] nums, next_nums;
    reg [3:0] key_num;
    reg [9:0] last_key;
    
    wire shift_down;
    wire [511:0] key_down;
    wire [8:0] last_change;
    wire been_ready;
    
    assign shift_down = (key_down[LEFT_SHIFT_CODES] == 1'b1 || key_down[RIGHT_SHIFT_CODES] == 1'b1) ? 1'b1 : 1'b0;
    
    KeyboardDecoder key_de (
        .key_down(key_down),
        .last_change(last_change),
        .key_valid(been_ready),
        .PS2_DATA(PS2_DATA),
        .PS2_CLK(PS2_CLK),
        .rst(rst),
        .clk(clk)
    );

    assign ascii_code = last_change[7:0];


    always @ (posedge clk) begin
        // ascii_code <= ASCII[last_change];
        // ascii_code <= last_change[7:0];
        // if (key_down[last_change]) begin
        //     ascii_code <= last_change[7:0];
        // end
        // else begin
        //     ascii_code <= ascii_code;
        // end
        // if (rst) begin
        //     ascii_code <= 8'h00;
        // end else if (been_ready && key_down[last_change]) begin
        //     if (ASCII[last_change] != 8'h00) begin
        //         ascii_code <= ASCII[last_change];
        //     end
        //     else
        //         ascii_code <= ascii_code;
        // end
        // else
        //     ascii_code <= ascii_code;
        // if (last_change != 9'd0) begin
        //     ascii_code <= last_change[7:0];
        // end
        // else
        //     ascii_code <= ascii_code;
    end

    
endmodule


module key_to_ascii(clk, key, ascii);
    input clk;
    input [8:0] key;
    output reg [7:0] ascii;

    always @ (posedge clk) begin
        case(key[7:0]) 
            8'h1C: ascii <= 8'h41; // A
            8'h32: ascii <= 8'h42; // B
            8'h21: ascii <= 8'h43; // C
            8'h23: ascii <= 8'h44; // D
            8'h24: ascii <= 8'h45; // E
            8'h2B: ascii <= 8'h46; // F
            8'h34: ascii <= 8'h47; // G
            8'h33: ascii <= 8'h48; // H
            8'h43: ascii <= 8'h49; // I
            8'h3B: ascii <= 8'h4A; // J
            8'h42: ascii <= 8'h4B; // K
            8'h4B: ascii <= 8'h4C; // L
            8'h3A: ascii <= 8'h4D; // M
            8'h31: ascii <= 8'h4E; // N
            8'h44: ascii <= 8'h4F; // O
            8'h4D: ascii <= 8'h50; // P
            8'h15: ascii <= 8'h51; // Q
            8'h2D: ascii <= 8'h52; // R
            8'h1B: ascii <= 8'h53; // S
            8'h2C: ascii <= 8'h54; // T
            8'h3C: ascii <= 8'h55; // U
            8'h2A: ascii <= 8'h56; // V
            8'h1D: ascii <= 8'h57; // W
            8'h22: ascii <= 8'h58; // X
            8'h35: ascii <= 8'h59; // Y
            8'h1A: ascii <= 8'h5A; // Z

            8'h29: ascii <= 8'h20; // SPACE

            8'h45: ascii <= 8'h30; // 0
            8'h16: ascii <= 8'h31; // 1
            8'h1E: ascii <= 8'h32; // 2
            8'h26: ascii <= 8'h33; // 3
            8'h25: ascii <= 8'h34; // 4
            8'h2E: ascii <= 8'h35; // 5
            8'h36: ascii <= 8'h36; // 6
            8'h3D: ascii <= 8'h37; // 7
            8'h3E: ascii <= 8'h38; // 8
            8'h46: ascii <= 8'h39; // 9
            8'h49: ascii <= 8'h2E; // .

            8'h66: ascii <= 8'h08; // BACKSPACE
            8'h71: ascii <= 8'h7F; // DELETE
            8'h5A: ascii <= 8'h0D; // ENTER
            8'h75: ascii <= 8'h01; // UP
            8'h72: ascii <= 8'h02; // DOWN
            8'h6B: ascii <= 8'h03; // LEFT
            8'h74: ascii <= 8'h04; // RIGHT
            default: ascii <= key[7:0];
        endcase
    end

    // always @(posedge clk) begin
    //     ASCII[9'h1C] <= 8'h41; // A
    //     ASCII[9'h32] <= 8'h42; // B
    //     ASCII[9'h21] <= 8'h43; // C
    //     ASCII[9'h23] <= 8'h44; // D
    //     ASCII[9'h24] <= 8'h45; // E
    //     ASCII[9'h2B] <= 8'h46; // F
    //     ASCII[9'h34] <= 8'h47; // G
    //     ASCII[9'h33] <= 8'h48; // H
    //     ASCII[9'h43] <= 8'h49; // I
    //     ASCII[9'h3B] <= 8'h4A; // J
    //     ASCII[9'h42] <= 8'h4B; // K
    //     ASCII[9'h4B] <= 8'h4C; // L
    //     ASCII[9'h3A] <= 8'h4D; // M
    //     ASCII[9'h31] <= 8'h4E; // N
    //     ASCII[9'h44] <= 8'h4F; // O
    //     ASCII[9'h4D] <= 8'h50; // P
    //     ASCII[9'h15] <= 8'h51; // Q
    //     ASCII[9'h2D] <= 8'h52; // R
    //     ASCII[9'h1B] <= 8'h53; // S
    //     ASCII[9'h2C] <= 8'h54; // T
    //     ASCII[9'h3C] <= 8'h55; // U
    //     ASCII[9'h2A] <= 8'h56; // V
    //     ASCII[9'h1D] <= 8'h57; // W
    //     ASCII[9'h22] <= 8'h58; // X
    //     ASCII[9'h35] <= 8'h59; // Y
    //     ASCII[9'h1A] <= 8'h5A; // Z

    //     ASCII[9'h29] <= 8'h20; // SPACE

    //     ASCII[9'h45] <= 8'h30; // 0
    //     ASCII[9'h16] <= 8'h31; // 1
    //     ASCII[9'h1E] <= 8'h32; // 2
    //     ASCII[9'h26] <= 8'h33; // 3
    //     ASCII[9'h25] <= 8'h34; // 4
    //     ASCII[9'h2E] <= 8'h35; // 5
    //     ASCII[9'h36] <= 8'h36; // 6
    //     ASCII[9'h3D] <= 8'h37; // 7
    //     ASCII[9'h3E] <= 8'h38; // 8
    //     ASCII[9'h46] <= 8'h39; // 9
    // end

    
endmodule