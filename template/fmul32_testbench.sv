`timescale 1 ps/1 ps

module testbench();
  reg clock;
  reg reset;
  reg [31:0] io_a;
  reg [31:0] io_b;
  reg [2:0] io_rm;
  wire [31:0] io_result;
  wire [4:0] io_fflags;

  FMUL fmul_inst (
    // .clock(clock),
    // .reset(reset),
    .io_a(io_a),
    .io_b(io_b),
    .io_rm(io_rm),
    .io_result(io_result),
    .io_fflags(io_fflags)
  );

  initial begin
    bit [31:0]  a, b;
	  bit [2:0] rm;
    // Initialize signals
    clock = 0;
    reset = 0;
    io_a = 0;
    io_b = 0;
    io_rm = 0;


    // Prompt for input
    $value$plusargs("rm=%x", rm);
    $value$plusargs("a=%x", a);
    $value$plusargs("b=%x", b);


    // Assign inputs
    io_a = a;
    io_b = b;
    io_rm = rm;

    // Wait for a few clock cycles
    #10;

    // Display results
    $display("rm: %x", rm);
    $display("a: %x", a);
    $display("b: %x", b);
    $display("io_rm: %x", io_rm);
    $display("io_a: %x", io_a);
    $display("io_b: %x", io_b);
    $display("io_result: %x", io_result);
    $display("io_fflags: %x", io_fflags);

    // End simulation
    $finish;
  end


endmodule
