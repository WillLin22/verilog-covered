`timescale 1 ps/1 ps

module testbench();
  reg clock;
  reg reset;
  reg [63:0] io_int;
  reg io_sign;
  reg [2:0] io_rm;
  wire [63:0] io_result;
  wire [4:0] io_fflags;

  IntToFP int2fp_inst (
    // .clock(clock),
    // .reset(reset),
    .io_int(io_int),
    .io_sign(io_sign),
    .io_rm(io_rm),
    .io_result(io_result),
    .io_fflags(io_fflags)
  );

  initial begin
    bit [63:0] a;
	  bit [2:0] rm;
    bit sign;
    // Initialize signals
    clock = 0;
    reset = 0;
    io_int = 0;
    io_sign = 0;
    io_rm = 0;


    // Prompt for input
    $value$plusargs("rm=%x", rm);
    $value$plusargs("int=%x", a);
    $value$plusargs("sign=%x", sign);


    // Assign inputs
    io_int = a;
    io_sign = sign;
    io_rm = rm;

    // Wait for a few clock cycles
    #10;

    // Display results

    $display("rm: %x", rm);
    $display("int: %x", a);
    $display("sign: %x", sign);
    $display("io_rm: %x", io_rm);
    $display("io_int: %x", io_int);
    $display("io_sign: %x", io_sign);
    $display("io_result: %x", io_result);
    $display("io_fflags: %x", io_fflags);

    // End simulation
    $finish;
  end


endmodule
