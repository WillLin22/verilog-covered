//11：“规格化carry_out情况，右移sticky位”未考虑

module FADD(
  input  [31:0] io_a,
  input  [31:0] io_b,
  input  [2:0]  io_rm,
  output [31:0] io_result,
  output [4:0]  io_fflags
);

  // Sub-module 1: Component Extraction
wire sign_a =( io_a[31] == 0 ) ? 1'h0 : ( io_a[31] == ~0 ) ? 1'h0 : ( io_a[31]);
wire sign_b =( io_b[31] == 0 ) ? 1'h0 : ( io_b[31] == ~0 ) ? 1'h0 : ( io_b[31]);
wire [7:0] exp_a =( io_a[30:23] == 0 ) ? 8'h0 : ( io_a[30:23] == ~0 ) ? 8'h0 : ( io_a[30:23]);
wire [7:0] exp_b =( io_b[30:23] == 0 ) ? 8'h0 : ( io_b[30:23] == ~0 ) ? 8'h0 : ( io_b[30:23]);
wire [22:0] mant_a =( io_a[22:0] == 0 ) ? 23'h0 : ( io_a[22:0] == ~0 ) ? 23'h0 : ( io_a[22:0]);
wire [22:0] mant_b =( io_b[22:0] == 0 ) ? 23'h0 : ( io_b[22:0] == ~0 ) ? 23'h0 : ( io_b[22:0]);

  // Sub-module 2: Classification of Operands
wire is_normal_a =( mant_a == 0 && exp_a == 0 ) ? 1'h0 : ( mant_a == 0 && exp_a == ~0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == 0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == ~0 ) ? 1'h1 : ( (exp_a != 8'b0) && (mant_a != 23'b0));
wire is_normal_b =( exp_b == 0 && mant_b == 0 ) ? 1'h0 : ( exp_b == 0 && mant_b == ~0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == 0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == ~0 ) ? 1'h1 : ( (exp_b != 8'b0) && (mant_b != 23'b0));
wire is_subnormal_a =( mant_a == 0 && exp_a == 0 ) ? 1'h0 : ( mant_a == 0 && exp_a == ~0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == 0 ) ? 1'h1 : ( mant_a == ~0 && exp_a == ~0 ) ? 1'h0 : ( (exp_a == 8'b0) && (mant_a != 23'b0));
wire is_subnormal_b =( exp_b == 0 && mant_b == 0 ) ? 1'h0 : ( exp_b == 0 && mant_b == ~0 ) ? 1'h1 : ( exp_b == ~0 && mant_b == 0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == ~0 ) ? 1'h0 : ( (exp_b == 8'b0) && (mant_b != 23'b0));
wire is_zero_a =( mant_a == 0 && exp_a == 0 ) ? 1'h1 : ( mant_a == 0 && exp_a == ~0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == 0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == ~0 ) ? 1'h0 : ( (exp_a == 8'b0) && (mant_a == 23'b0));
wire is_zero_b =( exp_b == 0 && mant_b == 0 ) ? 1'h1 : ( exp_b == 0 && mant_b == ~0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == 0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == ~0 ) ? 1'h0 : ( (exp_b == 8'b0) && (mant_b == 23'b0));
wire is_inf_a =( mant_a == 0 && exp_a == 0 ) ? 1'h0 : ( mant_a == 0 && exp_a == ~0 ) ? 1'h1 : ( mant_a == ~0 && exp_a == 0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == ~0 ) ? 1'h0 : ( (exp_a == 8'hFF) && (mant_a == 23'b0));
wire is_inf_b =( exp_b == 0 && mant_b == 0 ) ? 1'h0 : ( exp_b == 0 && mant_b == ~0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == 0 ) ? 1'h1 : ( exp_b == ~0 && mant_b == ~0 ) ? 1'h0 : ( (exp_b == 8'hFF) && (mant_b == 23'b0));
wire is_nan_a =( mant_a == 0 && exp_a == 0 ) ? 1'h0 : ( mant_a == 0 && exp_a == ~0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == 0 ) ? 1'h0 : ( mant_a == ~0 && exp_a == ~0 ) ? 1'h1 : ( (exp_a == 8'hFF) && (mant_a != 23'b0));
wire is_nan_b =( exp_b == 0 && mant_b == 0 ) ? 1'h0 : ( exp_b == 0 && mant_b == ~0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == 0 ) ? 1'h0 : ( exp_b == ~0 && mant_b == ~0 ) ? 1'h1 : ( (exp_b == 8'hFF) && (mant_b != 23'b0));
wire is_Snan_a =( is_nan_a == 0 && io_a[22] == 0 ) ? 1'h0 : ( is_nan_a == 0 && io_a[22] == ~0 ) ? 1'h0 : ( is_nan_a == ~0 && io_a[22] == 0 ) ? 1'h1 : ( is_nan_a == ~0 && io_a[22] == ~0 ) ? 1'h1 : ( (is_nan_a) && (!io_a[22]));
wire is_Snan_b =( is_nan_b == 0 && io_b[22] == 0 ) ? 1'h0 : ( is_nan_b == 0 && io_b[22] == ~0 ) ? 1'h0 : ( is_nan_b == ~0 && io_b[22] == 0 ) ? 1'h1 : ( is_nan_b == ~0 && io_b[22] == ~0 ) ? 1'h1 : ( (is_nan_b) && (!io_b[22]));


  // Sub-module 3: Handling Special Cases
  wire is_nan = is_nan_a || is_nan_b || (is_inf_a && is_inf_b && (sign_a != sign_b));
wire is_inf =( is_nan == 0 && is_inf_b == 0 && is_inf_a == 0 ) ? 1'h0 : ( is_nan == 0 && is_inf_b == 0 && is_inf_a == ~0 ) ? 1'h1 : ( is_nan == 0 && is_inf_b == ~0 && is_inf_a == 0 ) ? 1'h1 : ( is_nan == 0 && is_inf_b == ~0 && is_inf_a == ~0 ) ? 1'h1 : ( is_nan == ~0 && is_inf_b == 0 && is_inf_a == 0 ) ? 1'h0 : ( is_nan == ~0 && is_inf_b == 0 && is_inf_a == ~0 ) ? 1'h0 : ( is_nan == ~0 && is_inf_b == ~0 && is_inf_a == 0 ) ? 1'h0 : ( is_nan == ~0 && is_inf_b == ~0 && is_inf_a == ~0 ) ? 1'h0 : ( (is_inf_a || is_inf_b) && !is_nan);
wire is_both_zero =( sign_b == 0 && is_zero_b == 0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == 0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == 0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == 0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == ~0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == ~0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h1 : ( sign_b == 0 && is_zero_b == ~0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == 0 && is_zero_b == ~0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == 0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == 0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == 0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == 0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == ~0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == ~0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == ~0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == ~0 && is_zero_b == ~0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h1 : ( is_zero_a && is_zero_b && (sign_a == sign_b));
  wire is_opposite = (sign_a != sign_b) && (exp_a == exp_b) && (mant_a == mant_b);
wire is_one_zero =( is_zero_b == 0 && is_both_zero == 0 && is_zero_a == 0 ) ? 1'h0 : ( is_zero_b == 0 && is_both_zero == 0 && is_zero_a == ~0 ) ? 1'h1 : ( is_zero_b == 0 && is_both_zero == ~0 && is_zero_a == 0 ) ? 1'h0 : ( is_zero_b == 0 && is_both_zero == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( is_zero_b == ~0 && is_both_zero == 0 && is_zero_a == 0 ) ? 1'h1 : ( is_zero_b == ~0 && is_both_zero == 0 && is_zero_a == ~0 ) ? 1'h1 : ( is_zero_b == ~0 && is_both_zero == ~0 && is_zero_a == 0 ) ? 1'h0 : ( is_zero_b == ~0 && is_both_zero == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( (is_zero_a || is_zero_b) && !is_both_zero);

  wire result_sign_nan = 1'b0;
  wire [7:0] result_exp_nan = 8'hFF;
  wire [22:0] result_mant_nan = 23'b10000000000000000000000;

wire result_sign_inf =( sign_b == 0 && sign_a == 0 && is_inf_a == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == 0 && is_inf_a == ~0 ) ? 1'h0 : ( sign_b == 0 && sign_a == ~0 && is_inf_a == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == ~0 && is_inf_a == ~0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == 0 && is_inf_a == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == 0 && is_inf_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == ~0 && is_inf_a == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && is_inf_a == ~0 ) ? 1'h1 : ( is_inf_a ? sign_a : sign_b);
  wire [7:0] result_exp_inf = 8'hFF;
  wire [22:0] result_mant_inf = 23'b0;

wire result_sign_both_zero =( sign_a == 0 ) ? 1'h0 : ( sign_a == ~0 ) ? 1'h1 : ( sign_a);
  wire [7:0] result_exp_both_zero = 8'b0;
  wire [22:0] result_mant_both_zero = 23'b0;

wire result_sign_opposite =( io_rm == 0 ) ? 1'h0 : ( io_rm == ~0 ) ? 1'h0 : ( (io_rm == 3'b010) ? 1'b1 : 1'b0);
  wire [7:0] result_exp_opposite = 8'b0;
  wire [22:0] result_mant_opposite = 23'b0;

wire result_sign_one_zero =( sign_b == 0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == 0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h1 : ( sign_b == 0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && is_zero_a == 0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && is_zero_a == ~0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && is_zero_a == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && is_zero_a == ~0 ) ? 1'h1 : ( is_zero_a ? sign_b : sign_a);
wire [7:0] result_exp_one_zero =( exp_a == 0 && exp_b == 0 && is_zero_a == 0 ) ? 8'h0 : ( exp_a == 0 && exp_b == 0 && is_zero_a == ~0 ) ? 8'h0 : ( exp_a == 0 && exp_b == ~0 && is_zero_a == 0 ) ? 8'h0 : ( exp_a == 0 && exp_b == ~0 && is_zero_a == ~0 ) ? 8'hff : ( exp_a == ~0 && exp_b == 0 && is_zero_a == 0 ) ? 8'hff : ( exp_a == ~0 && exp_b == 0 && is_zero_a == ~0 ) ? 8'h0 : ( exp_a == ~0 && exp_b == ~0 && is_zero_a == 0 ) ? 8'hff : ( exp_a == ~0 && exp_b == ~0 && is_zero_a == ~0 ) ? 8'hff : ( is_zero_a ? exp_b : exp_a);
wire [22:0] result_mant_one_zero =( is_zero_a == 0 && mant_a == 0 && mant_b == 0 ) ? 23'h0 : ( is_zero_a == 0 && mant_a == 0 && mant_b == ~0 ) ? 23'h0 : ( is_zero_a == 0 && mant_a == ~0 && mant_b == 0 ) ? 23'h7fffff : ( is_zero_a == 0 && mant_a == ~0 && mant_b == ~0 ) ? 23'h7fffff : ( is_zero_a == ~0 && mant_a == 0 && mant_b == 0 ) ? 23'h0 : ( is_zero_a == ~0 && mant_a == 0 && mant_b == ~0 ) ? 23'h7fffff : ( is_zero_a == ~0 && mant_a == ~0 && mant_b == 0 ) ? 23'h0 : ( is_zero_a == ~0 && mant_a == ~0 && mant_b == ~0 ) ? 23'h7fffff : ( is_zero_a ? mant_b : mant_a);


  // Sub-module 4: Prepare for Addition
wire effective_subtraction =( sign_b == 0 && sign_a == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == ~0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 ) ? 1'h0 : ( (sign_a != sign_b));
wire [23:0] mant_ext_a =( mant_a == 0 && is_subnormal_a == 0 ) ? 24'h800000 : ( mant_a == 0 && is_subnormal_a == ~0 ) ? 24'h0 : ( mant_a == ~0 && is_subnormal_a == 0 ) ? 24'hffffff : ( mant_a == ~0 && is_subnormal_a == ~0 ) ? 24'h7fffff : ( is_subnormal_a? {1'b0, mant_a} : {1'b1, mant_a});
wire [23:0] mant_ext_b =( is_subnormal_b == 0 && mant_b == 0 ) ? 24'h800000 : ( is_subnormal_b == 0 && mant_b == ~0 ) ? 24'hffffff : ( is_subnormal_b == ~0 && mant_b == 0 ) ? 24'h0 : ( is_subnormal_b == ~0 && mant_b == ~0 ) ? 24'h7fffff : ( is_subnormal_b? {1'b0, mant_b} : {1'b1, mant_b});
wire [7:0] exp_ext_a =( exp_a == 0 && is_subnormal_a == 0 ) ? 32'h0 : ( exp_a == 0 && is_subnormal_a == ~0 ) ? 32'h1 : ( exp_a == ~0 && is_subnormal_a == 0 ) ? 32'hff : ( exp_a == ~0 && is_subnormal_a == ~0 ) ? 32'h100 : ( is_subnormal_a ? (exp_a + 1) : exp_a);
wire [7:0] exp_ext_b =( is_subnormal_b == 0 && exp_b == 0 ) ? 32'h0 : ( is_subnormal_b == 0 && exp_b == ~0 ) ? 32'hff : ( is_subnormal_b == ~0 && exp_b == 0 ) ? 32'h1 : ( is_subnormal_b == ~0 && exp_b == ~0 ) ? 32'h100 : ( is_subnormal_b ? (exp_b + 1) : exp_b);
wire [7:0] exp_diff =( exp_ext_a == 0 && exp_ext_b == 0 ) ? 8'h0 : ( exp_ext_a == 0 && exp_ext_b == ~0 ) ? 8'hff : ( exp_ext_a == ~0 && exp_ext_b == 0 ) ? 8'hff : ( exp_ext_a == ~0 && exp_ext_b == ~0 ) ? 8'h0 : ( (exp_ext_a > exp_ext_b) ? (exp_ext_a - exp_ext_b) : (exp_ext_b - exp_ext_a));
wire [7:0] aligned_exp =( exp_ext_a == 0 && exp_ext_b == 0 ) ? 8'h0 : ( exp_ext_a == 0 && exp_ext_b == ~0 ) ? 8'hff : ( exp_ext_a == ~0 && exp_ext_b == 0 ) ? 8'hff : ( exp_ext_a == ~0 && exp_ext_b == ~0 ) ? 8'hff : ( (exp_ext_a > exp_ext_b) ? exp_ext_a : exp_ext_b);

  // Sub-module 5: Mantissa Alignment


wire  need_swap =( exp_ext_a == 0 && exp_ext_b == 0 && mant_ext_a == 0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == 0 && exp_ext_b == 0 && mant_ext_a == 0 && mant_ext_b == ~0 ) ? 1'h1 : ( exp_ext_a == 0 && exp_ext_b == 0 && mant_ext_a == ~0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == 0 && exp_ext_b == 0 && mant_ext_a == ~0 && mant_ext_b == ~0 ) ? 1'h0 : ( exp_ext_a == 0 && exp_ext_b == ~0 && mant_ext_a == 0 && mant_ext_b == 0 ) ? 1'h1 : ( exp_ext_a == 0 && exp_ext_b == ~0 && mant_ext_a == 0 && mant_ext_b == ~0 ) ? 1'h1 : ( exp_ext_a == 0 && exp_ext_b == ~0 && mant_ext_a == ~0 && mant_ext_b == 0 ) ? 1'h1 : ( exp_ext_a == 0 && exp_ext_b == ~0 && mant_ext_a == ~0 && mant_ext_b == ~0 ) ? 1'h1 : ( exp_ext_a == ~0 && exp_ext_b == 0 && mant_ext_a == 0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == 0 && mant_ext_a == 0 && mant_ext_b == ~0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == 0 && mant_ext_a == ~0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == 0 && mant_ext_a == ~0 && mant_ext_b == ~0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == ~0 && mant_ext_a == 0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == ~0 && mant_ext_a == 0 && mant_ext_b == ~0 ) ? 1'h1 : ( exp_ext_a == ~0 && exp_ext_b == ~0 && mant_ext_a == ~0 && mant_ext_b == 0 ) ? 1'h0 : ( exp_ext_a == ~0 && exp_ext_b == ~0 && mant_ext_a == ~0 && mant_ext_b == ~0 ) ? 1'h0 : ( (exp_ext_a < exp_ext_b) || ((exp_ext_a == exp_ext_b) && (mant_ext_a < mant_ext_b)));
  
wire [25:0]  shift_smaller =( mant_ext_a == 0 && need_swap == 0 && mant_ext_b == 0 ) ? 26'h0 : ( mant_ext_a == 0 && need_swap == 0 && mant_ext_b == ~0 ) ? 26'h3fffffc : ( mant_ext_a == 0 && need_swap == ~0 && mant_ext_b == 0 ) ? 26'h0 : ( mant_ext_a == 0 && need_swap == ~0 && mant_ext_b == ~0 ) ? 26'h0 : ( mant_ext_a == ~0 && need_swap == 0 && mant_ext_b == 0 ) ? 26'h0 : ( mant_ext_a == ~0 && need_swap == 0 && mant_ext_b == ~0 ) ? 26'h3fffffc : ( mant_ext_a == ~0 && need_swap == ~0 && mant_ext_b == 0 ) ? 26'h3fffffc : ( mant_ext_a == ~0 && need_swap == ~0 && mant_ext_b == ~0 ) ? 26'h3fffffc : (  need_swap ? {mant_ext_a,2'b00} : {mant_ext_b,2'b00});
wire  shift_too_large =( exp_diff == 0 ) ? 1'h0 : ( exp_diff == ~0 ) ? 1'h1 : ( (exp_diff >= 26));
wire [25:0] sticky;
assign sticky[0] = (0 < exp_diff) && shift_smaller[0];
assign sticky[1] = (1 < exp_diff) && shift_smaller[1];
assign sticky[2] = (2 < exp_diff) && shift_smaller[2];
assign sticky[3] = (3 < exp_diff) && shift_smaller[3];
assign sticky[4] = (4 < exp_diff) && shift_smaller[4];
assign sticky[5] = (5 < exp_diff) && shift_smaller[5];
assign sticky[6] = (6 < exp_diff) && shift_smaller[6];
assign sticky[7] = (7 < exp_diff) && shift_smaller[7];
assign sticky[8] = (8 < exp_diff) && shift_smaller[8];
assign sticky[9] = (9 < exp_diff) && shift_smaller[9];
assign sticky[10] = (10 < exp_diff) && shift_smaller[10];
assign sticky[11] = (11 < exp_diff) && shift_smaller[11];
assign sticky[12] = (12 < exp_diff) && shift_smaller[12];
assign sticky[13] = (13 < exp_diff) && shift_smaller[13];
assign sticky[14] = (14 < exp_diff) && shift_smaller[14];
assign sticky[15] = (15 < exp_diff) && shift_smaller[15];
assign sticky[16] = (16 < exp_diff) && shift_smaller[16];
assign sticky[17] = (17 < exp_diff) && shift_smaller[17];
assign sticky[18] = (18 < exp_diff) && shift_smaller[18];
assign sticky[19] = (19 < exp_diff) && shift_smaller[19];
assign sticky[20] = (20 < exp_diff) && shift_smaller[20];
assign sticky[21] = (21 < exp_diff) && shift_smaller[21];
assign sticky[22] = (22 < exp_diff) && shift_smaller[22];
assign sticky[23] = (23 < exp_diff) && shift_smaller[23];
assign sticky[24] = (24 < exp_diff) && shift_smaller[24];
assign sticky[25] = (25 < exp_diff) && shift_smaller[25];
wire [25:0]  main =( exp_diff == 0 && shift_smaller == 0 && shift_too_large == 0 ) ? 32'h0 : ( exp_diff == 0 && shift_smaller == 0 && shift_too_large == ~0 ) ? 32'h0 : ( exp_diff == 0 && shift_smaller == ~0 && shift_too_large == 0 ) ? 32'h3ffffff : ( exp_diff == 0 && shift_smaller == ~0 && shift_too_large == ~0 ) ? 32'h0 : ( exp_diff == ~0 && shift_smaller == 0 && shift_too_large == 0 ) ? 32'h0 : ( exp_diff == ~0 && shift_smaller == 0 && shift_too_large == ~0 ) ? 32'h0 : ( exp_diff == ~0 && shift_smaller == ~0 && shift_too_large == 0 ) ? 32'h0 : ( exp_diff == ~0 && shift_smaller == ~0 && shift_too_large == ~0 ) ? 32'h0 : (  shift_too_large ? 0 : ( |sticky ? shift_smaller >> exp_diff :shift_smaller >> exp_diff));
wire   smaller_sticky =( exp_diff == 0 && shift_smaller == 0 && shift_too_large == 0 ) ? 1'h0 : ( exp_diff == 0 && shift_smaller == 0 && shift_too_large == ~0 ) ? 1'h0 : ( exp_diff == 0 && shift_smaller == ~0 && shift_too_large == 0 ) ? 1'h0 : ( exp_diff == 0 && shift_smaller == ~0 && shift_too_large == ~0 ) ? 1'h1 : ( exp_diff == ~0 && shift_smaller == 0 && shift_too_large == 0 ) ? 1'h0 : ( exp_diff == ~0 && shift_smaller == 0 && shift_too_large == ~0 ) ? 1'h0 : ( exp_diff == ~0 && shift_smaller == ~0 && shift_too_large == 0 ) ? 1'h1 : ( exp_diff == ~0 && shift_smaller == ~0 && shift_too_large == ~0 ) ? 1'h1 : (  shift_too_large ? | shift_smaller : |( shift_smaller & ((1 << exp_diff) - 1)));

wire [27:0]  aligned_mant_smaller =( main == 0 && smaller_sticky == 0 ) ? 28'h0 : ( main == 0 && smaller_sticky == ~0 ) ? 28'h1 : ( main == ~0 && smaller_sticky == 0 ) ? 28'h7fffffe : ( main == ~0 && smaller_sticky == ~0 ) ? 28'h7ffffff : (  {1'b0,  main,  smaller_sticky});
wire [27:0]  aligned_mant_larger =( mant_ext_b == 0 && need_swap == 0 && mant_ext_a == 0 ) ? 28'h0 : ( mant_ext_b == 0 && need_swap == 0 && mant_ext_a == ~0 ) ? 28'h7fffff8 : ( mant_ext_b == 0 && need_swap == ~0 && mant_ext_a == 0 ) ? 28'h0 : ( mant_ext_b == 0 && need_swap == ~0 && mant_ext_a == ~0 ) ? 28'h0 : ( mant_ext_b == ~0 && need_swap == 0 && mant_ext_a == 0 ) ? 28'h0 : ( mant_ext_b == ~0 && need_swap == 0 && mant_ext_a == ~0 ) ? 28'h7fffff8 : ( mant_ext_b == ~0 && need_swap == ~0 && mant_ext_a == 0 ) ? 28'h7fffff8 : ( mant_ext_b == ~0 && need_swap == ~0 && mant_ext_a == ~0 ) ? 28'h7fffff8 : (  need_swap ? {1'b0, mant_ext_b,3'b000} : {1'b0, mant_ext_a,3'b000});

wire  resultant_sign =( sign_b == 0 && sign_a == 0 && need_swap == 0 && effective_subtraction == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == 0 && need_swap == 0 && effective_subtraction == ~0 ) ? 1'h0 : ( sign_b == 0 && sign_a == 0 && need_swap == ~0 && effective_subtraction == 0 ) ? 1'h0 : ( sign_b == 0 && sign_a == 0 && need_swap == ~0 && effective_subtraction == ~0 ) ? 1'h0 : ( sign_b == 0 && sign_a == ~0 && need_swap == 0 && effective_subtraction == 0 ) ? 1'h1 : ( sign_b == 0 && sign_a == ~0 && need_swap == 0 && effective_subtraction == ~0 ) ? 1'h1 : ( sign_b == 0 && sign_a == ~0 && need_swap == ~0 && effective_subtraction == 0 ) ? 1'h1 : ( sign_b == 0 && sign_a == ~0 && need_swap == ~0 && effective_subtraction == ~0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && need_swap == 0 && effective_subtraction == 0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && need_swap == 0 && effective_subtraction == ~0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && need_swap == ~0 && effective_subtraction == 0 ) ? 1'h0 : ( sign_b == ~0 && sign_a == 0 && need_swap == ~0 && effective_subtraction == ~0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && need_swap == 0 && effective_subtraction == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && need_swap == 0 && effective_subtraction == ~0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && need_swap == ~0 && effective_subtraction == 0 ) ? 1'h1 : ( sign_b == ~0 && sign_a == ~0 && need_swap == ~0 && effective_subtraction == ~0 ) ? 1'h1 : ( (!effective_subtraction) ? sign_a :(need_swap) ? sign_b : sign_a);

wire [27:0]  adder_result =( aligned_mant_larger == 0 && aligned_mant_smaller == 0 && effective_subtraction == 0 ) ? 28'h0 : ( aligned_mant_larger == 0 && aligned_mant_smaller == 0 && effective_subtraction == ~0 ) ? 28'h0 : ( aligned_mant_larger == 0 && aligned_mant_smaller == ~0 && effective_subtraction == 0 ) ? 28'hfffffff : ( aligned_mant_larger == 0 && aligned_mant_smaller == ~0 && effective_subtraction == ~0 ) ? 28'hfffffff : ( aligned_mant_larger == ~0 && aligned_mant_smaller == 0 && effective_subtraction == 0 ) ? 28'hfffffff : ( aligned_mant_larger == ~0 && aligned_mant_smaller == 0 && effective_subtraction == ~0 ) ? 28'hfffffff : ( aligned_mant_larger == ~0 && aligned_mant_smaller == ~0 && effective_subtraction == 0 ) ? 28'hffffffe : ( aligned_mant_larger == ~0 && aligned_mant_smaller == ~0 && effective_subtraction == ~0 ) ? 28'h0 : ( !effective_subtraction ?  aligned_mant_larger +  aligned_mant_smaller :aligned_mant_larger -  aligned_mant_smaller );


  // Sub-module 6: Result Normalization and Left shifting
wire carry_out =( adder_result[27] == 0 ) ? 1'h0 : ( adder_result[27] == ~0 ) ? 1'h0 : ( adder_result[27]);
wire implied_bit =( adder_result[26] == 0 ) ? 1'h0 : ( adder_result[26] == ~0 ) ? 1'h0 : ( adder_result[26]);
wire cancellation =( carry_out == 0 && implied_bit == 0 ) ? 1'h1 : ( carry_out == 0 && implied_bit == ~0 ) ? 1'h0 : ( carry_out == ~0 && implied_bit == 0 ) ? 1'h0 : ( carry_out == ~0 && implied_bit == ~0 ) ? 1'h0 : ( !carry_out && !implied_bit);
wire  keep =( carry_out == 0 && implied_bit == 0 ) ? 1'h0 : ( carry_out == 0 && implied_bit == ~0 ) ? 1'h1 : ( carry_out == ~0 && implied_bit == 0 ) ? 1'h0 : ( carry_out == ~0 && implied_bit == ~0 ) ? 1'h0 : ( !carry_out && implied_bit);
  // wire small_add = is_subnormal_a && is_subnormal_b;
wire small_add =( exp_a == 0 && exp_b == 0 ) ? 1'h1 : ( exp_a == 0 && exp_b == ~0 ) ? 1'h0 : ( exp_a == ~0 && exp_b == 0 ) ? 1'h0 : ( exp_a == ~0 && exp_b == ~0 ) ? 1'h0 : ( (exp_a == 8'h00) && (exp_b == 8'h00));
  wire [4:0] computed_shift = 
    (adder_result[25]) ? 5'd1 :
    (adder_result[24]) ? 5'd2 :
    (adder_result[23]) ? 5'd3 :
    (adder_result[22]) ? 5'd4 :
    (adder_result[21]) ? 5'd5 :
    (adder_result[20]) ? 5'd6 :
    (adder_result[19]) ? 5'd7 :
    (adder_result[18]) ? 5'd8 :
    (adder_result[17]) ? 5'd9 :
    (adder_result[16]) ? 5'd10 :
    (adder_result[15]) ? 5'd11 :
    (adder_result[14]) ? 5'd12 :
    (adder_result[13]) ? 5'd13 :
    (adder_result[12]) ? 5'd14 :
    (adder_result[11]) ? 5'd15 :
    (adder_result[10]) ? 5'd16 :
    (adder_result[9]) ? 5'd17 :
    (adder_result[8]) ? 5'd18 :
    (adder_result[7]) ? 5'd19 :
    (adder_result[6]) ? 5'd20 :
    (adder_result[5]) ? 5'd21 :
    (adder_result[4]) ? 5'd22 :
    (adder_result[3]) ? 5'd23 :
    5'd24;
wire [4:0] real_shift_norm =( computed_shift == 0 && aligned_exp == 0 ) ? 32'h1 : ( computed_shift == 0 && aligned_exp == ~0 ) ? 32'h0 : ( computed_shift == ~0 && aligned_exp == 0 ) ? 32'h1 : ( computed_shift == ~0 && aligned_exp == ~0 ) ? 32'h1f : ( (aligned_exp > computed_shift) ? computed_shift : (aligned_exp - 1));
wire [7:0] adjusted_exp =( computed_shift == 0 && aligned_exp == 0 ) ? 8'h0 : ( computed_shift == 0 && aligned_exp == ~0 ) ? 8'hff : ( computed_shift == ~0 && aligned_exp == 0 ) ? 8'h0 : ( computed_shift == ~0 && aligned_exp == ~0 ) ? 8'he0 : ( (aligned_exp > computed_shift) ? (aligned_exp - computed_shift) : 8'b0);
  
  wire [26:0]   normalized_mantissa =  carry_out ? { adder_result[27:2], adder_result[1]} :
                          ( keep || small_add) ? { adder_result[26:1],  adder_result[0]} :
                          ( cancellation && !small_add) ? { adder_result[25:0] <<  real_shift_norm} :  adder_result[26:0] ;
  wire [7:0]   normalized_exp =  carry_out ? aligned_exp + 1 :
                                keep ? aligned_exp:
                                cancellation ?  adjusted_exp: aligned_exp;

  // Sub-module 7: Rounding processing
wire [22:0] rounding_input =( normalized_mantissa[25:3] == 0 ) ? 23'h0 : ( normalized_mantissa[25:3] == ~0 ) ? 23'h0 : ( normalized_mantissa[25:3]);
wire f1 =( normalized_mantissa[3] == 0 ) ? 1'h0 : ( normalized_mantissa[3] == ~0 ) ? 1'h0 : ( normalized_mantissa[3]);
wire f2 =( normalized_mantissa[2] == 0 ) ? 1'h0 : ( normalized_mantissa[2] == ~0 ) ? 1'h0 : ( normalized_mantissa[2]);
wire f3 =( normalized_mantissa[1:0] == 0 ) ? 1'h0 : ( normalized_mantissa[1:0] == ~0 ) ? 1'h0 : ( | normalized_mantissa[1:0]);
wire inexact_flag =( f2 == 0 && f3 == 0 ) ? 1'h0 : ( f2 == 0 && f3 == ~0 ) ? 1'h1 : ( f2 == ~0 && f3 == 0 ) ? 1'h1 : ( f2 == ~0 && f3 == ~0 ) ? 1'h1 : ( f2 | f3);
  wire round_up = 
    (io_rm == 3'b000) ? (f2 && (f1 || f3)) :
    (io_rm == 3'b001) ? 1'b0 :
    (io_rm == 3'b010) ? (inexact_flag && resultant_sign) :
    (io_rm == 3'b011) ? (inexact_flag && !resultant_sign) :
    (io_rm == 3'b100) ? f2 :
    1'b0;
wire  n_carry_out =( round_up == 0 && rounding_input == 0 ) ? 1'h0 : ( round_up == 0 && rounding_input == ~0 ) ? 1'h0 : ( round_up == ~0 && rounding_input == 0 ) ? 1'h0 : ( round_up == ~0 && rounding_input == ~0 ) ? 1'h1 : (   round_up && & rounding_input);
wire [7:0]  rounded_exp =( n_carry_out == 0 && normalized_exp == 0 ) ? 8'h0 : ( n_carry_out == 0 && normalized_exp == ~0 ) ? 8'hff : ( n_carry_out == ~0 && normalized_exp == 0 ) ? 8'h1 : ( n_carry_out == ~0 && normalized_exp == ~0 ) ? 8'h0 : (  n_carry_out +   normalized_exp);
wire [22:0]  rounded_mantissa =( round_up == 0 && rounding_input == 0 ) ? 32'h0 : ( round_up == 0 && rounding_input == ~0 ) ? 32'h7fffff : ( round_up == ~0 && rounding_input == 0 ) ? 32'h1 : ( round_up == ~0 && rounding_input == ~0 ) ? 32'h800000 : (  round_up ?  rounding_input + 1 :  rounding_input);

  // Sub-module 8: Exception Flags
wire tiny =( small_add == 0 && cancellation == 0 && n_carry_out == 0 && keep == 0 ) ? 1'h0 : ( small_add == 0 && cancellation == 0 && n_carry_out == 0 && keep == ~0 ) ? 1'h0 : ( small_add == 0 && cancellation == 0 && n_carry_out == ~0 && keep == 0 ) ? 1'h0 : ( small_add == 0 && cancellation == 0 && n_carry_out == ~0 && keep == ~0 ) ? 1'h0 : ( small_add == 0 && cancellation == ~0 && n_carry_out == 0 && keep == 0 ) ? 1'h0 : ( small_add == 0 && cancellation == ~0 && n_carry_out == 0 && keep == ~0 ) ? 1'h0 : ( small_add == 0 && cancellation == ~0 && n_carry_out == ~0 && keep == 0 ) ? 1'h0 : ( small_add == 0 && cancellation == ~0 && n_carry_out == ~0 && keep == ~0 ) ? 1'h0 : ( small_add == ~0 && cancellation == 0 && n_carry_out == 0 && keep == 0 ) ? 1'h0 : ( small_add == ~0 && cancellation == 0 && n_carry_out == 0 && keep == ~0 ) ? 1'h1 : ( small_add == ~0 && cancellation == 0 && n_carry_out == ~0 && keep == 0 ) ? 1'h0 : ( small_add == ~0 && cancellation == 0 && n_carry_out == ~0 && keep == ~0 ) ? 1'h0 : ( small_add == ~0 && cancellation == ~0 && n_carry_out == 0 && keep == 0 ) ? 1'h1 : ( small_add == ~0 && cancellation == ~0 && n_carry_out == 0 && keep == ~0 ) ? 1'h1 : ( small_add == ~0 && cancellation == ~0 && n_carry_out == ~0 && keep == 0 ) ? 1'h1 : ( small_add == ~0 && cancellation == ~0 && n_carry_out == ~0 && keep == ~0 ) ? 1'h1 : ( small_add && (cancellation || (keep && !n_carry_out)));
wire overflow =( carry_out == 0 && rounded_exp == 0 && aligned_exp == 0 ) ? 1'h0 : ( carry_out == 0 && rounded_exp == 0 && aligned_exp == ~0 ) ? 1'h0 : ( carry_out == 0 && rounded_exp == ~0 && aligned_exp == 0 ) ? 1'h1 : ( carry_out == 0 && rounded_exp == ~0 && aligned_exp == ~0 ) ? 1'h1 : ( carry_out == ~0 && rounded_exp == 0 && aligned_exp == 0 ) ? 1'h0 : ( carry_out == ~0 && rounded_exp == 0 && aligned_exp == ~0 ) ? 1'h0 : ( carry_out == ~0 && rounded_exp == ~0 && aligned_exp == 0 ) ? 1'h1 : ( carry_out == ~0 && rounded_exp == ~0 && aligned_exp == ~0 ) ? 1'h1 : ( (rounded_exp == 8'hFF) || ((aligned_exp == 8'hFE) && carry_out));
wire inexact =( overflow == 0 && inexact_flag == 0 ) ? 1'h0 : ( overflow == 0 && inexact_flag == ~0 ) ? 1'h1 : ( overflow == ~0 && inexact_flag == 0 ) ? 1'h1 : ( overflow == ~0 && inexact_flag == ~0 ) ? 1'h1 : ( inexact_flag || overflow);
wire underflow =( tiny == 0 && overflow == 0 && inexact == 0 ) ? 1'h0 : ( tiny == 0 && overflow == 0 && inexact == ~0 ) ? 1'h0 : ( tiny == 0 && overflow == ~0 && inexact == 0 ) ? 1'h0 : ( tiny == 0 && overflow == ~0 && inexact == ~0 ) ? 1'h0 : ( tiny == ~0 && overflow == 0 && inexact == 0 ) ? 1'h0 : ( tiny == ~0 && overflow == 0 && inexact == ~0 ) ? 1'h1 : ( tiny == ~0 && overflow == ~0 && inexact == 0 ) ? 1'h0 : ( tiny == ~0 && overflow == ~0 && inexact == ~0 ) ? 1'h0 : ( tiny && inexact && !overflow);
  wire special_flag = is_Snan_a || is_Snan_b || (is_inf_a && is_inf_b && (sign_a != sign_b));

  // Sub-module 9: Result Construction
wire rmin =( io_rm == 0 && resultant_sign == 0 ) ? 1'h0 : ( io_rm == 0 && resultant_sign == ~0 ) ? 1'h0 : ( io_rm == ~0 && resultant_sign == 0 ) ? 1'h0 : ( io_rm == ~0 && resultant_sign == ~0 ) ? 1'h0 : ( (io_rm == 3'b001) || ((io_rm == 3'b010) && !resultant_sign) || ((io_rm == 3'b011) && resultant_sign));
wire [31:0] overflow_result =( rmin == 0 && resultant_sign == 0 ) ? 32'h7f800000 : ( rmin == 0 && resultant_sign == ~0 ) ? 32'hff800000 : ( rmin == ~0 && resultant_sign == 0 ) ? 32'h7f7fffff : ( rmin == ~0 && resultant_sign == ~0 ) ? 32'hff7fffff : ( {resultant_sign, rmin ? 8'hFE : 8'hFF, rmin ? 23'h7FFFFF : 23'b0});
wire [31:0] normal_result =( rounded_mantissa == 0 && rounded_exp == 0 && resultant_sign == 0 ) ? 32'h0 : ( rounded_mantissa == 0 && rounded_exp == 0 && resultant_sign == ~0 ) ? 32'h80000000 : ( rounded_mantissa == 0 && rounded_exp == ~0 && resultant_sign == 0 ) ? 32'h7f800000 : ( rounded_mantissa == 0 && rounded_exp == ~0 && resultant_sign == ~0 ) ? 32'hff800000 : ( rounded_mantissa == ~0 && rounded_exp == 0 && resultant_sign == 0 ) ? 32'h7fffff : ( rounded_mantissa == ~0 && rounded_exp == 0 && resultant_sign == ~0 ) ? 32'h807fffff : ( rounded_mantissa == ~0 && rounded_exp == ~0 && resultant_sign == 0 ) ? 32'h7fffffff : ( rounded_mantissa == ~0 && rounded_exp == ~0 && resultant_sign == ~0 ) ? 32'hffffffff : ( {resultant_sign, rounded_exp, rounded_mantissa});
  wire [31:0] special_result = 
    is_nan ? {result_sign_nan, result_exp_nan, result_mant_nan} :
    is_inf ? {result_sign_inf, result_exp_inf, result_mant_inf} :
    is_both_zero ? {result_sign_both_zero, result_exp_both_zero, result_mant_both_zero} :
    is_opposite ? {result_sign_opposite, result_exp_opposite, result_mant_opposite} :
    is_one_zero? {result_sign_one_zero, result_exp_one_zero, result_mant_one_zero}:
    {1'b0, 8'hFF, 23'b10000000000000000000000};
  wire special_case_happen = is_nan || is_inf || is_both_zero || is_opposite || is_one_zero;
  
  assign io_fflags = (is_nan || is_inf) ? {special_flag, 4'b0} : (is_both_zero || is_opposite || is_one_zero) ? {5'b0}: {1'b0, 1'b0, overflow, underflow, inexact};
  assign io_result = special_case_happen ? special_result : (overflow ? overflow_result : normal_result);

endmodule
